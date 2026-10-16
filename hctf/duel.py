"""DUEL workers: best-of-2 for the LLM stages that bound a day (brand-new Single Solves, repeat generalizes).

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
"""
import os
import shutil
import threading
import time

from . import cli, paths, solvers, timed, workers

ROOT = paths.ROOT
ENABLED = os.environ.get("HCTF_DUEL", "1") != "0"
# binary is out by default: Ghidra + a 230 MB solver corpus per copy on a 7 GB WSL box
LANES = {x.strip() for x in os.environ.get(
    "HCTF_DUEL_LANES", "warmups,metadata-forensics,script-analysis,mobile-android").split(",") if x.strip()}
MAX_CONCURRENT = int(os.environ.get("HCTF_DUEL_MAX", "3"))
MODEL = os.environ.get("HCTF_DUEL_MODEL", "")            # "" = the lane's normal worker model
EFFORT = os.environ.get("HCTF_DUEL_EFFORT", "medium")     # diversity + speed: the chain's worker runs at high
DELAY = float(os.environ.get("HCTF_DUEL_DELAY", "15"))    # single: give the reuse race its 3-9 s first
GEN_AFTER = int(os.environ.get("HCTF_DUEL_GENERALIZE_AFTER", "1"))   # duel the 2nd+ generalize of a mode; -1 = never
GEN_FIRST = os.environ.get("HCTF_DUEL_GENERALIZE_FIRST", "1") != "0"  # ... and the 1st when label-only / speed-only
WAIT = float(os.environ.get("HCTF_DUEL_WAIT", "600"))     # chain worker ended without a result: wait this long for the duel
POLL = float(os.environ.get("HCTF_DUEL_POLL", "1.0"))
STABLE = float(os.environ.get("HCTF_DUEL_STABLE", "0.75"))
GREEN_CASE_TIMEOUT = float(os.environ.get("HCTF_BASELINE_CASE_TIMEOUT", "8"))

_live = set()
_live_lock = threading.Lock()


def eligible(lane, key=None):
    """(ok, why). Checks only: the slot is taken at the actual launch (_reserve), after the single's DELAY -- rehearsal D14
    replay: duels still waiting out their delay (singles already won by the reuse race) blocked script's duel."""
    if not ENABLED:
        return False, "HCTF_DUEL=0"
    if lane not in LANES and not _binary_ok(lane):
        return False, f"lane {lane} not in HCTF_DUEL_LANES"
    with _live_lock:
        if len(_live) >= MAX_CONCURRENT:
            return False, f"{len(_live)} duels already running"
    return True, ""


# binary duel only with this much MemAvailable (GB) at the decision; 0 = never (default until measured on a rehearsal copy: two
# Ghidra JVMs on the 7 GB box). D15: binary single +89 s by the lone worker, no duel.
BINARY_MIN_AVAIL_GB = float(os.environ.get("HCTF_DUEL_BINARY_MIN_AVAIL_GB", "0"))


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


def _reserve(key):
    with _live_lock:
        if len(_live) >= MAX_CONCURRENT:
            return False
        _live.add(key)
        return True


def _mirror(sdir, kind):
    """.run/duel[-gen]-dayNN/<chal>/solver for challenges/dayNN/<chal>/solver (None for other layouts)."""
    try:
        rel = sdir.relative_to(paths.CHALLENGES).parts
    except ValueError:
        return None
    if len(rel) != 3:
        return None
    tag = "duel" if kind == "single" else "duel-gen"
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
        # case artifacts are big and never written: hard-link them; everything else (expected.json!) is a real copy
        if "/artifacts/" in s.replace(os.sep, "/"):
            try:
                os.link(s, d)
                return d
            except OSError:
                pass
        return shutil.copy2(s, d)
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns("__pycache__"), copy_function=link_or_copy)


def _code_mtimes(d):
    if not d.exists():
        return {}
    return {p.name: p.stat().st_mtime for p in d.iterdir() if p.is_file() and p.suffix == ".py"}


