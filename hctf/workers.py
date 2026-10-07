"""LLM worker processes. One process per challenge stage; the orchestrator verifies the outcome.

local:    `claude -p` in WSL (your subscription). Repo hooks (.claude/settings.json) and skills apply.
homebase: `codex exec` on Homebase over SSH (Homebase token credits). The repo slice is rsynced to
          ~/hw, skills to ~/.codex/skills, and results are rsynced back when the worker exits.
"""
import json
import os
import shlex
import subprocess
import sys
import threading
import time
from pathlib import Path

from . import remote
from .paths import BIN, TMP, TOOLS

ROOT = Path(__file__).resolve().parent.parent
PROMPTS = ROOT / "hctf" / "prompts"
HB_WORK = "hw"  # ~/hw on Homebase


def render(_template, **kw):
    text = (PROMPTS / f"{_template}.md").read_text()
    for k, v in kw.items():
        text = text.replace("{" + k + "}", str(v))
    return text


def _logfile(chal_dir, stage, pool):
    chal_dir.mkdir(parents=True, exist_ok=True)
    return chal_dir / f"worker-{stage}-{pool}-{time.strftime('%Y%m%dT%H%M%S')}.log"


# ilio-style bounds: cap each worker's turns so a stuck agent can't grind up cost. Wall-clock timeout
# is passed in; turns are a second, independent ceiling. Override via HCTF_MAX_TURNS_<STAGE>.
MAX_TURNS = {"single": 80, "generalize": 50, "fix": 30, "ratchet": 40}


def _max_turns(stage):
    return int(os.environ.get(f"HCTF_MAX_TURNS_{stage.upper()}", MAX_TURNS.get(stage, 60)))


# Local `claude -p` workers run Opus 5.5 at high effort by default — these are hard RE/forensics
# challenges and the extra reasoning pays for itself. Override per run with HCTF_WORKER_MODEL /
# HCTF_WORKER_EFFORT (e.g. a cheaper model for a day of easy warmups). Homebase workers use codex,
# so this only applies to the local pool.
WORKER_MODEL = os.environ.get("HCTF_WORKER_MODEL", "claude-opus-5-5")
WORKER_EFFORT = os.environ.get("HCTF_WORKER_EFFORT", "high")

# Per-lane effort/model overrides — the main wall-clock lever. On a heavy day the whole sweep is bound by
# ONE slow single_solve LLM worker (Day 5 script-analysis: 357 fields, ~6.5 min at effort=high), while the
# other four lanes finish their full chain in ~2 min. Deterministic reuse/triage runs BEFORE the model, so
# a recognized family never reaches here; this only tunes the genuine LLM solves. Defaults keep the hard,
# correctness-critical lanes at the global default and relax only genuinely-easy warmups. Override any lane
# with HCTF_WORKER_EFFORT_<LANE> / HCTF_WORKER_MODEL_<LANE>, where <LANE> is the index lane upper-cased with
# '-' -> '_' (e.g. HCTF_WORKER_EFFORT_SCRIPT_ANALYSIS=medium, HCTF_WORKER_EFFORT_METADATA_FORENSICS=medium).
# To break the 4-min sweep on a heavy scripting day, lower script-analysis here AFTER validating correctness
# over a few days — it is the only lane on the critical path.
# Owner's rule: EVERY lane runs at the global effort (>= high), warmups included — no lane is relaxed by default.
# LANE_EFFORT is a raise-only FLOOR: a lane runs at max(global, LANE_EFFORT[lane]), so it can never drop a lane below
# the global effort. Day 6 xhigh experiment: script-analysis went from 9-14 submits (high, Days 4-5) to 1 (all 399
# answers right first try); the easy lanes only got 1.5-3x slower at xhigh with no accuracy to gain (0 wrong at high).
# Precedence: HCTF_WORKER_EFFORT_<LANE> (exact) > max(HCTF_WORKER_EFFORT global, LANE_EFFORT[lane]) > "high".
EFFORT_LEVELS = ("low", "medium", "high", "xhigh", "max")
LANE_EFFORT = {}  # Day 6 xhigh floors for script/binary reverted 2026-10-06: ~50% slower turns, no wall-clock gain
LANE_MODEL = {}


