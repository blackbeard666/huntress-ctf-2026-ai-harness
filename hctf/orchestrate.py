"""`hctf run`: every released challenge as an independent chain, all chains in parallel.

chain(base) = Single Solve (LLM worker) -> solver proven on its regression case
            -> Time Trial (scripted; fix worker on failure) -> Mastery (scripted; fix worker on failure)

The GM enforces those prerequisites, so each chain is sequential while all chains run concurrently.
Worker slots: local `claude -p` (HCTF_LOCAL_SLOTS) + Homebase `codex exec` (HCTF_HB_SLOTS, credit-gated).
Fix workers racing a deadline skip the slot queue.
"""
import json
import os
import re
import threading
import time
import traceback
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from . import cli, paths, remote, solvers, timed, workers

ROOT = Path(__file__).resolve().parent.parent
CREDIT_SOFT = float(os.environ.get("HCTF_CREDIT_SOFT", "4"))   # below: no new Homebase (codex) workers
CREDIT_HARD = float(os.environ.get("HCTF_CREDIT_HARD", "1.5"))  # below: no new timed starts; VM kept for GM
SINGLE_TIMEOUT = int(os.environ.get("HCTF_SINGLE_TIMEOUT", str(25 * 60)))
GENERALIZE_TIMEOUT = int(os.environ.get("HCTF_GENERALIZE_TIMEOUT", str(12 * 60)))
MAX_SINGLE_LAUNCHES = 3
MAX_TIMED_RETRIES = 5

_print_lock = threading.Lock()


def _by_set(answers):
    """Group answers by their set/slot prefix so each unit submits separately (clearer accept/incorrect)."""
    groups = {}
    for aid, val in answers.items():
        m = re.match(r"(set|slot)[._-]?\d+", aid)
        groups.setdefault(m.group(0) if m else "_", {})[aid] = val
    return groups


def say(msg):
    with _print_lock:
        print(time.strftime("%H:%M:%S"), msg, flush=True)


# ---------------------------------------------------------------- governor

class Governor:
    def __init__(self):
        self._t, self._v, self._lock = 0, None, threading.Lock()

    def credits(self):
        with self._lock:
            if time.time() - self._t > 300 or self._v is None:
                try:
                    self._v = remote.power("status")["credits"]
                except Exception as e:  # noqa: BLE001 - governor must never kill the run
                    say(f"[governor] credit read failed: {e}")
                    self._v = self._v if self._v is not None else 99.0
                self._t = time.time()
            return self._v

    def allow_homebase_workers(self):
        return self.credits() > CREDIT_SOFT

    def allow_timed(self):
        return self.credits() > CREDIT_HARD


# ---------------------------------------------------------------- pools

class Pools:
    def __init__(self, local, homebase, gov):
        self.local = threading.BoundedSemaphore(local) if local else None
        self.hb = threading.BoundedSemaphore(homebase) if homebase else None
        self.gov = gov

    def acquire(self, prefer_homebase=False):
        """Block until a slot is free. Returns 'local' or 'homebase'."""
        while True:
            order = [("homebase", self.hb), ("local", self.local)] if prefer_homebase else \
                    [("local", self.local), ("homebase", self.hb)]
            for name, sem in order:
                if sem is None or (name == "homebase" and not self.gov.allow_homebase_workers()):
                    continue
                if sem.acquire(blocking=False):
                    return name
            time.sleep(2)

    def release(self, name):
        (self.local if name == "local" else self.hb).release()


# ---------------------------------------------------------------- chain state

def set_state(base, **kw):
    p = paths.challenge_root(base) / "chain.json"
    st = json.loads(p.read_text()) if p.exists() else {}
    st.update(kw, updated=time.strftime("%Y-%m-%dT%H:%M:%S"))
    p.write_text(json.dumps(st, indent=2))


def ensure_case_and_test(cid, sdir):
    """Turn the Single Solve's confirmed answers into regression case 'single_solve' and run all cases."""
    contract = cli.load(cid, "start.json")
    art = timed.latest_artifacts(cid)
    conf = cli.confirmed_answers(cid)
    if contract and art and conf and (sdir / "solve.py").exists():
        solvers.add_case(sdir, "single_solve", contract, art, conf)
    if not (sdir / "solve.py").exists():
        return False, "no solve.py"
    res = solvers.test_solver(sdir)
    return bool(res) and all(r["ok"] for r in res), res


def record_timed_case(cid, sdir):
    contract = cli.load(cid, "start.json")
    art = timed.latest_artifacts(cid)
    conf = cli.confirmed_answers(cid)
    if contract and art and conf:
        name = f"{solvers.mode_of(cid)}-{(cli.attempt_id(contract) or 'x')[:8]}"
        solvers.add_case(sdir, name, contract, art, conf)


