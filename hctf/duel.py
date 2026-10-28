"""DUEL workers: best-of-N for the LLM stages that bound a day (brand-new Single Solves, repeat generalizes).

Every top autonomous CTF system of 2025-26 races several differently-configured agents per challenge and keeps the
first verified result (Veria BSidesSF 2026, Team Atlanta's 8 patchers, 42-b3yond-6ug's temperature x prompt sweep,
Irregular: unreliable challenges succeed 30-60% per run). The harness ran ONE LLM worker per chain; this module adds a
second, local one with a different configuration (effort, optionally model) beside it:

  * single:     launched DELAY s after the chain's worker -- the reuse race usually wins in 3-9 s, and then no duel is
                spent. It works on a COPY of the solver in .run/duel-dayNN/<chal>/solver (same depth as
                challenges/dayNN/<chal>/solver: solvers locate the project root via parents[N]); inside its process tree
                paths.solver_dir() points there (HCTF_SOLVER_DIR_OVERRIDE), so `hctf submit --from-solver`, solver-test
                and the stop gate all use the copy. GM submissions are shared (same attempt, same confirmed.json).
                Once the single is CORRECT and the duel's solver reproduces every confirmed answer, the verified
                snapshot is handed to the chain exactly like the Homebase shadow's (chain._ready_snap + ready.set()).
  * generalize: from the GEN_AFTER+1-th generalize of a mode on. Works on a copy of the solver WITH its cases in
                .run/duel-gen-dayNN/<chal>/solver; green by the same rule as Chain._watch_green -> its code is copied
                over the live solver and the chain's transactional _accept_or_restore judges it like any other edit.

The duel is ended the moment the chain's own worker wins (or the chain leaves the stage).

Roster (2026-10-18, user): the duel is a GROUP of racers. Racer 1 = the original duel (HCTF_DUEL_MODEL / _EFFORT:
the lane's model at medium). HCTF_DUEL_EXTRA adds racers with a DIFFERENT model ("model:effort", comma-separated;
default claude-sonnet-5-5:high -- model diversity beside two Opus 5.5 configurations, Veria-style). Extras have their
own concurrency cap (EXTRA_MAX) and launch only with EXTRA_MIN_AVAIL_GB of MemAvailable, so racer 1 behaves exactly as
before. Each racer has its own solver copy (.run/duel{N}-dayNN/...), notes file and worker log pool.
"""
import os
import shutil
import threading
import time

from . import cli, paths, solvers, timed, workers

ROOT = paths.ROOT
ENABLED = os.environ.get("HCTF_DUEL", "1") != "0"
# binary is out by default: Ghidra + a 230 MB solver corpus per copy on a 7 GB WSL box. web in from its first day
# (D19, user 2026-10-18): no prior solvers -> no reuse race, the single is a cold LLM solve -- best-of-2's case.
LANES = {x.strip() for x in os.environ.get(
    "HCTF_DUEL_LANES", "warmups,metadata-forensics,script-analysis,mobile-android,web").split(",") if x.strip()}
MAX_CONCURRENT = int(os.environ.get("HCTF_DUEL_MAX", "4"))   # 4 since D19: six lanes (web), binary duel on
MODEL = os.environ.get("HCTF_DUEL_MODEL", "")            # "" = the lane's normal worker model
# medium (user, 2026-10-16): diversity + speed beside the chain's high-effort worker -- on D16 the medium duel won all
# three singles it ran (warmups, metadata, script). HCTF_DUEL_EFFORT="" = the lane's worker effort.
EFFORT = os.environ.get("HCTF_DUEL_EFFORT", "medium")
# extra racers: "model:effort" (empty effort = the lane's worker effort); HCTF_DUEL_EXTRA="" = best-of-2 as before
EXTRA = [tuple((x.strip().split(":", 1) + [""])[:2]) for x in
         os.environ.get("HCTF_DUEL_EXTRA", "claude-sonnet-5-5:high").split(",") if x.strip()]