def _lane_key(lane):
    return (lane or "").upper().replace("-", "_")


def worker_effort(lane):
    exact = os.environ.get(f"HCTF_WORKER_EFFORT_{_lane_key(lane)}")
    if exact:
        return exact
    floor = LANE_EFFORT.get(lane)
    rank = {e: i for i, e in enumerate(EFFORT_LEVELS)}
    if floor and rank.get(floor, -1) > rank.get(WORKER_EFFORT, -1):
        return floor
    return WORKER_EFFORT


def worker_model(lane):
    return os.environ.get(f"HCTF_WORKER_MODEL_{_lane_key(lane)}") or LANE_MODEL.get(lane, WORKER_MODEL)

# Each worker is told it is an expert CTF player in its lane's specialty. Keyed by the index.json lane.
LANE_PERSONA = {
    "warmups": "an expert-level CTF player who specializes in warm-up and miscellaneous puzzle "
               "challenges (quick encodings, ciphers, stego, and lateral-thinking puzzles)",
    "metadata-forensics": "an expert-level CTF player who specializes in digital forensics and "
                          "file-metadata analysis (file carving, EXIF/container metadata, hashes, "
                          "embedded and hidden data)",
    "script-analysis": "an expert-level CTF player who specializes in script reverse engineering and "
                       "deobfuscation (batch/cmd, PowerShell, VBScript, JavaScript, and shell obfuscation)",
    "binary-reverse-engineering": "an expert-level CTF player who specializes in binary reverse "
                                  "engineering (ELF/PE/.NET internals, disassembly, demangling, and "
                                  "static analysis of compiled executables)",
    "mobile-android": "an expert-level CTF player who specializes in Android mobile application reverse "
                      "engineering (APK/manifest analysis, smali/dex, intents, and deep links)",
    "welcome": "an expert-level CTF player working the event's onboarding challenges",
}


def lane_persona(lane):
    """One-line expert persona for a lane, injected into worker prompts (point 5)."""
    return LANE_PERSONA.get(lane, "an expert-level CTF player")


def lane_playbook(lane):
    """Per-lane field-label playbook (lib/playbook.py), injected as {playbook} so the worker starts from the
    GM's label grammar for this lane instead of guessing synonyms. Degrades to a short note if lib isn't importable."""
    try:
        from lib import playbook
        return playbook.for_lane(lane)
    except Exception:  # noqa: BLE001 - never fail a worker launch over the playbook
        return "(playbook unavailable; resolve non-flag labels with `hctf labels`.)"


STOPPED_RC = -15  # run_local's return code when `stop` ended the worker (its job was already done)

# Worker sandbox (bubblewrap): the rehearsal copy rehearsal (2026-10-06) caught a script-analysis worker running
# `find / -name solve.py`, then COPYING the main account's Day 6 solver out of ~/huntress-2026 -- cross-copy
# contamination that no prompt rule can be trusted to prevent. Every local worker now runs with these paths replaced
# by empty, throwaway tmpfs dirs: every other ~/huntress-2026* tree (the other account), all Claude session
# transcripts (~/.claude/projects: orchestrator sessions hold solutions), /mnt/c (Windows side), plus
# HCTF_SANDBOX_HIDE (colon-separated). HCTF_WORKER_SANDBOX=0 disables it.
WORKER_SANDBOX = os.environ.get("HCTF_WORKER_SANDBOX", "1") != "0"


def sandbox_hidden_paths():
    home = Path.home()
    hide = [p for p in home.glob("huntress-2026*") if p.is_dir() and p.resolve() != ROOT.resolve()]
    hide += [home / ".claude" / "projects", Path("/mnt/c")]
    hide += [Path(x) for x in os.environ.get("HCTF_SANDBOX_HIDE", "").split(":") if x]
    return [p for p in hide if p.exists()]


