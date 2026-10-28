"""D28 web track, offline: post-mortem items 7 (clue-less LFI in the first pass), 8 (MISS-RETRY only for not-ready
targets), 10 (plugin hot reload) and the web part of 14 (one regression per earlier web class). Fakes only -- every
request goes to a 127.0.0.1 mock app (a socket-level guard fails any other host); no GM, no live target.

Day 28: both web Masteries missed `proof-4`. Target 4 was the compounded Day-20 "Stay in Your Directory" PHP viewer
(lane-day 04): `/` 302 -> `/reader.php` (fail-open) or `/notes.php` (breach), runbook links `?doc=<page>.php`, NO
/api/clues; the proof is /run/huntress/objective.txt, read through `?doc=../../../../../../run/huntress/objective.txt`.
lib.web raced it as an unknown class (12 s cap): the day-20 prior keyed on a path the (other challenge's) prompt never
named, and the `default` ladder dropped `?doc=` links -> timed out; MISS-RETRY then re-raced the live target 3x (~45 s).
The mock apps below are rebuilt from the D28 worker logs (challenges/day28/web-*/mastery/worker-live-*.log: the exact
HTML, the PHP include warning with its base dir, the request that returned the proof).

Run:  source bin/env.sh && python3 tests/test_d28_web.py      (exit 0 = all pass)
"""
import contextlib
import http.server
import json
import os
import posixpath
import socket
import sys
import tempfile
import threading
import time
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
_TMP = Path(tempfile.mkdtemp(prefix="test_d28_web-"))
os.environ["HCTF_WEB_RACE_LOG"] = str(_TMP / "web_race.jsonl")     # never the live .run/web_race.jsonl
os.environ.pop("HCTF_SOLVE_DEADLINE", None)

# ---- offline guard: only loopback resolves --------------------------------------------------------------------------
_real_gai = socket.getaddrinfo
offnet = []


def _guard_gai(host, *a, **k):
    if str(host) not in ("127.0.0.1", "localhost", "::1"):
        offnet.append(str(host))
        raise socket.gaierror(f"test_d28_web: offline -- {host} is not a local mock")
    return _real_gai(host, *a, **k)


socket.getaddrinfo = _guard_gai

from lib import websolve  # noqa: E402
import lib.web as libweb  # noqa: E402
from lib.web import handlers as webhandlers  # noqa: E402

failures = []
FIRST_PASS_S = 15.0      # D28 post-mortem verification: proof-4 in the first pass, under 15 s
WELL_UNDER_S = 5.0       # what the fixed routing actually needs (a few requests at LATENCY)
# per-request latency of the viewer mocks: D28 live Cloudflare round trips were ~0.1-0.2 s, which is what turned the
# old ~100-request ladder into a 12 s timeout (on bare loopback it finishes in 0.2 s and the bug is invisible)
LATENCY = 0.12


def check(name, cond, detail=""):
    print(("ok  " if cond else "FAIL ") + name + ("" if cond else f"  -- {detail}"))
    if not cond:
        failures.append(name)


@contextlib.contextmanager
def patched(pairs):
    saved = {k: getattr(*k) for k in pairs}
    try:
        for (obj, name), v in pairs.items():
            setattr(obj, name, v)
        yield
    finally:
        for (obj, name), v in saved.items():
            setattr(obj, name, v)


def race_log():
    p = Path(os.environ["HCTF_WEB_RACE_LOG"])
    return [json.loads(x) for x in p.read_text().splitlines()] if p.exists() else []


