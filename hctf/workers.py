"""LLM worker processes. One process per challenge stage; the orchestrator verifies the outcome.

local:    `claude -p` in WSL (your subscription). Repo hooks (.claude/settings.json) and skills apply.
homebase: `codex exec` on Homebase over SSH (Homebase token credits). The repo slice is rsynced to
          ~/hw, skills to ~/.codex/skills, and results are rsynced back when the worker exits.
"""
import json
import re
import os
import shlex
import subprocess
import sys
import threading
import time
import uuid
from pathlib import Path

from . import paths, remote
from .paths import BIN, TMP, TOOLS

ROOT = Path(__file__).resolve().parent.parent
PROMPTS = ROOT / "hctf" / "prompts"
HB_WORK = "hw"  # ~/hw on Homebase
# Engine of the optional Homebase worker pool (`--homebase N`): "claude" = Claude Code on Bedrock through the VM's
# instance role (Opus 4.7, billed to the daily Homebase credits); "codex" = the VM's codex CLI (GPT-6 luna on Bedrock).
HB_ENGINE = os.environ.get("HCTF_HB_ENGINE", "claude")


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
MAX_TURNS = {"single": 80, "generalize": 50, "fix": 30, "ratchet": 110,  # ratchet: D15 used 78, D14 hit the 80 cap (exit 1); D8/D10 cut at 40
             "ratchet_log": 40,  # one lane's technique log + coverage atlas forecast (split out of the ratchet after D14)
             "live": 60,         # live-answer worker on an open untimed attempt (orchestrate.LiveAnswer)
             "prebuild": 40}   # off-peak breadth worker (hctf/prebuild.py): one module + fixtures


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


# Fast mode (Opus at faster output; ~97% of a worker's wall time is token generation) -- an opt-in EXPERIMENT:
# HCTF_FAST_MODE=all or a comma list of lanes. OFF by user decision (2026-10-14; revisit near the CTF end): fast mode is
# never in plan limits -- it bills the org's USAGE CREDITS at a premium ($8/$40 per MTok on Opus 5.5) and refuses to turn
# on without credits. Rehearsal D13 A/B: singles 27-35% faster, same correctness. Never enable without the user's OK.
FAST_MODE_LANES = {x.strip() for x in os.environ.get("HCTF_FAST_MODE", "").split(",") if x.strip()}


def worker_settings(lane):
    st = {"autoMemoryEnabled": False, "bashEditDiffEnabled": False}   # see _worker_env: 10-25 s first-Bash snapshot
    if FAST_MODE_LANES and ("all" in FAST_MODE_LANES or (lane or "") in FAST_MODE_LANES):
        st["fastMode"] = True
    return st


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
    "web": "an expert-level CTF player who specializes in web application security and web-traffic analysis "
           "(app source review, HTTP/HAR/pcap captures, server logs, web shells, client-side JS, tokens/cookies)",
    "welcome": "an expert-level CTF player working the event's onboarding challenges",
}


def lane_persona(lane):
    """One-line expert persona for a lane, injected into worker prompts (point 5)."""
    return LANE_PERSONA.get(lane, "an expert-level CTF player")


LANE_SKILL = {"warmups": "warmups", "metadata-forensics": "metadata-forensics", "script-analysis": "script-analysis",
              "binary-reverse-engineering": "binary-re", "mobile-android": "mobile-android", "web": "web"}
# Lane helper modules the solver should IMPORT (Day 7: mobile re-typed lib.android.decode_payload, warmups re-typed
# lib.decode.decode_chunked -- ~12-25 s of generation each for code that already existed).
LANE_HELPERS = {"warmups": ["lib.decode", "lib.ciphers"], "mobile-android": ["lib.android"],
                "metadata-forensics": ["lib.stego"], "script-analysis": ["lib.codec", "lib.scripts", "lib.pyc"],
                "binary-reverse-engineering": ["lib.elf", "lib.binary"], "web": ["lib.codec"]}


def lane_skill(lane):
    """The lane SKILL.md body (frontmatter stripped), inlined into the prompt: every Day 7 worker spent its first turn
    on `Skill(<lane>)`."""
    p = ROOT / "skills" / LANE_SKILL.get(lane, "huntress-ctf") / "SKILL.md"
    try:
        text = p.read_text()
    except OSError:
        return "(lane skill unavailable)"
    if text.startswith("---"):
        text = text.split("---", 2)[-1]
    return text.strip()


def lane_helpers(lane):
    """Generated index of the lane's helper functions (name, args, first docstring line) -- read from the source with
    ast at render time, so it never drifts from lib/."""
    import ast
    out = []
    for mod in LANE_HELPERS.get(lane, []) + ["lib.common"]:
        p = ROOT / (mod.replace(".", "/") + ".py")
        try:
            tree = ast.parse(p.read_text())
        except (OSError, SyntaxError):
            continue
        fns = [n for n in tree.body if isinstance(n, ast.FunctionDef) and not n.name.startswith("_")]
        if not fns:
            continue
        out.append(f"- `{mod}`:")
        for n in fns:
            doc = (ast.get_docstring(n) or "").strip().split("\n")[0][:100]
            out.append(f"  - `{n.name}({', '.join(a.arg for a in n.args.args)})` {doc}".rstrip())
    return "\n".join(out) or "(no lane helpers)"


def lane_playbook(lane):
    """Per-lane field-label playbook (lib/playbook.py), injected as {playbook} so the worker starts from the
    GM's label grammar for this lane instead of guessing synonyms. Degrades to a short note if lib isn't importable."""
    try:
        from lib import playbook
        return playbook.for_lane(lane)
    except Exception:  # noqa: BLE001 - never fail a worker launch over the playbook
        return "(playbook unavailable; resolve non-flag labels with `hctf labels`.)"


STOPPED_RC = -15  # run_local's return code when `stop` ended the worker (its job was already done)
ASYNC_STOP = os.environ.get("HCTF_ASYNC_STOP", "1") != "0"   # kill the stopped worker in the background (no 2 s grace wait)
AUTH_RC = -77     # run_local's return code when Claude auth failed (relaunching can't help: re-login on the host)

# Worker sandbox (bubblewrap): the rehearsal copy rehearsal (2026-10-06) caught a script-analysis worker running
# `find / -name solve.py`, then COPYING the main account's Day 6 solver out of ~/huntress-2026 -- cross-copy
# contamination that no prompt rule can be trusted to prevent. Every local worker now runs with these paths replaced
# by empty, throwaway tmpfs dirs: every other ~/huntress-2026* tree (the other account), all Claude session
# transcripts (~/.claude/projects: orchestrator sessions hold solutions), /mnt/c (Windows side), plus
# HCTF_SANDBOX_HIDE (colon-separated). HCTF_WORKER_SANDBOX=0 disables it.
WORKER_SANDBOX = os.environ.get("HCTF_WORKER_SANDBOX", "1") != "0"


# Stages that never talk to the GM (off-peak breadth workers): no pairing token in their env and secrets/ masked.
NO_GM_STAGES = {x.strip() for x in os.environ.get("HCTF_NO_GM_STAGES", "prebuild").split(",") if x.strip()}


def sandbox_hidden_paths(stage=None):
    home = Path.home()
    hide = [p for p in home.glob("huntress-2026*") if p.is_dir() and p.resolve() != ROOT.resolve()]
    hide += [home / ".claude" / "projects", Path("/mnt/c")]
    hide += [Path(x) for x in os.environ.get("HCTF_SANDBOX_HIDE", "").split(":") if x]
    if stage in NO_GM_STAGES:
        sec = (ROOT / "secrets").resolve()   # a symlinked secrets/ (worktree -> main): mask the target, unless an
        if not any(sec == h.resolve() or h.resolve() in sec.parents for h in hide if h.exists()):   # already-masked dir holds it
            hide.append(sec)
    return [p for p in hide if p.exists()]


def sandboxed(cmd, stage=None, extra_binds=()):
    """Wrap a worker command in bwrap with sandbox_hidden_paths() masked; unchanged if bwrap is unavailable.
    extra_binds: [(src, dst)] read-write binds (the parallel prebuild gives each lane worker a private lib/ + tests/data/)."""
    import shutil as _sh
    if not WORKER_SANDBOX or not _sh.which("bwrap"):
        return cmd
    hidden = sandbox_hidden_paths(stage)
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
    binds += [a for s, d in extra_binds for a in ("--bind", str(s), str(d))]
    return ["bwrap", "--dev-bind", "/", "/", *masks, *binds, "--die-with-parent", "--", *cmd]


def _worker_env(env_extra):
    env = dict(os.environ)
    env.update({k: str(v) for k, v in env_extra.items()})
    if env.get("HCTF_STAGE") in NO_GM_STAGES:
        env.pop("HUNTRESS_GM_TOKEN", None)
    env["HCTF_WORKER_START"] = str(time.time())
    env["TMPDIR"] = str(TMP)  # keep every worker's scratch files inside the project
    env["PYTHONPATH"] = f"{ROOT}:{env.get('PYTHONPATH', '')}"  # so solvers/tools can `import lib.*`
    env["PATH"] = f"{BIN}:{TOOLS / 'node' / 'bin'}:{ROOT / '.venv' / 'bin'}:{Path.home() / '.local/bin'}:{env.get('PATH', '')}"
    # Cap a Bash call that hangs (Day 8 binary single: the Day 7 solver's brute force over a 67 MB Swift ELF sat the
    # full 120 s default). The worker can still pass an explicit timeout for known-long tools (Ghidra, jadx).
    # 25 s (rehearsal D8: a copied Day 7 solver hung twice to the old 60 s cap on a 67 MB ELF, ~120 s of the binary single).
    env.setdefault("BASH_DEFAULT_TIMEOUT_MS", os.environ.get("HCTF_WORKER_BASH_TIMEOUT_MS", "25000"))
    # Claude Code's Bash edit-diff (default ON under bypassPermissions) snapshots the 3 GB / 394k-file project around
    # any Bash call that may write: D11/D12 workers' first Bash 10-25 s (D12 metadata single 24.6 s for cat+jq; idle
    # A/B 10 s vs 0.3 s). Our hooks don't read the changed-file list.
    env.setdefault("CLAUDE_CODE_BASH_EDIT_DIFF", "0")
    return env


# The tools workers actually use (Day 7-8 logs: Bash 183, Skill 10, Read/Write/Edit 1 each; Task for the subagent
# policy). The default init listed 26 (Cron*, Workflow, WebSearch, ...). HCTF_WORKER_TOOLS="" keeps the default set.
WORKER_TOOLS = os.environ.get("HCTF_WORKER_TOOLS", "Bash,Read,Write,Edit,Skill,Task")
CLAUDE_BIN = os.environ.get("HCTF_CLAUDE_BIN", "claude")   # tests point this at a stub


# Linux caps ONE argv string at MAX_ARG_STRLEN (128 KiB): D18 prebuild metadata (17 targets) died at launch with
# "OSError: [Errno 7] Argument list too long: 'bwrap'". A prompt past this goes to `claude -p` on stdin instead.
PROMPT_ARGV_MAX = int(os.environ.get("HCTF_PROMPT_ARGV_MAX", "100000"))


def _worker_cmd(stage, lane, prompt=None, model=None, effort=None, stdin_prompt=False):
    """claude argv. prompt=None -> stream-json input (a warm worker gets its messages on stdin).
    stdin_prompt -> plain-text prompt on stdin (the caller feeds it; too long for argv).
    model/effort: per-launch overrides (the duel worker runs a deliberately different configuration)."""
    cmd = [CLAUDE_BIN, "-p"] + ([prompt] if prompt is not None and not stdin_prompt else []) + [
           "--dangerously-skip-permissions", "--max-turns", str(_max_turns(stage)),
           "--model", model or worker_model(lane), "--effort", effort or worker_effort(lane),
           "--output-format", "stream-json", "--verbose",
           # Isolation: no claude.ai MCP connectors (23 connected at every worker start, none used) and no Claude
           # auto-memory (Day 6 workers wrote unversioned GM facts to ~/.claude/projects/-home-testpwn-huntress-2026/
           # memory and re-read them every run). Durable knowledge goes through lib/ via the post-run ratchet only.
           "--strict-mcp-config", "--settings", json.dumps(worker_settings(lane))]
    if WORKER_TOOLS:
        cmd += ["--tools", WORKER_TOOLS]
    if prompt is None and not stdin_prompt:
        cmd += ["--input-format", "stream-json"]
    return cmd