def sandboxed(cmd):
    """Wrap a worker command in bwrap with sandbox_hidden_paths() masked; unchanged if bwrap is unavailable."""
    import shutil as _sh
    if not WORKER_SANDBOX or not _sh.which("bwrap"):
        return cmd
    hidden = sandbox_hidden_paths()
    # directories -> empty tmpfs; FILES -> /dev/null bound over them (bwrap can't mount a tmpfs on a file: a masked
    # reference/SPEED.md made every worker exit 1 in the from-scratch main replay)
    masks = [a for p in hidden for a in (("--tmpfs", str(p)) if Path(p).is_dir() else ("--ro-bind", "/dev/null", str(p)))]
    # The rehearsal copy's .venv / tools / bin/* are SYMLINKS into the main tree: masking it silently took away pyzipper,
    # rizin, exiftool... (replay runs lost 25-30s per worker on that). Re-expose exactly those targets, read-only.
    binds = []
    for link in [*ROOT.glob(".venv"), *ROOT.glob("tools"), *(ROOT / "bin").glob("*")]:
        if link.is_symlink():
            tgt = link.resolve()
            if tgt.exists() and any(str(tgt).startswith(str(h) + "/") for h in hidden if Path(h).is_dir()):
                binds += ["--ro-bind", str(tgt), str(tgt)]
    return ["bwrap", "--dev-bind", "/", "/", *masks, *binds, "--die-with-parent", "--", *cmd]


def run_local(chal_dir, stage, prompt, env_extra, timeout, stop=None):
    """Blocking. Returns (returncode, logfile). `stop` (threading.Event): when set, the worker is terminated at once
    and STOPPED_RC returned -- the orchestrator sets it once the Single Solve is CORRECT and the solver verifiably
    reproduces it, so post-correct hardening never sits on the critical path (Day 6: 60% of worker time)."""
    log = _logfile(chal_dir, stage, "local")
    env = dict(os.environ)
    env.update({k: str(v) for k, v in env_extra.items()})
    env["HCTF_WORKER_START"] = str(time.time())
    env["TMPDIR"] = str(TMP)  # keep every worker's scratch files inside the project
    env["PYTHONPATH"] = f"{ROOT}:{env.get('PYTHONPATH', '')}"  # so solvers/tools can `import lib.*`
    env["PATH"] = f"{BIN}:{TOOLS / 'node' / 'bin'}:{ROOT / '.venv' / 'bin'}:{Path.home() / '.local/bin'}:{env.get('PATH', '')}"
    lane = env_extra.get("HCTF_LANE") or env.get("HCTF_LANE")
    cmd = ["claude", "-p", prompt, "--dangerously-skip-permissions", "--max-turns", str(_max_turns(stage)),
           "--model", worker_model(lane), "--effort", worker_effort(lane),
           "--output-format", "stream-json", "--verbose",
           # Isolation: no claude.ai MCP connectors (23 connected at every worker start, none used) and no Claude
           # auto-memory (Day 6 workers wrote unversioned GM facts to ~/.claude/projects/-home-testpwn-huntress-2026/
           # memory and re-read them every run). Durable knowledge goes through lib/ via the post-run ratchet only.
           "--strict-mcp-config", "--settings", json.dumps({"autoMemoryEnabled": False})]
    with open(log, "w") as out:
        p = subprocess.Popen(sandboxed(cmd), cwd=ROOT, stdout=out, stderr=subprocess.STDOUT, env=env,
                             start_new_session=True)
        deadline = time.time() + timeout
        while True:
            try:
                return p.wait(timeout=0.5), log
            except subprocess.TimeoutExpired:
                pass
            if stop is not None and stop.is_set():
                _kill_group(p, grace=2.0)
                return STOPPED_RC, log
            if time.time() >= deadline:
                _kill_group(p, grace=0)
                return -9, log


def _kill_group(p, grace):
    """SIGTERM the worker's process group, then SIGKILL after `grace` seconds."""
    import signal
    try:
        os.killpg(p.pid, signal.SIGTERM if grace else signal.SIGKILL)
        if grace:
            try:
                p.wait(timeout=grace)
            except subprocess.TimeoutExpired:
                os.killpg(p.pid, signal.SIGKILL)
                p.wait(timeout=5)
    except (ProcessLookupError, PermissionError):
        pass


