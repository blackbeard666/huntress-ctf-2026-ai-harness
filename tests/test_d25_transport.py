"""D25 Track B (routing + transport), offline: no GM, no VM.
- B1 no clock = local: workers._run_timed_auto runs an untimed mode HERE when there is evidence of no clock (the
  pre-start's body in the runner's dir, or an untimed TT/mode result); Homebase stays the fallback for a local
  environment failure; HCTF_NO_CLOCK_LOCAL=0 / HCTF_RUN_FOR_TIME=1 / a known window / no evidence = Homebase-first
- prestart_useful: False only when the mode runs on Homebase whatever happens
- B3 gm.py ranged download: a 206-honouring server -> parallel ranges, same bytes; Range ignored (200) -> ONE request;
  a broken part / sha mismatch -> today's single GET; a 404 verdict -> returned, not re-requested; off switch
- B4 public_pull keeps the pre-started files whose sha256 the contract lists (no re-download); paths.index.json is
  written atomically (tmp + os.replace) and a torn read is retried

Run:  source bin/env.sh && python3 tests/test_d25_transport.py      (exit 0 = all pass)
"""
import contextlib
import hashlib
import http.server
import importlib.util
import json
import os
import re
import shutil
import sys
import tempfile
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from hctf import paths, timed, workers  # noqa: E402

failures = []


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


TMP = Path(tempfile.mkdtemp(prefix="d25-transport-"))
QUIET = lambda *a, **k: None  # noqa: E731

# ---------------------------------------------------------------- B1 routing
calls = []


def fake_local(res):
    return lambda *a, **k: (calls.append(("local", k.get("op", "start"))), dict(res))[1]


def fake_hb(res):
    return lambda *a, **k: (calls.append(("homebase", k.get("op", "start"))), dict(res))[1]


BASE = {(workers.webtarget if hasattr(workers, "webtarget") else __import__("hctf.webtarget").webtarget, "is_live_cid"):
        lambda cid: False,
        (workers, "known_window"): lambda cid: None,
        (workers, "untimed_plan"): lambda cid: (10, 0),
        (workers, "_homebase_ready"): lambda log=None: True,
        (workers, "AUTO_HOMEBASE"): True,
        (workers, "NO_CLOCK_LOCAL"): True,
        (workers, "no_clock_local"): lambda cid, log=None: False,
        (workers, "slow_vm"): lambda: False,
        (workers.remote, "gm_transport"): lambda: "local",
        (workers, "no_clock_evidence"): lambda cid: True,
        (workers, "run_timed"): fake_local({"result": "correct"}),
        (workers, "run_hb_timed"): fake_hb({"result": "correct"})}
os.environ.pop("HCTF_RUN_FOR_TIME", None)

with patched(BASE):
    calls.clear()
    r = workers.run_timed_auto(ROOT, "x-day-25-a/mastery", log=QUIET)
check("B1 window unknown + untimed evidence -> local, routed `local (no clock)`",
      calls == [("local", "start")] and r.get("routed") == "local (no clock)", (calls, r))

with patched({**BASE, (workers, "no_clock_evidence"): lambda cid: False}):
    calls.clear()
    r = workers.run_timed_auto(ROOT, "x-day-25-a/time_trial", log=QUIET)
check("B1 no evidence of an untimed attempt (maybe clocked) -> Homebase as before",
      calls == [("homebase", "start")] and r.get("routed") == "homebase (window unknown)", (calls, r))

with patched({**BASE, (workers, "NO_CLOCK_LOCAL"): False}):
    calls.clear()
    workers.run_timed_auto(ROOT, "x-day-25-a/mastery", log=QUIET)
check("B1 HCTF_NO_CLOCK_LOCAL=0 -> the old Homebase-first routing", calls == [("homebase", "start")], calls)

os.environ["HCTF_RUN_FOR_TIME"] = "1"
try:
    with patched(BASE):
        calls.clear()
        workers.run_timed_auto(ROOT, "x-day-25-a/mastery", log=QUIET)
finally:
    os.environ.pop("HCTF_RUN_FOR_TIME", None)