NOTE = """

---
## You are the DUEL worker
Another worker (different configuration) is working on this same task right now from the same starting point; the
first verified result wins and the other is ended. Work independently:
- YOUR solver directory is `{ddir}` -- every mention of the solver directory above means this one, and
  `hctf submit --from-solver`, `hctf solver-test` and `hctf solver-run` already use it. Never write under `{main}`.
- Keep your notes in `{notes}` (the other worker writes notes.md; read it for leads, never edit it).
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
    def __init__(self, chain, cid, stage, prompt, timeout, cases, note_extra=""):
        self.chain, self.cid, self.stage, self.timeout = chain, cid, stage, timeout
        self.note_extra = note_extra
        self.key = f"{chain.base}:{stage}"
        self.ddir = _mirror(chain.sdir, stage)
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

    def alive(self):
        return self.thread is not None and self.thread.is_alive()

    def _render(self):
        main_rel, d_rel = str(self.chain.sdir.relative_to(ROOT)), str(self.ddir.relative_to(ROOT))
        text = self.prompt.replace(str(self.chain.sdir), str(self.ddir)).replace(main_rel, d_rel)
        notes = cli.cdir(self.cid).relative_to(ROOT) / "duel-notes.md"
        return text + NOTE.format(ddir=d_rel, main=main_rel, notes=notes) + self.note_extra.replace("<base>",
                                                                                                   self.chain.base)

    def _env(self):
        env = self.chain._worker_env(self.cid, self.stage)
        env.update({"HCTF_SOLVER_DIR": self.ddir, "HCTF_SOLVER_DIR_OVERRIDE": self.ddir, "HCTF_DUEL": "1",
                    "HCTF_LOG_POOL": "duel", "HCTF_X_EFFORT": EFFORT})
        if MODEL:
            env["HCTF_X_MODEL"] = MODEL
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
                if not _reserve(self.key):
                    log(f"[{self.cid}] no duel {self.stage}: {MAX_CONCURRENT} duels already running")
                    return
                if self.cases and self.stage == "single":
                    join = getattr(self.chain, "_join_prior_cases", None)
                    if join:
                        join(self.cid)    # the background prior cases/ copy (stage_prior_cases) must be complete
                _copy_solver(self.chain.sdir, self.ddir, self.cases)
                self.copied.set()
                log(f"[{self.cid}] duel {self.stage} worker -> local (effort {EFFORT}"
                    f"{', model ' + MODEL if MODEL else ''}) on {self.ddir.relative_to(ROOT)}")
                self.rc, lg = workers.run_local(cli.cdir(self.cid), self.stage, self._render(), self._env(),
                                                self.timeout, stop=self.stop_evt)
                log(f"[{self.cid}] duel {self.stage} worker exit {self.rc} ({lg.name})")
            except Exception as e:  # noqa: BLE001 - the duel is optional
                log(f"[{self.cid}] duel {self.stage} note: {e}")
            finally:
                with _live_lock:
                    _live.discard(self.key)
        self.thread = threading.Thread(target=body, daemon=True, name=f"duel-{self.stage}-{self.chain.base}")
        self.thread.start()

    def stop(self, join=10.0):
        self.stop_evt.set()
        if self.thread is not None:
            self.thread.join(timeout=join)
        with _live_lock:
            _live.discard(self.key)

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
    def watch_green(self, targets, baseline, need_fast, fill, green, log=print):
        try:
            while not self.copied.wait(0.5):
                if self.stop_evt.is_set() or (self.thread is not None and not self.alive()):
                    return
            start, checked = _code_mtimes(self.ddir), None
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
                    if not solvers.targets_pass(self.ddir, targets, fill, timeout=GREEN_CASE_TIMEOUT):
                        continue   # target still failing: no full-corpus replay for this edit
                    res = solvers.test_solver(self.ddir, timeout=GREEN_CASE_TIMEOUT)
                except Exception:  # noqa: BLE001
                    continue
                if _code_mtimes(self.ddir) != m:
                    checked = None
                    continue
                ok = {r["case"] for r in res if r.get("ok")}
                filled = {r["case"] for r in res if r.get("total") and r.get("answered") == r.get("total")
                          and not r.get("error")}
                fast = all(r.get("seconds", 99) < 2.0 for r in res if r["case"] in (targets | set(fill)))
                if targets <= ok and set(fill) <= filled and baseline <= ok and (fast or not need_fast):
                    if fill and not (targets & ok):
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