WARM_TURN_WAIT = float(os.environ.get("HCTF_WARM_TURN_WAIT", "15"))   # s send_task waits for the READY turn to end


class WarmWorker:
    """A Single Solve worker launched at CHAIN START (beside GM start + download + triage), on stream-json input:
    message 1 = the static prompt + "reply READY, wait"; message 2 (send_task) = triage + go. Day 8: workers launched at
    T+7-10 s and first called a tool at T+13-16 s; claude startup and the ~25k-token static prompt now overlap the GM
    I/O. The Stop hook lets the warm-up turn end while the flag file exists (.claude/hooks/stop_gate.py)."""

    def __init__(self, chal_dir, stage, warm_text, env_extra):
        self.started = time.time()   # metrics: a warm worker's wall time counts from its launch
        self.log = _logfile(chal_dir, stage, "local")
        self.flag = Path(chal_dir) / f".warm-{os.getpid()}-{time.time_ns()}"
        self.flag.write_text("warm")
        env = _worker_env({**env_extra, "HCTF_WARM_FLAG": self.flag})
        lane = env_extra.get("HCTF_LANE") or env.get("HCTF_LANE")
        self.out = open(self.log, "w")
        self.out.write(json.dumps({"type": "hctf", "event": "warm_launch", "t": time.time()}) + "\n")
        self.out.flush()
        self.p = subprocess.Popen(sandboxed(_worker_cmd(stage, lane)), cwd=ROOT, stdin=subprocess.PIPE,
                                  stdout=self.out, stderr=subprocess.STDOUT, env=env, start_new_session=True, text=True)
        self._send(warm_text)

    def _send(self, text):
        self.p.stdin.write(json.dumps({"type": "user", "message": {"role": "user", "content": text}}) + "\n")
        self.p.stdin.flush()

    def alive(self):
        return self.p.poll() is None

    def warm_turn_done(self):
        """The warm-up turn ("READY") has ended: its stream-json `result` line is in the log."""
        try:
            with open(self.log, errors="replace") as f:
                for ln in f:
                    if '"result"' in ln:   # cheap pre-filter; key order in the CLI's JSON is not fixed
                        try:
                            if json.loads(ln).get("type") == "result":
                                return True
                        except ValueError:
                            pass
        except OSError:
            pass
        return False

    def send_task(self, text):
        """Deliver the real task and close stdin (the worker exits after its last turn, like `claude -p`).
        Waits (bounded) for the warm turn to END first: unlinking the flag while it still runs made the Stop hook block
        "READY" with "Not done", and the worker set off without its task text (D10 metadata/mobile/warmups: "the go
        message never arrived")."""
        deadline = time.time() + WARM_TURN_WAIT
        while self.alive() and not self.warm_turn_done() and time.time() < deadline:
            time.sleep(0.05)
        self.flag.unlink(missing_ok=True)
        self._send(text)
        self.p.stdin.close()

    def cancel(self):
        self.flag.unlink(missing_ok=True)
        if self.alive():
            _kill_group(self.p, grace=0)
        try:
            self.out.close()
        except OSError:
            pass


def run_local(chal_dir, stage, prompt, env_extra, timeout, stop=None, warm=None, warm_task=None):
    """Blocking. Returns (returncode, logfile). `stop` (threading.Event): when set, the worker is terminated at once
    and STOPPED_RC returned -- the orchestrator sets it once the Single Solve is CORRECT and the solver verifiably
    reproduces it, so post-correct hardening never sits on the critical path (Day 6: 60% of worker time).
    `warm` (WarmWorker, still alive): hand it `warm_task` instead of launching a new process.
    Every process gets a metrics row; an API-error exit is classified (worker_outcome): auth -> AUTH_RC at once,
    usage limit / overload -> back off and relaunch inside the same timeout (API_RELAUNCHES)."""
    deadline = time.time() + timeout
    t0 = warm.started if warm is not None and warm.alive() else time.time()
    rc, log = _run_local_once(chal_dir, stage, prompt, env_extra, timeout, stop, warm, warm_task)
    for n in range(API_RELAUNCHES + 1):
        out = record_metrics(log, stage, env_extra, rc, time.time() - t0)
        if rc in (STOPPED_RC, -9) or out["outcome"] not in ("auth", "limit", "transient"):
            return rc, log
        if out["outcome"] == "auth":
            print(f"!!! [{env_extra.get('HCTF_CHAL', '?')}] CLAUDE AUTH FAILED ({out['detail'][:160]}) -- run "
                  "`claude auth login` on the host; no more workers can start until then", file=sys.stderr, flush=True)
            return AUTH_RC, log
        wait = API_BACKOFF[min(n, len(API_BACKOFF) - 1)]
        if n == API_RELAUNCHES or deadline - time.time() - wait < API_MIN_LEFT:
            return rc, log
        print(f"[{env_extra.get('HCTF_CHAL', '?')}] {stage} worker ended on an API error ({out['outcome']}: "
              f"{out['detail'][:120]}); relaunch {n + 1}/{API_RELAUNCHES} in {wait:.0f}s", file=sys.stderr, flush=True)
        if (stop.wait(wait) if stop is not None else time.sleep(wait)):
            return STOPPED_RC, log
        t0 = time.time()
        rc, log = _run_local_once(chal_dir, stage, prompt + RELAUNCH_NOTE.format(detail=out["detail"][:200]),
                                  env_extra, deadline - time.time(), stop, None, None)
    return rc, log


_live = {}
_live_lock = threading.Lock()


def _live_add(log, env_extra):
    """Register a running harness worker (the coordinator, hctf/coordinator.py, reads live_workers())."""
    key = str(log)
    with _live_lock:
        _live[key] = {"log": Path(log), "start": time.time(), "cid": env_extra.get("HCTF_CHAL", ""),
                      "stage": env_extra.get("HCTF_STAGE", ""), "lane": env_extra.get("HCTF_LANE", ""),
                      "base": env_extra.get("HCTF_BASE", ""), "chal_dir": Path(str(env_extra.get("HCTF_CHAL_DIR") or ".")),
                      "solver_dir": Path(str(env_extra.get("HCTF_SOLVER_DIR") or ".")),
                      "duel": bool(env_extra.get("HCTF_DUEL"))}
    return key


def _live_drop(key):
    with _live_lock:
        _live.pop(key, None)


def live_workers():
    """Snapshot of the harness workers running right now (local `claude -p` processes)."""
    with _live_lock:
        return [dict(v) for v in _live.values()]


def _run_local_once(chal_dir, stage, prompt, env_extra, timeout, stop, warm, warm_task):
    if warm is not None and warm.alive():
        try:
            warm.send_task(warm_task)
            key = _live_add(warm.log, env_extra)
            try:
                return _wait_worker(warm.p, warm.log, timeout, stop, out=warm.out, strays=env_extra)
            finally:
                _live_drop(key)
        except OSError:
            warm.cancel()                 # broken pipe: the warm process died -> cold launch below
    elif warm is not None:
        warm.cancel()
    # HCTF_LOG_POOL: a second worker on the same challenge (duel) logs under its own name -- the main worker's log is
    # stamped to the second and both start in the same second.
    log = _logfile(chal_dir, stage, str(env_extra.get("HCTF_LOG_POOL") or "local"))
    env = _worker_env(env_extra)
    lane = env_extra.get("HCTF_LANE") or env.get("HCTF_LANE")
    via_stdin = prompt is not None and len(prompt.encode()) > PROMPT_ARGV_MAX
    cmd = _worker_cmd(stage, lane, prompt, model=env_extra.get("HCTF_X_MODEL"), effort=env_extra.get("HCTF_X_EFFORT"),
                      stdin_prompt=via_stdin)
    stdin = None                        # inherit, as before
    if via_stdin:
        pf = Path(str(log) + ".prompt")
        pf.write_text(prompt)
        stdin = open(pf)
    with open(log, "w") as out:
        try:
            xb = [tuple(x) for x in json.loads(env_extra.get("HCTF_SANDBOX_BINDS") or "[]")]
        except (ValueError, TypeError):
            xb = []
        if env_extra.get("HCTF_NICE"):      # background breadth workers yield the CPU to timing-sensitive gates
            cmd = ["nice", "-n", str(env_extra["HCTF_NICE"]), *cmd]
        try:
            p = subprocess.Popen(sandboxed(cmd, stage, xb), cwd=ROOT, stdin=stdin, stdout=out,
                                 stderr=subprocess.STDOUT, env=env, start_new_session=True)
        finally:
            if via_stdin:
                stdin.close()           # the child holds its own copy of the fd
        key = _live_add(log, env_extra)
        try:
            return _wait_worker(p, log, timeout, stop, strays=env_extra)
        finally:
            _live_drop(key)


def _wait_worker(p, log, timeout, stop, out=None, strays=None):
    deadline = time.time() + timeout
    try:
        while True:
            if stop is not None:
                # Block on the stop event itself: the Single worker ends the instant its solver is verified (polling
                # the process every 0.5 s left up to 0.5 s between "ready" and the kill on the critical path).
                stopped = stop.wait(0.5)
                rc = p.poll()
                if rc is not None:
                    return rc, log
                if stopped:
                    if ASYNC_STOP:
                        # the worker's job is done: SIGTERM it in the background instead of holding the timed modes
                        # for its up-to-2 s grace (it usually exits within 1 s)
                        threading.Thread(target=_stop_all, args=(p, 2.0, strays), daemon=True,
                                         name=f"stop-{p.pid}").start()
                    else:
                        _stop_all(p, 2.0, strays)
                    return STOPPED_RC, log
            else:
                try:
                    return p.wait(timeout=0.5), log
                except subprocess.TimeoutExpired:
                    pass
            if time.time() >= deadline:
                _stop_all(p, 0, strays)
                return -9, log
    finally:
        if out is not None:
            out.close()


def _kill_strays(env_extra):
    """SIGKILL processes left over from an ended worker: a Claude Code background task (`run_in_background` shell) runs
    in its own session, so the process-group kill misses it (alt armA D15: a `hctf submit --from-solver` bisect kept
    submitting for 38 s after its single worker was ended). Matched on the worker's HCTF_CHAL + HCTF_STAGE +
    HCTF_LOG_POOL (a duel's are distinct), this user's processes only."""
    if not env_extra or not env_extra.get("HCTF_CHAL"):
        return 0
    import signal
    want = {f"HCTF_CHAL={env_extra['HCTF_CHAL']}".encode(), f"HCTF_STAGE={env_extra.get('HCTF_STAGE', '')}".encode()}
    pool = env_extra.get("HCTF_LOG_POOL")
    me, uid, n = os.getpid(), os.getuid(), 0
    for d in Path("/proc").iterdir():
        if not d.name.isdigit() or int(d.name) == me:
            continue
        try:
            if d.stat().st_uid != uid:
                continue
            env = set((d / "environ").read_bytes().split(b"\0"))
        except OSError:
            continue
        if not want <= env:
            continue
        their = next((e[len(b"HCTF_LOG_POOL="):].decode() for e in env if e.startswith(b"HCTF_LOG_POOL=")), None)
        if (their or None) != (pool or None):
            continue
        try:
            os.kill(int(d.name), signal.SIGKILL)
            n += 1
        except OSError:
            pass
    return n


def _stop_all(p, grace, strays):
    _kill_group(p, grace)
    try:
        _kill_strays(strays)
    except Exception:  # noqa: BLE001 - best effort
        pass


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


