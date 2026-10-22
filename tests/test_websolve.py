#!/usr/bin/env python3
"""Offline tests for lib.websolve pure helpers + a local-server fetch. Run: python3 tests/test_websolve.py"""
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lib import solverrt, websolve  # noqa: E402


def test_emit_reexported():
    assert websolve.emit_and_exit is solverrt.emit_and_exit


def test_target_url():
    c = {"targets": [{"id": "Target 1", "url": "http://a/"}, {"id": "Target 2", "url": "http://b/"}]}
    assert websolve.target_url({"artifact": "Target 2"}, c) == "http://b/"
    assert websolve.target_url({"artifact": "target 1"}, c) == "http://a/"          # case-insensitive
    assert websolve.target_url({"artifact": "the 2nd target"}, c) == "http://b/"    # by number
    assert websolve.target_url({"artifact": "x"}, {"targets": [{"id": "T", "url": "http://only/"}]}) == "http://only/"
    assert websolve.base_of({"artifact": "Target 1"}, c) == "http://a/"             # already trailing slash


def test_proof():
    assert websolve.proof('{"evidence": "flag proof_abc12345 here"}') == "proof_abc12345"
    assert websolve.proof("prefix proof_DEADBEEF99 suffix") == "proof_DEADBEEF99"
    assert websolve.proof('{"msg": "no token"}') is None
    assert websolve.proof("") is None


def test_clues_dispatch_key(monkeypatch=None):
    body = '{"framework": "flask", "feature_route": "/a", "current_role": "guest", "session_hint": "/login?sid="}'
    orig = websolve.fetch
    websolve.fetch = lambda *a, **k: (200, body, [])
    try:
        j, key = websolve.clues("http://x/")
        assert key == "session_hint", key                 # the one non-common key
        assert j["framework"] == "flask"
    finally:
        websolve.fetch = orig


def test_race_proof_wins():
    probes = [("slow_nonproof", lambda: "not-a-proof"),
              ("winner", lambda: "proof_cafebabe01"),
              ("err", lambda: (_ for _ in ()).throw(RuntimeError("boom")))]
    assert websolve.race(probes, budget=5) == "proof_cafebabe01"


def test_race_falls_back_to_best_nonproof():
    assert websolve.race([("a", lambda: "best-effort")], budget=2) == "best-effort"
    assert websolve.race([("a", lambda: None)], budget=2) is None


def test_fetch_local():
    class H(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header("Set-Cookie", "sid=abc; Path=/")
            self.end_headers()
            self.wfile.write(b'{"evidence": "proof_localtest1"}')

        def log_message(self, *a):
            pass

    srv = HTTPServer(("127.0.0.1", 0), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        st, body, cookies = websolve.fetch(f"http://127.0.0.1:{srv.server_address[1]}/")
        assert st == 200, st
        assert websolve.proof(body) == "proof_localtest1"
        assert any("sid=abc" in c for c in cookies), cookies
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
