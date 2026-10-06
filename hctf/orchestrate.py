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
import sys
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
CHAIN_CRASH_RETRIES = int(os.environ.get("HCTF_CHAIN_CRASH_RETRIES", "1"))  # re-run a crashed chain (done modes skip)
# Early handoff: once the Single Solve is CORRECT and a snapshot of the still-running worker's solver reproduces
# its confirmed answers, make ONE speculative Time Trial -> Mastery pass from that snapshot instead of idling until
# the worker exits (rehearsal Day 5: answers CORRECT at T+3:10, worker hardened the solver until T+6:25).
BASELINE_CASE_TIMEOUT = float(os.environ.get("HCTF_BASELINE_CASE_TIMEOUT", "8"))  # > any 6-7s window  # pre-generalize regression baseline
REUSE_PROBE_BUDGET = int(os.environ.get("HCTF_REUSE_PROBE_BUDGET", "20"))  # merged-reuse submits before the worker
STOP_WHEN_READY = os.environ.get("HCTF_STOP_WHEN_READY", "1") != "0"  # end the single worker at CORRECT + verified solver
SPEC_STABLE = float(os.environ.get("HCTF_SPEC_STABLE", "2"))  # solver files untouched this long before a snapshot
SPEC_POLL = float(os.environ.get("HCTF_SPEC_POLL", "1"))
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

_state_lock = threading.Lock()


def set_state(base, **kw):
    p = paths.challenge_root(base) / "chain.json"
    with _state_lock:
        try:
            st = json.loads(p.read_text()) if p.exists() else {}
        except ValueError:
            st = {}
        st.update(kw, updated=time.strftime("%Y-%m-%dT%H:%M:%S"))
        tmp = p.with_name(f".chain.json.{threading.get_ident()}")
        tmp.write_text(json.dumps(st, indent=2))
        os.replace(tmp, p)  # atomic: `hctf dash`/`why` never read a half-written file


def _rel(p):
    """Path for a worker prompt: project-relative when possible."""
    try:
        return Path(p).relative_to(ROOT)
    except (ValueError, TypeError):
        return p


