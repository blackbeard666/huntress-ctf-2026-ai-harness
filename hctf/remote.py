"""Bridge from the local machine to Homebase: SSH exec of hctf/gm.py, rsync of files, VM power.

The GM is only reachable from inside Homebase and sshd forbids port forwarding, so every GM call
is `ssh hb python3 ~/hctf/gm.py ...` over a single multiplexed connection (ControlMaster).
"""
import fcntl
import json
import os
import re
import shlex
import subprocess
import threading
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
    # Self-contained: skip ssh_config. Inside the worker sandbox (bwrap) /etc/ssh/ssh_config.d/* shows a foreign owner,
    # ssh refuses it ("Bad owner or permissions") and exits 255 -- so the Single Solve submit-via-Homebase path
    # (_master_alive) never fired on Day 7/8 and singles waited out public-GM 429s (warmups D8: 30 s).
    "-F", "/dev/null",
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


# gm.py IN-PROCESS (default): no interpreter start per call and kept-alive connections (gm.POOL) -- every orchestrator GM
# call used to be a fresh `python3 gm.py` + TLS handshake. HCTF_GM_INPROC=0 restores the subprocess per call.
GM_INPROC = os.environ.get("HCTF_GM_INPROC", "1") != "0"
_gm_client = None
_gm_client_lock = threading.Lock()


def gm_client():
    """hctf/gm.py loaded as a module (its own copy: the CLI script stays standalone/stdlib-only)."""
    global _gm_client
    with _gm_client_lock:
        if _gm_client is None:
            import importlib.util
            spec = importlib.util.spec_from_file_location("hctf_gm_client", GM_LOCAL)
            m = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(m)
            m.POOL = os.environ.get("HCTF_GM_KEEPALIVE", "1") != "0"
            _gm_client = m
    return _gm_client


def _gm_local(args, timeout):
    """Run gm.py HERE against the public GM with the pairing token."""
    if GM_INPROC:
        env = gm_client().run(args)
        env["transport"] = "inproc"
        if env.get("http") == 0:
            raise Unreachable(f"GM unreachable (local): {env.get('body')}")
        return env
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
    if args and args[0] == "start" and len(args) > 1 and _public_gm() and _big_start(str(args[1])):
        # A large start reply (script: ~650 KB contract) crosses the VPN at ~130 KB/s on the daemon's ONE stdio
        # channel and holds up every reply queued behind it: D15 script 8.9 s + binary (80 KB) 9.4 s client time for
        # GM calls of 2.4-2.6 s; the three small lanes 2.6-2.9 s. The public GM returns it directly.
        return _gm_local(args, timeout)
    if args and args[0] in ("start", "submit") and GM_VIA_DAEMON and _public_gm():
        env = _gm_via_daemon(args, timeout)      # the run's warm Homebase daemon, when this process has one
        if env is not None:
            return env
    if args and args[0] == "submit" and SUBMIT_VIA_HB and _public_gm() and _master_alive():
        env = _gm_submit_hb(args, timeout)
        if env is not None:
            return env
    if args and args[0] == "start" and START_VIA_HB and _public_gm() and _master_alive():
        try:
            env = _gm_submit_hb(args, timeout, op="start")
        except Unreachable:  # outcome unknown -- but start RESUMES a running attempt: the public one is safe
            env = None
        if env is not None:
            return env
    return _gm_local(args, timeout)  # local (default): public GM via pairing token


# Single Solve submits via Homebase's inside proxy (0.55 s vs 2.8 s, and Day 7's public-GM submits took 9.5-18 s).
# ONLY the submit: its payload is a few hundred bytes of answers; start/download stay public because the bytes are
# needed HERE (a proxy hop would only add transfer). HCTF_SUBMIT_VIA_HB=0 disables.
SUBMIT_VIA_HB = os.environ.get("HCTF_SUBMIT_VIA_HB", "1") != "0"
# `start` too: its reply is the JSON contract, not the artifact bytes. D9-D11 single starts on the public GM took
# 1.6-4.3 s (3-4 s on D11) vs 0.5-0.9 s for the same call from Homebase -- all of it before the worker's go.
# Downloads stay public (binary evidence is ~31 MB). HCTF_START_VIA_HB=0 disables.
START_VIA_HB = os.environ.get("HCTF_START_VIA_HB", "1") != "0"
# ...except a Single whose lane's previous start reply exceeded this many KB (0 = never public by size).
START_VIA_HB_MAX_KB = float(os.environ.get("HCTF_START_VIA_HB_MAX_KB", "200"))
_BIG_START = {}