def capture_variant(cid, sdir):
    """Save the current (unsolved) variant as a regression case so the offline fix worker can work on
    the real bytes. expected.json holds only answers the GM already confirmed (often empty here)."""
    contract = cli.load(cid, "start.json")
    art = timed.latest_artifacts(cid)
    if contract and art:
        name = f"variant-{solvers.mode_of(cid)}-{(cli.attempt_id(contract) or 'x')[:8]}"
        solvers.add_case(sdir, name, contract, art, cli.confirmed_answers(cid))


def wait_until_expired(cid, extra=3):
    """Block until the live attempt's deadline has passed, so a retry will be accepted."""
    contract = cli.load(cid, "start.json")
    left = timed.seconds_left(contract)
    if left and left > 0:
        time.sleep(left + extra)


# ---------------------------------------------------------------- chain

class Chain:
    def __init__(self, base, entries, pools, gov, only_modes=None):
        self.base, self.pools, self.gov = base, pools, gov
        self.entries = {e["mode"]: e for e in entries}
        ss = self.entries.get("single_solve") or next(iter(self.entries.values()))
        self.lane, self.name = ss.get("lane", "misc"), ss.get("name", base)
        self.sdir = paths.solver_dir(base)
        self.root = paths.challenge_root(base)
        self.only_modes = only_modes
        (self.root / "meta.json").write_text(json.dumps({"base": base, "lane": self.lane, "name": self.name,
                                     "ids": {m: e["id"] for m, e in self.entries.items()}}, indent=2, ensure_ascii=False))

    # -- workers
    def run_worker(self, cid, stage, prompt, timeout, urgent=False, prefer_homebase=False):
        env = {"HCTF_CHAL": cid, "HCTF_BASE": self.base, "HCTF_STAGE": stage, "HCTF_SOLVER_DIR": self.sdir,
               "HCTF_CHAL_DIR": cli.cdir(cid), "HCTF_LANE": self.lane}
        pool = "local" if urgent else self.pools.acquire(prefer_homebase)
        set_state(self.base, worker=f"{stage}@{pool}")
        say(f"[{cid}] {stage} worker -> {pool} (timeout {timeout:.0f}s)")
        try:
            if pool == "local":
                rc, log = workers.run_local(cli.cdir(cid), stage, prompt, env, timeout)
            else:
                rc, log = workers.run_homebase(self.root, cli.cdir(cid), stage, prompt, env, timeout)
        finally:
            if not urgent:
                self.pools.release(pool)
            set_state(self.base, worker=None)
        say(f"[{cid}] {stage} worker exit {rc} ({Path(log).name})")
        return rc

    def fix(self, cid, contract, art, problems, left):
        prompt = workers.render("fix", cid=cid, base=self.base, seconds_left=int(left or 0),
                                deadline=contract.get("deadline"), chal_dir=cli.cdir(cid).relative_to(ROOT),
                                solver_dir=self.sdir.relative_to(ROOT),
                                problems="\n".join(f"  - {p}" for p in problems) or "  - (none reported)")
        set_state(self.base, stage=f"{solvers.mode_of(cid)}:fixing")
        self.run_worker(cid, "fix", prompt, max(20, (left or 600) - 15), urgent=True)

    def generalize(self, cid):
        """Offline (no clock): improve the solver so it handles the captured variant and still passes old cases."""
        mode = solvers.mode_of(cid)
        probs = []
        _, res = ensure_case_and_test(paths.base_id(cid), self.sdir)
        for r in (res or []):
            if not r.get("ok"):
                probs.append(f"case {r['case']}: error={r.get('error')} diff={r.get('diff')} unverified={r.get('unverified')}")
        prompt = workers.render("generalize", cid=cid, base=self.base, mode=mode,
                                chal_dir=cli.cdir(cid).relative_to(ROOT), solver_dir=self.sdir.relative_to(ROOT),
                                problems="\n".join(f"  - {p}" for p in probs) or "  - solver did not produce all answers")
        set_state(self.base, stage=f"{mode}:generalizing")
        self.run_worker(cid, "generalize", prompt, GENERALIZE_TIMEOUT)

    def try_existing_solvers(self, cid):
        """Run the whole solver library (all days, matched by question text) against this challenge.
        If it answers every question and the submissions are accepted, copy the winning solver into this
        challenge's solver dir and return True. Returns False to fall through to an LLM worker."""
        contract = cli.load(cid, "start.json") or cli.load(cid, "contract.json")
        art = timed.latest_artifacts(cid)
        if not contract or not art:
            return False
        answers, problems = solvers.solve_contract(contract, art)  # no default -> library only
        ids = contract.get("answer_ids", [])
        if problems or not ids or any(a not in answers for a in ids):
            return False
        set_state(self.base, stage="single:reuse")
        for key, group in _by_set(answers).items():
            kind, body, refused = cli.submit(cid, group)
            if kind not in ("correct", "accepted"):
                say(f"[{cid}] reuse submit {key}: {kind or 'refused'} {json.dumps(body or refused)[:150]}")
                return cli.is_complete(cid)
        if cli.is_complete(cid):
            # adopt the matching solver so this challenge's timed modes reuse it directly
            groups, _ = solvers.dispatch(contract)
            src = next(iter(groups), None)
            if src and src != self.sdir and not (self.sdir / "solve.py").exists():
                import shutil
                self.sdir.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src / "solve.py", self.sdir / "solve.py")
            ensure_case_and_test(self.base, self.sdir)
            return True
        return False

    # -- stages
    def single(self):
        e = self.entries.get("single_solve")
        if not e:
            return True
        cid = e["id"]
        welcome = self.lane == "welcome"
        if cli.is_complete(cid) and (welcome or ensure_case_and_test(cid, self.sdir)[0]):
            return True
        set_state(self.base, stage="single:fetch")
        body, err = timed.ensure_started(cid)
        try:
            from . import triage as triage_mod
            triage_mod.triage(cid)  # deterministic grounding before the LLM worker starts
        except Exception as e:  # noqa: BLE001 - triage is best-effort
            say(f"[{cid}] triage note: {e}")
        # Reuse-first: a prior day's solver (matched by question text) may already solve this. No model time.
        if not welcome and self.try_existing_solvers(cid):
            say(f"[{cid}] solved by existing solver library (no worker needed)")
            return True
        if body is None:
            # e.g. read-the-rules: no artifact, but the contract still names the answer ids
            st = cli.call(cid, "status", cid)["body"] or {}
            if st.get("answer_ids") or st.get("questions"):
                cli.save(cid, "contract.json", st)
                if not cli.load(cid, "start.json"):
                    cli.save(cid, "start.json", st)
        timed_info = []
        for m in ("time_trial", "mastery"):
            if m in self.entries:
                tcid = self.entries[m]["id"]
                st = cli.call(tcid, "status", tcid)["body"] or {}
                if st.get("questions"):
                    cli.save(tcid, "contract.json", st)
                timed_info.append(f"  - {m}: `{tcid}` -> `{cli.cdir(tcid).relative_to(ROOT)}/contract.json`")
        for n in range(MAX_SINGLE_LAUNCHES):
            extra = ""
            notes = cli.cdir(cid) / "notes.md"
            if n and notes.exists():
                extra = (f"\nThis is relaunch #{n}: a previous worker stopped before finishing. Read `{notes.relative_to(ROOT)}` "
                         "first, do not repeat its dead ends, and pick the most promising unexplored lead.")
            if welcome:
                extra += "\nThis is an orientation challenge: no solver is needed, only a correct submission."
            prompt = workers.render("single", name=self.name, cid=cid, lane=self.lane,
                                    chal_dir=cli.cdir(cid).relative_to(ROOT), solver_dir=self.sdir.relative_to(ROOT),
                                    timed_contracts="\n".join(timed_info) or "  - (none: Single Solve only)", extra=extra)
            set_state(self.base, stage="single:solving", launches=n + 1)
            heavy = self.lane in ("binary-reverse-engineering", "binary")
            self.run_worker(cid, "single", prompt, SINGLE_TIMEOUT, prefer_homebase=heavy)
            done = cli.is_complete(cid)
            ok, res = (True, None) if welcome else ensure_case_and_test(cid, self.sdir)
            say(f"[{cid}] after worker: complete={done} solver_ok={ok}")
            if done and ok:
                return True
            if (cli.cdir(cid) / "HELP.md").exists():
                set_state(self.base, stage="single:help", help=(cli.cdir(cid) / "HELP.md").read_text()[:1500])
                return False
        set_state(self.base, stage="single:blocked")
        return False

    def timed_stage(self, mode):
        e = self.entries.get(mode)
        if not e:
            return True
        cid = e["id"]
        if cli.is_complete(cid):
            return True
        for attempt in range(MAX_TIMED_RETRIES + 1):
            while not self.gov.allow_timed():
                set_state(self.base, stage=f"{mode}:waiting-credits")
                time.sleep(300)
            set_state(self.base, stage=f"{mode}:running", attempt=attempt + 1)
            # Clock-critical path runs ON Homebase (adjacent to the GM; ~6s windows).
            res = timed.run(cid, self.sdir, log=say)
            say(f"[{cid}] result: {res}")
            set_state(self.base, **{f"{mode}_result": res})
            if res == "correct":
                record_timed_case(cid, self.sdir)
                return True
            if res.startswith("error:prerequisite"):
                time.sleep(20)  # CourseStack scoring may still be pending for the previous mode
                continue
            if res not in ("expired", "blocked"):
                break
            # A failed timed attempt means the solver is wrong or incomplete for this variant (with Homebase
            # execution the window is no longer the bottleneck). Always improve the solver offline, then retry.
            # The generalize worker re-derives the variant's correct answers itself (ground truth), so it can
            # fix WRONG answers too, not just missing ones. Fetch the variant locally for it to work on.
            try:
                timed.ensure_started(cid)  # local start+download of the current variant for offline work
            except Exception as e:  # noqa: BLE001
                say(f"[{cid}] local fetch for generalize failed: {e}")
            capture_variant(cid, self.sdir)
            say(f"[{cid}] {res}: improving the solver offline for this variant, then retrying")
            self.generalize(cid)
        set_state(self.base, stage=f"{mode}:blocked")
        return False

    def run(self):
        try:
            set_state(self.base, stage="queued", name=self.name, lane=self.lane, worker=None)
            modes = self.only_modes or ["single_solve", "time_trial", "mastery"]
            if "single_solve" in modes and not self.single():
                return
            for mode in ("time_trial", "mastery"):
                if mode in modes and not self.timed_stage(mode):
                    return
            set_state(self.base, stage="done")
            say(f"[{self.base}] chain complete")
        except Exception:  # noqa: BLE001 - one chain must never take down the others
            set_state(self.base, stage="crashed", error=traceback.format_exc()[-2000:])
            say(f"[{self.base}] CRASHED:\n{traceback.format_exc()}")


