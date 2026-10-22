#!/usr/bin/env python3
"""D (offline no-fail gate): the generic web solver must NEVER crash or hang -- for a known class, an UNKNOWN class,
an unsolvable target, or a target that is down / 410s, solve_target returns a value (proof or None) within its budget
and never raises. This is the offline half of the no-fail invariant (the live-target fault scenarios -- 410 mid-solve,
cleaned->revive, bot delay, slot contention -- run against the replay/live GM). Run: python3 tests/test_web_nofail.py"""
import json
import sys
import threading
import time
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lib import web  # noqa: E402


def _serve(router):
    class H(BaseHTTPRequestHandler):
        def do_GET(self):
            try:
                status, body = router(self.path, self.headers)
            except Exception:  # noqa: BLE001
                status, body = 500, "err"
            self.send_response(status)
            self.end_headers()
            self.wfile.write(body.encode())

        def log_message(self, *a):
            pass
    srv = HTTPServer(("127.0.0.1", 0), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, f"http://127.0.0.1:{srv.server_address[1]}/"


def _contract(url):
    return {"targets": [{"id": "Target 1", "url": url}]}


def _timed(fn, limit):
    t0 = time.time()
    out = fn()
    dt = time.time() - t0
    assert dt <= limit, f"took {dt:.1f}s > {limit}s budget (must be bounded)"
    return out


def test_unknown_class_unsolvable_returns_none_bounded():
    # unknown clue key, nothing exploitable -> default ladder + priors all miss -> None, fast, no raise.
    def router(path, headers):
        p = urllib.parse.urlparse(path).path
        if p == "/api/clues":
            return 200, json.dumps({"framework": "x", "feature_route": "/home",
                                    "current_role": "guest", "brand_new_concept": "/home"})
        return 200, "nothing exploitable here"
    srv, base = _serve(router)
    try:
        got = _timed(lambda: web.solve_target({"artifact": "Target 1"}, _contract(base), budget=12), 20)
        assert got is None, got            # unsolvable -> None, but it TRIED and never hung/raised
    finally:
        srv.shutdown()


def test_unknown_class_solvable_via_default():
    # unknown clue key, but an IDOR the default ladder finds -> proof (no handler needed).
    def router(path, headers):
        u = urllib.parse.urlparse(path)
        if u.path == "/api/clues":
            return 200, json.dumps({"framework": "x", "feature_route": "/doc",
                                    "current_role": "guest", "weird_key": "/doc"})
        if u.path == "/doc" and urllib.parse.parse_qs(u.query).get("id") == ["0"]:
            return 200, json.dumps({"evidence": "proof_defaultwin1"})
        return 200, "your document"
    srv, base = _serve(router)
    try:
        got = _timed(lambda: web.solve_target({"artifact": "Target 1"}, _contract(base), budget=15), 25)
        assert got == "proof_defaultwin1", got
    finally:
        srv.shutdown()


def test_target_error_graceful():
    # every route 500s -> solve_target returns None fast, never raises.
    def router(path, headers):
        return 500, "boom"
    srv, base = _serve(router)
    try:
        got = _timed(lambda: web.solve_target({"artifact": "Target 1"}, _contract(base), budget=10), 18)
        assert got is None
    finally:
        srv.shutdown()


def test_target_down_graceful():
    # no server at all (connection refused) -> None, fast, no raise.
    base = "http://127.0.0.1:1/"   # nothing listens on port 1
    got = _timed(lambda: web.solve_target({"artifact": "Target 1"}, _contract(base), budget=8), 15)
    assert got is None


def test_target_410_graceful():
    # a finished target 410s on everything -> None, no crash.
    def router(path, headers):
        return 410, json.dumps({"state": "completed"})
    srv, base = _serve(router)
    try:
        got = _timed(lambda: web.solve_target({"artifact": "Target 1"}, _contract(base), budget=10), 18)
        assert got is None
    finally:
        srv.shutdown()


def test_no_target_returns_none():
    assert web.solve_target({"artifact": "Target 9"}, {"targets": []}) is None


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    failed = 0
    for fn in fns:
        try:
            fn()
            print(f"PASS {fn.__name__}")
        except Exception as e:  # noqa: BLE001
            failed += 1
            print(f"FAIL {fn.__name__}: {e!r}")
    print(f"\n{len(fns) - failed}/{len(fns)} passed")
    sys.exit(1 if failed else 0)