# ---- mock apps ------------------------------------------------------------------------------------------------------
class App:
    """A tiny threaded HTTP app: route(method, path, query{k: [v]}, body bytes, headers) -> (status, ctype, body[,
    extra headers]). Counts requests per path."""

    def __init__(self, route, latency=0.0):
        self.route, self.hits, self.lock = route, [], threading.Lock()
        app = self

        class H(http.server.BaseHTTPRequestHandler):
            def log_message(self, *a):
                pass

            def _do(self):
                u = urllib.parse.urlsplit(self.path)
                n = int(self.headers.get("Content-Length") or 0)
                body = self.rfile.read(n) if n else b""
                with app.lock:
                    app.hits.append((self.command, self.path))
                if latency:
                    time.sleep(latency)     # a live target's round trip (loopback hides a 100-request ladder)
                # PHP decodes the query string once (a raw `%2f` arrives as `/`)
                q = urllib.parse.parse_qs(u.query, keep_blank_values=True)
                r = app.route(self.command, u.path, q, body, self.headers) or NOT_FOUND
                st, ct, out = r[:3]
                extra = r[3] if len(r) > 3 else {}
                data = out.encode() if isinstance(out, str) else out
                try:
                    self.send_response(st)
                    self.send_header("Content-Type", ct)
                    self.send_header("Content-Length", str(len(data)))
                    for k, v in extra.items():
                        self.send_header(k, v)
                    self.end_headers()
                    self.wfile.write(data)
                except (BrokenPipeError, ConnectionResetError):
                    pass

            do_GET = do_POST = do_PUT = do_HEAD = _do

        self.srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), H)
        self.srv.daemon_threads = True
        threading.Thread(target=self.srv.serve_forever, daemon=True).start()
        self.url = f"http://127.0.0.1:{self.srv.server_address[1]}/"

    def close(self):
        self.srv.shutdown()
        self.srv.server_close()


NOT_FOUND = (404, "text/plain", "not found")
TEXT = "text/html; charset=UTF-8"

# The D28 fail-open Target 4 page, verbatim from worker-live-local-20261028T210340.log (`{page}`/`{docs}`/`{body}` filled).
VIEWER_HTML = (
    '<!doctype html>\n<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,'
    'initial-scale=1"><title>Stay in Your Directory</title><link rel="stylesheet" href="/style.css"><style>:root{{'
    '--accent:#2b8a3e;--accent-soft:#e7f5e9;--ink:#15281a;--canvas:#f6fbf7}}</style></head>\n<body class="layout-split_'
    'hero"><nav class="nav"><a class="brand" href="/{page}"><span class="brand-mark">R</span>Stay in Your Directory</a>'
    '<span class="nav-note">Please return runbooks to their proper directory.</span></nav><main class="shell"><section '
    'class="hero"><div><div class="eyebrow">Pocket operations handbook</div><h1>Stay in Your Directory</h1><p>A '
    'lightweight runbook reader for people who absolutely stay in the approved folder.</p></div><img src="/hero.svg" '
    'alt="Illustrated filing cabinet"></section><section class="grid two"><aside class="card"><h2>Runbooks</h2>{docs}'
    '</aside><article class="card"><span class="pill">Document viewer</span>{body}</article></section><div class="'
    'footer">Plain PHP, real Apache, aggressively organized paperwork.</div></main></body></html>')
RUNBOOK = ('<div class="eyebrow">Runbook page</div>\n<h2>{title}</h2>\n<p>Begin with the normal user story.</p>\n'
           '<div class="alert">Nothing secret here. Just good incident habits.</div>\n')
WARN = ("<br />\n<b>Warning</b>:  include({path}): Failed to open stream: No such file or directory in <b>/var/www/html/"
        "index.php</b> on line <b>51</b><br />\n")
OBJECTIVE = "/run/huntress/objective.txt"


def viewer_app(proof, page="reader.php", docs=("start.php", "collect.php", "report.php"),
               base_dir="/var/www/html/pages/", strip_dotdot=False, files=None):
    """The lane-day 04 PHP viewer: `include(base_dir . $_GET['doc'])` (realpath-style normalisation, clamped at /).
    strip_dotdot: a non-recursive str_replace('../', '') filter (needs `....//`). files: extra readable abs paths."""
    fs = {OBJECTIVE: proof + "\n", "/etc/passwd": "root:x:0:0:root:/root:/bin/bash\n",
          "/etc/hostname": "3fbf7bbf-8b51-4af9-a8dd-ec967203e63c"}
    fs.update(files or {})
    links = "".join(f'<div class="record"><div><strong>{d}</strong></div><a class="button secondary" '
                    f'href="/{page}?doc={d}">Read</a></div>' for d in docs)

    def route(method, path, q, body, headers):
        if path == "/":
            return 302, TEXT, "", {"Location": f"/{page}"}
        if path == f"/{page}":
            doc = (q.get("doc") or [docs[0]])[0]
            if strip_dotdot:
                doc = doc.replace("../", "")
            full = doc if doc.startswith("/") else base_dir + doc
            real = posixpath.normpath(full)
            if real in fs:
                art = fs[real]
            elif posixpath.dirname(real) + "/" == base_dir and posixpath.basename(real) in docs:
                art = RUNBOOK.format(title=posixpath.basename(real))
            else:
                art = WARN.format(path=full)
            return 200, TEXT, VIEWER_HTML.format(page=page, docs=links, body=art)
        if path in ("/style.css", "/hero.svg"):
            return 200, "text/css", "/* static */"
        if path == "/robots.txt":
            return 200, "text/plain", "# As a condition of accessing this website, you agree to the content signals\n"
        return NOT_FOUND
    return route