def _big_start(cid):
    """True when `cid` is a Single Solve whose lane's newest earlier `single_solve/start.json` > START_VIA_HB_MAX_KB."""
    if START_VIA_HB_MAX_KB <= 0 or "/" in cid:
        return False
    m = re.match(r"(.+?)-day-(\d+)", cid)
    if not m:
        return False
    lane, day = m.group(1), int(m.group(2))
    if (lane, day) not in _BIG_START:
        size = 0
        for meta in sorted(ROOT.glob("challenges/day*/*/meta.json"), reverse=True):
            dm = re.match(r"day(\d+)$", meta.parent.parent.name)
            st = meta.parent / "single_solve" / "start.json"
            if not dm or int(dm.group(1)) >= day or not st.exists():
                continue
            try:
                if json.loads(meta.read_text()).get("lane") != lane:
                    continue
            except (OSError, ValueError):
                continue
            size = st.stat().st_size
            break
        _BIG_START[(lane, day)] = size > START_VIA_HB_MAX_KB * 1024
    return _BIG_START[(lane, day)]
_EXEC_MARK = "HCTF-EXEC"
# Single Solve start / submit over the run's long-lived Homebase daemon (warm GM pool, one stdio channel) instead of an
# ssh exec + `python3 gm.py` per call: D12's five drop-time starts went out 2-6 s late on the busy 2-vCPU VM. Only in the
# orchestrator process (workers' `hctf submit` has no daemon -> the ssh path below). HCTF_GM_VIA_DAEMON=0 disables.
GM_VIA_DAEMON = os.environ.get("HCTF_GM_VIA_DAEMON", "1") != "0"
PUBLIC_GM = "https://2026.huntress.ctf.games"


def _public_gm():
    """Only when this process talks to the REAL public GM: a replay points HUNTRESS_GAME_MASTER_URL at its local
    stand-in, and its singles must be judged there, never re-routed to the real GM through Homebase."""
    return os.environ.get("HUNTRESS_GAME_MASTER_URL", PUBLIC_GM).rstrip("/") == PUBLIC_GM


_master_cache = {"t": 0.0, "ok": False}


def _master_alive(max_age=2.0):
    """True if the shared SSH ControlMaster to Homebase is up (a ~10 ms local socket check, never a cold connect:
    a submit must not wait 15 s on a dead tunnel). Cached max_age s: every probe submit ran its own `ssh -O check`
    subprocess (rehearsal fair D16: 12 parallel probes, sporadic 0.5-6 s before the GM call even started)."""
    if time.time() - _master_cache["t"] < max_age:
        return _master_cache["ok"]
    try:
        r = subprocess.run(["ssh", *SSH_OPTS, "-O", "check", f"{HB_USER}@{HB_HOST}"],
                           capture_output=True, text=True, timeout=3)
        ok = r.returncode == 0
    except (subprocess.SubprocessError, OSError):
        ok = False
    _master_cache.update(t=time.time(), ok=ok)
    return ok


def _gm_via_daemon(args, timeout):
    """start / submit through workers' running Homebase daemon; None = no daemon / it never took the request (the
    caller falls back). A submit the daemon may have sent without a verdict raises Unreachable (never a second POST)."""
    from . import workers   # lazy: workers imports remote
    d = workers._daemon.get("d")
    if d is None or not d.alive() or len(args) < 2:
        return None
    kind, kw = str(args[0]), {"kind": str(args[0]), "cid": str(args[1])}
    if kind == "submit":
        try:
            kw["answers"] = json.loads(args[2])
        except (IndexError, ValueError):
            return None
    t0 = time.time()
    try:
        res = d.call("gm", timeout=min(float(timeout), 60.0), **kw)
    except workers.DaemonError as e:
        msg = str(e)
        if kind == "submit" and not msg.startswith(("daemon not running", "daemon write failed")):
            raise Unreachable(f"submit via the Homebase daemon: outcome unknown ({msg[:200]}) -- check `hctf status` "
                              "before resubmitting") from None
        return None      # start is idempotent (it resumes the live attempt): the other transports are safe
    env = {k: res.get(k) for k in ("http", "body", "text", "saved", "content_type", "elapsed", "retries", "slept")}
    env["saved"] = env["saved"] or []
    env["transport"] = "hb-daemon"
    # client wall time vs the VM-measured `elapsed`: the gap is the ssh channel (D14 race submits sat ~3-4 s between
    # the local solve and the GM call while pre-pushes shared the ControlMaster -- unproven without this number)
    env["client_elapsed"] = round(time.time() - t0, 3)
    return env


