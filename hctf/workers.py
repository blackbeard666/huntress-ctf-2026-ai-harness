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
MAX_TURNS = {"single": 80, "generalize": 50, "fix": 30}


def _max_turns(stage):
    return int(os.environ.get(f"HCTF_MAX_TURNS_{stage.upper()}", MAX_TURNS.get(stage, 60)))


# Local `claude -p` workers run Opus 5.5 at high effort by default — these are hard RE/forensics
# challenges and the extra reasoning pays for itself. Override per run with HCTF_WORKER_MODEL /
# HCTF_WORKER_EFFORT (e.g. a cheaper model for a day of easy warmups). Homebase workers use codex,
# so this only applies to the local pool.
WORKER_MODEL = os.environ.get("HCTF_WORKER_MODEL", "claude-opus-5-5")
WORKER_EFFORT = os.environ.get("HCTF_WORKER_EFFORT", "high")

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


def run_local(chal_dir, stage, prompt, env_extra, timeout):
    """Blocking. Returns (returncode, logfile)."""
    log = _logfile(chal_dir, stage, "local")
    env = dict(os.environ)
    env.update({k: str(v) for k, v in env_extra.items()})
    env["HCTF_WORKER_START"] = str(time.time())
    env["TMPDIR"] = str(TMP)  # keep every worker's scratch files inside the project
    env["PYTHONPATH"] = f"{ROOT}:{env.get('PYTHONPATH', '')}"  # so solvers/tools can `import lib.*`
    env["PATH"] = f"{BIN}:{TOOLS / 'node' / 'bin'}:{ROOT / '.venv' / 'bin'}:{Path.home() / '.local/bin'}:{env.get('PATH', '')}"
    cmd = ["claude", "-p", prompt, "--dangerously-skip-permissions", "--max-turns", str(_max_turns(stage)),
           "--model", WORKER_MODEL, "--effort", WORKER_EFFORT,
           "--output-format", "stream-json", "--verbose"]
    with open(log, "w") as out:
        p = subprocess.Popen(cmd, cwd=ROOT, stdout=out, stderr=subprocess.STDOUT, env=env, start_new_session=True)
        try:
            return p.wait(timeout=timeout), log
        except subprocess.TimeoutExpired:
            os.killpg(p.pid, 9)
            return -9, log


_sync_lock = threading.Lock()


def sync_homebase_base():
    """Push hctf + lib + skills + bin to Homebase (shared by all homebase workers)."""
    with _sync_lock:
        remote.ssh(f"mkdir -p ~/{HB_WORK}/challenges ~/.codex/skills")
        for d in ("hctf", "lib", "bin", "skills"):
            if (ROOT / d).exists():
                remote.rsync_to(ROOT / d, f"~/{HB_WORK}/")
        remote.ssh(f"rsync -a --delete ~/{HB_WORK}/skills/ ~/.codex/skills/ && cp ~/{HB_WORK}/hctf/gm.py ~/hctf/gm.py")
        for f in ("CLAUDE.md", "AGENTS.md"):
            if (ROOT / f).exists():
                remote.rsync_to(ROOT / f, f"~/{HB_WORK}/{f}")


def run_timed(solver_dir, cid, op="start", timeout=60):
    """Run the clock-critical timed attempt LOCALLY against the public GM (pairing token).
    No VM, no SSH — the whole start->download->solve->submit path runs here. Returns hb_timed's JSON dict."""
    rel = solver_dir.relative_to(ROOT)
    env = dict(os.environ, PYTHONPATH=f"{ROOT}:{os.environ.get('PYTHONPATH', '')}")
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
_hb = {"powered_by_us": False, "provisioned": False, "failed": False}


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


def _homebase_ready(log=print):
    """Power Homebase on (once per process) and provision its solver deps, for clock windows too tight for the
    public GM's ~2.7s round-trips. Returns False (caller stays local) if it can't be brought up."""
    with _hb_lock:
        if _hb["failed"]:
            return False
        try:
            st = remote.power("status")
            if st.get("state") != "running":
                if float(st.get("credits") or 0) <= CREDIT_FLOOR:
                    log(f"[homebase] not powering on: {st.get('credits')} credits (floor {CREDIT_FLOOR})")
                    _hb["failed"] = True
                    return False
                log("[homebase] tight clock window: powering Homebase on")
                remote.ensure_up()
                _hb["powered_by_us"] = True
            else:
                remote.ensure_up()
            if not _hb["provisioned"]:
                remote.rsync_to(ROOT / "setup" / "homebase_setup.sh", "~/homebase_setup.sh")
                remote.ssh("bash ~/homebase_setup.sh >/dev/null 2>&1", timeout=600, check=False)
                _hb["provisioned"] = True
            return True
        except Exception as e:  # noqa: BLE001 - never fail a run because Homebase is unavailable
            log(f"[homebase] unavailable, staying local: {e}")
            _hb["failed"] = True
            return False


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
        return run_hb_timed(solver_dir, cid, op=op, timeout=timeout)
    win = known_window(cid)
    tight = win is None or win <= TIGHT_WINDOW
    if AUTO_HOMEBASE and tight and _homebase_ready(log):
        res = run_hb_timed(solver_dir, cid, op=op, timeout=timeout)
        if str(res.get("result", "")).lower() != "exec_error":
            res["routed"] = f"homebase ({'window unknown' if win is None else f'window {win:g}s'})"
            return res
        log(f"[{cid}] Homebase run failed ({str(res.get('detail'))[:120]}); falling back to local")
    res = run_timed(solver_dir, cid, op=op, timeout=timeout)
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


def run_hb_timed(solver_dir, cid, op="start", timeout=60):
    """Run the clock-critical timed attempt ON Homebase (adjacent to the GM). Returns hb_timed's JSON dict.
    Syncs hctf+lib (base) and the solver so hb_timed can execute it next to the GM."""
    sync_homebase_base()
    rel = solver_dir.relative_to(ROOT)
    remote.ssh(f"mkdir -p ~/{HB_WORK}/{rel}")
    if solver_dir.exists():
        remote.rsync_to(str(solver_dir) + "/", f"~/{HB_WORK}/{rel}/")
    # Use the GM's INSIDE proxy from Homebase (network-path identity = same test account as the pairing token,
    # sub-ms latency) so tight windows (e.g. the 6s scripting Time Trial) fit; the public GM's ~2.7s/call
    # round-trips blow those windows even warm.
    r = remote.ssh(f"cd ~/{HB_WORK} && HUNTRESS_GAME_MASTER_URL={remote.INSIDE_GM} "
                   f"python3 hctf/hb_timed.py {shlex.quote(cid)} {shlex.quote(str(rel))} --op {op}",
                   timeout=timeout, check=False)
    try:
        res = json.loads(r.stdout.strip().splitlines()[-1])
    except (IndexError, ValueError):
        return {"result": "exec_error", "detail": (r.stdout + r.stderr)[-500:]}
    # Bring the attempt's bytes + result.json back, so the variant can become a local regression case.
    import re as _re
    slug = _re.sub(r"[^A-Za-z0-9]+", "_", cid)
    local = ROOT / ".run" / "tmp-timed" / slug
    try:
        if local.exists():
            for f in local.glob("*"):
                if f.is_file():
                    f.unlink()
        remote.rsync_from(f"~/{HB_WORK}/.run/tmp-timed/{slug}", str(local))
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