def contract_for(url, prompt, n=1, mode="mastery"):
    return {"mode": mode, "prompt": prompt, "answer_ids": [f"proof-{i}" for i in range(1, n + 1)],
            "questions": [{"id": f"proof-{i}", "question": f"Recover the proof from Target {i}.",
                           "artifact": f"Target {i}", "set": i} for i in range(1, n + 1)],
            "targets": [{"id": f"Target {i}", "url": url} for i in range(1, n + 1)]}


def saved_case(rel):
    """A saved D28 Mastery case's contract (read-only -- case artifacts are hardlinked to another account)."""
    return json.loads((ROOT / rel / "contract.json").read_text())


def with_target(contract, tid, url):
    c = json.loads(json.dumps(contract))
    for t in c.get("targets") or []:
        if t.get("id") == tid:
            t["url"] = url
    return c


def q_of(contract, qid):
    return next(q for q in contract["questions"] if q["id"] == qid)


def timed(fn, *a, **k):
    t0 = time.time()
    v = fn(*a, **k)
    return v, time.time() - t0


FAIL_OPEN = "challenges/day28/web-fail-open-friday/solver/cases/auto-mastery-d08c1077"
BREACH = "challenges/day28/web-if-a-breach-falls-in-a-log/solver/cases/auto-mastery-350e8802"
P4 = "proof_be1375b2252c4ac2a3aa26d71812652c"       # the proof the D28 fail-open live worker read on Target 4
P4B = "proof_db5f705111664d19bebb3187bf49581a"      # ... and the breach one

# ================================================================ item 7: clue-less LFI routes in the FIRST pass
reader = App(viewer_app(P4), LATENCY)
notes = App(viewer_app(P4B, page="notes.php", docs=("welcome.php", "triage.php", "contacts.php"),
                       base_dir="/var/www/html/app/runbooks/pages/"), LATENCY)
