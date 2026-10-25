"""D24 #12 MSS-clamping SSH ProxyCommand (hctf/mssproxy.py), offline: loopback servers only, no Homebase.
- relays both directions byte-exact, the connection's MSS is clamped (the server side sees <= 1100), TCP_NODELAY set
- a refused connect exits 255 (ssh's failure code: callers' exit-255 handling -> Unreachable -> local is unchanged)
- remote.SSH_OPTS carries the ProxyCommand by default (HCTF_SSH_MSS=1100); HCTF_SSH_MSS=0 / empty = today's options
- rsync's -e string keeps the ProxyCommand as one option; own_ssh_opts() keeps it
- remote.sshd_answers(): banner seen = sshd up (the health loop's "handshake doesn't (MTU?)" hint)

Run:  source bin/env.sh && python3 tests/test_mssproxy.py      (exit 0 = all pass)
"""
import os
import shlex
import socket
import subprocess
import sys
import threading
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from hctf import mssproxy, remote  # noqa: E402

failures = []


def check(name, cond, detail=""):
    print(("ok  " if cond else "FAIL ") + name + ("" if cond else f"  -- {detail}"))
    if not cond:
        failures.append(name)


def server(handler):
    srv = socket.socket()
    srv.bind(("127.0.0.1", 0))
    srv.listen(1)

    def run():
        c, _ = srv.accept()
        try:
            handler(c)
        finally:
            c.close()
            srv.close()
    threading.Thread(target=run, daemon=True).start()
    return srv.getsockname()[1]


seen = {}


def echo(c):
    seen["mss"] = c.getsockopt(socket.IPPROTO_TCP, socket.TCP_MAXSEG)
    buf = b""
    while len(buf) < 200000:
        d = c.recv(65536)
        if not d:
            break
        buf += d
    c.sendall(b"SSH-2.0-fake\r\n" + buf[::-1])


port = server(echo)
payload = os.urandom(200000)
argv = shlex.split(mssproxy.proxy_command(1100).replace("%h", "127.0.0.1").replace("%p", str(port)))
p = subprocess.run(argv, input=payload, capture_output=True, timeout=20)
check("1 relays both ways byte-exact (200 kB each way) and exits 0 when the server closes",
      p.returncode == 0 and p.stdout == b"SSH-2.0-fake\r\n" + payload[::-1], (p.returncode, len(p.stdout), p.stderr[-200:]))
check("1 the connection's MSS is clamped (server side sees <= 1100)", 0 < seen.get("mss", 0) <= 1100, seen)

s = mssproxy.connect("127.0.0.1", server(lambda c: c.recv(1)), 1100)
check("1 TCP_NODELAY + TCP_MAXSEG set on the socket",
      s.getsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY) == 1
      and s.getsockopt(socket.IPPROTO_TCP, socket.TCP_MAXSEG) <= 1100)
s.close()

dead = socket.socket()
dead.bind(("127.0.0.1", 0))
dport = dead.getsockname()[1]
dead.close()   # nothing listens there now
p = subprocess.run([*argv[:-3], "127.0.0.1", str(dport), "1100"], capture_output=True, timeout=20)
check("2 a refused connect exits 255 (ssh's own failure code)", p.returncode == 255, (p.returncode, p.stderr))
p = subprocess.run(argv[:-3], capture_output=True, timeout=20)
check("2 bad usage exits 255", p.returncode == 255)

opts = remote.SSH_OPTS
pc = [opts[i + 1] for i, o in enumerate(opts) if o == "-o" and opts[i + 1].startswith("ProxyCommand=")]
check("3 default HCTF_SSH_MSS=1100: SSH_OPTS has the MSS ProxyCommand",
      len(pc) == 1 and "mssproxy.py %h %p 1100" in pc[0] and " -S " in pc[0], pc)
for v in ("0", ""):
    out = subprocess.run([sys.executable, "-c", "from hctf import remote; print(repr(remote.SSH_OPTS))"],
                         capture_output=True, text=True, cwd=str(ROOT), env={**os.environ, "HCTF_SSH_MSS": v}).stdout
    check(f"3 HCTF_SSH_MSS={v!r}: no ProxyCommand (today's options)", "ProxyCommand" not in out and "ControlPersist=600" in out,
          out[-200:])
check("3 proxy_command(0 / '' / junk) = None", mssproxy.proxy_command(0) is None and mssproxy.proxy_command("") is None
      and mssproxy.proxy_command("x") is None)
own = remote.own_ssh_opts()
check("3 own_ssh_opts() (separate connections) keeps the ProxyCommand", any(o.startswith("ProxyCommand=") for o in own))
e = "ssh " + " ".join(shlex.quote(o) for o in remote.SSH_OPTS)   # what _rsync hands rsync -e
check("3 rsync's -e string keeps the ProxyCommand as ONE argument",
      sum(a.startswith("ProxyCommand=") and a.endswith("%h %p 1100") for a in shlex.split(e)) == 1)

bport = server(lambda c: c.sendall(b"SSH-2.0-OpenSSH_9.6\r\n"))
check("4 sshd_answers(): a banner = sshd is up", remote.sshd_answers(2, host="127.0.0.1", port=bport))
check("4 sshd_answers(): nothing listening = False", not remote.sshd_answers(1, host="127.0.0.1", port=dport))
src = (ROOT / "hctf" / "workers.py").read_text()
check("4 the health loop logs the MTU hint when the probe fails but sshd answers",
      "sshd answers, handshake doesn't (MTU?" in src and "remote.sshd_answers()" in src)

print(f"\n{len(failures)} failure(s)" + (": " + ", ".join(failures) if failures else ""))
sys.exit(1 if failures else 0)