EXTRA_MAX = int(os.environ.get("HCTF_DUEL_EXTRA_MAX", "3"))
EXTRA_MIN_AVAIL_GB = float(os.environ.get("HCTF_DUEL_EXTRA_MIN_AVAIL_GB", "1.5"))   # ~0.3 GB per claude worker
# D26 post-mortem: single-duel racers never produced a first CORRECT in D21-D26 (41 launches) yet were 6 of the 12 claude
# processes at the CPU peak (load 28 on 12 CPUs) -> they run niced; the chain's own worker and answer-first keep the CPU.
# "" = not niced (old).
SINGLE_NICE = os.environ.get("HCTF_DUEL_SINGLE_NICE", "10").strip()
# Rehearsal fair D26 (user, 10-27): single-duel racers are OFF at the drop -- still 0 first CORRECTs, and the host was the
# critical path (15 claude processes at T+0:21, load 24-26, binary's 7z extract 47.8 s vs 0.55 s idle). Generalize duels
# stay. HCTF_DUEL_SINGLE=1 = the old best-of-3 singles.
SINGLE = os.environ.get("HCTF_DUEL_SINGLE", "0") != "0"
DELAY = float(os.environ.get("HCTF_DUEL_DELAY", "15"))    # single: give the reuse race its 3-9 s first
GEN_AFTER = int(os.environ.get("HCTF_DUEL_GENERALIZE_AFTER", "1"))   # duel the 2nd+ generalize of a mode; -1 = never
GEN_FIRST = os.environ.get("HCTF_DUEL_GENERALIZE_FIRST", "1") != "0"  # ... and the 1st when label-only / speed-only
WAIT = float(os.environ.get("HCTF_DUEL_WAIT", "600"))     # chain worker ended without a result: wait this long for the duel
POLL = float(os.environ.get("HCTF_DUEL_POLL", "1.0"))
STABLE = float(os.environ.get("HCTF_DUEL_STABLE", "0.75"))
GREEN_CASE_TIMEOUT = float(os.environ.get("HCTF_BASELINE_CASE_TIMEOUT", "8"))


def _green_timeout(lane):
    """GREEN_CASE_TIMEOUT, lane-aware like the chain's baseline (D28 #11: web >= HCTF_WEB_BASELINE_CASE_TIMEOUT)."""
    try:
        from .orchestrate import WEB_BASELINE_CASE_TIMEOUT
        from . import webtarget
        if WEB_BASELINE_CASE_TIMEOUT > 0 and webtarget.is_live_lane(lane):
            return max(GREEN_CASE_TIMEOUT, WEB_BASELINE_CASE_TIMEOUT)
    except Exception:  # noqa: BLE001
        pass
    return GREEN_CASE_TIMEOUT

_live = set()
_live_extra = set()
_live_lock = threading.Lock()


def eligible(lane, key=None, stage=None):
    """(ok, why). Checks only: the slot is taken at the actual launch (_reserve), after the single's DELAY -- rehearsal D14
    replay: duels still waiting out their delay (singles already won by the reuse race) blocked script's duel."""
    if not ENABLED:
        return False, "HCTF_DUEL=0"
    if stage == "single" and not SINGLE:
        return False, "single duels off (HCTF_DUEL_SINGLE=0)"
    if lane not in LANES and not _binary_ok(lane):
        return False, f"lane {lane} not in HCTF_DUEL_LANES"
    with _live_lock:
        if len(_live) >= MAX_CONCURRENT:
            return False, f"{len(_live)} duels already running"
    return True, ""


# binary duel only with this much MemAvailable (GB) at the decision; 0 = never. D15: binary single +89 s by the lone
# worker; D19: +2:30 (the critical path: 8 overlay fields after the reuse race) -> ON at 2.5 GB (D19 web runs still had
# 3.5 GB free with 21 claude workers alive; cases/ are hardlinked, so a copy costs no disk).
BINARY_MIN_AVAIL_GB = float(os.environ.get("HCTF_DUEL_BINARY_MIN_AVAIL_GB", "2.5"))


