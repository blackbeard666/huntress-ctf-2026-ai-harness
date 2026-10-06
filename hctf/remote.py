"""Bridge from the local machine to Homebase: SSH exec of hctf/gm.py, rsync of files, VM power.

The GM is only reachable from inside Homebase and sshd forbids port forwarding, so every GM call
is `ssh hb python3 ~/hctf/gm.py ...` over a single multiplexed connection (ControlMaster).
"""
import fcntl
import json
import os
import shlex
import subprocess
import sys
import time
from contextlib import contextmanager
from pathlib import Path

from .paths import LOCKS, ROOT, RUN, SECRETS

HB_HOST = os.environ.get("HCTF_HB_HOST", "10.1.50.243")
HB_USER = "HuntressCTF"
HB_DIR = "hctf"  # relative to the remote home directory
KEY = SECRETS / "huntress_homebase"   # project-local key; nothing in ~/.ssh
CTL = RUN / "cm-%C"                   # ssh ControlMaster socket
KNOWN_HOSTS = RUN / "known_hosts"
WIN_PY = "/mnt/c/Users/cavila/AppData/Local/Python/pythoncore-3.14-64/python.exe"
MAX_PARALLEL = int(os.environ.get("HCTF_MAX_PARALLEL", "6"))  # sshd MaxSessions defaults to 10
LOCKDIR = LOCKS

SSH_OPTS = [
    "-i", str(KEY), "-o", "BatchMode=yes", "-o", "ConnectTimeout=15", "-o", "IdentitiesOnly=yes",
    "-o", f"UserKnownHostsFile={KNOWN_HOSTS}", "-o", "StrictHostKeyChecking=accept-new",
    # A dead tunnel is noticed in ~15s (was 45s with the default count of 3 at 15s), without killing a healthy
    # session on one lost keepalive.
    "-o", "ServerAliveInterval=5", "-o", "ServerAliveCountMax=3",
    "-o", "ControlMaster=auto", "-o", f"ControlPath={CTL}", "-o", "ControlPersist=600",
]


class Unreachable(RuntimeError):
    """Homebase (and so the GM) can't be reached: VM off, VPN down, or SSH failure."""


@contextmanager
def _slot():
    """Cross-process semaphore: at most MAX_PARALLEL concurrent SSH sessions from every worker."""
    LOCKDIR.mkdir(exist_ok=True)
    while True:
        for i in range(MAX_PARALLEL):
            f = open(LOCKDIR / f"ssh-{i}.lock", "w")
            try:
                fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                f.close()
                continue
            try:
                yield
            finally:
                fcntl.flock(f, fcntl.LOCK_UN)
                f.close()
            return
        time.sleep(0.2)


SSH_RETRIES = int(os.environ.get("HCTF_SSH_RETRIES", "3"))  # rides through transient UDP-VPN drops to Homebase


def ssh(cmd, timeout=180, check=True):
    for attempt in range(1, SSH_RETRIES + 1):
        with _slot():
            r = subprocess.run(["ssh", *SSH_OPTS, f"{HB_USER}@{HB_HOST}", cmd],
                               capture_output=True, text=True, timeout=timeout)
        if r.returncode != 255 or attempt == SSH_RETRIES:
            break
        clear_control_sockets()  # stale ControlMaster socket, or a transient VPN blip: drop it, back off, reconnect
        time.sleep(1.0 * attempt)
    if r.returncode == 255:
        raise Unreachable(r.stderr.strip() or "ssh failed")
    if check and r.returncode not in (0, 5):
        raise RuntimeError(f"remote command failed ({r.returncode}): {r.stderr.strip()[:500]}")
    return r


def probe(timeout=8):
    """ONE quick reachability check (no retries, 5s connect): True if Homebase answers. For the health thread --
    ssh() with its 3 retries x 15s connect took ~48s to report a dead tunnel."""
    opts = [o if o != "ConnectTimeout=15" else "ConnectTimeout=5" for o in SSH_OPTS]
    try:
        r = subprocess.run(["ssh", *opts, f"{HB_USER}@{HB_HOST}", "true"], capture_output=True, text=True,
                           timeout=timeout)
    except subprocess.TimeoutExpired:
        clear_control_sockets()
        return False
    if r.returncode == 255:
        clear_control_sockets()
    return r.returncode == 0