def _gm_submit_hb(args, timeout, op="submit"):
    """ONE ssh exec of gm.py submit on Homebase -- deliberately NOT ssh() (it retries exit 255, and 255 also means a
    drop AFTER the command started: a retried submit is a second POST). The remote side prints a marker before gm.py
    runs, so: no marker + ssh failure -> the POST never left -> None (caller uses the public GM). Marker present and
    no envelope -> outcome unknown -> Unreachable (never a blind second POST; the worker re-checks and resubmits)."""
    cmd = (f"echo {_EXEC_MARK} >&2; HUNTRESS_GAME_MASTER_URL={INSIDE_GM} python3 ~/{HB_DIR}/gm.py "
           + " ".join(shlex.quote(str(a)) for a in args))
    try:
        with _slot():
            r = subprocess.run(["ssh", *SSH_OPTS, f"{HB_USER}@{HB_HOST}", cmd],
                               capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired as e:
        if _EXEC_MARK in str(e.stderr or ""):
            raise Unreachable(f"{op} via Homebase timed out after it started: outcome unknown -- "
                              "check `hctf status` before resubmitting") from None
        return None
    except OSError:
        return None
    if _EXEC_MARK not in (r.stderr or ""):
        return None                                   # never reached gm.py: safe to send it the public way
    if r.returncode == 2 and not (r.stdout or "").strip() and "can't open file" in (r.stderr or ""):
        # python3 could not even open ~/hctf/gm.py (fresh VM, before the base sync): nothing was POSTed. Rehearsal fair D12:
        # the warmups race's submit landed here 3 s before the sync and was misread as "outcome unknown".
        return None
    try:
        env = _gm_parse(r, f"ssh-{op}")
    except RuntimeError as e:                         # includes Unreachable (http 0 from the inside proxy)
        raise Unreachable(f"{op} via Homebase failed after it started (outcome unknown): {e}") from None
    env["transport"] = "homebase"
    return env


def rsync_from(remote_path, local_dir, own_conn=False):
    """Copy a remote directory's contents into local_dir. own_conn: use a separate SSH connection instead of the shared
    ControlMaster, so a multi-MB background pull can't stall the next clock-critical attempt (replay run 3: a 3.9 MB
    pull held mobile's Mastery retry for 24.6s)."""
    Path(local_dir).mkdir(parents=True, exist_ok=True)
    if ON_HOMEBASE:
        src = os.path.expanduser(remote_path).rstrip("/") + "/"
        subprocess.run(["rsync", "-a", src, str(local_dir).rstrip("/") + "/"], check=True, capture_output=True)
        return
    _rsync(["rsync", "-a", "-e", "SSH_OWN" if own_conn else "SSH", f"{HB_USER}@{HB_HOST}:{remote_path.rstrip('/')}/",
            str(local_dir).rstrip("/") + "/"])


def own_ssh_opts():
    """SSH_OPTS for a SEPARATE connection (no ControlMaster): parallel flows each get their own TCP window."""
    own = [o for o in SSH_OPTS if not o.startswith(("ControlMaster=", "ControlPath=", "ControlPersist="))]
    own = [o for i, o in enumerate(own) if not (o == "-o" and (i + 1 >= len(own) or own[i + 1] == "-o"))]
    return [*own, "-o", "ControlMaster=no", "-o", "ControlPath=none"]


# 10 parallel SSH connections: 12 measured 42 s for 31 MB, 6 took 61 s; 16 tripped sshd's MaxStartups (connection reset).
FETCH_STREAMS = int(os.environ.get("HCTF_FETCH_STREAMS", "10"))


def fetch_file(rel_path, local_path, size, streams=None, min_rate=40_000):
    """Copy ONE remote file (path relative to the remote home) as `streams` parallel byte ranges, each over its own SSH
    connection, then concatenate. The CTF VPN limits each TCP flow (~0.1-0.5 MB/s), not the link: 8 flows measured
    1.0-1.5 MB/s total (2026-10-08), so a 31 MB delivery takes ~25-35 s instead of 1-4 min. Raises on any failure."""
    from concurrent.futures import ThreadPoolExecutor
    streams = max(1, min(streams or FETCH_STREAMS, max(1, size // (1 << 20))))
    step = -(-size // streams)
    parts = [(i, i * step, min(step, size - i * step)) for i in range(streams) if i * step < size]
    local_path = Path(local_path)
    q = shlex.quote(rel_path)

    def one(part):
        i, off, n = part
        dst = local_path.with_name(f".{local_path.name}.part{i}")
        cmd = f"tail -c +{off + 1} {q} | head -c {n}"
        for attempt in range(3):   # sshd MaxStartups resets a burst of new connections: back off and retry the range
            if attempt:
                time.sleep(0.5 * attempt + 0.1 * i)
            with open(dst, "wb") as f:
                r = subprocess.run(["ssh", *own_ssh_opts(), f"{HB_USER}@{HB_HOST}", cmd], stdout=f,
                                   stderr=subprocess.PIPE, timeout=max(60, n / min_rate))
            if not r.returncode and dst.stat().st_size == n:
                return dst
        raise RuntimeError(f"range {i} ({off}+{n}) failed: rc {r.returncode} got {dst.stat().st_size} "
                           f"{r.stderr.decode(errors='replace')[-200:]}")
    try:
        with ThreadPoolExecutor(max_workers=len(parts)) as ex:
            chunks = list(ex.map(one, parts))
        with open(local_path, "wb") as out:
            for c in chunks:
                out.write(c.read_bytes())
    finally:
        for i, _, _ in parts:
            local_path.with_name(f".{local_path.name}.part{i}").unlink(missing_ok=True)
    return local_path


def rsync_to(local_path, remote_path, exclude=(), mkdir=None, compress=False):
    """mkdir: create this remote dir in the same round-trip (via --rsync-path) instead of a separate ssh mkdir.
    compress: -z (JSON contracts shrink ~15x; the VPN moves ~140 KB/s)."""
    argv = ["rsync", "-a", *(["-z"] if compress else []), "--delete", "-e", "SSH", *[f"--exclude={x}" for x in exclude]]
    if mkdir:
        argv.append(f"--rsync-path=mkdir -p {mkdir} && rsync")
    _rsync([*argv, str(local_path), f"{HB_USER}@{HB_HOST}:{remote_path}"])


RSYNC_TIMEOUT = int(os.environ.get("HCTF_RSYNC_TIMEOUT", "600"))


def tar_push(local_dir, remote_dir, exclude=("cases", "__pycache__")):
    """Replace remote_dir (relative to the remote home) with local_dir's contents in ONE ssh round trip: tar | ssh tar
    into a sibling, then swap. A no-change rsync of a solver dir took 1.84 s over the VPN (several protocol round
    trips); this ~0.75 s. For small trees only (the solver minus cases/); the caller falls back to rsync on failure."""
    tar = subprocess.Popen(["tar", "czf", "-", *[f"--exclude={x}" for x in exclude], "-C", str(local_dir), "."],
                           stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    d = f"~/{remote_dir.lstrip('~/')}" if not remote_dir.startswith("~") else remote_dir
    cmd = (f"d={d}; rm -rf \"$d.new\" && mkdir -p \"$d.new\" && tar xzf - -C \"$d.new\" && rm -rf \"$d\" "
           f"&& mv \"$d.new\" \"$d\" && echo TAR-OK")
    try:
        with _slot():
            r = subprocess.run(["ssh", *SSH_OPTS, f"{HB_USER}@{HB_HOST}", cmd], stdin=tar.stdout,
                               capture_output=True, text=True, timeout=60)
    finally:
        tar.stdout.close()
        tar.wait()
    if "TAR-OK" not in r.stdout:
        raise RuntimeError(f"tar push failed: {(r.stderr or r.stdout)[-200:]}")


def _rsync(argv):
    """rsync over the shared ssh options; on ssh failure (exit 255, usually a stale ControlMaster socket left by a
    killed session) clear the sockets and retry once instead of crashing the caller."""
    own = [o for o in SSH_OPTS if not o.startswith(("ControlMaster=", "ControlPath=", "ControlPersist="))]
    own = [o for i, o in enumerate(own) if not (o == "-o" and (i + 1 >= len(own) or own[i + 1] == "-o"))]
    argv = [("ssh " + " ".join(shlex.quote(o) for o in SSH_OPTS)) if a == "SSH" else
            ("ssh " + " ".join(shlex.quote(o) for o in [*own, "-o", "ControlMaster=no", "-o", "ControlPath=none"]))
            if a == "SSH_OWN" else a for a in argv]
    for attempt in range(1, SSH_RETRIES + 1):
        with _slot():
            r = subprocess.run(argv, capture_output=True, timeout=RSYNC_TIMEOUT)
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