def _mem_avail_gb():
    try:
        for ln in open("/proc/meminfo"):
            if ln.startswith("MemAvailable:"):
                return int(ln.split()[1]) / 1048576
    except (OSError, ValueError, IndexError):
        pass
    return 0.0


def _binary_ok(lane):
    return (lane == "binary-reverse-engineering" and BINARY_MIN_AVAIL_GB > 0
            and _mem_avail_gb() >= BINARY_MIN_AVAIL_GB)


def _reserve(key, extra=False):
    """Racer 1 counts against MAX_CONCURRENT; extra racers against EXTRA_MAX and need EXTRA_MIN_AVAIL_GB free."""
    if extra and _mem_avail_gb() < EXTRA_MIN_AVAIL_GB:
        return False
    with _live_lock:
        live, cap = (_live_extra, EXTRA_MAX) if extra else (_live, MAX_CONCURRENT)
        if len(live) >= cap:
            return False
        live.add(key)
        return True


def _release(key):
    with _live_lock:
        _live.discard(key)
        _live_extra.discard(key)


def _mirror(sdir, kind, n=1):
    """.run/duel[N][-gen]-dayNN/<chal>/solver for challenges/dayNN/<chal>/solver (None for other layouts); racer n."""
    try:
        rel = sdir.relative_to(paths.CHALLENGES).parts
    except ValueError:
        return None
    if len(rel) != 3:
        return None
    tag = ("duel" if n == 1 else f"duel{n}") + ("" if kind == "single" else "-gen")
    return ROOT / ".run" / f"{tag}-{rel[0]}" / rel[1] / "solver"


def _copy_solver(src, dst, cases):
    if dst.parent.exists():
        shutil.rmtree(dst.parent)
    dst.parent.mkdir(parents=True)
    meta = src.parent / "meta.json"
    if meta.exists():
        shutil.copy2(meta, dst.parent / "meta.json")
    if not src.exists():
        dst.mkdir()
        return
    if not cases:
        shutil.copytree(src, dst, ignore=shutil.ignore_patterns("cases", "__pycache__"))
        return

    def link_or_copy(s, d):
        # case artifacts are big and never written: hard-link them; everything else (expected.json!) is a real copy.
        # Never into an existing d (orchestrate.safe_place: a hardlinked dst would carry the write to every link).
        from .orchestrate import safe_place
        return safe_place(s, d, link="/artifacts/" in s.replace(os.sep, "/"))
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns("__pycache__"), copy_function=link_or_copy)


def _code_mtimes(d):
    if not d.exists():
        return {}
    return {p.name: p.stat().st_mtime for p in d.iterdir() if p.is_file() and p.suffix == ".py"}


NOTE = """

---
## You are the DUEL worker
Other workers (different configurations) are working on this same task right now from the same starting point; the
first verified result wins and the others are ended. Work independently:
- YOUR solver directory is `{ddir}` -- every mention of the solver directory above means this one, and
  `hctf submit --from-solver`, `hctf solver-test` and `hctf solver-run` already use it. Never write under `{main}`.
- Keep your notes in `{notes}` (the chain's worker writes notes.md; read it for leads, never edit it).
- GM submissions are shared: answers either worker gets accepted appear in confirmed.json -- re-read it before
  re-deriving a field. The per-field wrong-answer budget is shared too: submit only values derived from the bytes.
- Diversity is the point: if the other worker's notes.md commits to one hypothesis, test the strongest alternative first.
"""