filtered = App(viewer_app("proof_ffffeeee11112222", strip_dotdot=True), LATENCY)
try:
    home = websolve.fetch(reader.url)[1]
    fp = webhandlers.lfi_fingerprint(home)
    check("fingerprint: the D28 Target-4 page (no /api/clues) is the lane-day 04 viewer",
          ("/reader.php", "doc", "start.php") in fp, fp)
    check("fingerprint: nothing on a plain kit page / a search form (q is not a file parameter)",
          webhandlers.lfi_fingerprint('<a href="/api/clues">notes</a><form action="/search"><input name="q"></form>'
                                      '<a href="/notes/2">n</a><a href="/list?sort=asc">l</a>') == [])
    check("fingerprint generalizes beyond `doc` (file / page / template / view links, a bare viewer page)",
          all(webhandlers.lfi_fingerprint(h) for h in (
              '<a href="/show?file=a.txt">', '<a href="/index.php?page=about">', '<a href="/r?template=x.tpl">',
              '<a href="/v?view=home">', '<a href="/read.php">read</a>')))
    check("_routes keeps the path of a query-bearing link (it dropped every `?doc=` link)",
          "/reader.php" in webhandlers._routes({}, reader.url, home), webhandlers._routes({}, reader.url, home))
    check("_query_links: one (path, param) per viewer link, in page order",
          webhandlers._query_links(home) == [("/reader.php", "doc", "start.php")], webhandlers._query_links(home))

    # (a) the day-20 prior on its own, with the compounding challenge's prompt (names no path)
    c = with_target(saved_case(FAIL_OPEN), "Target 4", reader.url)
    day20 = dict(libweb._prior_web_solvers()).get("day20/web-stay-in-your-directory")
    check("day-20 prior solver is loaded as a prior", day20 is not None)
    n0 = len(reader.hits)
    v, dt = timed(day20.answer, "proof-4", q_of(c, "proof-4"), None, c)
    check("(a) day-20 lfi() reads /run/huntress/objective.txt with a prompt that names no path", v == P4, v)
    check("(a) ... and puts lfi first on a `?doc=` viewer page (few requests, not SQLi/backup first)",
          len(reader.hits) - n0 <= 6, reader.hits[n0:])
    for app, want, what in ((notes, P4B, "a deeper include base (breach's notes.php)"),
                            (filtered, "proof_ffffeeee11112222", "a non-recursive `../` strip (needs `....//`)")):
        cc = contract_for(app.url, saved_case(FAIL_OPEN)["prompt"])
        v = day20.answer("proof-1", cc["questions"][0], None, cc)
        check(f"(a) day-20 lfi() handles {what}", v == want, v)

    # (b) the default ladder alone: the param-bearing route with its own payloads FIRST
    n0 = len(reader.hits)
    v, dt = timed(webhandlers.default, reader.url, {})
    check("(b) default ladder reads the proof through the viewer link's own `doc` param", v == P4, v)
    check("(b) ... within a handful of requests (was ~100 sequential probes)", len(reader.hits) - n0 <= 6,
          len(reader.hits) - n0)
    v = webhandlers.default(filtered.url, {})
    check("(b) default ladder: filter bypass on the viewer link", v == "proof_ffffeeee11112222", v)

    # (c) end to end through solve_target on the SAVED D28 Mastery cases' contracts (Target 4 -> the mock)
    for rel, app, want in ((FAIL_OPEN, reader, P4), (BREACH, notes, P4B)):
        c = with_target(saved_case(rel), "Target 4", app.url)
        nlog = len(race_log())
        v, dt = timed(libweb.solve_target, q_of(c, "proof-4"), c)
        rec = (race_log()[nlog:] or [{}])[-1]
        name = rel.split("/")[2]
        check(f"(c) {name}: proof-4 found in the first pass", v == want, v)
        check(f"(c) {name}: under {FIRST_PASS_S:.0f} s, well under ({dt:.2f} s < {WELL_UNDER_S:g} s at "
              f"{LATENCY:g} s/request)", dt < min(FIRST_PASS_S, WELL_UNDER_S), dt)
        check(f"(c) {name}: fingerprinted as the known LFI class (not the {libweb.UNKNOWN_KEY_BUDGET:g} s unknown cap)",
              rec.get("known") is True and rec.get("fp") == "lfi" and rec.get("budget") == libweb.KNOWN_BUDGET, rec)
        check(f"(c) {name}: did not time out", rec.get("timed_out") is False, rec)

    # the race order: the traversal probe first; HCTF_WEB_CLUELESS_LFI=0 restores the old routing
    names = [n for n, _f in libweb.candidates(reader.url, {}, None, home=home)]
    check("(c) candidates() races the `lfi` probe first on a fingerprinted page", names[:2] == ["lfi", "default"], names)
    with patched({(libweb, "CLUELESS_LFI"): False}):
        names = [n for n, _f in libweb.candidates(reader.url, {}, None, home=home)]
        check("(c) CLUELESS_LFI off -> no lfi probe (old routing)", "lfi" not in names, names)

    # whole Mastery solve (forked per target, the real run_sets) on a 5-target contract: 4 viewers + the D28 page
    c = saved_case(FAIL_OPEN)
    for t in c["targets"]:
        t["url"] = reader.url
    nlog = len(race_log())
    out, dt = timed(libweb.solve, c)
    check("(c) lib.web.solve: all 5 targets of the case contract answered in one pass",
          all(out.get(f"proof-{i}") == P4 for i in range(1, 6)), out)
    check("(c) lib.web.solve: no miss-retry pass needed", not any("miss_retry" in r for r in race_log()[nlog:]))
    check(f"(c) lib.web.solve: under {FIRST_PASS_S:.0f} s, well under ({dt:.2f} s < {WELL_UNDER_S:g} s)",
          dt < min(FIRST_PASS_S, WELL_UNDER_S), dt)
finally:
    for a in (reader, notes, filtered):
        a.close()