check("B1 HCTF_RUN_FOR_TIME=1 (clocked HoF pool) -> Homebase", calls == [("homebase", "start")], calls)

with patched({**BASE, (workers, "known_window"): lambda cid: 7.0}):
    calls.clear()
    workers.run_timed_auto(ROOT, "x-day-25-a/mastery", log=QUIET)
check("B1 a known 7 s clock -> Homebase (next to the GM)", calls == [("homebase", "start")], calls)

logs = []
with patched({**BASE, (workers, "run_timed"): fake_local({"result": "exec_error", "detail": "local hb_timed did not "
                                                          "start: [Errno 7] Argument list too long",
                                                          "attempt_id": "att-1"})}):
    calls.clear()
    r = workers.run_timed_auto(ROOT, "x-day-25-a/mastery", op="retry", log=logs.append)
check("B1 the local runner breaks (exec_error) -> the same attempt on Homebase (op start resumes it, never a re-roll)",
      calls == [("local", "retry"), ("homebase", "start")] and r.get("routed") == "homebase (local no-clock run failed)",
      (calls, r, logs))

for label, res in (("a GM rate limit", {"result": "exec_error", "gm_rate_limited": True, "detail": "download failed"}),
                   ("a solver timeout", {"result": "exec_error", "detail": "solve.py timed out after 60s"}),
                   ("the runner deadline", {"result": "exec_error", "detail": "local hb_timed timed out"}),
                   ("a solver gap", {"result": "solver_incomplete", "missing": ["a"]})):
    with patched({**BASE, (workers, "run_timed"): fake_local(res)}):
        calls.clear()
        r = workers.run_timed_auto(ROOT, "x-day-25-a/mastery", log=QUIET)
    check(f"B1 {label} locally -> returned as-is (Homebase meets the same GM / solver)",
          calls == [("local", "start")] and r.get("result") == res["result"], (calls, r))

with patched({**BASE, (workers, "_homebase_ready"): lambda log=None: False,
              (workers, "run_timed"): fake_local({"result": "exec_error", "detail": "boom"})}):
    calls.clear()
    r = workers.run_timed_auto(ROOT, "x-day-25-a/mastery", log=QUIET)
check("B1 local env failure + Homebase down -> the local result", calls == [("local", "start")]
      and r.get("result") == "exec_error", (calls, r))

# no_clock_evidence: the runner dir's body / the TT's or the mode's last result
tdirs = {}


def fake_timed_dir(cid):
    return tdirs.setdefault(cid, TMP / "tmp-timed" / re.sub(r"[^A-Za-z0-9]+", "_", cid))


lasts = {}
with patched({(timed, "timed_dir"): fake_timed_dir, (timed, "last_result"): lambda cid: lasts.get(cid)}):
    cid = "x-day-25-b/time_trial"
    check("B1 evidence: nothing known -> False", workers.no_clock_evidence(cid) is False)
    d = fake_timed_dir(cid)
    d.mkdir(parents=True)
    (d / "contract.json").write_text(json.dumps({"attempt_id": "a1", "answer_ids": ["q"], "deadline": None}))
    check("B1 evidence: the pre-start's untimed body in the runner dir -> True", workers.no_clock_evidence(cid) is True)
    (d / "contract.json").write_text(json.dumps({"attempt_id": "a1", "answer_ids": ["q"],
                                                 "deadline": "2026-10-25T13:00:06Z"}))
    check("B1 evidence: a CLOCKED body there -> False", workers.no_clock_evidence(cid) is False)
    lasts["x-day-25-b/time_trial"] = {"attempt_id": "t1", "deadline": None, "no_clock": True, "run_for_time": False}
    check("B1 evidence: the chain's TT came back untimed -> True for its Mastery",
          workers.no_clock_evidence("x-day-25-b/mastery") is True)
    lasts["x-day-25-b/time_trial"] = {"attempt_id": "t1", "deadline": "2026-10-25T13:00:06Z"}
    check("B1 evidence: a clocked TT -> False", workers.no_clock_evidence("x-day-25-b/mastery") is False)