_sync_lock = threading.Lock()


def _base_sig():
    """Fingerprint of the code Homebase needs (hctf, lib, bin, skills, CLAUDE.md, AGENTS.md): path+size+mtime."""
    import hashlib
    h = hashlib.sha1()
    for d in ("hctf", "lib", "bin", "skills", "CLAUDE.md", "AGENTS.md"):
        base = ROOT / d
        files = [base] if base.is_file() else sorted(base.rglob("*")) if base.exists() else []
        for f in files:
            if "__pycache__" in f.parts or not (f.is_file() or f.is_symlink()):
                continue
            st = f.lstat()
            h.update(f"{f.relative_to(ROOT)}|{st.st_size}|{st.st_mtime_ns}\n".encode())
    return h.hexdigest()


def sync_homebase_base(force=False):
    """Push hctf + lib + skills + bin to Homebase (shared by all homebase workers). Done once per process. If the VM
    already holds this exact code (fingerprint written after the last sync -- e.g. by day.sh's arm-time warm-up), it is
    ONE `cat` round-trip; otherwise the rsyncs run in parallel (sequential over the ~255ms VPN cost ~12s, which kept the
    first timed attempts of a run on the local fallback)."""
    from concurrent.futures import ThreadPoolExecutor
    with _sync_lock:
        if _hb.get("base_synced") and not force:
            return
        sig = _base_sig()
        if not force:
            r = remote.ssh(f"cat ~/{HB_WORK}/.base_sig 2>/dev/null", timeout=20, check=False)
            if r.stdout.strip() == sig:
                _hb["base_synced"] = True
                return
        remote.ssh(f"mkdir -p ~/{HB_WORK}/challenges ~/.codex/skills ~/hctf")  # ~/hctf: absent on a fresh VM
        items = [(ROOT / d, f"~/{HB_WORK}/") for d in ("hctf", "lib", "bin", "skills") if (ROOT / d).exists()]
        items += [(ROOT / f, f"~/{HB_WORK}/{f}") for f in ("CLAUDE.md", "AGENTS.md") if (ROOT / f).exists()]
        with ThreadPoolExecutor(max_workers=len(items)) as ex:
            list(ex.map(lambda it: remote.rsync_to(*it), items))
        remote.ssh(f"rsync -a --delete ~/{HB_WORK}/skills/ ~/.codex/skills/ && cp ~/{HB_WORK}/hctf/gm.py ~/hctf/gm.py"
                   f" && echo {sig} > ~/{HB_WORK}/.base_sig")
        _hb["base_synced"] = True


def run_timed(solver_dir, cid, op="start", timeout=60):
    """Run the clock-critical timed attempt LOCALLY against the public GM (pairing token).
    No VM, no SSH — the whole start->download->solve->submit path runs here. Returns hb_timed's JSON dict."""
    rel = solver_dir.relative_to(ROOT)
    env = dict(os.environ, PYTHONPATH=f"{ROOT}:{os.environ.get('PYTHONPATH', '')}")
    if os.environ.get("HCTF_TIMED_GM_URL"):
        # Clock-critical calls straight to this GM (e.g. the real one while a replay proxy fronts everything else: the
        # proxy opens a fresh TLS connection per call, ~0.5-1 s each inside a 6-7 s window).
        env["HUNTRESS_GAME_MASTER_URL"] = os.environ["HCTF_TIMED_GM_URL"]
    try:
        r = subprocess.run([sys.executable, str(ROOT / "hctf" / "hb_timed.py"), cid, str(rel), "--op", op],
                           cwd=ROOT, capture_output=True, text=True, timeout=timeout, env=env)
    except subprocess.TimeoutExpired:
        return {"result": "exec_error", "detail": "local hb_timed timed out"}
    try:
        return json.loads(r.stdout.strip().splitlines()[-1])
    except (IndexError, ValueError):
        return {"result": "exec_error", "detail": (r.stdout + r.stderr)[-500:]}