# ================================================================ item 14 (web): one regression per earlier web class
# Each class gets a mock rebuilt from its solver / plugin docstring and the D28 fail-open prompt (a compounded target
# carries another challenge's prompt). Lane-day 04 (clue-less LFI) is above; here 05 (admin bypass, unprotected
# feature route), 13 (mass assignment, Posted Too Much) and 16 (command injection, Shell Company) -- the three that
# never won a race on record.
PROMPT = saved_case(FAIL_OPEN)["prompt"]


def kit(clues, extra):
    def route(method, path, q, body, headers):
        if path == "/api/clues":
            return 200, "application/json", json.dumps(clues)
        if path == "/":
            return 200, TEXT, '<a href="/api/clues">Open workspace notes</a>'
        r = extra(method, path, q, body, headers)
        return r or NOT_FOUND
    return route


def admin_route(method, path, q, body, headers):
    if path == "/dispatch-fa3df6":
        return 200, "application/json", json.dumps({"ok": True, "effect": "framework_authorization_bypassed",
                                                    "evidence": "proof_0505aaaabbbbcccc"})


_bound = {}


def dto_route(method, path, q, body, headers):
    if path == "/api/profile":
        if method != "POST":
            return 405, "application/json", '{"error":"post_required"}'
        try:
            _bound.update(json.loads(body or b"{}"))
        except ValueError:
            pass
        return 200, "application/json", json.dumps({"ok": True, "display_name": _bound.get("display_name")})
    if path == "/api/admin/report":
        if _bound.get("role") in ("admin", "administrator") or _bound.get("is_admin") is True:
            return 200, "application/json", json.dumps({"effect": "bound_privileged_property",
                                                        "evidence": "proof_1313aaaabbbbcccc"})
        return 403, "application/json", '{"error":"administrator_required"}'


def shell_route(method, path, q, body, headers):
    if path == "/api/worker":
        p = (q.get("path") or [""])[0]
        if not p:
            return 400, "application/json", '{"error":"path_required","example_path":"/app/static"}'
        out = f"drwxr-xr-x 2 app app 4096 Oct 25 13:00 {p.split(';')[0]}\n"
        if "cat /run/huntress/objective.txt" in p or "cat /run/huntress/*" in p:
            out += "proof_1616aaaabbbbcccc\n"
        return 200, "application/json", json.dumps({"ok": True, "effect": "worker_command_completed", "stdout": out})


CLASSES = [
    ("lane-day 05 admin bypass (Administratively Speaking)",
     {"framework": "Django", "feature_route": "/dispatch-fa3df6", "current_role": "analyst"}, admin_route,
     "proof_0505aaaabbbbcccc"),
    ("lane-day 13 mass assignment (Posted Too Much)",
     {"framework": "ASP.NET Core", "feature_route": "/api/profile", "secondary_route": "/api/admin/report",
      "current_role": "user"}, dto_route, "proof_1313aaaabbbbcccc"),
    ("lane-day 16 command injection (Shell Company)",
     {"current_role": "worker", "example_path": "/app/static", "feature_route": "/api/worker", "framework": "Gin",
      "input_parameter": "path"}, shell_route, "proof_1616aaaabbbbcccc"),
]
for name, clues, extra, want in CLASSES:
    app = App(kit(clues, extra))
    try:
        c = contract_for(app.url, PROMPT)
        v, dt = timed(libweb.solve_target, c["questions"][0], c)
        check(f"regression {name}: first pass", v == want, v)
        check(f"regression {name}: under {FIRST_PASS_S:.0f} s ({dt:.2f} s)", dt < FIRST_PASS_S, dt)
    finally:
        app.close()

# ================================================================ item 8: MISS-RETRY skips a live, timed-out target


