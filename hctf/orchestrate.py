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
import shutil
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
# Time Trial scouting before Mastery (hctf/scout.py): extra TT attempts that harvest new variants and learn label
# spellings on the cheap clock. 0 = off. `hctf run --scout N` overrides.
SCOUT_ROUNDS = int(os.environ.get("HCTF_SCOUT_ROUNDS", "0"))
SCOUT_CLEAN = int(os.environ.get("HCTF_SCOUT_CLEAN", "2"))          # stop after this many clean rounds in a row
SCOUT_GENERALIZE = int(os.environ.get("HCTF_SCOUT_GENERALIZE", "2"))  # offline fix cycles between scout bursts

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
    """Credits only gate the OPTIONAL Homebase codex pool now. GM access and timed runs go direct over
    the pairing token, so they no longer depend on credits. When Homebase is unused, credits aren't read."""

    def __init__(self, hb_enabled=False):
        self._t, self._v, self._lock = 0, None, threading.Lock()
        self.hb_enabled = hb_enabled

    def credits(self):
        if not self.hb_enabled:
            return 99.0  # Homebase unused: credits gate nothing, and reading them spins up the browser session
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
        return self.hb_enabled and self.credits() > CREDIT_SOFT

    def allow_timed(self):
        return True  # timed runs locally against the public GM; no credit gate


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
    art = timed.artifacts_for(cid, contract)
    if contract and art:
        name = f"variant-{solvers.mode_of(cid)}-{(cli.attempt_id(contract) or 'x')[:8]}"
        solvers.add_case(sdir, name, contract, art, timed.present_only(contract, art, cli.confirmed_answers(cid)))


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
                                solver_dir=self.sdir.relative_to(ROOT), persona=workers.lane_persona(self.lane),
                                problems="\n".join(f"  - {p}" for p in problems) or "  - (none reported)")
        set_state(self.base, stage=f"{solvers.mode_of(cid)}:fixing")
        self.run_worker(cid, "fix", prompt, max(20, (left or 600) - 15), urgent=True)

    def generalize(self, cid, wrong=None, fixed=None, diag=None):
        """Offline (no clock): improve the solver so it handles the captured variant and still passes old cases.
        `wrong`: (answer_id, solver_value) pairs the GM rejected; `fixed`: {answer_id: value} the GM accepted as the
        right label on that attempt; `diag`: facts about the attempt (window, elapsed, how much was judged), so the
        worker is told the truth — "timing" only when every field was actually judged correct."""
        mode = solvers.mode_of(cid)
        probs = []
        _, res = ensure_case_and_test(paths.base_id(cid), self.sdir)
        for r in (res or []):
            if not r.get("ok"):
                probs.append(f"case {r['case']}: error={r.get('error')} diff={r.get('diff')} unverified={r.get('unverified')}")
        lines = []
        for a, v in (wrong or []):
            if fixed and a in fixed:
                lines.append(f"  - `{a}`: solver produced {v!r}; the GM REJECTED it and ACCEPTED {fixed[a]!r} on the same "
                             "attempt. Find the byte-level feature that selects this label (compare with cases where the "
                             "solver's label was right) and make solve.py emit it — never hard-code the variant.")
            else:
                lines.append(f"  - `{a}`: solver produced {v!r}, the GM judged this INCORRECT — re-derive this exact field "
                             "from the bytes and make the solver reproduce the GM's value")
        d = diag or {}
        if lines:
            gm_wrong = "\n".join(lines)
        elif wrong == [] and d.get("complete") and d.get("probed") == d.get("total"):
            gm_wrong = (f"  - every one of the {d.get('total')} fields was judged CORRECT individually, so this is a TIMING "
                        f"failure: window {d.get('window')}s, attempt took {d.get('elapsed')}s, phases {d.get('phases')}. "
                        "Do NOT change answers; reduce the solver's own time only if `solve` dominates the phases.")
        elif wrong == []:
            gm_wrong = (f"  - the probe was CUT SHORT: only {d.get('probed')}/{d.get('total')} fields were judged (all of those "
                        f"correct). The wrong field(s) are among the unjudged ones: {d.get('unjudged', [])[:40]}. "
                        "Re-derive those from the bytes. Do NOT treat this as a timing problem.")
        else:
            gm_wrong = "  - (no per-field GM verdict was available this cycle)"
        if d.get("window") or d.get("elapsed"):
            gm_wrong += f"\n  - attempt facts: window {d.get('window')}s, elapsed {d.get('elapsed')}s, routed {d.get('routed') or 'local'}"
        prompt = workers.render("generalize", cid=cid, base=self.base, mode=mode,
                                chal_dir=cli.cdir(cid).relative_to(ROOT), solver_dir=self.sdir.relative_to(ROOT),
                                persona=workers.lane_persona(self.lane), playbook=workers.lane_playbook(self.lane),
                                problems="\n".join(f"  - {p}" for p in probs) or "  - solver did not produce all answers",
                                gm_wrong=gm_wrong)
        set_state(self.base, stage=f"{mode}:generalizing")
        self._snapshot_solver()
        try:
            self.run_worker(cid, "generalize", prompt, GENERALIZE_TIMEOUT)
        finally:
            self._accept_or_restore(cid)

    # -- transactional generalize: a worker that is killed / times out / breaks old cases must never leave a
    #    half-edited solver behind (happened twice on the rehearsal copy: warmups solve.py, Dim and Dimmer vbsplan.py).
    def _snap_dir(self):
        return self.root / ".generalize-snapshot"

    def _snapshot_solver(self):
        snap = self._snap_dir()
        if snap.exists():
            shutil.rmtree(snap)
        if self.sdir.exists():
            shutil.copytree(self.sdir, snap, ignore=shutil.ignore_patterns("__pycache__"))
        # Baseline: which cases pass BEFORE the worker. Unverified variant cases are legitimately red; the bar is
        # "nothing that passed may break", not "everything green".
        try:
            res = solvers.test_solver(self.sdir) if (self.sdir / "solve.py").exists() else []
            self._baseline = {r.get("case") for r in (res or []) if r.get("ok")}
        except Exception:  # noqa: BLE001
            self._baseline = set()

    def _restore_snapshot(self, why):
        snap = self._snap_dir()
        if not snap.exists():
            return
        rejected = self.root / ".generalize-rejected"
        if rejected.exists():
            shutil.rmtree(rejected)
        if self.sdir.exists():
            shutil.move(str(self.sdir), str(rejected))   # kept for inspection; never imported by the dispatcher
        shutil.move(str(snap), str(self.sdir))
        say(f"[{self.base}] generalize REJECTED ({why}); solver restored to its pre-worker state "
            f"(worker's version kept in {rejected.relative_to(ROOT)})")

    def _accept_or_restore(self, cid):
        """After the generalize worker exits for ANY reason: keep its edits only if every case that passed before
        still passes (and the solver still runs at all)."""
        snap = self._snap_dir()
        if not snap.exists():
            return
        try:
            res = solvers.test_solver(self.sdir) if (self.sdir / "solve.py").exists() else []
        except Exception as e:  # noqa: BLE001
            res = None
            err = repr(e)
        passed = {r.get("case") for r in (res or []) if r.get("ok")}
        broken = sorted(getattr(self, "_baseline", set()) - passed)
        if res and not broken:
            shutil.rmtree(snap)
            gained = sorted(passed - getattr(self, "_baseline", set()))
            if gained:
                say(f"[{self.base}] generalize accepted: now also passes {gained[:6]}")
            return
        self._restore_snapshot(f"broke previously-passing cases {broken[:6]}" if res else
                               f"solver no longer runs ({err if res is None else 'no solve.py / no cases'})")

    def recover_interrupted_generalize(self):
        """A snapshot left on disk means the orchestrator died mid-generalize (killed run): restore it."""
        if self._snap_dir().exists():
            self._restore_snapshot("previous run was interrupted mid-generalize")

    def try_existing_solvers(self, cid):
        """Run the whole solver library (all days, matched by question text) against this challenge.
        If it answers every question and the submissions are accepted, copy the winning solver into this
        challenge's solver dir and return True. Returns False to fall through to an LLM worker."""
        contract = cli.load(cid, "start.json") or cli.load(cid, "contract.json")
        art = timed.latest_artifacts(cid)
        if not contract or not art:
            return False
        groups, _ = solvers.dispatch(contract)
        # A compound bundle is split across days by question text; one newer solver often covers ALL of it.
        whole, answers = (solvers.whole_contract_solver(contract, art, list(groups)) if len(groups) > 1
                          else (None, {}))
        problems = []
        if not whole:
            answers, problems = solvers.solve_contract(contract, art, try_whole=False)  # library only, split
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
            src = whole or next(iter(groups), None)
            if src and src != self.sdir and not (self.sdir / "solve.py").exists():
                import shutil
                self.sdir.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src / "solve.py", self.sdir / "solve.py")
            ensure_case_and_test(self.base, self.sdir)
            return True
        return False

    def auto_labels(self, cid, budget=12):
        """No-model fallback after a Single Solve worker stops short: for each still-unconfirmed field whose ending
        has a known label vocabulary (lib/vocab.json / sibling confirmed labels), run the label resolver with the
        solver's own value as the term source. Returns cli.is_complete(cid)."""
        from . import labels
        contract = cli.load(cid, "start.json")
        art = timed.latest_artifacts(cid)
        if not contract or not art or not (self.sdir / "solve.py").exists():
            return False
        try:
            answers, _ = solvers.solve_contract(contract, art, default_solver=self.sdir)
        except Exception:  # noqa: BLE001
            return False
        conf = cli.confirmed_answers(cid)
        vocab = labels.load_vocab()
        for aid in contract.get("answer_ids") or []:
            has_playbook = bool(labels.playbook and labels.playbook.entry_for(self.lane, aid))
            if aid in conf or (labels.ending(aid) not in vocab and not labels.sibling_labels(aid) and not has_playbook):
                continue
            cands = labels.candidates(cid, aid, solver_value=answers.get(aid), lane=self.lane)
            if answers.get(aid) and answers[aid] not in labels.judged_wrong(cid, aid):
                cands = [answers[aid]] + cands
            r = labels.probe(cid, aid, cands, budget=budget, log=say)
            say(f"[{cid}] auto-labels {aid}: {r.get('accepted') or 'not resolved'} ({len(r.get('tried', []))} tried)")
        return cli.is_complete(cid)

    # -- stages
    def single(self):
        e = self.entries.get("single_solve")
        if not e:
            return True
        cid = e["id"]
        welcome = self.lane == "welcome"
        if cli.is_complete(cid) or cli.gm_solved(cid):
            # Solved: a solver that exists is good enough to proceed. Failing auto-* variant cases are the timed
            # stages' business (they feed the generalize worker); they must not relaunch the Single Solve worker.
            if welcome or (self.sdir / "solve.py").exists() or all(
                    cli.gm_solved(self.entries[m]["id"]) for m in ("time_trial", "mastery") if m in self.entries):
                if not welcome:
                    ok, _ = ensure_case_and_test(cid, self.sdir)
                    say(f"[{cid}] already solved (solver regression {'ok' if ok else 'has failing cases'})")
                return True
        set_state(self.base, stage="single:fetch")
        body, err = timed.ensure_started(cid)
        # The GM sometimes hands the flag back directly (issued_flag, e.g. orientation challenges). Use it instead of
        # solving when there's a single answer_id to put it in — a free first-blood the harness used to discard.
        fb = body or {}
        if fb.get("issued_flag") and len(fb.get("answer_ids") or []) == 1 and not cli.is_complete(cid):
            cli.submit(cid, {fb["answer_ids"][0]: fb["issued_flag"]})
            if cli.is_complete(cid):
                say(f"[{cid}] solved via GM issued_flag (no solver needed)")
                return True
        # Reuse-first (no model time): a prior solver matched by question text may already solve this. Try it
        # BEFORE triage so a hit skips triage and the LLM worker entirely — the fastest path to first blood.
        if not welcome and self.try_existing_solvers(cid):
            say(f"[{cid}] solved by existing solver library (no worker needed)")
            return True
        try:
            from . import triage as triage_mod
            triage_mod.triage(cid)  # deterministic grounding before the LLM worker starts
        except Exception as e:  # noqa: BLE001 - triage is best-effort
            say(f"[{cid}] triage note: {e}")
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
                                    persona=workers.lane_persona(self.lane), playbook=workers.lane_playbook(self.lane),
                                    chal_dir=cli.cdir(cid).relative_to(ROOT), solver_dir=self.sdir.relative_to(ROOT),
                                    timed_contracts="\n".join(timed_info) or "  - (none: Single Solve only)", extra=extra)
            set_state(self.base, stage="single:solving", launches=n + 1)
            heavy = self.lane in ("binary-reverse-engineering", "binary")
            self.run_worker(cid, "single", prompt, SINGLE_TIMEOUT, prefer_homebase=heavy)
            done = cli.is_complete(cid)
            if not done and not welcome:
                done = self.auto_labels(cid)
            ok, res = (True, None) if welcome else ensure_case_and_test(cid, self.sdir)
            say(f"[{cid}] after worker: complete={done} solver_ok={ok}")
            if done and ok:
                # Cache the Single Solve's confirmed closed-vocab labels into vocab.json NOW (untimed), so the timed
                # modes enter with those spellings already confirmed and never carry an unconfirmed label onto a clock.
                try:
                    from . import labels
                    labels.record_from_confirmed(cid, lane=self.lane, log=say)
                except Exception as e:  # noqa: BLE001 - label caching is best-effort
                    say(f"[{cid}] label cache note: {e}")
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
        if cli.is_complete(cid) or cli.gm_solved(cid):
            return True
        for attempt in range(MAX_TIMED_RETRIES + 1):
            while not self.gov.allow_timed():
                set_state(self.base, stage=f"{mode}:waiting-credits")
                time.sleep(300)
            set_state(self.base, stage=f"{mode}:running", attempt=attempt + 1)
            # Clock-critical path runs locally against the public GM (pairing token; ~6s windows).
            res = timed.run(cid, self.sdir, log=say)
            say(f"[{cid}] result: {res}")
            set_state(self.base, **{f"{mode}_result": res})
            if res == "correct":
                record_timed_case(cid, self.sdir)
                return True
            if res.startswith("error:prerequisite"):
                # The GM's status shows only the LATEST attempt: if a scout/probe attempt after the Time Trial pass
                # left it expired, re-pass the Time Trial so Mastery's prerequisite is satisfied again.
                tt = self.entries.get("time_trial")
                if mode == "mastery" and tt and not cli.gm_latest_correct(tt["id"]):
                    say(f"[{cid}] prerequisite: latest Time Trial attempt is not CORRECT; re-passing it")
                    self.ensure_latest_pass(tt["id"])
                else:
                    time.sleep(20)  # CourseStack scoring may still be pending for the previous mode
                continue
            if res not in ("expired", "blocked"):
                break
            last = timed.last_result(cid) or {}
            if (res == "expired" and (last.get("phases") or {}).get("solve") is not None and not last.get("missing")
                    and attempt < MAX_TIMED_RETRIES):
                # The solver answered everything and the CLOCK ran out: a transport/timing failure. Probing can't judge
                # anything on an expired clock and a generalize worker can't speed up the network (rehearsal copy,
                # Dim and Dimmer mastery: 0/462 judged, worker concluded "solver correct, timing"). Just retry.
                say(f"[{cid}] expired on the CLOCK (in-window {last.get('in_window')}s / window {last.get('window')}s, "
                    f"phases {last.get('phases')}): timing, not the solver -- retrying without probe/generalize")
                set_state(self.base, stage=f"{mode}:timing")
                time.sleep(8)
                continue
            # A failed timed attempt means the solver is wrong or incomplete for this variant (with Homebase
            # execution the window is no longer the bottleneck). Always improve the solver offline, then retry.
            # The generalize worker re-derives the variant's correct answers itself (ground truth), so it can
            # fix WRONG answers too, not just missing ones. Fetch the variant locally for it to work on.
            wrong, fixed, diag = None, None, {}
            last = timed.last_result(cid) or {}
            diag = {k: last.get(k) for k in ("window", "elapsed", "phases", "routed")}
            if last.get("wrong") is not None:
                # The timed runner already localized this attempt in-window (same variant, saved as an auto-* case
                # with the GM-verified answers): use that instead of burning a fresh attempt on a different variant.
                wrong = [tuple(x) for x in last["wrong"]]
                fixed = last.get("fixed") or {}
                diag.update(complete=bool(last.get("localize_complete")), probed=None, total=None)
                if not wrong and not last.get("localize_complete"):
                    wrong = None  # cut short with nothing found: fall back to the probe below
            if wrong is None:
                try:
                    timed.ensure_started(cid)  # fresh attempt + download of the current variant for offline work
                    wrong = timed.probe_fields(cid, self.sdir, log=say)  # binary search, per-field verdicts
                    pd = json.loads((cli.cdir(cid) / "diagnosis.json").read_text())
                    diag.update({k: pd.get(k) for k in ("complete", "probed", "total", "unjudged")})
                except Exception as e:  # noqa: BLE001
                    say(f"[{cid}] local fetch/probe for generalize failed: {e}")
                capture_variant(cid, self.sdir)  # expected.json now enriched by the probe-confirmed fields
            # Online label resolution FIRST: for closed-vocab label fields, probe the GM (the only authority on the
            # spelling) rather than letting the offline generalize worker GUESS and burn another attempt (the Q6 pain).
            if wrong:
                try:
                    got = timed.resolve_labels_online(cid, self.sdir, [a for a, _ in wrong], self.lane, log=say)
                except Exception as e:  # noqa: BLE001
                    got = set()
                    say(f"[{cid}] online label resolve note: {e}")
                if got:
                    if cli.is_complete(cid):
                        set_state(self.base, **{f"{mode}_result": "correct"})
                        record_timed_case(cid, self.sdir)
                        return True
                    wrong = [(a, v) for a, v in wrong if a not in got]
                    if not wrong:
                        say(f"[{cid}] resolved {len(got)} label(s) online (cached); retrying without generalize")
                        continue
            say(f"[{cid}] {res}: improving the solver offline for this variant, then retrying")
            self.generalize(cid, wrong=wrong, fixed=fixed, diag=diag)
        set_state(self.base, stage=f"{mode}:blocked")
        return False

    def ensure_latest_pass(self, cid, tries=3):
        """Make the GM's LATEST attempt for this timed mode CORRECT (after scouting), so a prerequisite check that
        reads the latest status sees a pass. The solve itself is already banked on the scoreboard."""
        from . import scout
        for _ in range(tries):
            if cli.gm_latest_correct(cid):
                return True
            scout._wait_expired((timed.last_result(cid) or {}).get("deadline"), say, cid)
            time.sleep(scout.RATE_GAP)
            timed.run(cid, self.sdir, log=say)
        return cli.gm_latest_correct(cid)

    def scout_stage(self):
        """Between a passed Time Trial and Mastery: run Time Trial scout rounds (new variant each) so unseen
        constructs get their GM label on the cheap clock; generalize offline on fields the in-window corrector
        couldn't fix; finally leave the latest Time Trial attempt CORRECT. Advisory: Mastery runs regardless."""
        tt, ms = self.entries.get("time_trial"), self.entries.get("mastery")
        if not SCOUT_ROUNDS or not tt or not ms or cli.gm_solved(ms["id"]):
            return
        from . import scout
        cid = tt["id"]
        s = {}
        for cycle in range(SCOUT_GENERALIZE + 1):
            set_state(self.base, stage="time_trial:scouting", scout_cycle=cycle + 1)
            s = scout.scout(cid, self.sdir, rounds=SCOUT_ROUNDS, clean=SCOUT_CLEAN, log=say)
            set_state(self.base, scout={"cycle": cycle + 1, "clean_streak": s["clean_streak"],
                                        "new_labels": s["new_labels"], "fixed": s["fixed"],
                                        "unresolved": s["unresolved"][:20], "solver_failed": s.get("solver_failed")})
            if (not s["unresolved"] and not s.get("solver_failed")) or cycle == SCOUT_GENERALIZE:
                break
            last = timed.last_result(cid) or {}
            say(f"[{cid}] scout found {len(s['unresolved'])} unresolved field(s); generalizing before Mastery")
            self.generalize(cid, wrong=s["unresolved"] or None, fixed=s["fixed"],
                            diag={k: last.get(k) for k in ("window", "elapsed", "phases", "routed")})
        ok = self.ensure_latest_pass(cid)
        say(f"[{cid}] scouting done: clean_streak={s.get('clean_streak')} new_labels={len(s.get('new_labels') or {})} "
            f"unresolved={len(s.get('unresolved') or [])}; latest Time Trial {'CORRECT' if ok else 'NOT correct'}")

    def run(self):
        try:
            set_state(self.base, stage="queued", name=self.name, lane=self.lane, worker=None)
            self.recover_interrupted_generalize()
            modes = self.only_modes or ["single_solve", "time_trial", "mastery"]
            if "single_solve" in modes and not self.single():
                return
            for mode in ("time_trial", "mastery"):
                if mode == "mastery" and mode in modes:
                    self.scout_stage()   # no-op unless SCOUT_ROUNDS > 0
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