ON_HOMEBASE = bool(os.environ.get("HCTF_ON_HOMEBASE"))  # set for workers running on Homebase itself
GM_LOCAL = ROOT / "hctf" / "gm.py"
INSIDE_GM = "http://10.0.0.219/huntress-ctf-proxy"  # the GM's inside address (SSH/Homebase fallback)


def _have_token():
    return bool(os.environ.get("HUNTRESS_GM_TOKEN")) or (SECRETS / "gm_pairing_token").exists()


def gm_transport():
    """How to reach the GM. 'local' (default) runs gm.py here against the public GM with the pairing
    token; 'ssh' SSH-execs it on Homebase against the inside proxy (fallback: forced, or no token)."""
    t = os.environ.get("HCTF_GM_TRANSPORT")
    if t:
        return t
    if ON_HOMEBASE:
        return "homebase-local"
    return "local" if _have_token() else "ssh"


def _gm_parse(r, transport):
    """Parse gm.py's last stdout line into its JSON envelope; raise Unreachable if the GM didn't answer."""
    try:
        env = json.loads(r.stdout.strip().splitlines()[-1])
    except (IndexError, ValueError):
        raise RuntimeError(f"bad gm.py output: {r.stdout[:300]!r} {r.stderr[:300]!r}")
    if env.get("http") == 0:
        raise Unreachable(f"GM unreachable ({transport}): {env.get('body')}")
    return env


def _gm_local(args, timeout):
    """Run gm.py HERE against the public GM with the pairing token."""
    r = subprocess.run([sys.executable, str(GM_LOCAL), *map(str, args)],
                       capture_output=True, text=True, timeout=timeout)
    return _gm_parse(r, "local")


def gm(*args, timeout=180):
    """Return gm.py's JSON envelope. Default transport runs the client LOCALLY against the public GM
    (pairing token). With HCTF_GM_TRANSPORT=ssh it SSH-execs on Homebase against the inside proxy (sub-second
    vs the public GM's ~1.3-8s/call) and, on any SSH/Homebase failure, falls back to the local public GM when
    a pairing token is present. 'homebase-local' runs on Homebase itself (for workers already on the VM)."""
    transport = gm_transport()
    if transport == "ssh":
        try:
            r = ssh(f"HUNTRESS_GAME_MASTER_URL={INSIDE_GM} python3 ~/{HB_DIR}/gm.py "
                    + " ".join(shlex.quote(str(a)) for a in args), timeout=timeout)
            return _gm_parse(r, "ssh")
        except (Unreachable, subprocess.SubprocessError, RuntimeError, OSError) as e:
            # Homebase hiccup mid-run (SSH drop, cold reconnect, inside proxy down): don't fail the call —
            # fall back to the public GM via the pairing token (slower ~1.3-8s, but it lands). Only the
            # clock-critical timed path (run_hb_timed) can't afford this; ordinary calls prefer correctness.
            if _have_token():
                return _gm_local(args, timeout)
            raise Unreachable(f"Homebase GM unreachable and no pairing token for fallback: {e}")
    if transport == "homebase-local":
        r = subprocess.run(["python3", str(Path.home() / HB_DIR / "gm.py"), *map(str, args)],
                           capture_output=True, text=True, timeout=timeout,
                           env=dict(os.environ, HUNTRESS_GAME_MASTER_URL=INSIDE_GM))
        return _gm_parse(r, "homebase-local")
    return _gm_local(args, timeout)  # local (default): public GM via pairing token


