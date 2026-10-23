#!/usr/bin/env python3
"""Web solver for Uploading Expectations (unrestricted upload -> server-side template preview), on top of the generic
web LANE SEED (lib.web). One solver serves single / time_trial / every Mastery target.

    solve.py --contract <contract.json> --artifacts <dir>   ->  {answer_id: proof} JSON on the last line

Per target: GET /api/clues once. An upload-class clue set (`upload_shape` / `upload_policy` keys) goes straight to
`upload()` (2 requests); anything else (compounded earlier-day Mastery targets) falls back to lib.web.solve_target.
Targets run in parallel. `answer()` is exposed (upload class only, no lib.web call -> no recursion) so later days'
generic solver races it on compounded targets."""
import json
import re
import sys
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from lib import solverrt, web, websolve  # noqa: E402

# (filename, content_type) ladder: the "bouncer" only polices one of the two in every variant seen so far.
_UPLOADS = [("note.html", "text/html"), ("note.html", "text/plain"), ("note.txt.html", "text/plain"),
            ("note.htm", "text/html"), ("note.html.txt", "text/html"), ("note.svg", "image/svg+xml")]


def _is_upload(cl):
    return any(re.search(r"upload", k, re.I) for k in cl)


def _route(cl, *pats):
    for p in pats:
        for k, v in cl.items():
            if re.search(p, k, re.I) and isinstance(v, str) and v.startswith("/"):
                return v
    return None


def _payload(base, cl, read_guide=True):
    """Template expression for the objective field, spelled from the preview guide (`{{author}}` -> `{{objective}}`);
    falls back to the common engines' syntaxes. read_guide=False: defaults only (saves a round trip)."""
    field, toks = "objective", []
    guide = _route(cl, r"guide|doc|help") if read_guide else None
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


def upload(base, cl):
    """Upload an HTML note carrying the template field, then open the preview link the server returns."""
    post = _route(cl, r"feature|upload_route|submit|action")
    render = _route(cl, r"render|preview_route|view|serve")
    if not post:
        return None
    shape = str(cl.get("upload_shape", ""))
    first = _payload(base, cl, read_guide=False)
    return _upload(base, post, render, shape, first, _UPLOADS[:1]) \
        or _upload(base, post, render, shape, _payload(base, cl), _UPLOADS)


def _upload(base, post, render, shape, content, ladder):
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
        links = [v for v in (j.values() if isinstance(j, dict) else []) if isinstance(v, str) and v.startswith(("/", "http"))]
        if not links and render and 200 <= st < 300:
            links = [f"{render}?{urllib.parse.urlencode({'file': fn})}"]
        for link in links:
            p = websolve.proof(websolve.fetch(urllib.parse.urljoin(base, link))[1])
            if p:
                return p
    return None


def answer(_dir, question, _art, contract):
    """Upload-class proof for one target, else None (raced by later days' generic solver; never calls lib.web)."""
    base = websolve.base_of(question, contract)
    if not base:
        return None
    cl, _ = websolve.clues(base)
    return upload(base, cl) if _is_upload(cl) else None


def solve_target(question, contract):
    base = websolve.base_of(question, contract)
    if not base:
        return None
    cl, key = websolve.clues(base)
    if _is_upload(cl):
        p = upload(base, cl)
        if p:
            return p
    # earlier-day class (compounded Mastery): lib.web's race, reusing this clues fetch
    return websolve.race(web.candidates(base, cl, key, question, contract))


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--contract", required=True)
    ap.add_argument("--artifacts", required=False)
    a = ap.parse_args()
    contract = json.loads(Path(a.contract).read_text())
    out, pool = {}, []
    solverrt.arm_deadline(out, pool)

    from concurrent.futures import ThreadPoolExecutor, as_completed
    jobs = web._iter_pairs(contract)
    # targets are I/O bound: threads, merged into `out` as each finishes (the deadline watchdog emits partials)
    ex = ThreadPoolExecutor(max_workers=max(1, len(jobs)))
    futs = {ex.submit(solve_target, q, contract): aid for aid, q in jobs}
    for f in as_completed(futs):
        try:
            if f.result():
                out[futs[f]] = f.result()
        except Exception as e:  # noqa: BLE001 - one bad target must not sink the others
            print(f"target failed: {e!r}", file=sys.stderr)
    solverrt.emit_and_exit(out, pool)


if __name__ == "__main__":
    main()