with patched({(workers.remote, "gm_transport"): lambda: "local", (workers, "NO_CLOCK_LOCAL"): True}):
    check("prestart_useful: no-clock local routing -> the local pre-start is used", workers.prestart_useful("c") is True)
with patched({(workers.remote, "gm_transport"): lambda: "local", (workers, "NO_CLOCK_LOCAL"): False,
              (workers, "AUTO_HOMEBASE"): True}):
    check("prestart_useful: HCTF_NO_CLOCK_LOCAL=0 + Homebase on -> skipped (the VM never reads local bytes)",
          workers.prestart_useful("c") is False)
with patched({(workers.remote, "gm_transport"): lambda: "ssh"}):
    check("prestart_useful: forced ssh transport -> skipped", workers.prestart_useful("c") is False)

# ---------------------------------------------------------------- B4 public_pull keeps sha-matching files
from hctf import hb_timed as ht  # noqa: E402

A, B = b"A" * 5000, b"B" * 7000
capA, capB = "a" * 64, "b" * 64
body = {"attempt_id": "att-9", "answer_ids": ["set1.alpha", "set2.beta"],
        "questions": [{"artifact": "d1.zip -> x"}, {"artifact": "d2.zip -> y"}],
        "artifacts": [{"download": f"/?op=download&capability={capA}", "sha256": hashlib.sha256(A).hexdigest()},
                      {"download": f"/?op=download&capability={capB}", "sha256": hashlib.sha256(B).hexdigest()}]}
local = TMP / "pull"
local.mkdir()
(local / "d1.zip").write_bytes(A)            # pre-started, matching
(local / "d2.zip").write_bytes(b"stale")     # same name, other bytes
(local / "old.bin").write_bytes(b"x")        # not this attempt's
(local / ".prefetch.json").write_text("{}")
got = []
with patched({(ht, "_post_once"): lambda payload, tries=3: dict(body),
              (ht, "_get_bytes"): lambda cap, timeout=20: (got.append(cap), A if cap == capA else B)[1],
              (ht, "_POOL"): object()}):
    names = workers.public_pull({"attempt_id": "att-9", "missing": ["set1.alpha", "set2.beta"]}, "slug", local, "c")
check("B4 public_pull: the sha-matching pre-started d1.zip is kept, only d2.zip is fetched",
      names == ["d1.zip", "d2.zip"] and got == [capB] and (local / "d1.zip").read_bytes() == A
      and (local / "d2.zip").read_bytes() == B, (names, got))
check("B4 public_pull: files that are not this attempt's deliveries are still cleared",
      not (local / "old.bin").exists() and not (local / ".prefetch.json").exists()
      and (local / "contract.json").exists())
got.clear()
(local / "d1.zip").write_bytes(A)
with patched({(ht, "_post_once"): lambda payload, tries=3: dict(body), (workers, "PULL_KEEP_SHA"): False,
              (ht, "_get_bytes"): lambda cap, timeout=20: (got.append(cap), A if cap == capA else B)[1],
              (ht, "_POOL"): object()}):
    workers.public_pull({"attempt_id": "att-9", "missing": ["set1.alpha", "set2.beta"]}, "slug", local, "c")
check("B4 HCTF_PULL_KEEP_SHA=0: everything refetched (old behaviour)", sorted(got) == sorted([capA, capB]), got)

import subprocess  # noqa: E402

srcs = {"d1.zip": A, "d2.zip": B, "contract.json": json.dumps(body).encode(), "result.json": b"{}"}
listing = "".join(f"{len(v)}\t{k}\n" for k, v in srcs.items())
fetched = []


def fake_fetch(rpath, dst, size, streams=4):
    fetched.append(Path(rpath).name)
    Path(dst).write_bytes(srcs[Path(rpath).name])


sp = TMP / "scoped"
sp.mkdir()
(sp / "d1.zip").write_bytes(A)
(sp / "d2.zip").write_bytes(b"stale")
(sp / "junk.bin").write_bytes(b"j")
with patched({(workers.remote, "ssh"): lambda *a, **k: subprocess.CompletedProcess(a, 0, listing, ""),
              (workers.remote, "fetch_file"): fake_fetch}):
    names = workers.scoped_pull({"attempt_id": "att-9", "missing": ["set1.alpha", "set2.beta"]}, "slug", sp)
