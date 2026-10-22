#!/usr/bin/env python3
"""Offline tests for lib.web dispatch + handlers against mock live targets. Run: python3 tests/test_libweb.py"""
import json
import sys
import threading
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lib import web  # noqa: E402
from lib.web import handlers  # noqa: E402

PROOF_SESS = "proof_sessfix01"
PROOF_IDOR = "proof_idor0001"


def _server(router):
    class H(BaseHTTPRequestHandler):
        def do_GET(self):
            status, body, cookie = router(self.path, self.headers)
            self.send_response(status)
            if cookie:
                self.send_header("Set-Cookie", cookie)
            self.end_headers()
            self.wfile.write(body.encode())

        def log_message(self, *a):
            pass

    srv = HTTPServer(("127.0.0.1", 0), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, f"http://127.0.0.1:{srv.server_address[1]}/"


def _sess_router(path, headers):
    p = urllib.parse.urlparse(path)
    qs = urllib.parse.parse_qs(p.query)
    if p.path == "/api/clues":
        return 200, json.dumps({"framework": "flask", "feature_route": "/dash",
                                "current_role": "guest", "session_hint": "abc123"}), None
    if p.path == "/dash":
        if qs.get("sid") == ["abc123"]:
            return 200, json.dumps({"evidence": PROOF_SESS}), "session=abc123"
        return 200, "Please provide your session to continue", None
    return 404, "nope", None


def _idor_router(path, headers):
    p = urllib.parse.urlparse(path)
    qs = urllib.parse.parse_qs(p.query)
    if p.path == "/api/clues":
        return 200, json.dumps({"framework": "x", "feature_route": "/profile",
                                "current_role": "guest", "mystery_key": "/profile"}), None
    if p.path == "/profile":
        if qs.get("id") == ["0"]:
            return 200, json.dumps({"evidence": PROOF_IDOR}), None
        return 200, "your profile (nothing here)", None
    return 404, "nope", None


def test_import():
    assert hasattr(web, "solve") and hasattr(web, "solve_target")
    assert callable(handlers.session_fixation) and callable(handlers.default)


def test_for_key():
    assert [n for n, _ in handlers.for_key("session_hint", {})] == ["session_fixation"]
    assert handlers.for_key("callback_nonce", {}) == []     # unknown key -> only default + priors race it
    assert handlers.for_key(None, {}) == []


def test_session_fixation_handler():
    srv, base = _server(_sess_router)
    try:
        j, _ = web.websolve.clues(base)
        assert handlers.session_fixation(base, j) == PROOF_SESS
    finally:
        srv.shutdown()


def test_default_ladder_idor():
    srv, base = _server(_idor_router)
    try:
        j, _ = web.websolve.clues(base)
        assert handlers.default(base, j) == PROOF_IDOR
    finally:
        srv.shutdown()


def test_solve_target_dispatch():
    srv, base = _server(_sess_router)
    try:
        # a contract question whose target is this mock app; solve_target must dispatch + race to the proof
        contract = {"targets": [{"id": "Target 1", "url": base}]}
        got = web.solve_target({"artifact": "Target 1"}, contract, budget=20)
        assert got == PROOF_SESS, got
    finally:
        srv.shutdown()


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