# ---------------------------------------------------------------- entry points

_provisioned = False


def ensure_homebase_provisioned():
    """Provision Homebase's solver deps once per process (idempotent; cheap if already installed).
    A factory reset wipes them, so this guarantees hb_timed can run any solver next to the GM."""
    global _provisioned
    if _provisioned:
        return
    try:
        remote.rsync_to(ROOT / "setup" / "homebase_setup.sh", "~/homebase_setup.sh")
        r = remote.ssh("bash ~/homebase_setup.sh 2>&1 | tail -2", timeout=600, check=False)
        say(f"[homebase] provisioned: {r.stdout.strip()[-160:]}")
        _provisioned = True
    except Exception as e:  # noqa: BLE001 - provisioning best-effort; hb_timed will surface real gaps
        say(f"[homebase] provisioning note: {e}")


def released_challenges(day=None):
    args = ["list", "--all"] if day is None else ["list", "--day", str(day)]
    body = cli.call(None, *args)["body"] or {}
    return body.get("challenges", [])


def run(day=None, only=None, local_slots=5, hb_slots=0, modes=None):
    remote.ensure_up()
    remote.deploy()
    ensure_homebase_provisioned()  # solvers run on Homebase (hb_timed); make sure their deps are present
    gov = Governor()
    pools = Pools(local_slots, hb_slots, gov)
    groups = {}
    for c in released_challenges(day):
        groups.setdefault(solvers.base_id(c["id"]), []).append(c)
    if only:
        groups = {b: v for b, v in groups.items() if any(o in b for o in only)}
    say(f"{len(groups)} chains ({sum(map(len, groups.values()))} challenge modes), "
        f"slots local={local_slots} homebase={hb_slots}, credits={gov.credits()}")
    with ThreadPoolExecutor(max_workers=max(1, len(groups))) as ex:
        for base, entries in sorted(groups.items()):
            ex.submit(Chain(base, entries, pools, gov, modes).run)
    say("all chains finished")


