"""MSS-clamping TCP relay for ssh's ProxyCommand: fixes the Homebase PMTUD blackhole without root.

The VPN path to the VM carries ~1200-byte packets while tun0 says 1500 and the ICMP "frag needed" is filtered, so the
SSH key exchange (post-quantum KEX: large packets) vanishes and every Homebase call hangs at the handshake (memory
homebase-mtu-pmtud, 2026-10-21/25). The root fix is `ip link set tun0 mtu 1200`, lost on every VPN reconnect. Clamping
this one socket's MSS (TCP_MAXSEG before connect: our SYN advertises it, so the VM's segments are small too) does the
same for SSH only, from user space.

    ssh -o ProxyCommand='python3 -S hctf/mssproxy.py %h %p 1100' ...

stdin -> socket, socket -> stdout until either side closes. Exit 255 when the connection can't be made (ssh's own
"connection failed" code: the callers' exit-255 handling -- clear sockets, retry, then `Unreachable` -> local -- is
unchanged). Stdlib only, no site import (-S): it starts in ~20 ms.
"""
import os
import select
import socket
import sys

CONNECT_TIMEOUT = float(os.environ.get("HCTF_SSH_MSS_CONNECT_S", "15"))   # = SSH_OPTS ConnectTimeout
BUF = 65536


def connect(host, port, mss, timeout=CONNECT_TIMEOUT):
    """A connected socket with TCP_MAXSEG=mss (set before connect: it goes into the SYN) and TCP_NODELAY."""
    err = None
    for fam, typ, proto, _, addr in socket.getaddrinfo(host, port, 0, socket.SOCK_STREAM):
        s = socket.socket(fam, typ, proto)
        try:
            if mss:
                s.setsockopt(socket.IPPROTO_TCP, socket.TCP_MAXSEG, int(mss))
            s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            s.settimeout(timeout)
            s.connect(addr)
            s.settimeout(None)
            return s
        except OSError as e:
            err = e
            s.close()
    raise err or OSError(f"no address for {host}")


def pump(s, fin=0, fout=1):
    """Relay until EOF on the socket (the session is over) -- stdin EOF only half-closes the socket's send side."""
    open_in = True
    while True:
        rl = [s] + ([fin] if open_in else [])
        r, _, _ = select.select(rl, [], [])
        if s in r:
            data = s.recv(BUF)
            if not data:
                return 0
            view = memoryview(data)
            while view:
                n = os.write(fout, view)
                view = view[n:]
        if open_in and fin in r:
            data = os.read(fin, BUF)
            if not data:
                open_in = False
                try:
                    s.shutdown(socket.SHUT_WR)
                except OSError:
                    return 0
            else:
                s.sendall(data)


def main(argv):
    if len(argv) < 2:
        sys.stderr.write("usage: mssproxy.py HOST PORT [MSS]\n")
        return 255
    host, port = argv[0], int(argv[1])
    mss = int(argv[2]) if len(argv) > 2 and argv[2] not in ("", "0") else 0
    try:
        s = connect(host, port, mss)
    except OSError as e:
        sys.stderr.write(f"mssproxy: connect {host}:{port} failed: {e}\n")
        return 255
    try:
        return pump(s)
    except (OSError, ValueError) as e:   # reset mid-session: ssh sees the pipe close and reports it itself
        sys.stderr.write(f"mssproxy: {e}\n")
        return 255
    finally:
        s.close()


def proxy_command(mss):
    """The ProxyCommand value for SSH_OPTS (`%h %p` expanded by ssh), or None when the clamp is off (mss 0/empty)."""
    try:
        mss = int(mss or 0)
    except ValueError:
        return None
    if mss <= 0:
        return None
    py = "/usr/bin/python3" if os.path.exists("/usr/bin/python3") else (sys.executable or "python3")
    here = os.path.abspath(__file__)
    import shlex
    return f"{shlex.quote(py)} -S {shlex.quote(here)} %h %p {mss}"


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