def rsync_from(remote_path, local_dir):
    """Copy a remote directory's contents into local_dir."""
    Path(local_dir).mkdir(parents=True, exist_ok=True)
    if ON_HOMEBASE:
        src = os.path.expanduser(remote_path).rstrip("/") + "/"
        subprocess.run(["rsync", "-a", src, str(local_dir).rstrip("/") + "/"], check=True, capture_output=True)
        return
    _rsync(["rsync", "-a", "-e", "SSH", f"{HB_USER}@{HB_HOST}:{remote_path.rstrip('/')}/",
            str(local_dir).rstrip("/") + "/"])


def rsync_to(local_path, remote_path, exclude=(), mkdir=None):
    """mkdir: create this remote dir in the same round-trip (via --rsync-path) instead of a separate ssh mkdir."""
    argv = ["rsync", "-a", "--delete", "-e", "SSH", *[f"--exclude={x}" for x in exclude]]
    if mkdir:
        argv.append(f"--rsync-path=mkdir -p {mkdir} && rsync")
    _rsync([*argv, str(local_path), f"{HB_USER}@{HB_HOST}:{remote_path}"])


def _rsync(argv):
    """rsync over the shared ssh options; on ssh failure (exit 255, usually a stale ControlMaster socket left by a
    killed session) clear the sockets and retry once instead of crashing the caller."""
    argv = [("ssh " + " ".join(shlex.quote(o) for o in SSH_OPTS)) if a == "SSH" else a for a in argv]
    for attempt in range(1, SSH_RETRIES + 1):
        with _slot():
            r = subprocess.run(argv, capture_output=True, timeout=600)
        if r.returncode == 0:
            return r
        if r.returncode == 255 and attempt < SSH_RETRIES:
            clear_control_sockets()  # stale socket or transient VPN blip: reconnect after a short backoff
            time.sleep(1.0 * attempt)
            continue
        raise subprocess.CalledProcessError(r.returncode, argv, r.stdout, r.stderr)


def clear_control_sockets():
    for s in RUN.glob("cm-*"):
        try:
            s.unlink()
        except OSError:
            pass


def deploy():
    """Install/refresh the remote GM client (needed again after a Homebase factory reset)."""
    ssh(f"mkdir -p ~/{HB_DIR}/dl")
    rsync_to(ROOT / "hctf" / "gm.py", f"~/{HB_DIR}/gm.py")


def power(action="status"):
    """VM power/credits through the Windows-side browser session. Returns {"state","ip","credits"}.

    WSL-native fallback: when Claude Code runs natively in WSL the Windows browser session isn't wired
    up, but the VM is reachable over the CTF VPN. For status/on, short-circuit to 'running' when SSH
    answers (the VM is already up), skipping the browser entirely. Powering OFF still needs the browser
    (and runs never call it unless they powered the VM on themselves)."""
    if action in ("status", "on"):
        try:
            ssh("true", timeout=12)
            return {"state": "running", "ip": HB_HOST, "credits": None}
        except Exception:  # noqa: BLE001 - VM not reachable via SSH; fall back to the browser path
            pass
    # The Windows browser session belongs to ONE CourseStack account; a copy wired to another account's VM
    # (the rehearsal copy) sets this so a failed SSH check can never power/inspect the wrong account's VM.
    if os.environ.get("HCTF_NO_BROWSER_POWER") == "1":
        raise RuntimeError(f"Homebase {HB_HOST} unreachable over SSH and browser power is disabled")
    script =subprocess.run(["wslpath", "-w", str(ROOT / "hctf" / "hbpower.py")],
                            capture_output=True, text=True, check=True).stdout.strip()
    r = subprocess.run([WIN_PY, script, action], capture_output=True, text=True, timeout=420)
    if r.returncode:
        raise RuntimeError(f"hbpower failed (is browser/launch.py running and logged in?): {r.stderr[-500:]}")
    return json.loads(r.stdout.strip().splitlines()[-1])


def ensure_up(wait=300):
    """Power the VM on if needed and wait until SSH answers."""
    st = power("status")
    if st["state"] != "running":
        st = power("on")
    deadline = time.time() + wait
    while True:
        try:
            ssh("true", timeout=20)
            return st
        except (Unreachable, subprocess.TimeoutExpired):
            if time.time() > deadline:
                raise
            time.sleep(5)