# LLM-side failures (ilio-style). Claude Code already retries API errors itself (`api_retry`, 10x) and falls back to
# claude-opus-4-8 on a cyber refusal (`model_refusal_fallback`: Day 1/4/6 mobile singles, all recovered). What it can't
# fix ends the process with an `api_error` result: OAuth expiry (Day 1: six single workers died within 50 s with
# "OAuth session expired and could not be refreshed", nothing flagged it), a usage limit, overload past its retries.
# A relaunch is a FRESH session (the sandbox masks ~/.claude/projects, so --resume can't find the transcript) with the
# same prompt + RELAUNCH_NOTE; the worker's files on disk carry the progress.
API_RELAUNCHES = int(os.environ.get("HCTF_API_RELAUNCHES", "3"))
API_BACKOFF = [float(x) for x in os.environ.get("HCTF_API_BACKOFF", "20,60,180").split(",")]
API_MIN_LEFT = float(os.environ.get("HCTF_API_MIN_LEFT", "90"))   # don't relaunch with less stage time than this
RELAUNCH_NOTE = ("\n\n---\nHARNESS: an earlier session on this exact task ended on an API error ({detail}) before it "
                 "finished. Its files are still on disk (solver/, notes, work/): read them first and continue from "
                 "where it stopped instead of starting over.")
_AUTH_RE = re.compile(r"authenticat|oauth|\b401\b|\b403\b|log ?in again|invalid api key|credential", re.I)
_LIMIT_RE = re.compile(r"usage limit|hit your limit|limit reached|rate.?limit|\b429\b", re.I)
_TRANSIENT_RE = re.compile(r"overload|\b5\d\d\b|api error|connection|timed? ?out|network|econn|socket", re.I)
METRICS = ROOT / ".run" / "metrics.tsv"
METRIC_COLS = ("ts", "base", "cid", "stage", "lane", "rc", "outcome", "wall_s", "ttft_s", "turns", "cost_usd", "cost_src",
               "in_tok", "cache_read_tok", "cache_write_tok", "out_tok", "refusal_fallbacks", "models", "log")
_metrics_lock = threading.Lock()


# Effective $/Mtok used to ESTIMATE cost when a worker has no session-final `result` event -- the common case: the
# harness kills the Single worker at CORRECT (STOPPED_RC), and a warm worker's only result is its warm-up turn. Fitted
# 2026-10-09 (least squares) on the stream-derived features below against 123 complete logs' exact total_cost_usd:
# median error 2.4%, summed total within 1.4%. NOT list prices: the streamed output count is a first-token snapshot, so
# output is approximated (thinking deltas + emitted chars / 4) and the fitted `out` rate absorbs the undercount.
# Refit (model/pricing change): least squares of exact total_cost_usd on (input+cache_write, cache_read, out) over logs.
EST_RATES = {"write": 7.64, "read": 0.15, "out": 36.47}


