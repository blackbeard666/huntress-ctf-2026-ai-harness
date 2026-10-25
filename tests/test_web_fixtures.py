#!/usr/bin/env python3
"""Web lane fixtures (the `hctf prebuild --lane web` gate, D25 D5). OFFLINE: every request goes to a 127.0.0.1 mock;
any other host fails the suite (socket-level guard) -- no live target, no GM.

tests/data/web_fixtures/<name>.json = a RECORDED KIT replayed by a declarative mock app:
    {"handler": "<lib.web.handlers name>", "expected": "proof_<hex>" | null, "decoy": bool,
     "source": "where the bodies come from (a day's worker log / plugin docstring / atlas row)",
     "oracle": "why `expected` is right (the GM accepted this request shape on Dnn / planted by the exploit-path rule)",
     "routes": [rule, ...],                         # first matching rule answers; no match -> 404 {"error":"not_found"}
     "dispatch_excludes": ["<handler>", ...],       # optional: lib.web.handlers.for_key must NOT pick these
     "budget_s": 8}                                 # optional: the handler's wall-clock budget on the mock
  rule = {"method": "GET"|"POST"|..., "path": "/exact" | "path_re": "regex",
          "query": {"param": "regex"}, "form": {"field": "regex"}, "json": {"key": "regex"}, "body_re": "regex",
          "headers": {"Name": "regex"}, "cookie_re": "regex",                       # all present ones must match
          "status": 200, "response": {...} | "text": "...", "content_type": "...", "set_cookie": ["k=v; Path=/"]}
  Regexes use re.search (anchor them yourself). /api/clues must be one of the routes.

Checks: every fixture's handler is loaded and dispatched by for_key on the mock's /api/clues (non-decoy), returns
`expected` within budget (a decoy: no proof); every lib/web/handlers module imports; every prebuilt module
(lib/web/handlers/prebuilt/prebuilt_<id>.py) names its handlers `prebuilt_*`, keys only on CONCEPT clue keys (never
kit furniture: websolve.COMMON_KEYS), declares companions it maps, and has >= 2 fixtures incl. a decoy, all with
source + oracle provenance.

Run:  source bin/env.sh && python3 tests/test_web_fixtures.py      (exit 0 = all pass)
"""
import http.server
import importlib
import json
import os
import re
import socket
import sys
import threading
import time
import urllib.parse
from http.cookies import SimpleCookie
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

FIX = Path(os.environ.get("HCTF_WEB_FIXTURES") or (ROOT / "tests" / "data" / "web_fixtures"))
HDIR = ROOT / "lib" / "web" / "handlers"
SLACK = float(os.environ.get("HCTF_TEST_TIME_SLACK", "1"))
probs = []
offnet = []

# ---- offline guard: only loopback resolves --------------------------------------------------------------------------
_real_gai = socket.getaddrinfo


def _guard_gai(host, *a, **k):
    if str(host) not in ("127.0.0.1", "localhost", "::1"):
        offnet.append(str(host))
        raise socket.gaierror(f"test_web_fixtures: offline -- {host} is not the local mock")
    return _real_gai(host, *a, **k)


socket.getaddrinfo = _guard_gai

from lib import websolve  # noqa: E402
from lib.web import handlers  # noqa: E402


# ---- the mock app ---------------------------------------------------------------------------------------------------
def _match(rule, method, path, query, body, headers):
    if rule.get("method") and rule["method"].upper() != method:
        return False
    if "path" in rule and rule["path"] != path:
        return False
    if "path_re" in rule and not re.search(rule["path_re"], path):
        return False
    for k, rx in (rule.get("query") or {}).items():
        if not any(re.search(rx, v) for v in query.get(k, [])):
            return False
    if rule.get("form"):
        form = urllib.parse.parse_qs(body.decode("utf-8", "replace"))
        for k, rx in rule["form"].items():
            if not any(re.search(rx, v) for v in form.get(k, [])):
                return False
    if rule.get("json"):
        try:
            j = json.loads(body or b"{}")
        except ValueError:
            return False
        if not isinstance(j, dict):
            return False
        for k, rx in rule["json"].items():
            if k not in j or not re.search(rx, j[k] if isinstance(j[k], str) else json.dumps(j[k])):
                return False
    if rule.get("body_re") and not re.search(rule["body_re"], body.decode("utf-8", "replace")):
        return False
    for k, rx in (rule.get("headers") or {}).items():
        if not re.search(rx, headers.get(k) or ""):
            return False
    if rule.get("cookie_re") and not re.search(rule["cookie_re"], headers.get("Cookie") or ""):
        return False
    return True