check("B4 scoped_pull: the sha-matching local d1.zip is not pulled over the VPN again; d2.zip (stale) is",
      names == ["d1.zip", "d2.zip"] and "d1.zip" not in fetched and "d2.zip" in fetched
      and (sp / "d2.zip").read_bytes() == B and (sp / "d1.zip").read_bytes() == A, (names, fetched))
check("B4 scoped_pull: a local file that is not a needed delivery is removed", not (sp / "junk.bin").exists())

# ---------------------------------------------------------------- B4 atomic index.json
idx_path = TMP / "challenges" / "index.json"
idx_path.parent.mkdir(parents=True)
with patched({(paths, "INDEX"): idx_path, (paths, "CHALLENGES"): idx_path.parent, (paths, "LOCKS"): TMP / "locks"}):
    paths.register([{"id": "warmups-day-25", "day": 25, "lane": "warmups", "name": "You Have A Point"}])
    first = json.loads(idx_path.read_text())
    seen_bad = []
    stop = threading.Event()

    def reader():
        while not stop.is_set():
            try:
                paths._load_index(tries=1)
            except ValueError as e:
                seen_bad.append(e)

    th = [threading.Thread(target=reader) for _ in range(3)]
    for t in th:
        t.start()

    def writer(k):
        for i in range(40):
            paths.register([{"id": f"lane{k}-day-25-c{i}", "day": 25, "lane": "warmups", "name": f"c{k}-{i}"}])
    ws = [threading.Thread(target=writer, args=(k,)) for k in range(3)]
    for t in ws:
        t.start()
    for t in ws:
        t.join()
    stop.set()
    for t in th:
        t.join()
    final = json.loads(idx_path.read_text())
    check("B4 index.json: concurrent readers never see a partial file while 3 writers register",
          not seen_bad, seen_bad[:2])
    check("B4 index.json: no lost update (read-modify-write under the lock): 1 + 3 x 40 ids",
          len(final) == 121 and "warmups-day-25" in final, len(final))
    check("B4 index.json: no tmp files left behind", not list(idx_path.parent.glob(".index.json.*")))
    # a torn read (an old writer truncating in place) is retried, not raised
    idx_path.write_text("")

    def fix():
        time.sleep(0.03)
        idx_path.write_text(json.dumps(first))
    threading.Thread(target=fix).start()
    check("B4 _load_index: an empty/partial file is retried until it parses", paths._load_index() == first)

# ---------------------------------------------------------------- B3 ranged download (gm.py vs a local server)
DATA = os.urandom(3 * (1 << 20) + 12345)
SHA = hashlib.sha256(DATA).hexdigest()
reqs = []


class H(http.server.BaseHTTPRequestHandler):
    mode = "range"

    def log_message(self, *a):
        pass

    def do_GET(self):
        rng = self.headers.get("Range")
        reqs.append((rng, self.headers.get("Authorization")))
        if "capability=dead" in self.path:
            b = b'{"error":"not_found"}'
            self.send_response(404)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(b)))
            self.end_headers()
            self.wfile.write(b)
            return
        m = re.match(r"bytes=(\d+)-(\d+)", rng or "")
        if H.mode == "ignore" or not m:
            self.send_response(200)
            self.send_header("Content-Type", "application/octet-stream")
            self.send_header("Content-Length", str(len(DATA)))
            self.end_headers()
            self.wfile.write(DATA)
            return
        lo, hi = int(m.group(1)), min(int(m.group(2)), len(DATA) - 1)
        if H.mode == "broken" and lo > 0:
            hi = hi - 1                                   # a short part with a lying Content-Range
        part = DATA[lo:hi + 1]
        self.send_response(206)
        self.send_header("Content-Type", "application/octet-stream")
        self.send_header("Content-Range", f"bytes {lo}-{hi}/{len(DATA)}")
        self.send_header("Content-Length", str(len(part)))
        self.end_headers()
        try:
            self.wfile.write(part)
        except (BrokenPipeError, ConnectionResetError):
            pass                                          # the client read its share and closed (by design)


srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), H)
threading.Thread(target=srv.serve_forever, daemon=True).start()
spec = importlib.util.spec_from_file_location("gm_under_test", ROOT / "hctf" / "gm.py")
gm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gm)
os.environ["HUNTRESS_GM_TOKEN"] = "test-token-xyz"
out = TMP / "dl"
CAP = "c" * 64
try:
    with patched({(gm, "GM"): f"http://127.0.0.1:{srv.server_address[1]}", (gm, "RANGE_FIRST"): 1 << 20,
                  (gm, "RANGE_STREAMS"): 4, (gm, "ratebucket"): None}):
        H.mode = "range"
        reqs.clear()
        env = gm.cmd_download(CAP, str(out), "evidence.zip", SHA)
        saved = env["saved"][0] if env.get("saved") else {}
        check("B3 206 server: parallel ranges, the bytes and sha256 are exact",
              env["http"] == 200 and saved.get("sha256") == SHA and (out / "evidence.zip").read_bytes() == DATA
              and env.get("ranges") == 4 and len(reqs) == 4, (env.get("http"), env.get("ranges"), len(reqs)))
        check("B3 every range carries the bearer (same auth as today)",
              all(a == "Bearer test-token-xyz" for _r, a in reqs), reqs)
        H.mode = "ignore"
        reqs.clear()
        env = gm.cmd_download(CAP, str(out), "e2.zip")
        check("B3 Range ignored (200): ONE request, the whole file (= today's single stream)",
              len(reqs) == 1 and env["saved"][0]["sha256"] == SHA and "ranges" not in env, (len(reqs), env.get("ranges")))
        H.mode = "broken"
        reqs.clear()
        env = gm.cmd_download(CAP, str(out), "e3.zip", SHA)
        check("B3 a broken part -> today's single GET, correct bytes",
              # sibling ranges still in flight may log after the fallback GET (seen under sweep load): order-free
              env["saved"][0]["sha256"] == SHA and sum(r[0] is None for r in reqs) == 1, reqs[-3:])
        H.mode = "range"
        reqs.clear()
        env = gm.cmd_download(CAP, str(out), "e4.zip", "0" * 64)
        check("B3 a sha256 mismatch after the ranges -> today's single GET",
              reqs[-1][0] is None and env["saved"][0]["sha256"] == SHA, reqs[-1])
        reqs.clear()
        env = gm.cmd_download("dead" + "0" * 60, str(out), "e5.zip")
        check("B3 a 404 verdict on the first range is returned as-is (not re-requested)",
              env["http"] == 404 and len(reqs) == 1 and not env["saved"], (env.get("http"), len(reqs)))
        reqs.clear()
        with patched({(gm, "RANGE_FIRST"): 8 << 20}):
            env = gm.cmd_download(CAP, str(out), "e6.zip")
        check("B3 a file under RANGE_FIRST: one request (the first range is all of it)",
              len(reqs) == 1 and env["saved"][0]["sha256"] == SHA and env.get("ranges") == 1, (len(reqs), env.get("ranges")))
    with patched({(gm, "GM"): f"http://127.0.0.1:{srv.server_address[1]}", (gm, "RANGE_STREAMS"): 1}):
        reqs.clear()
        env = gm.cmd_download(CAP, str(out), "e7.zip")
        check("B3 HCTF_GM_RANGE_STREAMS=1: today's request exactly (no Range header)",
              len(reqs) == 1 and reqs[0][0] is None and env["saved"][0]["sha256"] == SHA, reqs)
finally:
    srv.shutdown()
    os.environ.pop("HUNTRESS_GM_TOKEN", None)
    shutil.rmtree(TMP, ignore_errors=True)

print(f"\n{len(failures)} failure(s)" + (": " + ", ".join(failures) if failures else ""))
sys.exit(1 if failures else 0)