QUICK_FIX_NOTE = """- YOUR STRATEGY IS DIFFERENT -- QUICK FIX (the other worker does the principled rule-fit): make the SMALLEST
  change to the solver that makes the failing case(s) produce the GM-accepted labels shown above WITHOUT breaking any
  other case. No new framework, no broad tabulation, no investigation of why the grader changed. Edit within your first
  ~5 tool calls, check with `hctf solver-test <base> --case 'variant-*' --timeout 20`, then the full suite once. A
  regression is rejected automatically, so a narrow fix is safe. (rehearsal D13 replays: both duel workers ran the same
  2-3 minute tabulation and duplicated each other.)
"""


class Duel:
    def __init__(self, chain, cid, stage, prompt, timeout, cases, note_extra="", n=1, model=None, effort=None):
        self.chain, self.cid, self.stage, self.timeout = chain, cid, stage, timeout
        self.note_extra = note_extra
        self.n = n                                   # racer number: 1 = the original duel, 2+ = HCTF_DUEL_EXTRA
        self.model = MODEL if model is None else model
        self.effort = EFFORT if effort is None else effort
        self.key = f"{chain.base}:{stage}" + ("" if n == 1 else f":r{n}")
        self.ddir = _mirror(chain.sdir, stage, n)
        self.cases = cases
        self.prompt = prompt
        self.stop_evt = threading.Event()
        self.thread = None
        self.rc = None
        self.snap = None
        self.won = False
        self.green_res = None
        self._checked = None
        self.copied = threading.Event()
        self.src = None   # copy the solver from here instead of the live dir (D25 C1: the pre-worker snapshot)

    def alive(self):
        return self.thread is not None and self.thread.is_alive()

    def _render(self):
        main_rel, d_rel = str(self.chain.sdir.relative_to(ROOT)), str(self.ddir.relative_to(ROOT))
        text = self.prompt.replace(str(self.chain.sdir), str(self.ddir)).replace(main_rel, d_rel)
        notes = cli.cdir(self.cid).relative_to(ROOT) / ("duel-notes.md" if self.n == 1 else f"duel{self.n}-notes.md")
        return text + NOTE.format(ddir=d_rel, main=main_rel, notes=notes) + self.note_extra.replace("<base>",
                                                                                                   self.chain.base)

    def _env(self):
        env = self.chain._worker_env(self.cid, self.stage)
        env.update({"HCTF_SOLVER_DIR": self.ddir, "HCTF_SOLVER_DIR_OVERRIDE": self.ddir, "HCTF_DUEL": "1",
                    "HCTF_LOG_POOL": "duel" if self.n == 1 else f"duel{self.n}"})
        if self.stage == "single" and SINGLE_NICE:
            env["HCTF_NICE"] = SINGLE_NICE   # the chain's own worker + answer-first keep the CPU at the drop
        if self.effort:
            env["HCTF_X_EFFORT"] = self.effort
        if self.model:
            env["HCTF_X_MODEL"] = self.model
        return env

    def start(self, delay=0.0, skip=None, log=print, wake=None):
        """Copy the solver and launch the worker in a thread: after `delay` s at most, or as soon as `wake` (the reuse
        race finished: rehearsal D13 replay, the race was done at +3 s and the winning duel still waited until +18 s) --
        unless stopped or `skip()` is true by then."""
        def body():
            try:
                if self.ddir is None:
                    log(f"[{self.cid}] duel {self.stage}: solver dir outside challenges/dayNN/<chal>/ -- no duel")
                    return
                if delay:
                    end = time.time() + delay
                    while time.time() < end and not self.stop_evt.is_set():
                        if wake is not None and wake.is_set():
                            break
                        self.stop_evt.wait(0.2)
                    if self.stop_evt.is_set() or (skip and skip()):
                        return
                if not (_reserve(self.key, extra=True) if self.n > 1 else _reserve(self.key)):
                    log(f"[{self.cid}] no duel{'' if self.n == 1 else f' racer {self.n}'} {self.stage}: "
                        + (f"{MAX_CONCURRENT} duels already running" if self.n == 1 else
                           f"{EXTRA_MAX} extra racers running or < {EXTRA_MIN_AVAIL_GB:g} GB available"))
                    return
                if self.cases and self.stage == "single":
                    join = getattr(self.chain, "_join_prior_cases", None)
                    if join:
                        join(self.cid)    # the background prior cases/ copy (stage_prior_cases) must be complete
                gate = getattr(self.chain, "_offpath_wait", None)
                if gate is not None and self.stage != "single":
                    # D28 #6: no solver copy + duel worker start while this chain downloads a timed mode's bytes
                    gate(f"duel {self.stage}", self.stop_evt, mode=solvers.mode_of(self.cid))
                    if self.stop_evt.is_set():
                        return
                _copy_solver(self.src or self.chain.sdir, self.ddir, self.cases)
                self.copied.set()
                if self.stop_evt.is_set() or (skip and skip()):
                    # D26: warmups' racers launched 3-5 s after the single was already CORRECT (skip() ran only before
                    # the prior-cases join + copy)
                    log(f"[{self.cid}] duel {self.stage}{'' if self.n == 1 else f' racer {self.n}'}: not launched "
                        "(the mode completed during the solver copy)")
                    return
                log(f"[{self.cid}] duel {self.stage} worker -> local (effort "
                    f"{self.effort or workers.worker_effort(self.chain.lane)}"
                    f"{', model ' + self.model if self.model else ''}{'' if self.n == 1 else f', racer {self.n}'}) "
                    f"on {self.ddir.relative_to(ROOT)}")
                self.rc, lg = workers.run_local(cli.cdir(self.cid), self.stage, self._render(), self._env(),
                                                self.timeout, stop=self.stop_evt)
                log(f"[{self.cid}] duel {self.stage} worker exit {self.rc} ({lg.name})")
            except Exception as e:  # noqa: BLE001 - the duel is optional
                log(f"[{self.cid}] duel {self.stage} note: {e}")
            finally:
                _release(self.key)
        self.thread = threading.Thread(target=body, daemon=True,
                                       name=f"duel{'' if self.n == 1 else self.n}-{self.stage}-{self.chain.base}")
        self.thread.start()

    def stop(self, join=10.0):
        self.stop_evt.set()
        if self.thread is not None:
            self.thread.join(timeout=join)
        _release(self.key)

    def signal_stop(self):
        """End the worker without waiting for it (the chain's handoff must not; HCTF_DUEL_STOP_AT_READY): stop() joins."""
        self.stop_evt.set()

    # ---- single: verified snapshot of the duel's solver
    def verified_snapshot(self, log=print):
        m = _code_mtimes(self.ddir)
        if "solve.py" not in m or time.time() - max(m.values()) < STABLE or m == self._checked:
            return self.snap
        contract, art, conf = cli.load(self.cid, "start.json"), timed.latest_artifacts(self.cid), \
            cli.confirmed_answers(self.cid)
        if not (contract and art and conf):
            return None
        snap = self.ddir.parent.parent.parent / (self.ddir.parent.parent.name + "-snap") / self.ddir.parent.name / "solver"
        if snap.parent.exists():
            shutil.rmtree(snap.parent)
        snap.parent.mkdir(parents=True)
        shutil.copytree(self.ddir, snap, ignore=shutil.ignore_patterns("cases", "__pycache__"))
        if (self.chain.root / "meta.json").exists():
            shutil.copy2(self.chain.root / "meta.json", snap.parent / "meta.json")
        if _code_mtimes(self.ddir) != m:
            return None   # edited mid-copy: next poll
        self._checked = m
        got, err, dt = solvers.run_solver(snap, contract, art)
        bad = sorted(k for k, v in conf.items() if got.get(k) != v)
        if err or bad:
            log(f"[{self.cid}] duel solver not verified yet ({err or f'{len(bad)} field(s) differ, e.g. {bad[:3]}'})")
            return None
        self.snap = snap
        log(f"[{self.cid}] duel solver verified ({dt:.1f}s)")
        return snap

    def watch_single(self, ready_get, log=print):
        """Thread body beside a single duel: hand a verified snapshot to the chain the moment the single is CORRECT."""
        errs = 0
        while not self.stop_evt.wait(POLL):
            try:
                if not cli.is_complete(self.cid):
                    if not self.alive() and self.thread is not None:
                        return
                    continue
                ready, lock = ready_get()
                if ready is not None and ready.is_set():
                    return   # the chain's own worker (or the Homebase shadow) handed over first
                if ready is None:
                    continue
                snap = self.verified_snapshot(log)
                if snap:
                    with lock:
                        if not ready.is_set():
                            self.chain._ready_snap = snap
                            self.won = True
                            log(f"[{self.cid}] duel reached a verified solver first -> ending the chain's worker")
                            getattr(self.chain, "_prefetch_tt", lambda: None)()   # the TT pre-start belongs to the verified handoff
                            ready.set()
                    return
                if not self.alive():
                    return
            except Exception as e:  # noqa: BLE001 - must never hurt the chain; one bad poll must not end the watch
                errs += 1
                if errs <= 3:
                    log(f"[{self.cid}] duel watch note: {e}")
                if errs >= 50:
                    return

    def wait_snap(self, seconds, log=print):
        """Chain's own worker ended without a passing solver: wait (bounded) for the duel's verified one."""
        end = time.time() + seconds
        while time.time() < end and self.snap is None:
            if cli.is_complete(self.cid):
                self.verified_snapshot(log)
            if self.snap is not None or not self.alive():
                break
            time.sleep(POLL)
        return self.snap

    # ---- generalize: green check on the duel's copy (Chain._watch_green's rule)
    def watch_green(self, targets, baseline, need_fast, fill, green, log=print, reject_free=frozenset(), ready=None):
        """`reject_free`: unverified cases with GM rejections -- green once complete with none of them (D25 C2).
        `ready`: blocks until the chain's async baseline (C1) filled targets / fill / reject_free / baseline in place."""
        try:
            while not self.copied.wait(0.5):
                if self.stop_evt.is_set() or (self.thread is not None and not self.alive()):
                    return
            start, checked = _code_mtimes(self.ddir), None
            if ready is not None and not ready():
                return
            if not (targets or fill or reject_free):
                return
            while not self.stop_evt.wait(2.0):
                if green.is_set():
                    return
                m = _code_mtimes(self.ddir)
                if not m or m == start or time.time() - max(m.values()) < 3 or m == checked:
                    if self.thread is not None and not self.alive() and m == checked:
                        return
                    continue
                checked = m
                try:
                    tmo = _green_timeout(getattr(self.chain, "lane", None))
                    if not solvers.targets_pass(self.ddir, targets, fill, timeout=tmo, reject_free=reject_free):
                        continue   # target still failing: no full-corpus replay for this edit
                    res = solvers.test_solver(self.ddir, timeout=tmo)
                except Exception:  # noqa: BLE001
                    continue
                if _code_mtimes(self.ddir) != m:
                    checked = None
                    continue
                ok = {r["case"] for r in res if r.get("ok")}
                filled = {r["case"] for r in res if r.get("total") and r.get("answered") == r.get("total")
                          and not r.get("error")}
                rf_ok = {r["case"] for r in res if r.get("reject_free")}
                fast = all(r.get("seconds", 99) < 2.0 for r in res if r["case"] in (targets | set(fill)))
                if (targets <= ok and set(fill) <= filled and set(reject_free) <= rf_ok and baseline <= ok
                        and (fast or not need_fast)):
                    if fill and not (targets & ok) and not reject_free:
                        continue   # fill-only evidence never wins (VERIFIED_GREEN, D12)
                    with self.chain.__dict__.setdefault("_gen_lock", threading.Lock()):
                        if green.is_set():
                            return
                        self.won = True
                        # the chain's accept step reuses this full-suite run when the adopted code + case set match
                        self.green_res = (m, sorted(p.name for p in (self.ddir / "cases").glob("*/")), res)
                        log(f"[{self.chain.base}] duel generalize green first -> adopting its solver, ending the "
                            "chain's worker")
                        green.set()
                    return
        except Exception as e:  # noqa: BLE001
            log(f"[{self.chain.base}] duel green-watch note: {e}")

    def adopt_into(self, sdir, log=print):
        """Copy the winning duel's code (not cases/) over the live solver; drop live code files the duel doesn't have."""
        keep = {p.name for p in self.ddir.iterdir() if p.is_file()}
        for p in sdir.iterdir():
            if p.is_file() and p.suffix == ".py" and p.name not in keep:
                p.unlink()
        for src in self.ddir.rglob("*"):
            rel = src.relative_to(self.ddir)
            if not src.is_file() or rel.parts[0] == "cases" or "__pycache__" in rel.parts:
                continue
            dst = sdir / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
        log(f"[{self.chain.base}] duel solver copied into {sdir.relative_to(ROOT)}")