def ensure_case_and_test(cid, sdir, full=True):
    """Turn the Single Solve's confirmed answers into regression case 'single_solve' and run all cases
    (full=False: only record the case -- the caller already verified the solver on it)."""
    contract = cli.load(cid, "start.json")
    art = timed.latest_artifacts(cid)
    conf = cli.confirmed_answers(cid)
    if contract and art and conf and (sdir / "solve.py").exists():
        solvers.add_case(sdir, "single_solve", contract, art, conf)
    if not (sdir / "solve.py").exists():
        return False, "no solve.py"
    if not full:
        return True, None
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
    def run_worker(self, cid, stage, prompt, timeout, urgent=False, prefer_homebase=False, stop=None):
        env = {"HCTF_CHAL": cid, "HCTF_BASE": self.base, "HCTF_STAGE": stage, "HCTF_SOLVER_DIR": self.sdir,
               "HCTF_CHAL_DIR": cli.cdir(cid), "HCTF_LANE": self.lane}
        pool = "local" if urgent else self.pools.acquire(prefer_homebase)
        set_state(self.base, worker=f"{stage}@{pool}")
        say(f"[{cid}] {stage} worker -> {pool} (timeout {timeout:.0f}s)")
        try:
            if pool == "local":
                rc, log = workers.run_local(cli.cdir(cid), stage, prompt, env, timeout, stop=stop)
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
        if d.get("hb_env_mismatch"):
            gm_wrong += ("\n  - THE SOLVER PRODUCED NO ANSWERS ON HOMEBASE although it works locally: it depends on something the "
                         "Homebase VM lacks. Homebase has python3 + the pip deps (pyzipper, pyelftools, pefile, capstone, "
                         "pycryptodome, androguard, ...) but NOT 7z/p7zip or other apt tools. Open zips with "
                         "`lib.common.read_member` / pyzipper; no subprocess to 7z, jadx, or anything outside the import list.")
        if d.get("solver_too_slow"):
            gm_wrong += ("\n  - THE SOLVER IS TOO SLOW: solve.py hit the in-window timeout on this variant (answers may well be right). "
                         "Make it fast -- no per-set brute force over every decoder, no subprocess per set, decode once, "
                         "early-exit on the first candidate that matches the answer_format; time it with `time hctf solver-run`.")
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
            # Short per-case timeout: a too-slow solver otherwise burns 120s PER CASE here before the generalize worker
            # can even start (rehearsal rehearsal: 4 min). A case that slow can't pass a 7s window anyway.
            res = (solvers.test_solver(self.sdir, timeout=BASELINE_CASE_TIMEOUT)
                   if (self.sdir / "solve.py").exists() else [])
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
        """Merged reuse (no model time): run EVERY same-lane solver (+ question-text matches) on the full contract,
        merge per field, and submit what they agree on -- partial is fine, the untimed GM accepts it and pins each
        field. Seeds this challenge's solver from the best one. Returns True if the single is complete; otherwise
        self._reuse_note tells the worker exactly which fields are left (it starts from the seeded solver)."""
        self._reuse_note = ""
        contract = cli.load(cid, "start.json") or cli.load(cid, "contract.json")
        art = timed.latest_artifacts(cid)
        if not contract or not art:
            return False
        ids = list(contract.get("answer_ids") or [])
        t0 = time.time()
        plan = solvers.reuse_plan(contract, art, self.lane, exclude=[self.sdir])
        high, spec, alts = plan["high"], plan["spec"], plan["alts"]
        if not high and not spec:
            say(f"[{cid}] reuse: no prior solver answers any of {len(ids)} field(s) ({len(plan['runs'])} tried)")
            return False
        set_state(self.base, stage="single:reuse")
        say(f"[{cid}] reuse: {len(high)} confident + {len(spec)} speculative of {len(ids)} field(s) from "
            f"{len(plan['runs'])} solver(s) in {time.time() - t0:.1f}s; seed {plan['best'] and plan['best'].parent.name}")
        budget = [REUSE_PROBE_BUDGET]
        wrong = set()

        def narrow(group):
            """Submit a group; on incorrect, bisect (probe-tagged) until the wrong fields are isolated."""
            group = {a: v for a, v in group.items() if a not in cli.confirmed_answers(cid)}
            if not group or budget[0] <= 0 or cli.is_complete(cid):
                return
            budget[0] -= 1
            kind, _body, refused = cli.submit(cid, group, force=True, probe=True)
            if kind in ("correct", "accepted") or refused:
                return
            if len(group) == 1:
                wrong.update(group)
                return
            keys = list(group)
            narrow({k: group[k] for k in keys[:len(keys) // 2]})
            narrow({k: group[k] for k in keys[len(keys) // 2:]})

        narrow(high)
        rest = {a: v for a, v in spec.items() if a not in cli.confirmed_answers(cid)}
        left = [a for a in ids if a not in cli.confirmed_answers(cid)]
        if rest and set(left) <= set(rest):
            narrow(rest)  # speculative values only when they could finish it (Day 6 binary: 8/8 were wrong)
        for a in sorted(wrong):  # a field judged wrong: try the other solvers' distinct values (Day 4 mobile)
            for v in [x for x in alts.get(a, []) if x != high.get(a, spec.get(a))][:3]:
                if budget[0] <= 0 or a in cli.confirmed_answers(cid):
                    break
                budget[0] -= 1
                if cli.submit(cid, {a: v}, force=True, probe=True)[0] in ("correct", "accepted"):
                    break
        # Seed this challenge's own solver from the best prior one (the worker extends it; timed modes run it).
        best = plan["best"]
        if best and not (self.sdir / "solve.py").exists():
            shutil.copytree(best, self.sdir, dirs_exist_ok=True, ignore=shutil.ignore_patterns("cases", "__pycache__"))
        conf = cli.confirmed_answers(cid)
        if cli.is_complete(cid):
            got, err, _ = solvers.run_solver(self.sdir, contract, art)
            missing = sorted(a for a, v in conf.items() if got.get(a) != v)
            if not err and not missing:
                ensure_case_and_test(cid, self.sdir, full=False)
                say(f"[{cid}] solved by merged reuse in {time.time() - t0:.1f}s (seed reproduces every answer)")
                return True
            # Complete, but the answers came from several solvers: the worker only has to make the seed emit them.
            self._reuse_note = (f"\nREUSE PRE-PASS: the Single Solve is already CORRECT (merged from several prior solvers). "
                                f"Your only job: make `{_rel(self.sdir)}/solve.py` (seeded from "
                                f"{best and _rel(best)}) also emit these confirmed answers, then STOP: "
                                f"{json.dumps({a: conf[a] for a in missing[:40]})}")
            return False
        remaining = [a for a in ids if a not in conf]
        hints = {a: spec[a] for a in remaining if a in spec}
        self._reuse_note = (
            f"\nREUSE PRE-PASS (already done by the harness, {time.time() - t0:.0f}s): {len(conf)}/{len(ids)} answers are "
            f"ALREADY ACCEPTED by the GM (see confirmed.json) -- do not re-derive or re-submit them. "
            f"`{_rel(self.sdir)}/solve.py` is seeded from `{best and _rel(best)}` and already emits "
            f"most of them: run `hctf solver-run {cid}` first. Only these {len(remaining)} answer_id(s) are left: "
            f"{', '.join(remaining[:80])}{' ...' if len(remaining) > 80 else ''}."
            + (f" Unverified values older solvers produced for some of them (hints, may be wrong): "
               f"{json.dumps(dict(list(hints.items())[:20]))}." if hints else "")
            + (f" Judged WRONG by the GM: {', '.join(sorted(wrong)[:20])}." if wrong else ""))
        say(f"[{cid}] reuse: {len(conf)}/{len(ids)} accepted; worker gets the {len(remaining)} remaining field(s)")
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

    def _record_labels(self, cid):
        # Cache the Single Solve's confirmed closed-vocab labels into vocab.json NOW (untimed), so the timed
        # modes enter with those spellings already confirmed and never carry an unconfirmed label onto a clock.
        try:
            from . import labels
            labels.record_from_confirmed(cid, lane=self.lane, log=say)
        except Exception as e:  # noqa: BLE001 - label caching is best-effort
            say(f"[{cid}] label cache note: {e}")

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
        tmodes = [m for m in ("time_trial", "mastery") if m in self.entries]

        def fetch(m):  # both timed contracts at once (no clock starts on a status call)
            tcid = self.entries[m]["id"]
            st = cli.call(tcid, "status", tcid)["body"] or {}
            if st.get("questions"):
                cli.save(tcid, "contract.json", st)
            return f"  - {m}: `{tcid}` -> `{cli.cdir(tcid).relative_to(ROOT)}/contract.json`"
        with ThreadPoolExecutor(max_workers=2) as ex:
            timed_info = list(ex.map(fetch, tmodes))
        for n in range(MAX_SINGLE_LAUNCHES):
            extra = ""
            notes = cli.cdir(cid) / "notes.md"
            if n and notes.exists():
                extra = (f"\nThis is relaunch #{n}: a previous worker stopped before finishing. Read `{notes.relative_to(ROOT)}` "
                         "first, do not repeat its dead ends, and pick the most promising unexplored lead.")
            if welcome:
                extra += "\nThis is an orientation challenge: no solver is needed, only a correct submission."
            extra += getattr(self, "_reuse_note", "")
            prompt = workers.render("single", name=self.name, cid=cid, lane=self.lane,
                                    persona=workers.lane_persona(self.lane), playbook=workers.lane_playbook(self.lane),
                                    chal_dir=cli.cdir(cid).relative_to(ROOT), solver_dir=self.sdir.relative_to(ROOT),
                                    timed_contracts="\n".join(timed_info) or "  - (none: Single Solve only)", extra=extra)
            set_state(self.base, stage="single:solving", launches=n + 1)
            heavy = self.lane in ("binary-reverse-engineering", "binary")
            ready, done_evt, watch = threading.Event(), threading.Event(), None
            self._ready_snap = None
            if STOP_WHEN_READY and not welcome:
                watch = threading.Thread(target=self._watch_ready, args=(cid, ready, done_evt), daemon=True)
                watch.start()
            try:
                rc = self.run_worker(cid, "single", prompt, SINGLE_TIMEOUT, prefer_homebase=heavy, stop=ready)
            finally:
                done_evt.set()
                if watch:
                    watch.join()
            if rc == workers.STOPPED_RC and self._ready_snap:
                # Ended on purpose: CORRECT + verified solver. Restore the verified files, record the single as a
                # regression case and go straight to the timed modes (the full-suite replay is not needed: the
                # snapshot was just verified on this exact case).
                self._restore_ready_snapshot(self._ready_snap)
                ensure_case_and_test(cid, self.sdir, full=False)
                say(f"[{cid}] after worker: stopped at CORRECT with a verified solver")
                self._record_labels(cid)
                return True
            done = cli.is_complete(cid)
            if not done and not welcome:
                done = self.auto_labels(cid)
            ok, res = (True, None) if welcome else ensure_case_and_test(cid, self.sdir)
            say(f"[{cid}] after worker: complete={done} solver_ok={ok}")
            if done and ok:
                self._record_labels(cid)
                return True
            if (cli.cdir(cid) / "HELP.md").exists():
                set_state(self.base, stage="single:help", help=(cli.cdir(cid) / "HELP.md").read_text()[:1500])
                return False
        set_state(self.base, stage="single:blocked")
        return False

    # -- early handoff (speculative timed attempts while the Single Solve worker is still running)
    def _solver_mtimes(self):
        if not self.sdir.exists():
            return {}
        # Solver CODE only: a late NOTES.md / scratch write must not reset the stability clock (Day 6).
        return {p.name: p.stat().st_mtime for p in self.sdir.iterdir() if p.is_file() and p.suffix == ".py"}

    def _spec_snapshot(self, cid):
        """Copy the worker's in-progress solver (minus cases) to `.run/spec-dayNN/<chal>/solver` -- the same depth as
        challenges/dayNN/<chal>/solver, since solvers locate the project root via parents[N] -- if its files have been
        stable for SPEC_STABLE s and it reproduces the GM-confirmed Single Solve answers. Returns the dir or None."""
        m0 = self._solver_mtimes()
        if "solve.py" not in m0 or time.time() - max(m0.values()) < SPEC_STABLE:
            return None
        if m0 == getattr(self, "_spec_rejected", None):
            return None  # this exact solver already failed verification; wait for the worker to change it
        contract, art, conf = cli.load(cid, "start.json"), timed.latest_artifacts(cid), cli.confirmed_answers(cid)
        if not (contract and art and conf):
            return None
        rel = self.sdir.relative_to(paths.CHALLENGES).parts  # (dayNN, <chal>, solver)
        if len(rel) != 3:
            return None
        snap = ROOT / ".run" / f"spec-{rel[0]}" / rel[1] / "solver"
        if snap.exists():
            shutil.rmtree(snap)
        shutil.copytree(self.sdir, snap, ignore=shutil.ignore_patterns("cases", "__pycache__"))
        if (self.root / "meta.json").exists():
            shutil.copy2(self.root / "meta.json", snap.parent / "meta.json")  # hb_timed reads the lane from it
        if self._solver_mtimes() != m0:
            return None  # the worker edited mid-copy; next poll
        got, err, _ = solvers.run_solver(snap, contract, art)
        bad = sorted(k for k, v in conf.items() if got.get(k) != v)
        if err or bad:
            self._spec_rejected = m0
            say(f"[{cid}] early handoff: snapshot not ready ({err or f'{len(bad)} field(s) differ, e.g. {bad[:3]}'})")
            return None
        return snap

    def _watch_ready(self, cid, ready, done):
        """Runs beside the Single Solve worker. The moment the single is CORRECT and the worker's solver (stable 2s)
        reproduces every GM-confirmed answer, keep that verified snapshot and set `ready`: run_local then ends the
        worker and the timed modes start from the snapshot at once. Day 6: 60% of worker time (1101/1850s) came after
        the first CORRECT, and every first-correct snapshot already passed its real TT+Mastery variants offline."""
        try:
            while not done.wait(SPEC_POLL):
                if cli.is_complete(cid):
                    snap = self._spec_snapshot(cid)
                    if snap:
                        self._ready_snap = snap
                        say(f"[{cid}] single CORRECT + solver verified -> ending the worker, timed modes start now")
                        ready.set()
                        return
        except Exception as e:  # noqa: BLE001 - the watcher must never hurt the chain
            say(f"[{cid}] ready-watch note: {e}")

    def _restore_ready_snapshot(self, snap):
        """After a stopped worker: put the verified snapshot's files back over the live solver (the worker may have been
        mid-edit when it was ended). cases/ in the live dir is kept."""
        for src in snap.rglob("*"):
            if src.is_file() and "__pycache__" not in src.parts:
                dst = self.sdir / src.relative_to(snap)
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)

    @staticmethod
    def _clock_expiry(cid):
        """The last attempt expired although the solver answered everything: the clock, not the solver."""
        last = timed.last_result(cid) or {}
        return (last.get("phases") or {}).get("solve") is not None and not last.get("missing")

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
                    time.sleep(3)  # CourseStack scoring may still be pending for the previous mode
                continue
            if res == "error:exec":
                # Transport failure (Day 6 binary TT: exec_error -> 12-min generalize path). Wait briefly for Homebase
                # health (local is the fallback anyway) and retry; it costs a TT attempt, never a worker.
                if attempt < MAX_TIMED_RETRIES:
                    say(f"[{cid}] timed runner failed ({(timed.last_result(cid) or {}).get('detail', '')!s:.120}); retrying")
                    set_state(self.base, stage=f"{mode}:retrying")
                    workers.wait_homebase(10)
                    continue
                break
            if res not in ("expired", "blocked"):
                break
            last = timed.last_result(cid) or {}
            if res == "expired" and self._clock_expiry(cid) and attempt < MAX_TIMED_RETRIES:
                # The solver answered everything and the CLOCK ran out: a transport/timing failure. Probing can't judge
                # anything on an expired clock and a generalize worker can't speed up the network (rehearsal copy,
                # Dim and Dimmer mastery: 0/462 judged, worker concluded "solver correct, timing"). Just retry.
                say(f"[{cid}] expired on the CLOCK (in-window {last.get('in_window')}s / window {last.get('window')}s, "
                    f"phases {last.get('phases')}): timing, not the solver -- retrying without probe/generalize")
                set_state(self.base, stage=f"{mode}:timing")
                time.sleep(2)
                continue
            # A failed timed attempt means the solver is wrong or incomplete for this variant (with Homebase
            # execution the window is no longer the bottleneck). Always improve the solver offline, then retry.
            # The generalize worker re-derives the variant's correct answers itself (ground truth), so it can
            # fix WRONG answers too, not just missing ones. Fetch the variant locally for it to work on.
            wrong, fixed, diag = None, None, {}
            last = timed.last_result(cid) or {}
            diag = {k: last.get(k) for k in ("window", "elapsed", "phases", "routed", "solver_too_slow", "hb_env_mismatch")}
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
                    tdir = timed.timed_dir(cid)
                    tc = json.loads((tdir / "contract.json").read_text()) if (tdir / "contract.json").exists() else None
                    if last.get("solver_too_slow") and tc and cli.attempt_id(tc) == last.get("attempt_id", cli.attempt_id(tc)):
                        # The failed attempt's contract + bytes are already local (pulled after the failure): work on
                        # THAT variant instead of starting a fresh attempt just to download one (~45s on Mastery).
                        cli.save(cid, "start.json", tc)
                        cli.save(cid, "contract.json", tc)
                    else:
                        timed.ensure_started(cid)  # fresh attempt + download of the current variant for offline work
                    if last.get("solver_too_slow"):
                        # Probing runs the same too-slow solver: it learns nothing (rehearsal rehearsal: 3 min for "28/28
                        # wrong" from an empty output). The fix is speed -- straight to generalize with that diagnosis.
                        say(f"[{cid}] solver too slow for the window: skipping the field probe, generalizing for speed")
                    else:
                        wrong = timed.probe_fields(cid, self.sdir, log=say)  # binary search, per-field verdicts
                        dj = cli.cdir(cid) / "diagnosis.json"
                        if dj.exists():  # probe_fields returns early (no file) when there is nothing to probe
                            pd = json.loads(dj.read_text())
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
            if wrong == [] and diag.get("complete") and attempt < MAX_TIMED_RETRIES:
                # The probe judged EVERY field and found none wrong: the solver is right, the failure was the
                # environment or the clock (rehearsal rehearsal: 399/399 ok after a Homebase-only failure, yet a 12-min
                # generalize started). Retry instead; the Homebase 7z shim / local fallback handle the environment.
                say(f"[{cid}] probe: every field correct -> environment/timing, retrying without generalize")
                set_state(self.base, stage=f"{mode}:retrying")
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
        for n in range(CHAIN_CRASH_RETRIES + 1):
            try:
                return self._run()
            except Exception:  # noqa: BLE001 - one chain must never take down the others
                tb = traceback.format_exc()
                if n < CHAIN_CRASH_RETRIES:
                    say(f"[{self.base}] CRASHED; retrying the chain in 10s (solved modes are skipped):\n{tb}")
                    set_state(self.base, stage="crash-retry", error=tb[-2000:])
                    time.sleep(10)
                    continue
                set_state(self.base, stage="crashed", error=tb[-2000:])
                say(f"[{self.base}] CRASHED:\n{tb}")

    def _run(self):
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
    if RATCHET and day is not None:
        ratchet(day)


RATCHET = os.environ.get("HCTF_RATCHET", "1") != "0"
RATCHET_TIMEOUT = float(os.environ.get("HCTF_RATCHET_TIMEOUT", str(15 * 60)))


def ratchet(day):
    """Post-run, single-writer knowledge merge: collect every `## Proposed lib additions` section the day's workers
    wrote in solver/NOTES.md and let ONE worker fold the GM-confirmed ones into lib/ (workers no longer edit lib/
    mid-run: Day 6's script worker rewrote lib/knowledge.py + lib/scripts.py while four other lanes imported them)."""
    tag = f"day{int(day):02d}"
    props = []
    for notes in sorted((paths.CHALLENGES / tag).glob("*/solver/NOTES.md")):
        text = notes.read_text(errors="replace")
        m = re.search(r"^##\s*Proposed lib additions\s*$(.*?)(?=^##\s|\Z)", text, re.M | re.S)
        if m and m.group(1).strip():
            props.append(f"### {notes.relative_to(ROOT)}\n{m.group(1).strip()}")
    if not props:
        say(f"[ratchet] {tag}: no proposed lib additions")
        return
    prompt = workers.render("ratchet", day=tag, day_num=int(day), proposals="\n\n".join(props))
    say(f"[ratchet] {tag}: merging {len(props)} proposal section(s) into lib/")
    # Transactional: a killed/timed-out ratchet left lib/ half-edited on the rehearsal replay (an unvalidated helper that
    # extracted 0 files). Snapshot lib/, and restore it unless the worker exits 0 AND the test suites still pass.
    backup = ROOT / ".run" / f"ratchet-lib-{tag}"
    shutil.rmtree(backup, ignore_errors=True)
    shutil.copytree(ROOT / "lib", backup, ignore=shutil.ignore_patterns("__pycache__"))
    rc, log = workers.run_local(paths.CHALLENGES / tag, "ratchet", prompt, {"HCTF_STAGE": "ratchet"}, RATCHET_TIMEOUT)
    ok = rc == 0
    if ok:
        import subprocess as _sp
        for t in ("tests/test_orchestrate.py", "tests/test_day6_fixes.py"):
            if (ROOT / t).exists() and _sp.run([sys.executable, t], cwd=ROOT, capture_output=True, timeout=600).returncode:
                ok = False
                say(f"[ratchet] {tag}: {t} fails after the merge")
    if ok:
        shutil.rmtree(backup, ignore_errors=True)
        say(f"[ratchet] {tag}: merged ({Path(log).name})")
    else:
        shutil.rmtree(ROOT / "lib")
        shutil.copytree(backup, ROOT / "lib")
        say(f"[ratchet] {tag}: REVERTED lib/ (worker exit {rc}); proposals stay in solver/NOTES.md ({Path(log).name})")


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