def run(day=None, only=None, local_slots=5, hb_slots=0, modes=None, prewarm_homebase=None, keep_homebase=None,
        scout_rounds=None):
    global SCOUT_ROUNDS
    if scout_rounds is not None:
        SCOUT_ROUNDS = scout_rounds
    if keep_homebase is None:
        keep_homebase = os.environ.get("HCTF_KEEP_HOMEBASE", "0") != "0"
    timed_in_scope = (not modes) or any(m in ("time_trial", "mastery") for m in modes)
    if prewarm_homebase is None:
        # Default ON for timed runs: boot + provision Homebase in the BACKGROUND at run start, so a tight-window
        # failover never waits on a cold VM (start it immediately, don't wait for an expiry — user request). Singles
        # run locally while it boots, so the warm VM costs ~nothing extra. Disable with HCTF_PREWARM_HOMEBASE=0.
        prewarm_homebase = (workers.AUTO_HOMEBASE and timed_in_scope and not hb_slots
                            and os.environ.get("HCTF_PREWARM_HOMEBASE", "1") != "0")
    if hb_slots:  # Homebase is opt-in now (extra codex pool); GM + timed run locally via the pairing token
        remote.ensure_up()
        remote.deploy()
        ensure_homebase_provisioned()  # codex workers run on Homebase; make sure their deps are present
    elif prewarm_homebase:
        # Boot + provision Homebase in the background NOW, so it's already up when a tight timed window needs it
        # (the on-demand path blocks on the same lock, so no cold-start stall mid-clock). Powered off at run end.
        threading.Thread(target=workers._homebase_ready, args=(say,), daemon=True).start()
        say("[homebase] pre-warming in the background for tight timed windows (powers off at end of run)")
    gov = Governor(hb_enabled=bool(hb_slots))
    pools = Pools(local_slots, hb_slots, gov)
    groups = {}
    for c in released_challenges(day):
        groups.setdefault(solvers.base_id(c["id"]), []).append(c)
    if only:
        groups = {b: v for b, v in groups.items() if any(o in b for o in only)}
    say(f"{len(groups)} chains ({sum(map(len, groups.values()))} challenge modes), "
        f"slots local={local_slots} homebase={hb_slots}, credits={gov.credits()}")
    try:
        with ThreadPoolExecutor(max_workers=max(1, len(groups))) as ex:
            for base, entries in sorted(groups.items()):
                ex.submit(Chain(base, entries, pools, gov, modes).run)
    finally:
        if not hb_slots and not keep_homebase:  # Homebase switched on only for tight timed windows: switch it off again
            workers.power_off_homebase_if_ours(say)
        elif keep_homebase:
            say("[homebase] left running (--keep-homebase); power it off with `hctf hb off` when done")
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
    try:
        ok = chain.timed_stage(paths.mode_of(cid))
    finally:
        if os.environ.get("HCTF_KEEP_HOMEBASE", "0") == "0":
            workers.power_off_homebase_if_ours(say)
    return 0 if ok else 1