TIGHT_WINDOW = float(os.environ.get("HCTF_TIGHT_WINDOW", "8"))      # clocks this short go to Homebase
AUTO_HOMEBASE = os.environ.get("HCTF_AUTO_HOMEBASE", "1") != "0"   # 0: never power Homebase on by itself
CREDIT_FLOOR = float(os.environ.get("HCTF_CREDIT_HARD", "1.5"))      # never power on below this many credits
_hb_lock = threading.Lock()
HB_HEALTH_S = float(os.environ.get("HCTF_HB_HEALTH_S", "5"))   # background Homebase reachability probe period
HB_FRESH_S = 3 * HB_HEALTH_S                                     # a health verdict older than this is "unknown"
_hb = {"powered_by_us": False, "provisioned": False, "ok": False, "checked": 0.0, "thread": None}
HB_DEPS = ["elftools", "pefile", "capstone", "Crypto", "pyzipper", "androguard", "droidasc", "refinery"]


def known_window(cid):
    """Clock length (s) this challenge's timed mode has shown: the last timed result, else the saved start.json."""
    from . import cli
    try:
        return float(json.loads((cli.cdir(cid) / "window.json").read_text())["seconds"])
    except (OSError, ValueError, KeyError, TypeError):
        pass
    start = cli.load(cid, "start.json") or {}
    try:
        import datetime as dt
        a = dt.datetime.fromisoformat(start["started_at"].replace("Z", "+00:00"))
        d = dt.datetime.fromisoformat(start["deadline"].replace("Z", "+00:00"))
        return (d - a).total_seconds()
    except (KeyError, TypeError, ValueError, AttributeError):
        return None


def _provision(log):
    """Make sure Homebase has the solver deps: a 2s import check, and the full setup only if something is missing.
    Runs in the health thread -- never under a lock a timed attempt waits on (Day 6: the first-time apt/pip setup ran
    under _hb_lock at the first timed attempt and queued three lanes' Time Trials behind it)."""
    try:
        mods = ",".join(repr(m) for m in HB_DEPS)
        r = remote.ssh(f"python3 -c \"import importlib.util as u,sys; sys.exit(any(u.find_spec(m) is None for m in [{mods}]))\"",
                       timeout=30, check=False)
        if r.returncode != 0:
            log("[homebase] solver deps missing -> provisioning in the background")
            remote.rsync_to(ROOT / "setup" / "homebase_setup.sh", "~/homebase_setup.sh")
            remote.ssh("bash ~/homebase_setup.sh >/dev/null 2>&1", timeout=600, check=False)
        sync_homebase_base()
        _hb["provisioned"] = True
    except Exception as e:  # noqa: BLE001 - provisioning is best-effort; deps usually already present
        log(f"[homebase] provisioning note (continuing): {e}")
        _hb["provisioned"] = True


def _health_loop(log):
    was = None
    while True:
        ok = remote.probe()
        _hb.update(ok=ok, checked=time.time())
        if ok != was:
            log(f"[homebase] {'reachable' if ok else 'NOT reachable'} (health probe every {HB_HEALTH_S:g}s)")
            was = ok
        if ok and not _hb["provisioned"]:
            _provision(log)
        time.sleep(HB_HEALTH_S)


def start_homebase_health(log=print):
    """Start the background Homebase health thread once per process (prewarm at run start)."""
    with _hb_lock:
        if _hb["thread"] is None:
            t = threading.Thread(target=_health_loop, args=(log,), daemon=True, name="hb-health")
            _hb["thread"] = t
            t.start()


def _homebase_ready(log=print):
    """Non-blocking readiness for a tight timed window: the health thread's latest verdict. Never holds a lock across
    an SSH call and never latches a failure for the run (Day 6: one probe in a VPN gap sent every attempt local).
    Without a fresh verdict (first call / CLI use), probe once synchronously."""
    start_homebase_health(log)
    if time.time() - _hb["checked"] > HB_FRESH_S:
        _hb.update(ok=remote.probe(), checked=time.time())
    return bool(_hb["ok"] and _hb["provisioned"])