def chain_for(cid, pools, gov):
    """Build a Chain for one challenge from the local index (no extra list call needed)."""
    base = paths.base_id(cid)
    info = paths.lookup(base) or {}
    entries = [{"id": base if m == "single_solve" else f"{base}/{m}", "mode": m,
                "lane": info.get("lane", "misc"), "name": info.get("name", base)} for m in paths.MODES]
    if info.get("lane") == "welcome":
        entries = entries[:1]
    return Chain(base, entries, pools, gov)


def run_one_timed(cid, local_slots=2):
    gov = Governor()
    chain = chain_for(cid, Pools(local_slots, 0, gov), gov)
    ok = chain.timed_stage(paths.mode_of(cid))
    return 0 if ok else 1


def dashboard():
    rows = []
    for p in sorted(paths.CHALLENGES.glob("day*/*/chain.json")):
        s = json.loads(p.read_text())
        rows.append((str(p.parent.relative_to(paths.CHALLENGES)), s.get("lane", ""), s.get("stage", ""), s.get("worker") or "",
                     s.get("time_trial_result", ""), s.get("mastery_result", ""), s.get("updated", "")))
    w = [max(len(str(r[i])) for r in rows + [("chain", "lane", "stage", "worker", "tt", "mastery", "updated")])
         for i in range(7)]
    for r in [("chain", "lane", "stage", "worker", "tt", "mastery", "updated")] + rows:
        print("  ".join(str(x).ljust(w[i]) for i, x in enumerate(r)))