class DuelGroup:
    """Racer 1 (the original duel) + the HCTF_DUEL_EXTRA racers behind the Duel interface the chain already uses:
    first verified single snapshot / first green generalize wins (each racer's watcher takes the chain's own
    ready / _gen_lock, so exactly one hands over)."""

    def __init__(self, members):
        self.members = members

    def start(self, **kw):
        for m in self.members:
            m.start(**kw)

    def stop(self, join=10.0):
        for m in self.members:
            m.stop_evt.set()
        for m in self.members:
            m.stop(join=join)

    def signal_stop(self):
        for m in self.members:
            m.signal_stop()

    def alive(self):
        return any(m.alive() for m in self.members)

    def _winner(self):
        return next((m for m in self.members if m.won), None)

    @property
    def won(self):
        return self._winner() is not None

    @property
    def snap(self):
        w = self._winner()
        if w is not None and w.snap is not None:
            return w.snap
        return next((m.snap for m in self.members if m.snap is not None), None)

    @property
    def green_res(self):
        w = self._winner()
        return w.green_res if w is not None else None

    def _fan(self, fn, args):
        ts = [threading.Thread(target=getattr(m, fn), args=args, daemon=True,
                               name=f"{fn}-r{m.n}-{m.chain.base}") for m in self.members]
        for t in ts:
            t.start()
        for t in ts:
            t.join()

    def watch_single(self, ready_get, log=print):
        self._fan("watch_single", (ready_get, log))

    def watch_green(self, targets, baseline, need_fast, fill, green, log=print, reject_free=frozenset(), ready=None):
        self._fan("watch_green", (targets, baseline, need_fast, fill, green, log, reject_free, ready))

    def wait_snap(self, seconds, log=print):
        end = time.time() + seconds
        while time.time() < end and self.snap is None:
            if cli.is_complete(self.members[0].cid):
                for m in self.members:
                    m.verified_snapshot(log)
            if self.snap is not None or not self.alive():
                break
            time.sleep(POLL)
        return self.snap

    def adopt_into(self, sdir, log=print):
        (self._winner() or self.members[0]).adopt_into(sdir, log=log)


def make(chain, cid, stage, prompt, timeout, cases, note_extra="", src=None):
    """The duel for a chain stage: racer 1 alone when HCTF_DUEL_EXTRA is empty, else a DuelGroup. A strategy note
    (QUICK_FIX_NOTE) goes to racer 1 only: the extra racers' diversity is the model. `src`: copy the solver from there
    (a generalize duel started after its worker: the pre-worker snapshot)."""
    first = Duel(chain, cid, stage, prompt, timeout, cases, note_extra=note_extra)
    first.src = src
    if not EXTRA:
        return first
    extra = [Duel(chain, cid, stage, prompt, timeout, cases, n=i, model=m, effort=e)
             for i, (m, e) in enumerate(EXTRA, start=2)]
    for m in extra:
        m.src = src
    return DuelGroup([first, *extra])