def wait_homebase(timeout, log=print):
    """Wait up to `timeout` seconds for Homebase to be healthy (e.g. riding out a VPN gap before a retry)."""
    start_homebase_health(log)
    end = time.time() + timeout
    while time.time() < end:
        if _hb["ok"] and _hb["provisioned"]:
            return True
        time.sleep(0.5)
    return bool(_hb["ok"])


def power_off_homebase_if_ours(log=print):
    """Called when a run ends: switch Homebase off again if this process switched it on (it burns ~2 credits/h)."""
    with _hb_lock:
        if not _hb["powered_by_us"]:
            return
        try:
            remote.power("off")
            _hb["powered_by_us"] = False
            log("[homebase] powered off (we powered it on for tight timed windows)")
        except Exception as e:  # noqa: BLE001
            log(f"[homebase] power-off failed, switch it off manually (`hctf hb off`): {e}")


def run_timed_auto(solver_dir, cid, op="start", timeout=60, log=print):
    """Dispatch a timed attempt. HOMEBASE-FIRST for strict clocks (user policy): a window <= HCTF_TIGHT_WINDOW
    seconds, or one not yet known (a fresh mode; every Day 2-4 TT/Mastery window was 6-7s), runs next to the GM on
    Homebase (prewarmed at run start). Local over the pairing token is the fallback (Homebase unavailable / below the
    credit floor / remote exec failure) and the default for known-roomy windows. The old "local first, Homebase only
    after a local expiry" rule burned one attempt per tight mode, and the rehearsal copy run showed local fits a 7s
    462-field Mastery only by ~0.9s (GM origin ~1.3-1.5s/call from here). HCTF_GM_TRANSPORT=ssh forces Homebase."""
    if remote.gm_transport() != "local":
        res = run_hb_timed(solver_dir, cid, op=op, timeout=timeout)
        if str(res.get("result", "")).lower() == "exec_error" and remote._have_token():
            log(f"[{cid}] Homebase run failed ({str(res.get('detail'))[:120]}); falling back to local")
            res = run_timed(solver_dir, cid, op=op, timeout=timeout)
            res["routed"] = "local (forced-ssh homebase failed)"
        else:
            res.setdefault("routed", "homebase (forced transport)")
        return res
    win = known_window(cid)
    tight = win is None or win <= TIGHT_WINDOW
    if AUTO_HOMEBASE and tight and _homebase_ready(log):
        res = run_hb_timed(solver_dir, cid, op=op, timeout=timeout)
        if (str(res.get("result", "")).lower() in ("solver_incomplete", "solver_error") and res.get("missing")
                and not res.get("submitted")):
            # The solver produced NOTHING on Homebase. Blame the environment only if the SAME variant (bytes pulled back
            # after the failure) works locally (rehearsal rehearsal: solve.py shelled out to 7z, absent on the the VM).
            # Otherwise it is a solver gap (run 3: mobile Mastery's `delivery N: x.apk` names) -> plain generalize.
            try:
                import re as _re
                from . import solvers as _solvers
                tdir = ROOT / ".run" / "tmp-timed" / _re.sub(r"[^A-Za-z0-9]+", "_", cid)
                tc = json.loads((tdir / "contract.json").read_text())
                got, err, _ = _solvers.run_solver(Path(solver_dir), tc, tdir, timeout=20)
                if not err and any(got.get(a) for a in res["missing"]):
                    res["hb_env_mismatch"] = True
                    log(f"[{cid}] solver produced no answers ON HOMEBASE but does locally on the same variant -- "
                        "Homebase environment mismatch")
            except Exception as e:  # noqa: BLE001 - diagnosis only
                log(f"[{cid}] env-mismatch check skipped: {e}")
        detail = str(res.get("detail", ""))
        if str(res.get("result", "")).lower() != "exec_error" or (
                "solve.py" in detail and ("timed out" in detail or "TimeoutExpired" in detail)):
            # (A SOLVER timeout on Homebase is returned as-is: running the same solver locally only burns another
            # attempt -- replay run 2 lost ~19s that way. The caller routes it to a speed generalize.)
            res["routed"] = f"homebase ({'window unknown' if win is None else f'window {win:g}s'})"
            return res
        log(f"[{cid}] Homebase run failed ({str(res.get('detail'))[:120]}); falling back to local")
    res = run_timed(solver_dir, cid, op=op, timeout=timeout)
    res.setdefault("routed", "local" if not tight else "local (Homebase unavailable)")
    w = res.get("window") or win
    if w is not None and w <= TIGHT_WINDOW and str(res.get("result", "")).lower() == "expired":
        _mark_expired_locally(cid, w)
        if AUTO_HOMEBASE and _homebase_ready(log):
            log(f"[{cid}] {w:g}s window expired locally; retrying on Homebase next to the GM")
            res = run_hb_timed(solver_dir, cid, op="start", timeout=timeout)
            res["routed"] = f"homebase after local expiry (window {w:g}s)"
    return res