def worker_outcome(log):
    """Parse a worker's stream-json log. outcome: ok | max_turns | auth | limit | transient | error | no_result.
    Tokens/calls are summed over every assistant message (usage per API call, de-duplicated by message id), so a
    killed worker is still counted. cost_src: `exact` = the last result event covers the whole session, else `est`."""
    res, refusals, msgs, after, thinking, chars = None, 0, {}, 0, 0, 0
    try:
        lines = Path(log).read_text(errors="replace").splitlines()
    except OSError:
        lines = []
    for line in lines:
        if '"model_refusal_fallback"' in line:
            refusals += 1
        if '"result"' not in line and '"assistant"' not in line and '"thinking_tokens"' not in line:
            continue
        try:
            ev = json.loads(line)
        except ValueError:
            continue
        if not isinstance(ev, dict):
            continue
        if ev.get("type") == "result":
            res, after = ev, 0
        elif ev.get("type") == "system" and ev.get("subtype") == "thinking_tokens":
            thinking += int(ev.get("estimated_tokens_delta") or 0)
        elif ev.get("type") == "assistant" and isinstance(ev.get("message"), dict):
            m = ev["message"]
            u, cur = m.get("usage") or {}, msgs.setdefault(m.get("id") or len(msgs), {"model": m.get("model", "")})
            if cur.get("seen") is None:
                after += 1
                cur["seen"] = True
            for k in ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens", "output_tokens"):
                cur[k] = max(cur.get(k, 0), int(u.get(k) or 0))
            for c in m.get("content") or []:   # one block per event; the streamed usage's output count is a first-token
                if isinstance(c, dict):         # snapshot, so output = thinking estimate + emitted chars / 4
                    chars += len(c.get("text") or "") + (len(json.dumps(c["input"])) if "input" in c else 0)
    tok = lambda k: sum(m.get(k, 0) for m in msgs.values())  # noqa: E731
    out_stream = max(tok("output_tokens"), thinking + chars // 4)
    models = sorted({m["model"] for m in msgs.values() if m.get("model")})
    est = (EST_RATES["write"] * (tok("input_tokens") + tok("cache_creation_input_tokens"))
           + EST_RATES["read"] * tok("cache_read_input_tokens") + EST_RATES["out"] * out_stream) / 1e6
    exact = res is not None and after == 0 and res.get("total_cost_usd") is not None
    out = {"detail": "", "refusal_fallbacks": refusals, "session": (res or {}).get("session_id", ""),
           "turns": (res or {}).get("num_turns", "") if exact else len(msgs),
           "cost_usd": round(float(res["total_cost_usd"]) if exact else est, 4), "cost_src": "exact" if exact else "est",
           "ttft_s": round(((res or {}).get("ttft_ms") or 0) / 1000, 1), "in_tok": tok("input_tokens"),
           "cache_read_tok": tok("cache_read_input_tokens"), "cache_write_tok": tok("cache_creation_input_tokens"),
           "out_tok": out_stream, "models": "+".join(models)}
    if exact:   # the result's modelUsage is authoritative when it covers the session
        mu = res.get("modelUsage") or {}
        for col, k in (("in_tok", "inputTokens"), ("cache_read_tok", "cacheReadInputTokens"),
                       ("cache_write_tok", "cacheCreationInputTokens"), ("out_tok", "outputTokens")):
            out[col] = max(out[col], sum(int(m.get(k) or 0) for m in mu.values()))
        out["models"] = "+".join(mu) or out["models"]
    if res is None:
        out["outcome"] = "no_result"
        return out
    if not res.get("is_error"):
        out["outcome"] = "ok"
        return out
    detail = " ".join(str(x) for x in (res.get("result"), res.get("errors"), res.get("api_error_status"),
                                       res.get("terminal_reason")) if x)
    out["detail"] = detail
    if res.get("subtype") == "error_max_turns" or res.get("terminal_reason") == "max_turns":
        out["outcome"] = "max_turns"
    elif _AUTH_RE.search(detail):
        out["outcome"] = "auth"
    elif _LIMIT_RE.search(detail):
        out["outcome"] = "limit"
    elif res.get("terminal_reason") == "api_error" or _TRANSIENT_RE.search(detail):
        out["outcome"] = "transient"
    else:
        out["outcome"] = "error"
    return out


def record_metrics(log, stage, env_extra, rc, wall_s):
    """Append one row per worker process to .run/metrics.tsv (`hctf cost` / `hctf dash` read it). Never raises.
    Only harness launches (HCTF_STAGE in env_extra) are recorded: unit tests' bare run_local calls stay out."""
    out = worker_outcome(log)
    if not env_extra.get("HCTF_STAGE"):
        return out
    if rc == STOPPED_RC:      # the harness ended it on purpose (CORRECT + verified solver): not a failure
        out = {**out, "outcome": "stopped"}
    elif rc == -9 and out["outcome"] == "no_result":
        out = {**out, "outcome": "timeout"}
    row = {"ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "base": env_extra.get("HCTF_BASE", ""),
           "cid": env_extra.get("HCTF_CHAL", ""), "stage": stage + ("-duel" if env_extra.get("HCTF_DUEL") else ""), "lane": env_extra.get("HCTF_LANE", ""), "rc": rc,
           "wall_s": round(wall_s, 1), "log": _rel_log(log), **out}
    try:
        with _metrics_lock:
            METRICS.parent.mkdir(parents=True, exist_ok=True)
            if METRICS.exists() and METRICS.read_text().split("\n", 1)[0] != "\t".join(METRIC_COLS):
                METRICS.rename(METRICS.with_name(f"metrics.tsv.old-{time.strftime('%Y%m%dT%H%M%S')}"))  # columns changed
            new = not METRICS.exists()
            with open(METRICS, "a") as f:
                if new:
                    f.write("\t".join(METRIC_COLS) + "\n")
                f.write("\t".join(str(row.get(c, "")).replace("\t", " ") for c in METRIC_COLS) + "\n")
    except OSError:
        pass
    return out


def _rel_log(log):
    try:
        return str(Path(log).resolve().relative_to(ROOT))
    except ValueError:
        return str(log)


def read_metrics():
    """metrics.tsv rows as dicts (numeric fields as float where possible)."""
    if not METRICS.exists():
        return []
    rows = []
    lines = METRICS.read_text().splitlines()
    cols = lines[0].split("\t") if lines else list(METRIC_COLS)
    for line in lines[1:]:
        r = dict(zip(cols, line.split("\t")))
        for k in ("wall_s", "ttft_s", "turns", "cost_usd", "in_tok", "cache_read_tok", "cache_write_tok", "out_tok"):
            try:
                r[k] = float(r.get(k) or 0)
            except ValueError:
                r[k] = 0.0
        rows.append(r)
    return rows


def metrics_report(day=None):
    """`hctf cost`: per chain x stage worker cost/turns/tokens, day totals, and every non-ok worker outcome."""
    rows = [r for r in read_metrics() if not day or f"challenges/day{int(day):02d}/" in r.get("log", "")]
    if not rows:
        return f"no worker metrics yet ({METRICS.relative_to(ROOT)})"
    agg = {}
    for r in rows:
        a = agg.setdefault((r["base"], r["stage"]), {"n": 0, "wall_s": 0.0, "turns": 0.0, "cost_usd": 0.0, "out_tok": 0.0})
        a["n"] += 1
        for k in ("wall_s", "turns", "cost_usd", "out_tok"):
            a[k] += r[k]
    hdr = ("chain", "stage", "procs", "wall_s", "turns", "cost_usd", "out_tok")
    table = [hdr] + [(b, s, a["n"], f"{a['wall_s']:.0f}", f"{a['turns']:.0f}", f"{a['cost_usd']:.2f}", f"{a['out_tok']:.0f}")
                     for (b, s), a in sorted(agg.items())]
    w = [max(len(str(t[i])) for t in table) for i in range(len(hdr))]
    lines = ["  ".join(str(x).ljust(w[i]) for i, x in enumerate(t)) for t in table]
    tot = lambda k: sum(r[k] for r in rows)  # noqa: E731
    cached = tot("cache_read_tok") / max(1.0, tot("cache_read_tok") + tot("in_tok") + tot("cache_write_tok"))
    n_est = sum(1 for r in rows if r.get("cost_src") == "est")
    lines.append(f"\nTOTAL {len(rows)} worker processes: ${tot('cost_usd'):.2f} ({n_est} estimated from tokens), {tot('turns'):.0f} turns, "
                 f"{tot('wall_s') / 60:.1f} worker-min, {tot('out_tok') / 1e3:.0f}k output tokens, {cached:.0%} of input "
                 f"from cache, {sum(int(r.get('refusal_fallbacks') or 0) for r in rows)} refusal fallbacks")
    bad = [r for r in rows if r.get("outcome") not in ("ok", "stopped", "")]
    if bad:
        lines.append("\nnon-ok worker exits:")
        lines += [f"  {r['ts']}  {r['base']} {r['stage']}: {r['outcome']} (rc {r['rc']})  {r['log']}" for r in bad]
    return "\n".join(lines)


def chain_cost():
    """{base: total worker cost_usd} for `hctf dash`."""
    out = {}
    for r in read_metrics():
        out[r["base"]] = out.get(r["base"], 0.0) + r["cost_usd"]
    return out


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
    with _sync_lock:
        if _hb.get("base_synced") and not force:
            return
        sig = _base_sig()
        if not force:
            r = remote.ssh(f"cat ~/{HB_WORK}/.base_sig 2>/dev/null", timeout=20, check=False)
            if r.stdout.strip() == sig:
                _hb["base_synced"] = True
                return
        _push_base(sig)
    # The run's prewarm may have started the timed daemon BEFORE this push: it holds the previous hb_timed / hb_daemon
    # in memory and never reloads (rehearsal D13 replay a13sota4: the new same-attempt resubmit never ran). Restart it so the
    # next attempt runs the code just pushed. Outside _sync_lock: HbDaemon startup may itself sync (lock order).
    if _daemon.get("d") is not None:
        restart_hb_daemon()


def _push_base(sig):
    """The actual push (caller holds _sync_lock): parallel rsyncs, then the fingerprint."""
    from concurrent.futures import ThreadPoolExecutor
    remote.ssh(f"mkdir -p ~/{HB_WORK}/challenges ~/.codex/skills ~/hctf")  # ~/hctf: absent on a fresh VM
    items = [(ROOT / d, f"~/{HB_WORK}/") for d in ("hctf", "lib", "bin", "skills", ".claude") if (ROOT / d).exists()]
    items += [(ROOT / f, f"~/{HB_WORK}/{f}") for f in ("CLAUDE.md", "AGENTS.md") if (ROOT / f).exists()]
    with ThreadPoolExecutor(max_workers=len(items)) as ex:
        list(ex.map(lambda it: remote.rsync_to(*it), items))
    remote.ssh(f"rsync -a --delete ~/{HB_WORK}/skills/ ~/.codex/skills/ && cp ~/{HB_WORK}/hctf/gm.py ~/hctf/gm.py"
               f" && echo {sig} > ~/{HB_WORK}/.base_sig")
    _hb["base_synced"] = True


# Small files that change DURING a run and that hb_timed reads on Homebase: labels learned mid-run (vocab.json) and
# hot-fixes to the timed runner. sync_homebase_base pushes the tree once per process, so on Day 8 both live hb_timed
# fixes and every mid-run vocab label had to be pushed by hand.
HOT_FILES = ("hctf/hb_timed.py", "hctf/hb_daemon.py", "hctf/hb_zygote.py", "lib/vocab.json", "lib/playbook.py")
DAEMON_CODE = ("hctf/hb_timed.py", "hctf/hb_daemon.py", "hctf/hb_zygote.py")
_hot_pushed = {}


def push_hot_files():
    """rsync any HOT_FILES whose size/mtime changed since the last push (local stat only when nothing changed)."""
    changed = []
    for f in HOT_FILES:
        p = ROOT / f
        try:
            st = p.stat()
        except OSError:
            continue
        sig = (st.st_size, st.st_mtime_ns)
        if f not in _hot_pushed:
            _hot_pushed[f] = sig      # the base sync just pushed this version
        elif _hot_pushed[f] != sig:
            changed.append((f, sig))
    for f, sig in changed:
        remote.rsync_to(ROOT / f, f"~/{HB_WORK}/{f}")
        _hot_pushed[f] = sig
    if any(f in DAEMON_CODE for f, _ in changed):
        restart_hb_daemon()       # the running daemon holds the old code; the next attempt starts a fresh one


TIMED_FWD = ("HCTF_PIPELINE_SETS", "HCTF_PIPELINE_MIN_MB", "HCTF_PIPELINE_DL", "HCTF_SOLVER_PARALLEL",
             "HCTF_UNTIMED_BUDGET")
UNTIMED_BUDGET = float(os.environ.get("HCTF_UNTIMED_BUDGET", "60"))   # solver seconds on an untimed (no-clock) attempt
UNTIMED_ON_HOMEBASE = os.environ.get("HCTF_UNTIMED_ON_HOMEBASE", "1") != "0"   # untimed/resume attempts next to the GM


def runner_progress(cid, since=0.0):
    """hb_timed's progress file for this mode (attempt id, banked per-set results), if written after `since`."""
    import re as _re
    p = ROOT / ".run" / "tmp-timed" / (_re.sub(r"[^A-Za-z0-9]+", "_", cid) + ".progress.json")
    try:
        if p.stat().st_mtime < since:
            return {}
        d = json.loads(p.read_text())
    except (OSError, ValueError):
        return {}
    d.pop("result", None)
    return d


LOCALIZE_UNTIMED_MAX = float(os.environ.get("HCTF_LOCALIZE_UNTIMED_MAX", "420"))
UNTIMED_DL_MBPS = float(os.environ.get("HCTF_UNTIMED_DL_MBPS", "0.5"))   # worst local public-GM download rate seen (D16)


def _contract_shape(cid):
    """(answer ids, delivery bytes, sets) of the mode's saved status-time contract; zeros when unknown."""
    from . import cli
    try:
        c = json.loads((cli.cdir(cid) / "contract.json").read_text())
    except (OSError, ValueError):
        return 0, 0, 0
    ids = c.get("answer_ids") or [q.get("id") for q in c.get("questions") or [] if isinstance(q, dict)]
    nb = sum(int(a.get("size") or 0) for a in c.get("artifacts") or [] if isinstance(a, dict))
    sets = {str(i).split(".", 1)[0] for i in ids if "." in str(i)}
    if not nb and paths.base_id(cid) != cid:
        # status-time contracts carry no sizes: one delivery per set, each about the size of the single's bytes
        # (D9/D16 binary: 31 MB single, 5 x 31 MB Mastery)
        try:
            from . import timed
            art = timed.latest_artifacts(paths.base_id(cid))
            one = sum(f.stat().st_size for f in art.rglob("*") if f.is_file()) if art else 0
            nb = one * max(1, len(sets))
        except (OSError, AttributeError):
            pass
    return len(ids), nb, len(sets)


def untimed_plan(cid):
    """(runner timeout s, in-attempt localize budget s) for a NO-CLOCK attempt, scaled to the contract.
    D16 script Mastery (5475 ids, 5 sets): the flat UNTIMED_BUDGET + 60 = 120 s cut a ~259 s localization six times."""
    n, nb, nsets = _contract_shape(cid)
    if "HCTF_LOCALIZE_UNTIMED_S" in os.environ:
        loc = float(os.environ["HCTF_LOCALIZE_UNTIMED_S"])
    else:
        loc = max(75.0, min(LOCALIZE_UNTIMED_MAX, 60 + n / 40))
    dl = min(240.0, nb / 1e6 / UNTIMED_DL_MBPS)
    sub = (nsets + 2) * max(4.0, n / 1000 * 2)          # full + per-set submits (+ the final resubmit)
    return round(20 + dl + UNTIMED_BUDGET + sub + loc + 30), round(loc)


def timed_env(cid):
    """Env for hb_timed (local or over ssh): pipeline knobs from this process + HCTF_EXPECT_BYTES = the delivery bytes
    the saved status-time contract lists (the live start body carries no sizes: the rehearsal's binary Mastery,
    5 x 31 MB, skipped the per-set pipeline on a 0-byte total)."""
    from . import cli
    env = {k: os.environ[k] for k in TIMED_FWD if k in os.environ}
    if "HCTF_RUN_FOR_TIME" not in os.environ:
        try:   # the GM said no ranked attempt is left: a run_for_time request can only be refused -> plain (regular pool)
            if json.loads((cli.cdir(cid) / "last_timed.json").read_text()).get("ranked_attempts_remaining") == 0:
                env["HCTF_RUN_FOR_TIME"] = "0"
        except (OSError, ValueError, AttributeError):
            pass
    try:
        c = json.loads((cli.cdir(cid) / "contract.json").read_text())
        n = sum(int(a.get("size") or 0) for a in c.get("artifacts") or [] if isinstance(a, dict))
        if n:
            env["HCTF_EXPECT_BYTES"] = str(n)
    except (OSError, ValueError, TypeError):
        pass
    ov = live_overlay(cid)
    if ov:
        env["HCTF_LIVE_OVERLAY"] = json.dumps(ov, separators=(",", ":"))
    env.setdefault("HCTF_LOCALIZE_UNTIMED_S", str(untimed_plan(cid)[1]))   # only used on a no-clock attempt
    try:   # every challenge's in-window label fixes (wrong -> right) rank the corrector's alternatives
        from . import labels
        h = labels.all_label_hints()
        js = json.dumps(h, separators=(",", ":")) if h else ""
        if js and len(js) <= 20000:        # env var size: never a truncated (invalid) JSON
            env["HCTF_LABEL_HINTS"] = js
    except Exception:  # noqa: BLE001 - ranking aid only
        pass
    return env


def live_overlay(cid, attempt=None):
    """{"attempt", "answers"}: values the GM ACCEPTED on the mode's current attempt through submits outside hb_timed
    (the live-answer worker's `hctf submit`), from <mode dir>/submissions.jsonl. hb_timed overlays them on a resumed
    attempt next to its own bank, so a reconnect completes it. None when there are none."""
    from . import cli
    try:
        attempt = attempt or json.loads((cli.cdir(cid) / "last_timed.json").read_text()).get("attempt_id")
    except (OSError, ValueError, AttributeError):
        return None
    if not attempt:
        return None
    got = {}
    try:
        for ln in open(cli.cdir(cid) / "submissions.jsonl"):
            try:
                r = json.loads(ln)
            except ValueError:
                continue
            # only plain submits (the live worker's few fields): harness probe batches can be ~800 fields and an env
            # var that size fails execve (E2BIG) on the local / ssh routes
            if (r.get("attempt") == attempt and str(r.get("kind", "")).lower() in ("accepted", "correct")
                    and not r.get("probe") and not r.get("harness") and len(r.get("answers") or {}) <= 50):
                got.update({k: v for k, v in (r.get("answers") or {}).items() if v not in (None, "")})
    except OSError:
        return None
    if len(got) > LIVE_OVERLAY_MAX:
        got = dict(list(got.items())[-LIVE_OVERLAY_MAX:])
    return {"attempt": attempt, "answers": got} if got else None


LIVE_OVERLAY_MAX = int(os.environ.get("HCTF_LIVE_OVERLAY_MAX", "200"))


def run_timed(solver_dir, cid, op="start", timeout=60, budget=None):
    """Run the clock-critical timed attempt LOCALLY against the public GM (pairing token).
    No VM, no SSH — the whole start->download->solve->submit path runs here. Returns hb_timed's JSON dict.
    budget: solver seconds on a no-clock attempt (HCTF_UNTIMED_BUDGET for this run only)."""
    rel = solver_dir.relative_to(ROOT)
    env = dict(os.environ, PYTHONPATH=f"{ROOT}:{os.environ.get('PYTHONPATH', '')}", **timed_env(cid))
    if budget:
        env["HCTF_UNTIMED_BUDGET"] = f"{budget:g}"
    if os.environ.get("HCTF_TIMED_GM_URL"):
        # Clock-critical calls straight to this GM (e.g. the real one while a replay proxy fronts everything else: the
        # proxy opens a fresh TLS connection per call, ~0.5-1 s each inside a 6-7 s window).
        env["HUNTRESS_GAME_MASTER_URL"] = os.environ["HCTF_TIMED_GM_URL"]
    from . import procgov
    # hb_timed stops localizing ~15 s before this deadline and prints its result (never killed mid-localization)
    env["HCTF_RUNNER_DEADLINE"] = f"{time.time() + timeout:.3f}"
    t_call = time.time()
    try:
        r = procgov.run([sys.executable, str(ROOT / "hctf" / "hb_timed.py"), cid, str(rel), "--op", op],
                        cwd=ROOT, timeout=timeout, env=env, background=False)
    except subprocess.TimeoutExpired:
        # what the runner persisted before the kill: the attempt id (-> the next try RESUMES it, never op=start) and
        # what the GM accepted (-> _prev_banked)
        return {"result": "exec_error", "detail": "local hb_timed timed out", **runner_progress(cid, since=t_call)}
    except OSError as e:   # e.g. E2BIG: never crash the chain on a runner that could not start
        return {"result": "exec_error", "detail": f"local hb_timed did not start: {e}"[:300]}
    try:
        return json.loads(r.stdout.strip().splitlines()[-1])
    except (IndexError, ValueError):
        return {"result": "exec_error", "detail": (r.stdout + r.stderr)[-500:]}


# Clocks this short go to Homebase. Default: EVERY clock (inf) -- Homebase bills VM uptime, not calls, and local over the
# public GM spent 9.53 of an 11s window on Day 7's 469-field script TT (start 3.9s + download 3.1s + submit 6.0s).
TIGHT_WINDOW = float(os.environ.get("HCTF_TIGHT_WINDOW", "inf"))
AUTO_HOMEBASE = os.environ.get("HCTF_AUTO_HOMEBASE", "1") != "0"   # 0: never power Homebase on by itself
CREDIT_FLOOR = float(os.environ.get("HCTF_CREDIT_HARD", "1.5"))      # never power on below this many credits
_hb_lock = threading.Lock()
HB_HEALTH_S = float(os.environ.get("HCTF_HB_HEALTH_S", "5"))   # background Homebase reachability probe period
HB_FRESH_S = 3 * HB_HEALTH_S                                     # a health verdict older than this is "unknown"
# Slow-VM routing: the VM's CPU is benchmarked against this host once per run (_bench_vm). When it is >= SLOW_VM_RATIO
# times slower, attempts with NO clock or a roomy one (> SLOW_VM_WINDOW s) run locally; tight windows stay next to the GM.
# rehearsal D15 (t3.small, 2 GB after the 10-12 reset): binary Mastery solve 29.7 s on Homebase vs 0.8 s locally, same bytes.
SLOW_VM_RATIO = float(os.environ.get("HCTF_SLOW_VM_RATIO", "4"))   # unmeasured on main: logged at every prewarm
SLOW_VM_WINDOW = float(os.environ.get("HCTF_SLOW_VM_WINDOW", "10"))
# 4 processes at once (Mastery solvers fan sets out over a process pool): catches a 2-vCPU / throttled VM, not just a
# slower core
BENCH_PY = ("import time,hashlib\nfrom concurrent.futures import ProcessPoolExecutor\n"
            "def w(_):\n b=bytes(1<<20);[hashlib.sha256(b).digest() for _ in range(100)];s=0\n"
            " for i in range(2800000): s+=i*i\n return s\n"
            "t=time.perf_counter()\nwith ProcessPoolExecutor(4) as ex: list(ex.map(w,range(4)))\n"
            "print(round(time.perf_counter()-t,4))")
_hb = {"powered_by_us": False, "provisioned": False, "ok": False, "checked": 0.0, "thread": None}
HB_DEPS = ["elftools", "pefile", "capstone", "Crypto", "pyzipper", "androguard", "droidasc", "refinery",
           "bs4", "jwt", "dpkt"]   # last line: web lane (homebase_setup.sh installs them)


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
        warm_homebase_imports()
        hb_daemon(log)            # up before the first clock (its own TLS handshakes + interpreter start)
        _bench_vm(log)
    except Exception as e:  # noqa: BLE001 - provisioning is best-effort; deps usually already present
        log(f"[homebase] provisioning note (continuing): {e}")
        _hb["provisioned"] = True


def _bench_vm(log=print, again=True):
    """CPU benchmark: the same pure-Python + sha256 loop here and on the VM (timed inside the interpreter, so ssh latency
    is not counted) -> _hb["cpu_ratio"] (VM seconds / local seconds) + _hb["mem_mb"]. Best of two runs on the VM; a VM
    booted < 5 min ago is benchmarked again at 5 min of uptime (D16: x14.3 at boot + 2 min, x9-10 steady). Best effort."""
    try:
        loc = subprocess.run([sys.executable, "-c", BENCH_PY], capture_output=True, text=True, timeout=60)
        t_loc = float(loc.stdout.strip().splitlines()[-1])
        r = remote.ssh(f"python3 -c {shlex.quote(BENCH_PY)}; python3 -c {shlex.quote(BENCH_PY)}; "
                       "awk '/^MemTotal/{print int($2/1024)}' /proc/meminfo; awk '{print int($1)}' /proc/uptime; nproc",
                       timeout=150, check=False)
        lines = r.stdout.strip().splitlines()
        t_vm = min(float(lines[0]), float(lines[1]))
        mem = int(lines[2]) if len(lines) > 2 else None
        up = int(lines[3]) if len(lines) > 3 else None
        cores = int(lines[4]) if len(lines) > 4 and lines[4].strip().isdigit() else None
        _hb.update(cpu_ratio=round(t_vm / max(t_loc, 1e-3), 2), mem_mb=mem, **({"vm_cores": cores} if cores else {}))
        slow = _hb["cpu_ratio"] >= SLOW_VM_RATIO
        log(f"[homebase] CPU benchmark: VM {t_vm:.2f}s vs local {t_loc:.2f}s (x{_hb['cpu_ratio']:g}), {mem} MB RAM"
            + (f", VM up {up // 60} min" if up is not None else "")
            + (" -> SLOW VM (routing weighs CPU against bytes + GM round trips)" if slow else ""))
        if again and up is not None and up < 300:
            def later():
                time.sleep(300 - up + 5)
                _bench_vm(log, again=False)
            threading.Thread(target=later, daemon=True, name="hb-rebench").start()
    except Exception as e:  # noqa: BLE001 - routing then stays Homebase-first
        log(f"[homebase] CPU benchmark skipped: {str(e)[:120]}")


# Cost model for an attempt with no / a roomy clock: bytes + GM round trips + solver time, local vs Homebase.
# D16: the CPU-only slow-VM rule sent binary's 31 MB Time Trial local -> 52 s of download at ~0.6 MB/s; the VM pulls
# ~140 MB/s and sits next to the GM. Rates are conservative defaults, overridable.
# Per download STREAM (hb_timed fetches every set's delivery at once): D16 local, a 31 MB single in ~10 s (~3 MB/s) and
# the 5 x 32 MB Mastery in 14.6 s; the TT's 52 s was the host at load 27.
LOCAL_DL_BPS = float(os.environ.get("HCTF_LOCAL_DL_MBPS", "3")) * 1e6
HB_DL_BPS = float(os.environ.get("HCTF_HB_DL_MBPS", "40")) * 1e6
LOCAL_RTT = float(os.environ.get("HCTF_LOCAL_GM_RTT", "1.8"))      # public GM submit, measured 2026-10-16
HB_RTT = float(os.environ.get("HCTF_HB_GM_RTT", "0.4"))            # next to the GM (daemon), incl. the ssh hop


ROUTE_FAIL_WEIGHT = float(os.environ.get("HCTF_ROUTE_FAIL_WEIGHT", "0.3"))   # expected share of a per-set breakdown
VM_CORES = int(os.environ.get("HCTF_HB_CORES", "2"))     # t3.small; _bench_vm measures it (nproc) -> _hb["vm_cores"]


def _phase_solve_local(c):
    """The solve phase of mode c's last attempt in LOCAL seconds (a Homebase-run phase divided by the VM ratio)."""
    from . import cli
    try:
        lt = json.loads((cli.cdir(c) / "last_timed.json").read_text())
        s = float((lt.get("phases") or {}).get("solve") or 0)
    except (OSError, ValueError, AttributeError, TypeError):
        return None
    if not s:
        return None
    return s / float(_hb.get("cpu_ratio") or 1.0) if str(lt.get("routed", "")).startswith("homebase") else s


def _solve_estimate(cid):
    """(local seconds, per_set) for this mode's solver: its own last attempt's solve phase (the whole mode), else a
    ONE-SET measurement -- the Time Trial's solve phase, or the single's stamp scaled to one set's size -- that
    route_costs multiplies by the solve waves. (2.0, True) when nothing is known."""
    from . import cli
    own = _phase_solve_local(cid)
    if own:
        return own, False
    est = []
    tt = f"{paths.base_id(cid)}/time_trial"
    if tt != cid:
        s = _phase_solve_local(tt)
        if s:
            est.append(s)
    try:
        st = json.loads((cli.cdir(paths.base_id(cid)) / ".solver_stamp.json").read_text())
        n1 = max(1, len(st.get("answers") or {}))
        n, _, nsets = _contract_shape(cid)
        est.append(float(st.get("seconds") or 2.0) * max(1.0, n / max(1, nsets) / n1))   # one set's share
    except (OSError, ValueError, AttributeError):
        pass
    return (min(est) if est else 2.0), True   # the fastest measurement: a contended one (D16 load 27) overstates it


def route_costs(cid):
    """(local s, homebase s) estimates for one attempt of this mode.
    Calls: the runner's fast path is ONE submit of every answer (+ start); a per-set breakdown follows only an incorrect
    full submit -- weighted by ROUTE_FAIL_WEIGHT and capped. D17 warmups Mastery (83 one-field sets): the old
    "3 + nsets" put local at 155 s against a measured 1.24 s submit phase. Solve: a per-set estimate runs in WAVES of
    the host's CPU count (local cores vs the VM's, usually 2) times the VM's per-core ratio."""
    n, nb, nsets = _contract_shape(cid)
    calls = 3 + n / 1000 + ROUTE_FAIL_WEIGHT * min(max(nsets, 1), 6)
    solve, per_set = _solve_estimate(cid)
    ratio = float(_hb.get("cpu_ratio") or 1.0)
    waves_loc = waves_hb = 1
    if per_set and nsets > 1:
        waves_loc = -(-nsets // max(1, os.cpu_count() or 1))
        waves_hb = -(-nsets // max(1, int(_hb.get("vm_cores") or VM_CORES)))
    per_stream = nb / max(1, nsets)       # the deliveries download in parallel, one stream per set
    return (per_stream / LOCAL_DL_BPS + calls * LOCAL_RTT + solve * waves_loc,
            per_stream / HB_DL_BPS + calls * HB_RTT + solve * ratio * waves_hb)


def homebase_cheaper(cid, log=None):
    loc, hb = route_costs(cid)
    if log:
        log(f"[{cid}] route estimate: local {loc:.1f}s vs Homebase {hb:.1f}s (VM x{_hb.get('cpu_ratio') or '?'})")
    return hb < loc


def slow_vm():
    return float(_hb.get("cpu_ratio") or 0) >= SLOW_VM_RATIO


VM_METER_S = float(os.environ.get("HCTF_HB_METER_S", "60"))   # how often a reachable VM's uptime is booked


def meter_vm():
    """Book the VM's current uptime span in the credit ledger (hbbudget): its boot time + now. One cheap ssh."""
    from . import hbbudget
    try:
        r = remote.ssh("awk '/^btime/{print $2}' /proc/stat", timeout=20, check=False)
        hbbudget.record_vm(int(r.stdout.strip()))
        return True
    except Exception:  # noqa: BLE001 - metering is best-effort
        return False


def _health_loop(log):
    was = None
    metered = 0.0
    while True:
        ok = remote.probe()
        _hb.update(ok=ok, checked=time.time())
        if ok and time.time() - metered >= VM_METER_S:
            metered = time.time()
            threading.Thread(target=meter_vm, daemon=True).start()
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


UNTIMED_LOCAL_BUDGET = float(os.environ.get("HCTF_UNTIMED_LOCAL_BUDGET", "150"))   # solver s, forced local no-clock rerun


def run_timed_auto(solver_dir, cid, op="start", timeout=60, log=print, on_event=None, force_local=False):
    """Dispatch a timed attempt. HOMEBASE-FIRST (user policy): every window <= HCTF_TIGHT_WINDOW seconds (default: all),
    or one not yet known, runs next to the GM on Homebase (prewarmed at run start). Local over the pairing token is the
    fallback (Homebase unavailable / remote exec failure); set HCTF_TIGHT_WINDOW=8 to bring back local-first for
    known-roomy windows (Day 7: that sent an 11s script TT local, 9.53s in-window vs ~2s on Homebase). The old "local first, Homebase only
    after a local expiry" rule burned one attempt per tight mode, and the rehearsal copy run showed local fits a 7s
    462-field Mastery only by ~0.9s (GM origin ~1.3-1.5s/call from here). HCTF_GM_TRANSPORT=ssh forces Homebase.
    force_local: a no-clock re-run of a live attempt HERE with UNTIMED_LOCAL_BUDGET solver seconds (the orchestrator's
    answer to a CPU-bound solve that ran out of its budget on a slow VM)."""
    if force_local:
        res = run_timed(solver_dir, cid, op=op, timeout=max(timeout, untimed_plan(cid)[0] + UNTIMED_LOCAL_BUDGET),
                        budget=UNTIMED_LOCAL_BUDGET)
        res.setdefault("routed", "local (forced no-clock rerun)")
        return res
    from . import webtarget
    if webtarget.is_live_cid(cid):
        # web: no bytes to move, no clock by default, and the runner may first wait out a `preparing` target (up to
        # HCTF_WEB_PREPARE_WAIT s) + revive a `cleaned` one via the arena (public origin only) -> always HERE
        res = run_timed(solver_dir, cid, op=op, timeout=max(timeout, untimed_plan(cid)[0]) + webtarget.WAIT + 30)
        res.setdefault("routed", "local (web live target)")
        return res
    if op in ("untimed", "resume"):
        # resume = reconnecting to a live attempt that holds banked ids (mostly an untimed one). No clock, but the
        # attempt's GM calls still dominate: rehearsal D13 replay, a script retry took 115 s locally (~25 localize submits at
        # ~3.3 s over the public GM) vs ~0.5 s/submit next to the GM. Homebase when it is up (the failure path pulls
        # the variant bytes back for the generalize worker either way); local is the fallback.
        ut = max(timeout, untimed_plan(cid)[0])     # scaled to the contract (D16: a flat 120 s, killed 6x)
        if (UNTIMED_ON_HOMEBASE and AUTO_HOMEBASE and remote.gm_transport() == "local"
                and (not slow_vm() or homebase_cheaper(cid, log)) and _homebase_ready(log)):
            res = run_hb_timed(solver_dir, cid, op=op, timeout=ut)
            if str(res.get("result", "")).lower() != "exec_error" or res.get("gm_rate_limited"):
                res.setdefault("routed", "homebase (untimed)")
                return res
            log(f"[{cid}] Homebase untimed run failed ({str(res.get('detail'))[:120]}); falling back to local")
        res = run_timed(solver_dir, cid, op=op, timeout=ut)
        res.setdefault("routed", "local (untimed)")
        return res
    if remote.gm_transport() != "local":
        res = run_hb_timed(solver_dir, cid, op=op, timeout=timeout, on_event=on_event)
        if str(res.get("result", "")).lower() == "exec_error" and remote._have_token():
            log(f"[{cid}] Homebase run failed ({str(res.get('detail'))[:120]}); falling back to local")
            res = run_timed(solver_dir, cid, op=op, timeout=timeout)
            res["routed"] = "local (forced-ssh homebase failed)"
        else:
            res.setdefault("routed", "homebase (forced transport)")
        return res
    win = known_window(cid)
    tight = win is None or win <= TIGHT_WINDOW
    if tight and slow_vm() and (win is None or win > SLOW_VM_WINDOW) and not homebase_cheaper(cid, log):
        tight = False
        log(f"[{cid}] Homebase VM is x{_hb.get('cpu_ratio')} slower than this host and the window is "
            f"{'unknown/untimed' if win is None else f'{win:g}s'}: running locally")
    if win is None:
        # no known clock (HCTF_RUN_FOR_TIME=auto -> the untimed regular pool): the attempt may localize for up to
        # HCTF_LOCALIZE_UNTIMED_S; a 60 s call timeout cut it off and re-ran it over ssh + locally (a13sota6: 12 min)
        timeout = max(timeout, untimed_plan(cid)[0])
    if AUTO_HOMEBASE and tight and _homebase_ready(log):
        res = run_hb_timed(solver_dir, cid, op=op, timeout=timeout, on_event=on_event)
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
        if str(res.get("result", "")).lower() != "exec_error" or res.get("gm_rate_limited") or (
                "solve.py" in detail and ("timed out" in detail or "TimeoutExpired" in detail)):
            # (A SOLVER timeout on Homebase is returned as-is: running the same solver locally only burns another
            # attempt -- replay run 2 lost ~19s that way. The caller routes it to a speed generalize. A GM 429 is
            # returned as-is too: a local run hits the same rate limiter -- the caller backs off instead.)
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
_prepush = {}  # solver dir -> threading.Event, set once prepush_solver() finished (pushed + warmed, or gave up)
_warmed = {}  # solver dir -> signature whose Homebase zygote prepush_solver() warmed
PREPUSH_WAIT = float(os.environ.get("HCTF_PREPUSH_WAIT", "6"))      # max s a timed kickoff waits for a pre-push
PREPUSH_SIGNAL_EARLY = os.environ.get("HCTF_PREPUSH_SIGNAL_EARLY", "1") != "0"   # release the kickoff after the push


def _solver_sig(solver_dir):
    """(path, mtime_ns, size) of the files a timed run needs (cases/ and __pycache__ excluded)."""
    solver_dir = Path(solver_dir)
    return tuple(sorted((str(f.relative_to(solver_dir)), f.stat().st_mtime_ns, f.stat().st_size)
                        for f in solver_dir.rglob("*") if f.is_file()
                        and "cases" not in f.relative_to(solver_dir).parts and "__pycache__" not in f.parts))


def push_solver(src, rel):
    """Solver dir (minus cases/) -> Homebase ~/hw/<rel>: one tar-over-ssh round trip (~0.75 s) for a small tree, rsync
    otherwise or if that fails."""
    size = sum(f.stat().st_size for f in Path(src).rglob("*")
               if f.is_file() and "cases" not in f.relative_to(src).parts and "__pycache__" not in f.parts)
    if size <= TAR_PUSH_MAX:
        try:
            remote.tar_push(src, f"{HB_WORK}/{rel}")
            return "tar"
        except (RuntimeError, OSError, subprocess.SubprocessError):
            pass
    remote.rsync_to(str(src) + "/", f"~/{HB_WORK}/{rel}/", exclude=["cases/", "__pycache__/"], mkdir=f"~/{HB_WORK}/{rel}")
    return "rsync"


TAR_PUSH_MAX = int(os.environ.get("HCTF_TAR_PUSH_MB", "5")) * 1024 * 1024


def prepush_solver(src, dst, log=print, warm=True):
    """Background, the moment the Single Solve is CORRECT + verified: push the verified snapshot `src` to Homebase at
    `dst`'s path while the worker is ended and the single recorded, so the first timed kickoff finds it in place (D9:
    single CORRECT -> TT start 3.9-6.6 s on every lane; the kickoff's no-op rsync alone was 1.84 s over the VPN).
    copy2 keeps mtime/size, so once `src` is restored over `dst` the signature matches and run_hb_timed skips the push.
    (A per-solver warm-up run here was measured at ~4.9 s -- longer than the cold penalty it saves; the heavy imports'
    page cache is warmed once at provisioning instead: warm_homebase_imports.)"""
    import threading
    key, ev = str(dst), threading.Event()
    prev, _prepush[key] = _prepush.get(key), ev

    def go():
        t0 = time.time()
        try:
            if prev is not None:
                prev.wait(PREPUSH_WAIT)   # an earlier (stamp-time) pre-push of this dir is in flight: never rsync beside it
            rel = Path(dst).relative_to(ROOT)
            sig = _solver_sig(src)
            if _pushed.get(key) != sig:   # an earlier (speculative / stamp-time) pre-push may have shipped this code
                sync_homebase_base()
                push_hot_files()
                how = push_solver(src, rel)
                _pushed[key] = sig
                log(f"[homebase] pre-pushed {rel} ({how}) in {time.time() - t0:.1f}s{'' if warm else ' (speculative)'}")
            if PREPUSH_SIGNAL_EARLY:
                # the kickoff only waits so it never rsyncs beside this push: release it now, not after the warm (D14
                # mobile: push done 21:00:12, warm call returned 21:00:14 for an 89 ms load -> 2 s more prepush_wait)
                ev.set()
            # warm zygote for this solver before the first clock -- verified pushes only: a speculative push must not
            # load the 2-vCPU VM while other lanes may be inside a timed window
            d = hb_daemon(log) if warm and _warmed.get(key) != sig else None
            if d is not None:
                w = d.call("warm", timeout=30, solver=str(rel))
                _warmed[key] = sig
                log(f"[homebase] solver zygote warm ({w.get('warm_ms')} ms load)")
        except Exception as e:  # noqa: BLE001 - an optimization: the kickoff pushes as before
            log(f"[homebase] pre-push note: {str(e)[:200]}")
        finally:
            ev.set()
    threading.Thread(target=go, name=f"prepush-{Path(dst).parent.name}", daemon=True).start()
    return ev


def warm_homebase_imports():
    """Fire-and-forget on the VM: import every lib/ module + the heavy solver deps and start node/7z once, so the first
    Time Trial's solver doesn't pay cold EBS reads (D9: TT solves 1.2-1.8 s slower than the next Mastery's on the same
    VM -- mobile 1.99 s vs 0.17 s). Returns at once; runs well before any clock."""
    mods = " ".join(["lib." + p.stem for p in sorted((ROOT / "lib").glob("*.py")) if p.stem != "__init__"]
                    + ["lib.meta", "lib.meta.spell", "lib.meta.pe", "lib.meta.cfb", "lib.meta.msi"] + HB_DEPS
                    + ["androguard.core.apk", "androguard.core.dex"])
    py = ("import importlib,sys\nfor m in sys.argv[1:]:\n    try: importlib.import_module(m)\n    except Exception: pass")
    job = (f"cd ~/{HB_WORK} && PYTHONPATH=~/{HB_WORK} timeout 120 python3 -c {shlex.quote(py)} {mods}; "
           "node -e 0; 7z i")
    remote.ssh(f"setsid nohup sh -c {shlex.quote(job)} </dev/null >/dev/null 2>&1 &", timeout=20, check=False)


# Warm timed-attempt daemon on Homebase (hctf/hb_daemon.py): one persistent ssh stdio channel per run; attempts run in
# it with warm solver zygotes and kept-alive GM connections. HCTF_HB_DAEMON=0 -> ssh exec of hb_timed.py per attempt.
HB_DAEMON = os.environ.get("HCTF_HB_DAEMON", "1") != "0"
# Timed GM traffic from Homebase to the PUBLIC GM with this copy's bearer (170 ms/call vs 232 ms via the inside proxy;
# identity = the token, not the VM). 0 -> inside proxy, no token sent.
HB_PUBLIC_GM = os.environ.get("HCTF_HB_PUBLIC_GM", "1") != "0"
DAEMON_RETRY_S = 60


class DaemonError(RuntimeError):
    pass


class HbDaemon:
    """Client for hb_daemon.py over `ssh ... python3 hctf/hb_daemon.py --stdio` (requests answered concurrently)."""

    def __init__(self, log=print, argv=None, gm_url=None, token=None):
        """argv/gm_url/token: tests run the daemon locally against a stand-in GM."""
        self.log, self.lock, self.pending, self.p = log, threading.Lock(), {}, None
        self.events = {}   # request id -> callback(msg) for mid-attempt events (HCTF_EARLY_GENERALIZE)
        # mkdir: on a freshly reset VM ~/hw/.run doesn't exist yet when the daemon starts, the stderr redirect fails and
        # the daemon is "unavailable" for the run's first minutes (rehearsal fair D12: up 2 s before the base sync made .run)
        cmd = f"mkdir -p ~/{HB_WORK}/.run && cd ~/{HB_WORK} && exec python3 hctf/hb_daemon.py --stdio 2>>.run/hb_daemon.err"
        self.p = subprocess.Popen(argv or ["ssh", *remote.SSH_OPTS, f"{remote.HB_USER}@{remote.HB_HOST}", cmd],
                                  stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
        threading.Thread(target=self._read, name="hb-daemon-read", daemon=True).start()
        if gm_url:
            gm, tok = gm_url, token
        else:
            gm, tok = (remote.PUBLIC_GM, _gm_token()) if HB_PUBLIC_GM else (remote.INSIDE_GM, None)
        ev, res = threading.Event(), {}
        self.pending["hello"] = (ev, res)
        self._write({"hello": 1, "gm": gm, "token": tok})   # the bearer goes over the ssh channel only
        if not ev.wait(40) or not res.get("ok"):
            self.close()
            raise DaemonError(f"daemon did not come up: {res or 'timeout'}")
        self.gm = res.get("gm")

    def _write(self, obj):
        with self.lock:
            self.p.stdin.write(json.dumps(obj) + "\n")
            self.p.stdin.flush()

    def _read(self):
        for line in self.p.stdout:
            try:
                r = json.loads(line)
            except ValueError:
                continue
            if r.get("event") is not None:
                cb = self.events.get(r.get("id"))
                if cb is not None:   # never on the reader thread: a slow callback would stall every chain's channel
                    threading.Thread(target=cb, args=(r,), daemon=True).start()
                continue
            slot = self.pending.pop(r.get("id"), None)
            self.events.pop(r.get("id"), None)
            if slot:
                slot[1].update(r)
                slot[0].set()
        for ev, res in list(self.pending.values()):
            res.update(ok=False, error="daemon channel closed")
            ev.set()

    def alive(self):
        return self.p is not None and self.p.poll() is None

    def call(self, op, timeout=60, on_event=None, **kw):
        if not self.alive():
            raise DaemonError("daemon not running")
        rid, ev, res = uuid.uuid4().hex, threading.Event(), {}
        self.pending[rid] = (ev, res)
        if on_event is not None:
            self.events[rid] = on_event
            kw["events"] = True
        try:
            self._write({"id": rid, "op": op, **kw})
        except (OSError, ValueError) as e:
            raise DaemonError(f"daemon write failed: {e}") from None
        if not ev.wait(timeout):
            self.pending.pop(rid, None)
            self.events.pop(rid, None)
            raise DaemonError(f"daemon {op} timed out after {timeout}s")
        if not res.get("ok"):
            raise DaemonError(str(res.get("error"))[:300])
        return res

    def close(self):
        try:
            if self.alive():
                self._write({"id": "bye", "op": "shutdown"})
                self.p.stdin.close()
                self.p.wait(timeout=5)
        except Exception:  # noqa: BLE001
            pass
        if self.p is not None and self.p.poll() is None:
            self.p.kill()


_daemon = {"d": None, "failed_at": 0.0}
_daemon_lock = threading.Lock()


def _gm_token():
    try:
        return (ROOT / "secrets" / "gm_pairing_token").read_text().strip() or None
    except OSError:
        return os.environ.get("HUNTRESS_GM_TOKEN")


def hb_daemon(log=print):
    """The run's daemon, started on first use; None when disabled or (recently) unavailable."""
    if not HB_DAEMON:
        return None
    with _daemon_lock:
        d = _daemon["d"]
        if d is not None and d.alive():
            return d
        if time.time() - _daemon["failed_at"] < DAEMON_RETRY_S:
            return None
        try:
            t0 = time.time()
            _daemon["d"] = HbDaemon(log)
            log(f"[homebase] timed daemon up in {time.time() - t0:.1f}s (gm {_daemon['d'].gm})")
            return _daemon["d"]
        except Exception as e:  # noqa: BLE001 - the ssh-exec path still works
            _daemon.update(d=None, failed_at=time.time())
            log(f"[homebase] timed daemon unavailable ({str(e)[:160]}); per-attempt ssh exec")
            return None


def restart_hb_daemon(log=print):
    with _daemon_lock:
        d, _daemon["d"], _daemon["failed_at"] = _daemon["d"], None, 0.0
    if d is not None:
        d.close()
        log("[homebase] timed daemon restarted (code changed)")


# Early generalize (default OFF): the daemon reports "solved" (answers + missing + the attempt's bytes inline) BEFORE
# hb_timed's in-window partial submit / localization, so the orchestrator can start the generalize worker ~15 s sooner
# (D13 warmups Mastery: submit phase 15.5 s); the verdicts land in the variant case's gm_feedback.json afterwards.
EARLY_GENERALIZE = os.environ.get("HCTF_EARLY_GENERALIZE", "0") == "1"


def _early_handler(cid, on_event):
    """Daemon event -> write the inline bytes to .run/tmp-timed/<slug> (the timed dir capture_variant reads), then
    on_event(data). Errors stay here: an event must never cost the attempt."""
    import re as _re
    local = ROOT / ".run" / "tmp-timed" / _re.sub(r"[^A-Za-z0-9]+", "_", cid)

    def handle(msg):
        try:
            data = dict(msg.get("data") or {})
            if msg.get("_inline"):
                write_inline(msg["_inline"], local)
                data["local"] = str(local)
            on_event(data)
        except Exception as e:  # noqa: BLE001
            print(f"[{cid}] early event note: {e}", flush=True)
    return handle


def run_hb_timed(solver_dir, cid, op="start", timeout=60, on_event=None):
    """Run the clock-critical timed attempt ON Homebase (adjacent to the GM). Returns hb_timed's JSON dict.
    Syncs hctf+lib (base) and the solver so hb_timed can execute it next to the GM. `on_event` (EARLY_GENERALIZE,
    daemon only): called with the "solved" event's data (+ "local" = the bytes' dir) mid-attempt."""
    rel = solver_dir.relative_to(ROOT)
    t_kick, prepush_wait = time.time(), 0.0
    # Kickoff (sync + solver push) runs over the flaky local->Homebase VPN link; the retrying ssh/rsync ride
    # through transient drops, but if it still fails, return exec_error so run_timed_auto falls back to local
    # rather than crashing the whole attempt. (Once hb_timed is running, its in-window GM calls are HB->inside
    # proxy, off the VPN, so they stay fast and stable.)
    try:
        sync_homebase_base()
        push_hot_files()
        if solver_dir.exists():
            # Skip the push when the solver code is unchanged since the last push of this dir (TT -> Mastery: same
            # solver, ~1 round-trip saved between modes). ONE round-trip otherwise: the remote rsync creates the dir
            # itself; cases/ (6-8 MB of regression bytes on the hard lanes) is never needed to run the solver.
            ev = _prepush.get(str(solver_dir))
            if ev is not None:
                t_w = time.time()
                ev.wait(PREPUSH_WAIT)   # a pre-push of this verified solver is in flight: never rsync beside it
                prepush_wait = time.time() - t_w
            sig = _solver_sig(solver_dir)
            if _pushed.get(str(solver_dir)) != sig:
                push_solver(solver_dir, rel)
                _pushed[str(solver_dir)] = sig
        else:
            remote.ssh(f"mkdir -p ~/{HB_WORK}/{rel}")
    except (RuntimeError, subprocess.SubprocessError, OSError) as e:  # incl. remote-command failures
        return {"result": "exec_error", "detail": f"homebase kickoff failed: {e}"}
    # Use the GM's INSIDE proxy from Homebase (network-path identity = same test account as the pairing token,
    # sub-ms latency) so tight windows (e.g. the 6s scripting Time Trial) fit; the public GM's ~2.7s/call
    # round-trips blow those windows even warm.
    t_exec = time.time()
    res = None
    d = hb_daemon()
    if d is not None:
        opts = timed_env(cid)
        opts["HCTF_RUNNER_BUDGET"] = str(max(10, timeout - 5))   # hb_timed prints before this call times out
        if os.environ.get("HCTF_RUN_FOR_TIME") is not None:
            opts["HCTF_RUN_FOR_TIME"] = os.environ["HCTF_RUN_FOR_TIME"]
        try:
            extra = {"inline_max": INLINE_PULL_MAX, "inline_z": True} if INLINE_PULL_MAX > 0 else {}
            if EARLY_GENERALIZE and on_event is not None:
                extra["on_event"] = _early_handler(cid, on_event)
                opts["HCTF_EARLY_GENERALIZE"] = "1"
            res = d.call("attempt", timeout=timeout, cid=cid, solver=str(rel), op_mode=op, opts=opts, **extra)["result"]
            res["via"] = "daemon"
        except DaemonError as e:
            # Mid-attempt loss: the ssh path's `start` reconnects to the same attempt (start is idempotent).
            res = None
            print(f"[homebase] daemon attempt failed ({e}); ssh exec of hb_timed.py", flush=True)
    if res is None:
        try:
            rft = os.environ.get("HCTF_RUN_FOR_TIME")   # pool policy (hb_timed._rft); default there: auto (regular first)
            fwd = "".join(f"{k}={shlex.quote(v)} " for k, v in {**timed_env(cid),
                                                                 "HCTF_RUNNER_BUDGET": str(max(10, timeout - 8))}.items())
            r = remote.ssh(f"cd ~/{HB_WORK} && HUNTRESS_GAME_MASTER_URL={remote.INSIDE_GM} "
                           + (f"HCTF_RUN_FOR_TIME={shlex.quote(rft)} " if rft is not None else "") + fwd
                           + f"python3 hctf/hb_timed.py {shlex.quote(cid)} {shlex.quote(str(rel))} --op {op}",
                           timeout=timeout, check=False)
        except (remote.Unreachable, subprocess.SubprocessError, OSError) as e:
            return {"result": "exec_error", "detail": f"homebase exec failed: {e}"}
        try:
            res = json.loads(r.stdout.strip().splitlines()[-1])
        except (IndexError, ValueError):
            return {"result": "exec_error", "detail": (r.stdout + r.stderr)[-500:]}
    inline = res.pop("_inline", None) if isinstance(res, dict) else None
    # kickoff = local sync/push before the ssh exec; exec_total = the whole remote round trip (start..result)
    res["kickoff"] = {"push": round(t_exec - t_kick, 2), "prepush_wait": round(prepush_wait, 2),
                      "exec_total": round(time.time() - t_exec, 2)}
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
    if not needs_variant_pull(res):
        # No new variant to capture (rotation_exhausted, rate limit, prerequisite, start error): the remote dir only
        # holds an OLD attempt's bytes. Blind D7 replay: a rotation_exhausted Mastery pulled 13 MB of stale evidence
        # at ~130 KB/s over the VPN -- ~100 s on the critical path for nothing.
        res["capture_note"] = "no new variant on Homebase (no attempt_id): pull skipped"
        return res
    if not needs_bytes(res):
        # A clock / transport failure (expired, submit dropped, solver starved of clock): the solver is fine and the
        # orchestrator just retries -- nothing needs this variant's bytes. Day 8 binary Mastery: a synchronous pull of
        # 5 x 31 MB over the ~140 KB/s VPN held the retry for 442 s, then 186 s.
        res["capture_note"] = "clock/transport failure: variant pull skipped (retry needs no bytes)"
        return res
    if inline:
        try:
            got = write_inline(inline, local)
            res["capture_note"] = f"inline from the daemon: {', '.join(got)} ({sum(len(v) for v in inline.values()) * 3 // 4} B)"
            return res
        except Exception as e:  # noqa: BLE001 - fall through to the pull
            res["capture_note"] = f"inline bytes unusable ({str(e)[:120]}); "
    if PUBLIC_FAIL_PULL and res.get("deadline") is None and (res.get("untimed") or res.get("no_clock")
                                                              or res.get("run_for_time") is False):
        try:
            t0 = time.time()
            got = public_pull(res, slug, local, cid)
            res["capture_note"] = (res.get("capture_note") or "") + \
                f"public refetch: {', '.join(got)} in {time.time() - t0:.1f}s"
            return res
        except Exception as e:  # noqa: BLE001 - fall back to the Homebase pull
            res["capture_note"] = (res.get("capture_note") or "") + f"public refetch failed ({str(e)[:120]}); "
    try:
        # A failure needs the variant's bytes locally (generalize on it) before anything else -- but only the deliveries
        # of the failing sets, fetched as parallel byte ranges (D8 binary Mastery: 5 x 31 MB = 157 MB took 10-20 min).
        t0 = time.time()
        got = scoped_pull(res, slug, local)
        res["capture_note"] = (res.get("capture_note") or "") + f"scoped pull: {', '.join(got)} in {time.time() - t0:.1f}s"
    except Exception as e:  # noqa: BLE001 - capture is best-effort
        res["capture_note"] = (res.get("capture_note") or "") + f"scoped pull failed ({str(e)[:160]}); full pull"
        try:
            pull()
        except Exception as e2:  # noqa: BLE001
            res["capture_note"] += f"; could not fetch the attempt's bytes from Homebase: {e2}"
    return res


SET_KEY = re.compile(r"^((?:set|slot)[._-]?\d+)[._-](.+)$")
# A failed attempt that is still live and untimed: fetch its bytes from the PUBLIC GM (MB/s from here) rather than
# pulling them back from Homebase over the VPN (~130 KB/s: D15 script Mastery 26.8 s, metadata TT 15.3 s).
PUBLIC_FAIL_PULL = os.environ.get("HCTF_PUBLIC_FAIL_PULL", "1") == "1"


def public_pull(res, slug, local, cid):
    """Reconnect publicly (`start` resumes the live attempt; it never re-rolls), save its contract + result into
    `local` and download the failing sets' deliveries (deliveries_for) from the public GM, sha256-checked. The same
    files scoped_pull writes. Returns the container names; raises -> the caller falls back to scoped_pull."""
    import hashlib
    from concurrent.futures import ThreadPoolExecutor as _TPE
    from . import hb_timed as ht
    with ht._POOL_LOCK:   # a small pool in this process (the default pre-opens 32 TLS sockets for a Mastery window)
        if ht._POOL is None:
            ht._POOL = ht._Pool(ht.GM, size=4)
    # _post_once, NOT _post_start: the pool policy could upgrade this to run_for_time (a fresh ranked attempt)
    body = ht._post_once({"op": "start", "challenge": cid})
    if not isinstance(body, dict) or body.get("attempt_id") != res.get("attempt_id") or not body.get("answer_ids"):
        raise RuntimeError(f"public start did not resume attempt {str(res.get('attempt_id'))[:8]}: "
                           f"{str((body or {}).get('error') or (body or {}).get('result') or 'other attempt')[:80]}")
    if local.exists():
        for f in local.glob("*"):
            if f.is_file():
                f.unlink()
    local.mkdir(parents=True, exist_ok=True)
    (local / "contract.json").write_text(json.dumps(body))
    (local / "result.json").write_text(json.dumps({k: v for k, v in res.items() if not callable(v)}, default=str))
    plan = dict(ht._plan(body))
    names = [n for n in deliveries_for(res, body) if n in plan]
    shas = {a.get("sha256") for a in body.get("artifacts") or [] if isinstance(a, dict) and a.get("sha256")}
    if not names and BUNDLE_FALLBACK and len(plan) == 1:
        names = list(plan)          # one bundle (warmups Mastery): the lone delivery is the variant
        if body.get("sha256"):
            shas = shas | {body["sha256"]}
    if not names:
        raise RuntimeError(f"no failing-set delivery in the public contract (have {sorted(plan)[:6]})")

    def fetch(n):
        (local / n).write_bytes(ht._get_bytes(plan[n]))
        if shas and hashlib.sha256((local / n).read_bytes()).hexdigest() not in shas:
            raise RuntimeError(f"{n}: sha256 not in the contract's artifacts")
    with _TPE(max_workers=min(8, len(names))) as ex:
        list(ex.map(fetch, names))
    return names


def deliveries_for(res, contract):
    """Container names to pull for a failed attempt: the fewest sets covering every failing field family (wrong /
    missing / partial-wrong ids with the `setN.` prefix stripped); one representative set when nothing is localized
    (solver crash / too slow / unlocalized incorrect). Every container when the contract has a single delivery."""
    ids = contract.get("answer_ids") or []
    qs = contract.get("questions") or []
    by_set, all_c = {}, []
    for i, aid in enumerate(ids):
        art = (qs[i].get("artifact") if i < len(qs) and isinstance(qs[i], dict) else "") or ""
        c = art.split("->", 1)[0].strip()
        if not c:
            continue
        if c not in all_c:
            all_c.append(c)
        m = SET_KEY.match(aid)
        if m:
            by_set.setdefault(m.group(1), set()).add(c)
    if len(all_c) <= 1 or not by_set:
        return all_c
    failing = [x[0] if isinstance(x, (list, tuple)) else x for x in (res.get("wrong") or [])]
    failing += list(res.get("missing") or [])
    failing += [x[0] if isinstance(x, (list, tuple)) else x for x in (res.get("partial_wrong") or [])]
    fams = {}
    for aid in failing:
        m = SET_KEY.match(str(aid))
        if m:
            fams.setdefault(m.group(2), set()).add(m.group(1))
    chosen = []
    for fam in sorted(fams):
        if not any(sk in chosen for sk in fams[fam]):
            chosen.append(sorted(fams[fam], key=lambda k: int(re.sub(r"\D", "", k) or 0))[0])
    if not chosen:
        bad = [b for b in (res.get("bad_sets") or []) if b in by_set]
        chosen = [bad[0] if bad else sorted(by_set, key=lambda k: int(re.sub(r"\D", "", k) or 0))[0]]
    out = []
    for sk in chosen:
        for c in sorted(by_set.get(sk, ())):
            if c not in out:
                out.append(c)
    return out


BUNDLE_FALLBACK = os.environ.get("HCTF_BUNDLE_FALLBACK", "1") != "0"
# A failed daemon attempt's files (<= this many bytes in total) come back INLINE in the result (hb_daemon
# _inline_bytes): no post-failure ssh listing + fetch. 0 = off; an old daemon ignores the field (pull as before).
INLINE_PULL_MAX = int(os.environ.get("HCTF_INLINE_PULL_MAX", "262144"))


def write_inline(inline, local):
    """Write hb_daemon's {name: base64} attempt files into `local` (cleared first) -> [delivery names]."""
    import base64
    local = Path(local)
    if local.exists():
        for f in local.glob("*"):
            if f.is_file():
                f.unlink()
    local.mkdir(parents=True, exist_ok=True)
    for name, b64 in inline.items():
        if "/" in name or name.startswith("."):
            raise ValueError(f"bad inline name {name!r}")
        if b64.startswith("z:"):   # zlib-packed by a daemon that got inline_z (hb_daemon._inline_bytes)
            import zlib
            data = zlib.decompress(base64.b64decode(b64[2:]))
        else:
            data = base64.b64decode(b64)
        (local / name).write_bytes(data)
    return sorted(n for n in inline if not n.endswith(".json"))


def scoped_pull(res, slug, local):
    """Fetch contract.json + result.json, then only deliveries_for(...) of a failed Homebase attempt into `local`
    (parallel byte ranges, sha256-checked against the contract). Returns the fetched container names."""
    import hashlib
    rdir = f"{HB_WORK}/.run/tmp-timed/{slug}"
    if local.exists():
        for f in local.glob("*"):
            if f.is_file():
                f.unlink()
    local.mkdir(parents=True, exist_ok=True)
    listing = remote.ssh(f"cd ~/{rdir} && find . -maxdepth 1 -type f -printf '%s\\t%P\\n'", timeout=30, check=False)
    sizes = {}
    for ln in listing.stdout.splitlines():
        sz, _, name = ln.partition("\t")
        if name:
            sizes[name] = int(sz)
    for small in ("contract.json", "result.json"):
        if small in sizes:
            remote.fetch_file(f"{rdir}/{small}", local / small, sizes[small], streams=1)
    contract = json.loads((local / "contract.json").read_text())
    names = [n for n in deliveries_for(res, contract) if n in sizes]
    shas = {a.get("sha256") for a in contract.get("artifacts") or [] if isinstance(a, dict) and a.get("sha256")}
    if not names and BUNDLE_FALLBACK:
        # Warmups Mastery (D2-D13): ONE zip of every set's blob-NN.txt saved as blob-01.txt, no artifacts[], only a
        # top-level sha256 -> no per-set name matches. The lone non-JSON file IS the delivery: fetch it (D13: the
        # "full pull" fallback took the rsync path instead).
        files = [n for n in sizes if not n.endswith(".json")]
        if len(files) == 1:
            names = files
            if contract.get("sha256"):
                shas = shas | {contract["sha256"]}
    if not names:
        raise RuntimeError(f"no failing-set delivery found on Homebase (have {sorted(sizes)[:6]})")
    for n in names:
        remote.fetch_file(f"{rdir}/{n}", local / n, sizes[n])
        if shas and hashlib.sha256((local / n).read_bytes()).hexdigest() not in shas:
            raise RuntimeError(f"{n}: sha256 not in the contract's artifacts")
    return names


def needs_bytes(res):
    """A failed attempt whose variant the next step WORKS ON (generalize/probe on the failed variant): wrong or missing
    answers, a solver crash, or a genuinely too-slow solver. Clock/transport failures retry on a fresh variant."""
    r = str(res.get("result", "")).lower()
    if r in ("solver_incomplete", "solver_error", "incorrect", "accepted"):
        return True
    return r == "exec_error" and bool(res.get("solver_too_slow")) and not res.get("clock_short")


def needs_variant_pull(res):
    """A non-pass timed result has a variant worth pulling back only if the GM actually started an attempt."""
    r = str(res.get("result", "")).lower()
    return bool(res.get("attempt_id")) and not res.get("gm_rate_limited") and r not in (
        "rotation_exhausted", "no_answer_ids", "prerequisite_required", "start_required")


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
    path = f"PATH=~/{HB_WORK}/bin:~/hbtools/bin:~/{HB_WORK}/tools/node/bin:~/{HB_WORK}/.venv/bin:~/.local/bin:$PATH "
    if HB_ENGINE == "codex":
        cmd = (f"cd ~/{HB_WORK} && {envs} PYTHONPATH=~/{HB_WORK} {path}"
               f"timeout {int(timeout)} codex exec --dangerously-bypass-approvals-and-sandbox --skip-git-repo-check "
               f"{shlex.quote(prompt)} </dev/null")
    else:   # Claude Code on Bedrock (the VM's instance role), same flags as a local worker; prompt via stdin
        from . import hbbudget, hbshadow
        pf = TMP / f"hbworker-{int(time.time() * 1000)}.prompt"
        pf.write_text(prompt)
        remote.rsync_to(pf, f"~/{HB_WORK}/.run/{pf.name}", mkdir=f"~/{HB_WORK}/.run")
        bed = " ".join(f"{k}={shlex.quote(v)}" for k, v in hbshadow.BEDROCK_ENV.items())
        lane = env_extra.get("HCTF_LANE")
        flags = ["--dangerously-skip-permissions", "--max-turns", str(_max_turns(stage)), "--model", hbshadow.MODEL,
                 "--effort", worker_effort(lane), "--output-format", "stream-json", "--verbose", "--strict-mcp-config",
                 "--settings", json.dumps(worker_settings(lane)),
                 "--max-budget-usd", str(hbbudget.ai_cap_usd(hbshadow.SHADOW_USD))]
        if WORKER_TOOLS:
            flags += ["--tools", WORKER_TOOLS]
        cmd = (f"cd ~/{HB_WORK} && {envs} {bed} JAVA_HOME=~/hbtools/jdk PYTHONPATH=~/{HB_WORK} {path}"
               f"nice -n 10 timeout {int(timeout)} claude -p {' '.join(shlex.quote(f) for f in flags)} "
               f"< ~/{HB_WORK}/.run/{pf.name}")
    try:
        r = remote.ssh(cmd, timeout=timeout + 60, check=False)
        rc, text = r.returncode, r.stdout + r.stderr
    except subprocess.TimeoutExpired:
        rc, text = -9, "timeout"
    log.write_text(text)
    if HB_ENGINE != "codex":
        from . import hbbudget, hbshadow  # noqa: F401
        try:
            import importlib.util as _u
            spec = _u.spec_from_file_location("hbcost", ROOT / "hctf" / "hbcost.py")
            mod = _u.module_from_spec(spec)
            spec.loader.exec_module(mod)
            hbbudget.record_ai(mod.cost(str(log))["usd"], f"homebase {stage} {env_extra.get('HCTF_CHAL')}")
        except Exception:  # noqa: BLE001 - accounting is best-effort
            pass
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