def mock(routes, hits):
    class H(http.server.BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def _serve(self):
            u = urllib.parse.urlparse(self.path)
            n = int(self.headers.get("Content-Length") or 0)
            body = self.rfile.read(n) if n else b""
            q = urllib.parse.parse_qs(u.query, keep_blank_values=True)
            rule = next((r for r in routes if _match(r, self.command, u.path, q, body, self.headers)), None)
            hits.append((self.command, self.path, bool(rule)))
            if rule is None:
                st, ct, data, cookies = 404, "application/json", b'{"error":"not_found"}', []
            else:
                st = int(rule.get("status", 200))
                if "text" in rule:
                    ct, data = rule.get("content_type", "text/html"), str(rule["text"]).encode()
                else:
                    ct, data = rule.get("content_type", "application/json"), json.dumps(rule.get("response", {})).encode()
                cookies = rule.get("set_cookie") or []
            self.send_response(st)
            self.send_header("Content-Type", ct)
            for c in cookies:
                self.send_header("Set-Cookie", c)
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        do_GET = do_POST = do_PUT = do_PATCH = do_DELETE = do_OPTIONS = _serve

        def do_HEAD(self):
            self._serve()

    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


def run_bounded(fn, base, clues, budget):
    out = {}
    os.environ["HCTF_SOLVE_DEADLINE"] = str(time.time() + budget)

    def go():
        try:
            out["v"] = fn(base, clues)
        except Exception as e:  # noqa: BLE001
            out["e"] = repr(e)[:300]
    t0 = time.time()
    th = threading.Thread(target=go, daemon=True)
    th.start()
    th.join(budget + 1.0)
    os.environ.pop("HCTF_SOLVE_DEADLINE", None)
    return out.get("v"), out.get("e") or (f"no result within {budget:g}s" if th.is_alive() else None), time.time() - t0


# ---- 1) every handler module imports ----------------------------------------------------------------------------------
mods = [(f"lib.web.handlers.{p.stem}", p) for p in sorted(HDIR.glob("*.py")) if not p.name.startswith("_")]
mods += [(f"lib.web.handlers.prebuilt.{p.stem}", p) for p in sorted((HDIR / "prebuilt").glob("*.py"))
         if not p.name.startswith("_")]
loaded = {}
for name, p in mods:
    try:
        loaded[name] = importlib.import_module(name)
    except Exception as e:  # noqa: BLE001
        probs.append(f"{p.relative_to(ROOT)}: does not import ({e!r})"[:300])

# ---- 2) fixtures ------------------------------------------------------------------------------------------------------
fixtures = []
for fj in sorted(FIX.glob("*.json")) if FIX.is_dir() else []:
    if fj.name == "TARGETS.json":
        continue
    try:
        fixtures.append((fj, json.loads(fj.read_text())))
    except ValueError as e:
        probs.append(f"{fj.name}: bad json {e}")
n_ok = 0
for fj, fx in fixtures:
    name = fx.get("handler")
    routes = fx.get("routes") or []
    if not name or name not in handlers._HANDLERS:
        probs.append(f"{fj.name}: handler {name!r} is not loaded by lib.web.handlers")
        continue
    if not any(r.get("path") == "/api/clues" for r in routes):
        probs.append(f"{fj.name}: routes need the kit's /api/clues")
        continue
    if not (fx.get("source") and fx.get("oracle")):
        probs.append(f"{fj.name}: needs source + oracle provenance")
    exp = fx.get("expected")
    if fx.get("decoy") and exp is not None:
        probs.append(f"{fj.name}: a decoy expects null")
    if not fx.get("decoy") and not (isinstance(exp, str) and websolve.PROOF_RE.fullmatch(exp)):
        probs.append(f"{fj.name}: expected must be a proof_<hex> (or decoy: true + null)")
        continue
    hits = []
    srv = mock(routes, hits)
    try:
        base = f"http://127.0.0.1:{srv.server_address[1]}/"
        clues, key = websolve.clues(base)
        picked = [n for n, _f in handlers.for_key(key, clues)]
        if not fx.get("decoy") and name not in picked:
            probs.append(f"{fj.name}: for_key({key!r}) on the kit's clue keys {sorted(clues)} does not dispatch to "
                         f"{name} (picked {picked})")
        for ex in fx.get("dispatch_excludes") or []:
            if ex in picked:
                probs.append(f"{fj.name}: for_key must NOT dispatch to {ex} on this kit (picked {picked})")
        budget = float(fx.get("budget_s") or 8) * SLACK
        got, err, dt = run_bounded(handlers._HANDLERS[name], base, clues, budget)
        if fx.get("decoy"):
            if got is not None and websolve.PROOF_RE.search(str(got)):
                probs.append(f"{fj.name}: decoy returned a proof {got!r}")
            else:
                n_ok += 1
        elif err or got != exp:
            probs.append(f"{fj.name}: {name} got {got!r} (expected {exp!r}){' -- ' + err if err else ''} "
                         f"[{len(hits)} request(s), {dt:.1f}s]")
        else:
            n_ok += 1
    finally:
        srv.shutdown()
        srv.server_close()

# ---- 3) prebuilt module structure -------------------------------------------------------------------------------------
by_handler = {}
for fj, fx in fixtures:
    by_handler.setdefault(fx.get("handler"), []).append(fx)
for name, mod in loaded.items():
    if ".prebuilt." not in name:
        continue
    stem = name.rsplit(".", 1)[1]
    if not stem.startswith("prebuilt_"):
        probs.append(f"{stem}.py: prebuilt modules are named prebuilt_<atlas id>.py")
    km = list(getattr(mod, "KEY_MAP", None) or [])
    hs = dict(getattr(mod, "HANDLERS", None) or {})
    comp = dict(getattr(mod, "KEY_COMPANIONS", None) or {})
    if not km or not hs:
        probs.append(f"{stem}: needs KEY_MAP + HANDLERS")
        continue
    for hn, fn in hs.items():
        if not hn.startswith("prebuilt_") or not callable(fn):
            probs.append(f"{stem}: handler {hn!r} must be named prebuilt_* and callable")
        if handlers._HANDLERS.get(hn) is not fn:
            probs.append(f"{stem}: handler {hn!r} is not the one lib.web.handlers dispatches (name clash?)")
    for pat, hn in km:
        try:
            rx = re.compile(pat, re.I)
        except re.error as e:
            probs.append(f"{stem}: KEY_MAP regex {pat!r}: {e}")
            continue
        furn = [k for k in websolve.COMMON_KEYS if rx.search(k)]
        if furn:
            probs.append(f"{stem}: KEY_MAP {pat!r} matches kit furniture {furn} (it would race on EVERY target): "
                         "key on the class's concept key")
        if hn not in hs:
            probs.append(f"{stem}: KEY_MAP names {hn!r}, not in HANDLERS")
    for pat in comp:
        if pat not in [p for p, _h in km]:
            probs.append(f"{stem}: KEY_COMPANIONS {pat!r} is not a KEY_MAP pattern")
    mine = [fx for hn in hs for fx in by_handler.get(hn, [])]
    if len(mine) < 2 or not any(fx.get("decoy") for fx in mine):
        probs.append(f"{stem}: needs >= 2 fixtures in tests/data/web_fixtures/ incl. a decoy (has {len(mine)})")

if offnet:
    probs.append(f"a handler tried to reach a non-local host (offline gate): {sorted(set(offnet))[:5]}")

for p in probs:
    print("FAIL " + p)
print(f"{n_ok}/{len(fixtures)} web fixture(s) ok, {len(loaded)} handler module(s) imported")
if __name__ == "__main__":
    print("all web fixture checks passed" if not probs else f"{len(probs)} problem(s)")
    sys.exit(1 if probs else 0)