def _window_file(cid):
    from . import cli
    return cli.cdir(cid) / "window.json"


def _expired_locally(cid):
    """True once a local attempt of this challenge expired on its tight clock (a 6s window that the solver and
    answer count make too slow over the public GM; some 6s windows DO fit locally, so size alone isn't enough)."""
    try:
        return bool(json.loads(_window_file(cid).read_text()).get("local_expired"))
    except (OSError, ValueError):
        return False


def _mark_expired_locally(cid, seconds):
    p = _window_file(cid)
    try:
        d = json.loads(p.read_text())
    except (OSError, ValueError):
        d = {}
    d.update(seconds=seconds, local_expired=True)
    p.write_text(json.dumps(d))


_pushed = {}  # solver dir -> file signature last rsynced to Homebase (this process)


def run_hb_timed(solver_dir, cid, op="start", timeout=60):
    """Run the clock-critical timed attempt ON Homebase (adjacent to the GM). Returns hb_timed's JSON dict.
    Syncs hctf+lib (base) and the solver so hb_timed can execute it next to the GM."""
    rel = solver_dir.relative_to(ROOT)
    # Kickoff (sync + solver push) runs over the flaky local->Homebase VPN link; the retrying ssh/rsync ride
    # through transient drops, but if it still fails, return exec_error so run_timed_auto falls back to local
    # rather than crashing the whole attempt. (Once hb_timed is running, its in-window GM calls are HB->inside
    # proxy, off the VPN, so they stay fast and stable.)
    try:
        sync_homebase_base()
        if solver_dir.exists():
            # Skip the push when the solver code is unchanged since the last push of this dir (TT -> Mastery: same
            # solver, ~1 round-trip saved between modes). ONE round-trip otherwise: the remote rsync creates the dir
            # itself; cases/ (6-8 MB of regression bytes on the hard lanes) is never needed to run the solver.
            sig = tuple(sorted((str(f.relative_to(solver_dir)), f.stat().st_mtime_ns, f.stat().st_size)
                               for f in solver_dir.rglob("*") if f.is_file()
                               and "cases" not in f.relative_to(solver_dir).parts and "__pycache__" not in f.parts))
            if _pushed.get(str(solver_dir)) != sig:
                remote.rsync_to(str(solver_dir) + "/", f"~/{HB_WORK}/{rel}/", exclude=["cases/", "__pycache__/"],
                                mkdir=f"~/{HB_WORK}/{rel}")
                _pushed[str(solver_dir)] = sig
        else:
            remote.ssh(f"mkdir -p ~/{HB_WORK}/{rel}")
    except (RuntimeError, subprocess.SubprocessError, OSError) as e:  # incl. remote-command failures
        return {"result": "exec_error", "detail": f"homebase kickoff failed: {e}"}
    # Use the GM's INSIDE proxy from Homebase (network-path identity = same test account as the pairing token,
    # sub-ms latency) so tight windows (e.g. the 6s scripting Time Trial) fit; the public GM's ~2.7s/call
    # round-trips blow those windows even warm.
    try:
        r = remote.ssh(f"cd ~/{HB_WORK} && HUNTRESS_GAME_MASTER_URL={remote.INSIDE_GM} "
                       f"python3 hctf/hb_timed.py {shlex.quote(cid)} {shlex.quote(str(rel))} --op {op}",
                       timeout=timeout, check=False)
    except (remote.Unreachable, subprocess.SubprocessError, OSError) as e:
        return {"result": "exec_error", "detail": f"homebase exec failed: {e}"}
    try:
        res = json.loads(r.stdout.strip().splitlines()[-1])
    except (IndexError, ValueError):
        return {"result": "exec_error", "detail": (r.stdout + r.stderr)[-500:]}
    # Bring the attempt's bytes + result.json back, so the variant can become a local regression case.
    import re as _re
    slug = _re.sub(r"[^A-Za-z0-9]+", "_", cid)
    local = ROOT / ".run" / "tmp-timed" / slug
    def pull(own_conn=False):
        if local.exists():
            for f in local.glob("*"):
                if f.is_file():
                    f.unlink()
        remote.rsync_from(f"~/{HB_WORK}/.run/tmp-timed/{slug}", str(local), own_conn=own_conn)
    if str(res.get("result", "")).lower() == "correct":
        # A pass: the next mode must not wait on up to ~4 MB of evidence coming back over the VPN. timed.process_result
        # runs the pull + regression-case capture in the background via this hook.
        res["_pull"] = lambda: pull(own_conn=True)
        return res
    try:
        pull()  # a failure needs the variant's bytes locally (generalize / probe) before anything else
    except Exception as e:  # noqa: BLE001 - capture is best-effort
        res["capture_note"] = f"could not fetch the attempt's bytes from Homebase: {e}"
    return res


