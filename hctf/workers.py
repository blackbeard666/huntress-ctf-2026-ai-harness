"""LLM worker processes. One process per challenge stage; the orchestrator verifies the outcome.

local:    `claude -p` in WSL (your subscription). Repo hooks (.claude/settings.json) and skills apply.
homebase: `codex exec` on Homebase over SSH (Homebase token credits). The repo slice is rsynced to
          ~/hw, skills to ~/.codex/skills, and results are rsynced back when the worker exits.
"""
import json
import os
import shlex
import subprocess
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


def run_local(chal_dir, stage, prompt, env_extra, timeout):
    """Blocking. Returns (returncode, logfile)."""
    log = _logfile(chal_dir, stage, "local")
    env = dict(os.environ)
    env.update({k: str(v) for k, v in env_extra.items()})
    env["HCTF_WORKER_START"] = str(time.time())
    env["TMPDIR"] = str(TMP)  # keep every worker's scratch files inside the project
    env["PATH"] = f"{ROOT / 'bin'}:{Path.home() / '.local/bin'}:{Path.home() / 'tools/node/bin'}:{env.get('PATH', '')}"
    cmd = ["claude", "-p", prompt, "--dangerously-skip-permissions", "--output-format", "stream-json", "--verbose"]
    with open(log, "w") as out:
        p = subprocess.Popen(cmd, cwd=ROOT, stdout=out, stderr=subprocess.STDOUT, env=env, start_new_session=True)
        try:
            return p.wait(timeout=timeout), log
        except subprocess.TimeoutExpired:
            os.killpg(p.pid, 9)
            return -9, log


_sync_lock = threading.Lock()


def sync_homebase_base():
    """Push hctf + skills + bin to Homebase (shared by all homebase workers)."""
    with _sync_lock:
        remote.ssh(f"mkdir -p ~/{HB_WORK}/challenges ~/.codex/skills")
        for d in ("hctf", "bin", "skills"):
            remote.rsync_to(ROOT / d, f"~/{HB_WORK}/")
        remote.ssh(f"rsync -a --delete ~/{HB_WORK}/skills/ ~/.codex/skills/ && cp ~/{HB_WORK}/hctf/gm.py ~/hctf/gm.py")
        for f in ("CLAUDE.md", "AGENTS.md"):
            if (ROOT / f).exists():
                remote.rsync_to(ROOT / f, f"~/{HB_WORK}/{f}")


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
    cmd = (f"cd ~/{HB_WORK} && {envs} PATH=~/{HB_WORK}/bin:~/{HB_WORK}/tools/node/bin:$PATH "
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