def miss_retry(state_for, live=False, gen_bump=False):
    """_solve_into with solve_target stubbed: proof-1 solves; proof-2 misses the first pass (recording `state_for`
    as its readiness), solves on any retry. Returns (out, calls)."""
    calls = {}

    def fake_solve_target(q, contract):
        aid = q.get("id")
        calls[aid] = calls.get(aid, 0) + 1
        if aid == "proof-1":
            return "proof_aaaaaaaa"
        if calls[aid] >= 2:
            return "proof_bbbbbbbb"
        if state_for is not None:
            libweb._note_state(**state_for)
        if gen_bump:
            webhandlers.GENERATION += 1      # a plugin landed between the pass and the retry
        return None

    def fake_run_sets(jobs, fn, out, pool, io_bound=True):
        for job in jobs:
            out.update(fn(job))

    contract = contract_for("https://t.invalid/", PROMPT, n=2)
    os.environ["HCTF_SOLVE_DEADLINE"] = str(time.time() + 30)
    try:
        with patched({(libweb, "solve_target"): fake_solve_target,
                      (libweb.solverrt, "run_sets"): fake_run_sets,
                      (libweb, "WEB_MISS_RETRY_DELAY"): 0.0, (libweb, "WEB_MISS_RETRY_MIN_LEFT"): 0.0,
                      (libweb, "WEB_MISS_RETRY_LIVE"): live,
                      (libweb, "_is_one_shot"): lambda q, c: False}):
            out = {}
            libweb._solve_into(contract, out, [])
        return out, calls
    finally:
        os.environ.pop("HCTF_SOLVE_DEADLINE", None)


LIVE_TIMEOUT = {"responded": True, "timed_out": True, "gen": webhandlers.GENERATION}
out, calls = miss_retry(LIVE_TIMEOUT)
check("miss-retry SKIPS a live target whose race timed out (D28: 3 x 16.5 s wasted)",
      calls.get("proof-2") == 1 and "proof-2" not in out, (out, calls))
check("miss-retry never leaks its readiness record into the answers", set(out) == {"proof-1"}, out)
out, calls = miss_retry(LIVE_TIMEOUT, live=True)
check("HCTF_WEB_MISS_RETRY_LIVE=1 restores the old retry-every-miss", out.get("proof-2") == "proof_bbbbbbbb", calls)
out, calls = miss_retry({"responded": False, "status": 503})
check("miss-retry still retries a NOT-READY target (5xx / transport error)", out.get("proof-2") == "proof_bbbbbbbb",
      calls)
out, calls = miss_retry({"responded": True, "timed_out": False, "gen": webhandlers.GENERATION})
check("miss-retry still retries a live target whose race ended EARLY (a transient response, D27)",
      out.get("proof-2") == "proof_bbbbbbbb", calls)
out, calls = miss_retry(None)
check("miss-retry retries a miss with no readiness record (old behaviour)", out.get("proof-2") == "proof_bbbbbbbb")
out, calls = miss_retry(dict(LIVE_TIMEOUT), gen_bump=True)
check("miss-retry re-races a live timed-out target once a plugin landed since its race",
      out.get("proof-2") == "proof_bbbbbbbb", calls)

# real path (no stubs, forked run_sets): a 503-then-up target is retried; a live never-solvable target is not
_up = {"n": 0}


def late_route(method, path, q, body, headers):
    if path == "/":
        _up["n"] += 1
        if _up["n"] <= 1:
            return 503, "text/plain", "provisioning"
        return 200, TEXT, '<a href="/ready">ready</a>'
    if path == "/ready":
        return (503, "text/plain", "provisioning") if _up["n"] <= 1 else (200, TEXT, "proof_1a7e1a7e1a7e")


def slow_route(method, path, q, body, headers):
    time.sleep(0.15)      # live but slow + unsolvable: the 1 s race times out
    return 200, TEXT, '<a href="/a">a</a><a href="/b">b</a>'


late, slow = App(late_route), App(slow_route)
try:
    c = {"mode": "mastery", "prompt": PROMPT, "answer_ids": ["proof-1", "proof-2"],
         "questions": [{"id": "proof-1", "artifact": "Target 1"}, {"id": "proof-2", "artifact": "Target 2"}],
         "targets": [{"id": "Target 1", "url": late.url}, {"id": "Target 2", "url": slow.url}]}
    os.environ["HCTF_SOLVE_DEADLINE"] = str(time.time() + 40)
    nlog = len(race_log())
    try:
        with patched({(libweb, "WEB_MISS_RETRY_DELAY"): 0.2, (libweb, "WEB_MISS_RETRY_MIN_LEFT"): 1.0,
                      (libweb, "UNKNOWN_KEY_BUDGET"): 1.0, (libweb, "KNOWN_BUDGET"): 1.0}):
            out = {}
            libweb._solve_into(c, out, [])
    finally:
        os.environ.pop("HCTF_SOLVE_DEADLINE", None)
    recs = race_log()[nlog:]
    retried = [a for r in recs for a in r.get("miss_retry", [])]
    skipped = [a for r in recs for a in r.get("miss_skip_live", [])]
    check("real path: a target that was provisioning (503) on the first pass is retried and solved",
          out.get("proof-1") == "proof_1a7e1a7e1a7e" and "proof-1" in retried, (out, recs))
    check("real path: the live, timed-out target is skipped (never re-raced)",
          "proof-2" not in retried and "proof-2" in skipped and "proof-2" not in out, recs)