def _mode_solved_local(cid):
    """Local, network-free truth for whether a mode is solved: the gm_solved sticky marker or any recorded
    CORRECT submission. The live chain.json `stage` lags (it tracks worker activity, not per-mode completion),
    so a passed single_solve with timed stages still running used to display as `single:solving`."""
    try:
        return (cli.cdir(cid) / "solved_once").exists() or cli.ever_correct(cid)
    except Exception:  # noqa: BLE001 - unknown means "not known solved"
        return False


def dashboard():
    hdr = ("chain", "lane", "stage", "worker", "single", "tt", "mastery", "updated")
    rows = []
    for p in sorted(paths.CHALLENGES.glob("day*/*/chain.json")):
        s = json.loads(p.read_text())
        try:
            ids = (json.loads((p.parent / "meta.json").read_text()) or {}).get("ids", {})
        except (OSError, ValueError):
            ids = {}
        # Per-mode solved from local truth, falling back to the chain's recorded result (never the stale stage).
        single = "correct" if ids.get("single_solve") and _mode_solved_local(ids["single_solve"]) else ""
        tt = "correct" if (ids.get("time_trial") and _mode_solved_local(ids["time_trial"])) else s.get("time_trial_result", "")
        mastery = "correct" if (ids.get("mastery") and _mode_solved_local(ids["mastery"])) else s.get("mastery_result", "")
        rows.append((str(p.parent.relative_to(paths.CHALLENGES)), s.get("lane", ""), s.get("stage", ""),
                     s.get("worker") or "", single, tt, mastery, s.get("updated", "")))
    w = [max(len(str(r[i])) for r in rows + [hdr]) for i in range(len(hdr))]
    for r in [hdr] + rows:
        print("  ".join(str(x).ljust(w[i]) for i, x in enumerate(r)))