def run_homebase(chal_root, log_dir, stage, prompt, env_extra, timeout):
    """Blocking. chal_root: challenges/dayNN/<lane>-<title>/, mirrored to the same relative path under ~/hw
    (so every path in the prompt is valid on both sides). Returns (returncode, logfile)."""
    sync_homebase_base()
    rel = chal_root.relative_to(ROOT)
    remote.ssh(f"mkdir -p ~/{HB_WORK}/{rel}")
    remote.rsync_to(str(chal_root) + "/", f"~/{HB_WORK}/{rel}/")
    remote.rsync_to(ROOT / "challenges" / "index.json", f"~/{HB_WORK}/challenges/index.json")
    log = _logfile(log_dir, stage, "homebase")
    env_extra = {k: (str(Path(v).relative_to(ROOT)) if isinstance(v, Path) else v) for k, v in env_extra.items()}
    envs = " ".join(f"{k}={shlex.quote(str(v))}" for k, v in {**env_extra, "HCTF_ON_HOMEBASE": 1}.items())
    cmd = (f"cd ~/{HB_WORK} && {envs} PYTHONPATH=~/{HB_WORK} "
           f"PATH=~/{HB_WORK}/bin:~/{HB_WORK}/tools/node/bin:~/{HB_WORK}/.venv/bin:$PATH "
           f"timeout {int(timeout)} codex exec --dangerously-bypass-approvals-and-sandbox --skip-git-repo-check "
           f"{shlex.quote(prompt)} </dev/null")
    try:
        r = remote.ssh(cmd, timeout=timeout + 60, check=False)
        rc, text = r.returncode, r.stdout + r.stderr
    except subprocess.TimeoutExpired:
        rc, text = -9, "timeout"
    log.write_text(text)
    # Pull results back: solver, notes, submissions, confirmed answers, new artifacts.
    remote.rsync_from(f"~/{HB_WORK}/{rel}", chal_root)
    return rc, log


def last_text(log):
    """Final assistant text from a claude stream-json log (for dashboards/debugging)."""
    try:
        for line in reversed(Path(log).read_text().splitlines()):
            if line.startswith("{") and '"type":"result"' in line.replace(" ", ""):
                return json.loads(line).get("result", "")[-800:]
    except OSError:
        pass
    return ""