finally:
    late.close()
    slow.close()

# ================================================================ item 10: plugin hot reload (in-process)
HOT_KEY = f"zz_d28_hot_{os.getpid()}"
plug = ROOT / "lib" / "web" / "handlers" / f"zz_test_d28_hotreload_{os.getpid()}.py"
PLUGIN = '''"""test_d28_web hot-reload probe (deleted by the test)."""
from lib import websolve
import urllib.parse

KEY_MAP = [(r"^{key}$", "{name}")]


def exploit(base, clues):
    return websolve.proof(websolve.fetch(urllib.parse.urljoin(base, "/hot"), {{"X-Hot": "{tok}"}})[1])


HANDLERS = {{"{name}": exploit}}
'''


def hot_route(method, path, q, body, headers):
    if path == "/hot":
        tok = headers.get("X-Hot")
        return 200, "application/json", json.dumps({"evidence": f"proof_{tok}cafe0000"} if tok in ("1111", "2222")
                                                   else {"error": "nope"})


hot = App(kit({"framework": "x", HOT_KEY: "/hot"}, hot_route))
try:
    c = contract_for(hot.url, PROMPT)
    v = libweb.solve_target(c["questions"][0], c, budget=2)
    check("hot reload: before the plugin lands, the class is unsolved", v is None, v)
    gen0 = webhandlers.GENERATION
    plug.write_text(PLUGIN.format(key=HOT_KEY, name=f"zz_hot_{os.getpid()}", tok="1111"))
    nlog = len(race_log())
    v = libweb.solve_target(c["questions"][0], c, budget=5)
    rec = (race_log()[nlog:] or [{}])[-1]
    check("hot reload: a plugin written mid-run is raced by the SAME process on its next target",
          v == "proof_1111cafe0000" and rec.get("winner") == f"zz_hot_{os.getpid()}", (v, rec))
    check("hot reload: GENERATION bumped (a timed-out live miss gets re-raced)", webhandlers.GENERATION > gen0)
    check("hot reload: a refresh with nothing changed is a no-op", webhandlers.refresh() is False)
    time.sleep(0.01)
    plug.write_text(PLUGIN.format(key=HOT_KEY, name=f"zz_hot_{os.getpid()}", tok="2222") + "\n# v2 (a longer file)\n")
    v = libweb.solve_target(c["questions"][0], c, budget=5)
    check("hot reload: a CHANGED plugin is re-imported (new code raced, old handler replaced)",
          v == "proof_2222cafe0000", v)
    plug.unlink()
    webhandlers.refresh()
    check("hot reload: a deleted plugin is unregistered",
          f"zz_hot_{os.getpid()}" not in webhandlers._HANDLERS
          and not any(n == f"zz_hot_{os.getpid()}" for _p, n in webhandlers._KEY_MAP))
    plug.write_text("this is not python (a half-written file)\n")
    check("hot reload: a broken plugin is skipped, never fatal", webhandlers.refresh() is True
          and libweb.solve_target(c["questions"][0], c, budget=1) is None)
    with patched({(webhandlers, "HOT_RELOAD"): False}):
        plug.write_text(PLUGIN.format(key=HOT_KEY, name=f"zz_hot_{os.getpid()}", tok="1111"))
        check("HCTF_WEB_HOT_RELOAD=0: no rescan (load-once behaviour)", webhandlers.refresh() is False)
finally:
    hot.close()
    for p in (plug, *plug.parent.glob(f"__pycache__/{plug.stem}.*")):
        try:
            p.unlink()
        except OSError:
            pass
    webhandlers.refresh()

check("offline: no request left 127.0.0.1", not offnet, sorted(set(offnet)))
print()
if failures:
    print(f"FAILED ({len(failures)}): " + "; ".join(failures))
    sys.exit(1)
print("all D28 web clue-less LFI + miss-retry + hot-reload + class-regression checks passed")
