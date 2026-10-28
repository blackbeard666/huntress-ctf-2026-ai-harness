#!/usr/bin/env python3
"""Day 25 web post-mortem (Track D) offline checks.

D1: feed / timeline / kpi / effort_report count a web Time Trial passed by the live answer during the codify wait
    (D25: shell-company + resolver-revolt TTs uncounted -> feed 22/24, kpi web 7/9 while the GM had 24/24).
D2: lib.web.plugin verifies a draft plugin on a (local mock) target and promotes it atomically -- never an unverified
    or broken one over a working plugin; the web answer-first prompt asks for the plugin first; a plugin in place at the
    single's CORRECT makes codify a hardening pass and skips the TT's parallel live answer.
D3: a blocked web Mastery waits for codify's plugin (reconnect with start) like the TT; a TT live pass requests the
    Mastery target before the live worker is joined; the target kicks are once-per-chain under concurrency.
D4: companion-key routing (protected_reference without inventory_route is not Day 14's class); the answer-first cap
    scales with the day's chains.
D5: the web prebuild lane: config, ranking, opt-in, and its offline gate (tests/test_web_fixtures.py) accepting a good
    prebuilt module and rejecting a furniture-keyed one / one that reaches a non-local host.
No GM, no live targets, no workers: fakes + a 127.0.0.1 mock server.

Run:  source bin/env.sh && python3 tests/test_d25_web.py      (exit 0 = all pass)
"""
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from hctf import effort_report, feed, kpi, timeline  # noqa: E402

failures = []


def check(name, cond, detail=""):
    print(("ok  " if cond else "FAIL ") + name + ("" if cond else f"  -- {str(detail)[:400]}"))
    if not cond:
        failures.append(name)


# ---- D1: the D25 web lines, verbatim from .run/day25.log (5 regular lanes reduced to one solved line per mode) --------
SH, RE, RV = ("web-exploitation-day-16-shell-company", "web-exploitation-day-17-reset-expectations",
              "web-exploitation-day-18-resolver-revolt")
REG = ["mobile-android-day-25-integrity-signals", "metadata-forensics-day-25-hive-mind",
       "script-analysis-day-25-phoenix-stage-chain", "warmups-day-25",
       "binary-reverse-engineering-day-25-synthetic-vulnerability-root-cause"]
D25 = ["21:00:11 [wait] day 25 released (24 challenge modes) -- launching",
       "21:00:11 8 chains (24 challenge modes), slots local=5 homebase=0, credits=99.0"]
for i, b in enumerate(REG):
    D25 += [f"21:00:{20 + i:02d} [{b}] single CORRECT + solver verified -> ending the worker, timed modes start now",
            f"21:00:{40 + i:02d} [{b}/time_trial] result: correct",
            f"21:01:{30 + i:02d} [{b}/mastery] result: correct"]
D25 += [
    f"21:01:06 [{RV}] single complete -> ending the answer-first worker",
    f"21:01:09 [{SH}] single complete -> ending the answer-first worker",
    f"21:01:10 [{RE}] single CORRECT + solver verified -> ending the worker, timed modes start now",
    f"21:01:51 [{SH}/time_trial] live-answer: mode CORRECT -> ending the generalize",
    f"21:01:51 [{SH}/time_trial] passed by the live answer after 19s of the codify wait (no generalize)",
    f"21:02:14 [{RV}/time_trial] passed by the live answer after 36s of the codify wait (no generalize)",
    f"21:02:20 [{RE}/time_trial] result: correct",
    f'21:02:44 [{RV}/mastery] timed: {{"result": "correct", "elapsed": 13.96, "window": null}}',
    f"21:02:44 [{RV}/mastery] result: correct",
    f"21:02:51 [{RE}/mastery] result: correct",
    f"21:03:56 [{SH}/mastery] passed by the live answer: not waiting for the harvest",
    f"21:03:56 [{SH}/mastery] passed by the live-answer worker (attempt ddfc9d13)",
    "21:06:02 [hof] racing passed timed modes for the Hall of Fame (up to 3 each, >= 8 left, reserve 5)",
]
D25.sort(key=lambda s: s[:8])


with tempfile.TemporaryDirectory() as d:
    log = Path(d) / "day25.log"
    log.write_text("\n".join(D25) + "\n")
    k = kpi.compute(25, log=log, root=d)
    check("D1 kpi: regular 15/15", k["modes_solved"] == 15 and k["modes"] == 15, k)
    check("D1 kpi: web 9/9 (codify-wait live passes counted)", k["web_solved"] == 9 and k["web_modes"] == 9, k)
    check("D1 kpi: the two codify-wait passes are live-answer passes", k["live_passes"] >= 3, k)
    _t0, chains = timeline.parse(D25)
    check("D1 timeline: shell-company TT done at the codify-wait pass",
          chains[SH]["done"].get("time_trial") == 21 * 3600 + 60 + 51, chains.get(SH))
    check("D1 timeline: 8/8 chains complete", sum(1 for c in chains.values() if len(c["done"]) == 3) == 8)
    eff_root = Path(d) / "copy"
    (eff_root / ".run").mkdir(parents=True)
    (eff_root / ".run" / "day25.log").write_text("\n".join(D25) + "\n")
    try:
        s = effort_report.solves(eff_root, 25)
        web_tt = {lane for lane, m in s if m == "time_trial" and lane.startswith("web")}
        check("D1 effort_report: all three web TTs found (two codify-wait passes)", len(web_tt) == 3, s)
    except Exception as e:  # noqa: BLE001
        check("D1 effort_report: parses the log", False, e)

f = feed.Feed()
msgs = []
for ln in D25:
    msgs += f.process(ln)
check("D1 feed: 24/24 solved", len(f.solved) == 24, sorted(f.solved))
check("D1 feed: the codify-wait TT shows as a live-answer solve",
      any("web TT solved (live-answer)" in m or ("TT solved (live-answer)" in m and "web" in m) for m in msgs),
      [m for m in msgs if "TT" in m])
check("D1 orchestrate-style line `result: correct (live answer, codify wait)` is a timed pass",
      timeline.timed_passed("result: correct (live answer, codify wait)")
      and timeline.timed_passed("passed during the online resolution / live answer"))

# the real log, when this copy has it (main's .run/day25.log)
real = Path.home() / "huntress-2026" / ".run" / "day25.log"
if real.exists():
    k = kpi.compute(25, log=real, root=str(real.parents[1]))
    check("D1 real .run/day25.log: regular 15/15 + web 9/9", k["modes_solved"] == 15 and k["web_solved"] == 9,
          {x: k.get(x) for x in ("modes_solved", "web_solved", "web_modes")})


# ---- D2: lib.web.plugin -- verify on a live (mock) target, promote atomically --------------------------------------------
import contextlib  # noqa: E402
import http.server  # noqa: E402
import json  # noqa: E402
import os  # noqa: E402
import threading  # noqa: E402
import time  # noqa: E402
import urllib.parse  # noqa: E402

import shutil  # noqa: E402

from lib.web import plugin as webplugin  # noqa: E402


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


class Shell(http.server.BaseHTTPRequestHandler):
    """A D25 shell-company-shaped kit: /api/clues + a worker route that runs `ls -ld <path>` (injectable after `;`)."""
    def log_message(self, *a):
        pass

    def do_GET(self):
        u = urllib.parse.urlparse(self.path)
        q = urllib.parse.parse_qs(u.query)
        if u.path == "/api/clues":
            body = {"current_role": "viewer", "example_path": "/app/static", "feature_route": "/api/worker",
                    "framework": "gin", "input_parameter": "path"}
        elif u.path == "/api/worker":
            path = (q.get("path") or [""])[0]
            out = f"drwxr-xr-x 2 app app 4096 {path.split(';')[0]}"
            if ";cat /run/huntress/objective.txt" in path:
                out += "\nproof_0123456789abcdef"
            body = {"ok": True, "effect": "worker_command_completed", "stdout": out}
        else:
            body = {"error": "not_found"}
        data = json.dumps(body).encode()
        self.send_response(200 if "error" not in body else 404)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(data)


srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Shell)
threading.Thread(target=srv.serve_forever, daemon=True).start()
BASE = f"http://127.0.0.1:{srv.server_address[1]}/"

GOOD = """import urllib.parse
from lib import websolve


def exploit(base, clues):
    url = urllib.parse.urljoin(base, clues["feature_route"])
    p = clues.get("input_parameter") or "path"
    body = websolve.fetch(url + "?" + urllib.parse.urlencode({p: clues["example_path"] + ";cat /run/huntress/objective.txt"}))[1]
    return websolve.proof(body)


KEY_MAP = [(r"example_path|input_parameter", "day99_web_zz_shell")]
HANDLERS = {"day99_web_zz_shell": exploit}
"""
TD = Path(tempfile.mkdtemp())
DRAFTS, HDIR = TD / "drafts", TD / "handlers"
DRAFTS.mkdir()
HDIR.mkdir()
draft = DRAFTS / "day99_web_zz_shell.py"
draft.write_text(GOOD)
with patched({(webplugin, "BACKUP_DIR"): TD / "backup"}):
    rep = webplugin.verify(draft, BASE, timeout=10, dest_dir=HDIR)
    final = HDIR / "day99_web_zz_shell.py"
    check("D2 plugin verify: a working draft returns the proof (rc 0) on the live target",
          rep["rc"] == 0 and rep.get("proof") == "proof_0123456789abcdef" and rep["concept_keys"], rep)
    check("D2 ... and is promoted byte-identical, no temp file left in the handlers dir",
          final.read_text() == GOOD and not [x for x in HDIR.iterdir() if x.name.startswith(".")], list(HDIR.iterdir()))
    # a draft that returns nothing must not replace the working plugin
    broken = DRAFTS / "sub" / "day99_web_zz_shell.py"
    broken.parent.mkdir()
    broken.write_text(GOOD.replace("return websolve.proof(body)", "return None"))
    rep = webplugin.verify(broken, BASE, timeout=10, dest_dir=HDIR)
    check("D2 a draft with no proof: rc 1, the working plugin is NOT overwritten", rep["rc"] == 1
          and final.read_text() == GOOD, rep)
    broken.write_text("KEY_MAP = [(r'example_path', 'day99_web_zz_shell')]\nHANDLERS = {}\nimport nonexistent_mod_zz\n")
    rep = webplugin.verify(broken, BASE, timeout=10, dest_dir=HDIR)
    check("D2 a draft that does not import: rc 2, not promoted", rep["rc"] == 2 and final.read_text() == GOOD, rep)
    broken.write_text(GOOD.replace('r"example_path|input_parameter"', 'r"graphql_route"'))
    rep = webplugin.verify(broken, BASE, timeout=10, dest_dir=HDIR)
    check("D2 a draft whose KEY_MAP matches no /api/clues key: rc 3 (the solver would never dispatch to it)",
          rep["rc"] == 3 and final.read_text() == GOOD, rep)
    bad = DRAFTS / "shell_plugin.py"
    bad.write_text(GOOD)
    rep = webplugin.verify(bad, BASE, timeout=10, dest_dir=HDIR)
    check("D2 a draft not named dayNN_web_<slug>.py is refused (rc 2)", rep["rc"] == 2, rep)
    slow = DRAFTS / "sub" / "day99_web_zz_shell.py"
    slow.write_text(GOOD.replace("    url = urllib", "    import time; time.sleep(30)\n    url = urllib"))
    t0 = time.time()
    rep = webplugin.verify(slow, BASE, timeout=1.0, dest_dir=HDIR)
    check("D2 a hanging handler is bounded by --timeout (rc 1, not promoted)",
          rep["rc"] == 1 and time.time() - t0 < 5 and final.read_text() == GOOD, (rep, time.time() - t0))
    v2 = GOOD + "\n# v2\n"
    draft.write_text(v2)
    rep = webplugin.verify(draft, BASE, timeout=10, dest_dir=HDIR)
    check("D2 a verified improvement replaces the plugin; the old one is backed up",
          rep["rc"] == 0 and final.read_text() == v2 and len(list((TD / "backup").glob("day99_web_zz_shell.*.py"))) == 1,
          rep)
    io_buf = __import__("io").StringIO()
    with contextlib.redirect_stdout(io_buf):
        rc = webplugin.main([str(draft), BASE, "--no-promote", "--timeout", "10"])
    out = io_buf.getvalue()
    check("D2 CLI: prints PROOF + a JSON summary, --no-promote does not promote",
          rc == 0 and "PROOF proof_0123456789abcdef" in out and "PROMOTED" not in out
          and json.loads(out.strip().splitlines()[-1])["rc"] == 0, out)

# ---- D2: the harness side (prompt, codify as a hardening pass, no parallel live answer) ---------------------------------
from hctf import cli, orchestrate, timed, workers  # noqa: E402

PLUG = TD / "lib_handlers" / "day25_web_x.py"
PLUG.parent.mkdir()


def bare_chain():
    ch = orchestrate.Chain.__new__(orchestrate.Chain)
    ch.lane, ch.base = "web", "web-exploitation-day-25-x"
    ch.entries = {"single_solve": {"id": "web-exploitation-day-25-x"},
                  "time_trial": {"id": "web-exploitation-day-25-x/time_trial"},
                  "mastery": {"id": "web-exploitation-day-25-x/mastery"}}
    ch.sdir = ROOT / "challenges" / "day25" / "web-x" / "solver"
    return ch


started = []


def fake_start(self):
    started.append(self)
    return self


said = []
base_env = {(orchestrate, "say"): lambda *a, **k: said.append(a[0] if a else ""),
            (orchestrate, "web_plugin_path"): lambda sdir: PLUG, (orchestrate.WebCodify, "start"): fake_start,
            (cli, "is_complete"): lambda cid: False}
with patched(base_env):
    PLUG.unlink(missing_ok=True)
    ch = bare_chain()
    orchestrate.Chain._start_codify(ch, "web-exploitation-day-25-x")
    check("D2 no plugin at the single's CORRECT: codify writes it (not a hardening pass)",
          isinstance(ch._codify, orchestrate.WebCodify) and not ch._codify.prelanded and not ch._web_plugin_pre)
    PLUG.write_text(GOOD.replace("day99_web_zz_shell", "day25_web_x"))
    ch = bare_chain()
    orchestrate.Chain._start_codify(ch, "web-exploitation-day-25-x")
    check("D2 plugin promoted by the single's worker: codify starts as a HARDENING pass",
          isinstance(ch._codify, orchestrate.WebCodify) and ch._codify.prelanded and ch._web_plugin_pre
          and any("already in place" in m for m in said), said[-2:])
    with patched({(orchestrate, "WEB_PAR_LIVE"): True, (orchestrate, "LIVE_ANSWER"): True,
                  (orchestrate, "WebParLive"): lambda *a: (_ for _ in ()).throw(AssertionError("par live started"))}):
        r = orchestrate.Chain._web_par_live(ch, "web-exploitation-day-25-x/time_trial", "time_trial", 0, False)
    check("D2 ... and the TT's first attempt gets no parallel live answer (the runner dispatches to the plugin)",
          r is None)
    with patched({(orchestrate, "WEB_CODIFY_HARDEN"): False}):
        ch = bare_chain()
        orchestrate.Chain._start_codify(ch, "web-exploitation-day-25-x")
    check("D2 HCTF_WEB_CODIFY_HARDEN=0 + a plugin in place: no codify worker", ch._codify is False and ch._web_plugin_pre)

    # the codify prompt: hardening text only for a pre-landed plugin; the draft + verifier flow always
    rendered = {}
    with patched({(workers, "render"): lambda t, **kw: rendered.update(kw) or "x",
                  (orchestrate, "single_method_text"): lambda d: "curl ...",
                  (orchestrate.Chain, "run_worker"): lambda self, *a, **k: 0,
                  (orchestrate.WebCodify, "landed"): lambda self, timeout=15: False}):   # the real _rel (a Path:
        #                                     rehearsal fair D25 -- `"..." + _rel(plugin)` raised in the hardening prompt)
        ch = bare_chain()
        wc = orchestrate.WebCodify(ch, "web-exploitation-day-25-x", prelanded=True)
        wc._run()
        check("D2 hardening codify prompt says a verified plugin is in place", "ALREADY in place" in rendered["harden"])
        wc = orchestrate.WebCodify(ch, "web-exploitation-day-25-x", prelanded=False)
        wc._run()
        check("D2 first-write codify prompt carries no hardening text", rendered["harden"] == "")
    tmpl = (ROOT / "hctf" / "prompts" / "codify.md").read_text()
    check("D2 codify prompt: draft in $TMPDIR + lib.web.plugin verifier, never the plugin path in place",
          "$TMPDIR/{name}.py" in tmpl and "-m lib.web.plugin" in tmpl and "NEVER write that path directly" in tmpl
          and "{harden}" in tmpl)

# the web answer-first prompt asks for the plugin first (draft -> verifier -> submit its PROOF)
AF = TD / "af"
AF.mkdir()
contract = {"attempt_id": "att-s", "answer_ids": ["proof-1"], "targets": [{"id": "Target 1", "url": "https://t1/"}],
            "questions": [{"id": "proof-1", "question": "Read the proof", "artifact": "Target 1"}]}
cdir = ROOT / ".run" / "test_d25_web_af"
cdir.mkdir(parents=True, exist_ok=True)
(cdir / "start.json").write_text(json.dumps(contract))
af_env = {(cli, "load"): lambda cid, n: contract if n == "start.json" else None, (cli, "cdir"): lambda cid: cdir,
          (timed, "latest_artifacts"): lambda cid: cdir, (orchestrate, "triage_summary"): lambda cid, cap=0: "(none)",
          (orchestrate, "web_plugin_path"): lambda sdir: ROOT / "lib" / "web" / "handlers" / "day25_web_x.py"}
try:
    with patched(af_env):
        ch = bare_chain()
        af = orchestrate.AnswerFirst(ch, "web-exploitation-day-25-x")
        check("D2 web answer-first prompt: PLUGIN FIRST, draft in $TMPDIR, run the verifier on the single's target",
              "PLUGIN FIRST" in af.prompt and "$TMPDIR/day25_web_x.py" in af.prompt
              and "-m lib.web.plugin $TMPDIR/day25_web_x.py https://t1/" in af.prompt, af.prompt[-900:])
        with patched({(orchestrate, "WEB_SINGLE_PLUGIN"): False}):
            af = orchestrate.AnswerFirst(ch, "web-exploitation-day-25-x")
        check("D2 HCTF_WEB_SINGLE_PLUGIN=0: the old answer-only prompt", "PLUGIN FIRST" not in af.prompt)
        ch.lane = "warmups"
        af = orchestrate.AnswerFirst(ch, "warmups-day-25")
        check("D2 non-web answer-first prompt unchanged (no plugin text)", "PLUGIN FIRST" not in af.prompt)
finally:
    shutil.rmtree(cdir, ignore_errors=True)

# ---- D3: Mastery waits on codify's plugin like the TT; a TT live pass kicks the Mastery target at once ------------------
GM_CALLS = []
MCID = "web-exploitation-day-25-x/mastery"
TCID = "web-exploitation-day-25-x/time_trial"
MLAST = {"result": "solver_incomplete", "attempt_id": "att-m", "no_clock": True, "deadline": None,
         "missing": ["proof-4"], "verified": {"proof-1": "a", "proof-2": "b", "proof-3": "c"}}


class FakeLive:
    def __init__(self, attempt, pass_after=None):
        self.attempt, self.done = attempt, threading.Event()
        self.passed = self.all_accepted = False
        self.t0, self.pass_after, self.finished = time.time(), pass_after, 0

    def _state(self):
        ok = self.pass_after is not None and time.time() - self.t0 >= self.pass_after
        return ok, ok

    def finish(self, wait=5.0):
        self.finished += 1
        self.t_finish = time.time()
        self.done.set()
        self.passed, self.all_accepted = self._state()
        return self

    def link(self, evt):
        pass


class FakeCodify:
    def __init__(self, land_after=None):
        self.plugin, self.t0 = TD / "day25_web_x_codify.py", time.time() - 5
        self.plugin.unlink(missing_ok=True)
        self.done, self.stopped, self.land_after, self.prelanded = threading.Event(), 0, land_after, True

    def arm(self):
        if self.land_after is not None:
            threading.Timer(self.land_after, lambda: self.plugin.write_text("KEY_MAP = []\n")).start()

    def landed(self, timeout=15):
        return self.plugin.exists() and self.plugin.stat().st_mtime >= self.t0

    def stop(self, join=5.0):
        self.stopped += 1
        self.done.set()


class _Gov:
    @staticmethod
    def allow_timed():
        return True


def m_chain(codify, live_pass_after=None):
    ch = bare_chain()
    ch.entries = {"time_trial": {"id": TCID}, "mastery": {"id": MCID}}
    ch.root, ch.gov = TD, _Gov()
    ch._pre_attempt_done, ch._tstatus = True, {"mastery": "start_required"}
    ch._codify, ch._web_m_kicked = codify, True
    ch.calls = {"run": [], "gen": [], "lives": [], "kick": []}
    for name, fn in {"_codify_hold": lambda cid: None, "_ahead_new": lambda mode: 0,
                     "_slow_vm_no_clock": lambda cid: False, "_early_join": lambda cid: False,
                     "_early_kw": lambda cid, untimed: {}, "_bg_gen_take": lambda cid, why, only_won=False: False,
                     "_late_probes": lambda cid, wait=False, defer_compound=False: {},
                     "_await_probes": lambda t, ready=None: True, "_tt_pool_untimed": lambda: False,
                     "_tt_fix_gate": lambda cid: None, "_web_speed_gate": lambda cid: None,
                     "_prefetch_mastery_start": lambda: None, "_gm_passed": lambda cid: False}.items():
        setattr(ch, name, fn)

    def gen(cid, **kw):
        ch.calls["gen"].append(kw.get("live"))
        if kw.get("live") is not None:
            kw["live"].pass_after = 0       # the generalize's linked live answer passes meanwhile
    ch.generalize = gen

    def start_live(cid, last, fields, wrong, fixed):
        lv = FakeLive(last.get("attempt_id"), live_pass_after)
        ch.calls["lives"].append((last.get("attempt_id"), list(fields), lv))
        return lv
    ch._start_live = start_live
    return ch


def m_drive(ch, results, extra=None):
    seq = iter(results)

    def run(cid, sdir, log=None, **kw):
        ch.calls["run"].append(kw.get("op", "start"))
        if len(ch.calls["run"]) == 1 and hasattr(ch._codify, "arm"):
            ch._codify.arm()
        time.sleep(0.2)
        return next(seq)
    env = {(orchestrate, "say"): lambda *a, **k: None, (orchestrate, "set_state"): lambda *a, **k: None,
           (orchestrate, "AUTO_EARLY"): False, (orchestrate, "LIVE_ANSWER"): True,
           (orchestrate, "WEB_LIVE_COMPOUND"): False, (orchestrate, "TT_FIX_GATE"): True,
           (orchestrate, "label_only_failure"): lambda w: False, (orchestrate, "_code_sig"): lambda d: {},
           (orchestrate, "capture_variant"): lambda *a: None, (orchestrate, "record_timed_case"): lambda *a: None,
           (orchestrate, "WEB_GEN_WAIT_POLL"): 0.05,
           (cli, "is_complete"): lambda cid: False, (cli, "gm_solved"): lambda cid: False,
           (cli, "save"): lambda *a, **k: None,
           (cli, "call"): lambda *a, **k: (GM_CALLS.append(a), {"http": 0, "body": {}})[1],   # never the real GM
           (timed, "run"): run, (timed, "last_result"): lambda cid: dict(MLAST),
           (timed, "timed_dir"): lambda cid: TD / "tdir", (timed, "ensure_started"): lambda cid: (None, None),
           (timed, "resolve_format_alternates"): lambda *a, **k: set(),
           (timed, "resolve_labels_online"): lambda *a, **k: set()}
    env.update(extra or {})
    with patched(env):
        return orchestrate.Chain.timed_stage(ch, "mastery")


ch = m_chain(FakeCodify(land_after=0.3))
ok = m_drive(ch, ["blocked", "correct"])
check("D3 a blocked web Mastery while codify runs: waits for the plugin, reconnects with op=start, no generalize",
      ok is True and len(ch.calls["run"]) == 2 and ch.calls["run"][1] == "start" and "retry" not in ch.calls["run"]
      and not ch.calls["gen"], ch.calls)
check("D3 ... its live answer works on the missing field only (proof-4)",
      [f for _a, f, _l in ch.calls["lives"]] == [["proof-4"]], ch.calls["lives"])

ch = m_chain(FakeCodify(), live_pass_after=0.2)
ok = m_drive(ch, ["blocked"])
check("D3 Mastery: the live answer passing during the codify wait -> correct, no generalize",
      ok is True and len(ch.calls["run"]) == 1 and not ch.calls["gen"], ch.calls)

cod = FakeCodify()
ch = m_chain(cod)
ok = m_drive(ch, ["blocked"], extra={(orchestrate, "WEB_CODIFY_GEN_WAIT"): 0.4})
check("D3 Mastery wait runs out: codify ended before the ONE generalize (one writer per plugin file)",
      cod.stopped == 1 and len(ch.calls["gen"]) == 1, (cod.stopped, ch.calls))

ch = m_chain(FakeCodify(land_after=0.3))
ok = m_drive(ch, ["blocked"], extra={(orchestrate, "WEB_CODIFY_MASTERY"): False,
                                     (orchestrate, "WEB_CODIFY_GEN_WAIT"): 5})
check("D3 HCTF_WEB_CODIFY_MASTERY=0: a Mastery block goes straight to the generalize (old behaviour)",
      len(ch.calls["gen"]) == 1 and len(ch.calls["run"]) == 1, ch.calls)

check("D3 the Mastery drives never reached the real GM", not GM_CALLS, GM_CALLS)

# a TT live pass in the codify wait kicks the Mastery target BEFORE the live worker is joined
ch = m_chain(FakeCodify())
ch._web_m_kicked = False
kicks = []
ch._web_mastery_kick = lambda: kicks.append(time.time())
ch._prefetch_mastery_start = lambda: None
live = FakeLive("att-t", pass_after=0.1)
with patched({(orchestrate, "say"): lambda *a, **k: None, (orchestrate, "WEB_GEN_WAIT_POLL"): 0.05,
              (cli, "is_complete"): lambda cid: False, (orchestrate, "LIVE_ANSWER"): True}):
    par = orchestrate._HeldLive(live)
    verdict, _ = orchestrate.Chain._web_codify_gen_wait(ch, TCID, "time_trial", par, {"attempt_id": "att-t"})
check("D3 TT live pass in the codify wait: Mastery target requested once, before the live worker's join",
      verdict == "correct" and len(kicks) == 1 and kicks[0] <= live.t_finish, (verdict, kicks))

# the LiveAnswer watcher runs its on_pass hooks at the GM's CORRECT
la = orchestrate.LiveAnswer.__new__(orchestrate.LiveAnswer)
la.cid, la.done, la.stop_evt, la._links, la.on_pass = TCID, threading.Event(), threading.Event(), [], []
hits = []
la.on_pass.append(lambda: hits.append(1))
la._state = lambda: (True, True)
with patched({(orchestrate, "say"): lambda *a, **k: None}):
    la._watch()
check("D3 LiveAnswer: on_pass hooks fire once at the GM's CORRECT", hits == [1] and la.stop_evt.is_set())

# once-per-chain kicks under concurrency
calls = []


def fake_call(cid, op, *a, **k):
    calls.append((cid, op))
    time.sleep(0.05)
    return {"http": 200, "body": {"result": "active"}}


ch = bare_chain()
with patched({(orchestrate, "say"): lambda *a, **k: None, (cli, "call"): fake_call,
              (cli, "is_complete"): lambda cid: False, (orchestrate, "WEB_TT_KICK"): True}):
    ths = [threading.Thread(target=orchestrate.Chain._web_mastery_kick, args=(ch,)) for _ in range(16)]
    [t.start() for t in ths]
    [t.join() for t in ths]
    time.sleep(0.4)
check("D3 _web_mastery_kick from 16 threads: ONE start request", [c for c in calls if c[1] == "start"]
      == [(MCID, "start")], calls)

# ---- D4: companion-key routing ------------------------------------------------------------------------------------------
from lib import web as libweb  # noqa: E402
from lib.web import handlers as webhandlers  # noqa: E402

kit18 = {"current_user": "alice", "feature_route": "/graphql", "note": "Case 7 is private", "protected_reference": "7"}
kit14 = {"framework": "express", "feature_route": "/api/records", "inventory_route": "/api/inventory",
         "current_role": "viewer", "protected_reference": "7"}
d24 = "day24_web_the_api_has_opinions"
check("D4 Day 18's kit (protected_reference, no inventory_route) no longer dispatches to Day 14's handler",
      d24 not in [n for n, _f in webhandlers.for_key("current_user", kit18)]
      and d24 not in [n for n, _f in webhandlers.concept_handlers("current_user", kit18)])
check("D4 Day 14's kit still dispatches to it (inventory_route, and protected_reference beside it)",
      d24 in [n for n, _f in webhandlers.for_key("inventory_route", kit14)]
      and d24 in [n for n, _f in webhandlers.for_key("protected_reference", kit14)])
# a kit with protected_reference beside neither class's companion (no inventory_route, no note/current_user)
kitnew = {"framework": "x", "feature_route": "/api/v2/things", "protected_reference": "7"}
check("D4 class_known: protected_reference beside no companion is NOT known (12 s budget); Day 14's kit is",
      libweb.class_known(kitnew, "protected_reference") is False and libweb.class_known(kit14, "inventory_route") is True)
check("D4 handlers.gated_only: protected_reference gated without its companion, not with it",
      webhandlers.gated_only("protected_reference", kitnew) and not webhandlers.gated_only("protected_reference", kit14))
check("D4 Day 18's GraphQL kit dispatches to Day 25's resolver plugin (note/current_user companion), Day 14's does not",
      "day25_web_resolver_revolt" in [n for n, _f in webhandlers.for_key("current_user", kit18)]
      and "day25_web_resolver_revolt" not in [n for n, _f in webhandlers.for_key("inventory_route", kit14)])

# ---- D4: the answer-first cap scales with the day's chains (web included) -----------------------------------------------
from hctf import duel  # noqa: E402

from hctf import paths  # noqa: E402

CH_TD = TD / "chains"
with patched({(duel, "_mem_avail_gb"): lambda: 99.0, (orchestrate, "ANSWER_FIRST_MAX"): 0,
              (orchestrate, "_af_chains"): set(), (orchestrate, "_af_live"): set(),
              (paths, "solver_dir"): lambda b: CH_TD / b / "solver", (paths, "challenge_root"): lambda b: (CH_TD / b).mkdir(parents=True, exist_ok=True) or CH_TD / b}):
    D25_CHAINS = REG + [SH, RE, RV]
    for b in D25_CHAINS:
        orchestrate.Chain(b, [{"id": b, "mode": "single_solve", "lane": "web"}], None, None)
    check("D4 auto cap = one per chain this run (8 on D25, web included)", orchestrate.answer_first_cap() == 8,
          orchestrate.answer_first_cap())
    orchestrate._af_live.update({"warmups-day-25", RV, SH})
    ok, why = orchestrate.answer_first_eligible("web", 1)
    check("D4 D25 replay: reset-expectations gets its answer-first worker with 3 already running", ok, why)
    orchestrate._af_live.update({f"x{i}" for i in range(5)})
    ok, why = orchestrate.answer_first_eligible("web", 1)
    check("D4 ... and the cap still binds at one per chain", not ok and "cap 8" in why, why)
with patched({(duel, "_mem_avail_gb"): lambda: 2.4, (orchestrate, "ANSWER_FIRST_MAX"): 0,
              (orchestrate, "_af_chains"): {f"c{i}" for i in range(8)}, (orchestrate, "_af_live"): {"a", "b", "c", "d"}}):
    ok, why = orchestrate.answer_first_eligible("web", 1)
    check("D4 memory floor grows per worker beyond the old 3 (2.4 GB free, 4 running -> refused)",
          not ok and "GB available" in why, why)
with patched({(duel, "_mem_avail_gb"): lambda: 99.0, (orchestrate, "ANSWER_FIRST_MAX"): 3,
              (orchestrate, "_af_chains"): {f"c{i}" for i in range(8)}, (orchestrate, "_af_live"): {"a", "b", "c"}}):
    ok, why = orchestrate.answer_first_eligible("web", 1)
    check("D4 HCTF_ANSWER_FIRST_MAX=3: the old fixed cap", not ok and "cap 3" in why, why)

# ---- D5: the web prebuild lane --------------------------------------------------------------------------------------
import subprocess  # noqa: E402

from hctf import prebuild  # noqa: E402

cfg = prebuild.LANES.get("web") or {}
check("D5 prebuild has a `web` lane, enabled, writable = prebuilt handlers + web fixtures only",
      "web" in prebuild.enabled_lanes()
      and cfg.get("writable") == ("lib/web/handlers/prebuilt/", "tests/data/web_fixtures/")
      and prebuild.lane_key("web-exploitation") == "web", cfg)
check("D5 its gate is the offline fixture suite (no live-target regress replay)",
      prebuild.gate_suites("web", cfg) == ["tests/test_web_fixtures.py", "tests/test_d28_web.py"]
      and not cfg.get("regress_lane"),
      prebuild.gate_suites("web", cfg))
ids = [t["id"] for t in prebuild.targets(cfg)]
check("D5 targets: the D25 classes' generic forms (cmd injection, GraphQL, reset token) rank before priority-2 gaps",
      {"cmd-injection-generic", "graphql-generic", "reset-token-generic"} <= set(ids)
      and max(ids.index(x) for x in ("cmd-injection-generic", "graphql-generic", "reset-token-generic"))
      < min((ids.index(g["id"]) for g in prebuild.atlas_gaps(cfg) if g["priority"] >= 2), default=10 ** 6), ids[:30])
check("D5 the post-run batch leaves web out unless HCTF_PREBUILD_WEB=1", "web" not in prebuild.AUTO_LANES)
r = subprocess.run([sys.executable, "-c", "from hctf import prebuild; print('web' in prebuild.AUTO_LANES)"], cwd=ROOT,
                   capture_output=True, text=True, timeout=120, env=dict(os.environ, HCTF_PREBUILD_WEB="1"))
check("D5 HCTF_PREBUILD_WEB=1 adds web to AUTO_LANES", r.stdout.strip().endswith("True"), r.stdout + r.stderr)
txt = prebuild._render("web", cfg, {"id": "cmd-injection-generic", "goal": "x"}, 10, prebuild.default_deadline())
check("D5 the web brief is rendered (prebuilt module path, recorded-kit fixtures, offline rule)",
      "lib/web/handlers/prebuilt/prebuilt_" in txt and "tests/test_web_fixtures.py" in txt
      and "NEVER contact a live target" in txt)

PB = ROOT / "lib" / "web" / "handlers" / "prebuilt"
MODSRC = """import re
import urllib.parse

from lib import websolve


def exploit(base, clues):
    route = clues.get("feature_route") if isinstance(clues, dict) else None
    if not route or "zz_concept" not in clues:
        return None
    return websolve.proof(websolve.fetch(urllib.parse.urljoin(base, route) + "?" + urllib.parse.urlencode(
        {"zz": clues["zz_concept"] + ";cat"}))[1])


KEY_MAP = [(r"^zz_concept$", "prebuilt_zz_selftest")]
HANDLERS = {"prebuilt_zz_selftest": exploit}
"""
kit = {"framework": "x", "feature_route": "/api/zz", "current_role": "analyst", "zz_concept": "v"}


def fixture(decoy):
    routes = [{"method": "GET", "path": "/api/clues", "response": kit}]
    if not decoy:
        routes.append({"method": "GET", "path": "/api/zz", "query": {"zz": "^v;cat$"},
                       "response": {"stdout": "proof_abcdefabcdefabcdefabcdefabcdef12"}})
    routes.append({"method": "GET", "path": "/api/zz", "response": {"stdout": "nothing"}})
    return {"handler": "prebuilt_zz_selftest", "expected": None if decoy else "proof_abcdefabcdefabcdefabcdefabcdef12",
            "decoy": decoy, "source": "self-test", "oracle": "self-test", "routes": routes}


def gate_run(modsrc):
    fxd = Path(tempfile.mkdtemp())
    (fxd / "zz-plain.json").write_text(json.dumps(fixture(False)))
    (fxd / "zz-decoy.json").write_text(json.dumps(fixture(True)))
    mod = PB / "prebuilt_zz_selftest.py"
    try:
        mod.write_text(modsrc)
        return subprocess.run([sys.executable, "tests/test_web_fixtures.py"], cwd=ROOT, capture_output=True, text=True,
                              timeout=180, env=dict(os.environ, HCTF_WEB_FIXTURES=str(fxd)))
    finally:
        mod.unlink(missing_ok=True)
        shutil.rmtree(PB / "__pycache__", ignore_errors=True)
        shutil.rmtree(fxd, ignore_errors=True)


r = gate_run(MODSRC)
check("D5 gate: a concept-keyed prebuilt module with a plain + decoy recorded kit passes offline",
      r.returncode == 0 and "2/2 web fixture(s) ok" in r.stdout, r.stdout[-600:] + r.stderr[-300:])
r = gate_run(MODSRC.replace('r"^zz_concept$"', 'r"feature_route|zz_concept"'))
check("D5 gate: a prebuilt KEY_MAP on kit furniture (feature_route) is rejected",
      r.returncode == 1 and "kit furniture" in r.stdout, r.stdout[-600:])
r = gate_run(MODSRC.replace("return websolve.proof(websolve.fetch(urllib.parse.urljoin(base, route)",
                            "websolve.fetch('https://example.invalid/x')\n    return websolve.proof(websolve.fetch("
                            "urllib.parse.urljoin(base, route)"))
check("D5 gate: a handler reaching a non-local host fails the offline gate",
      r.returncode == 1 and "non-local host" in r.stdout, r.stdout[-600:])
check("D5 prebuild AST gate still bans urllib.request / socket in a prebuilt module",
      [m for m in prebuild._imports("import urllib.request\nimport socket\nfrom lib import websolve\n")[0]
       if not prebuild._allowed(m)] == ["socket", "urllib.request"]
      or sorted(m for m in prebuild._imports("import urllib.request\nimport socket\nfrom lib import websolve\n")[0]
                if not prebuild._allowed(m)) == ["socket", "urllib.request"])

srv.shutdown()

# ---- rehearsal fair D25: the answer-first worker keeps a grace at the single's CORRECT to promote its plugin --------------------
import threading  # noqa: E402
from types import SimpleNamespace  # noqa: E402

GR = TD / "grace"
GR.mkdir(parents=True, exist_ok=True)


def af_stub(lane):
    af = object.__new__(orchestrate.AnswerFirst)
    af.cid, af.stop_evt, af.done = "web-x", threading.Event(), threading.Event()
    af.chain = SimpleNamespace(lane=lane, sdir=GR / "solver", _deliver_note=lambda *a, **k: None)
    return af


plug = GR / "day99_web_x.py"
with patched({(orchestrate, "web_plugin_path"): lambda sdir: plug, (orchestrate.cli, "is_complete"): lambda cid: True,
              (orchestrate, "WEB_AF_PLUGIN_GRACE"): 3.0, (orchestrate, "say"): lambda *a, **k: None}):
    af = af_stub("web")
    t0 = time.time()
    af.stop(join=0)
    early = af.stop_evt.is_set()
    threading.Timer(0.6, lambda: plug.write_text("HANDLERS = {}\n")).start()
    af.stop_evt.wait(5)
    dt = time.time() - t0
    check("grace: stop() at a live-web single's CORRECT with no plugin yet waits for the promote, then stops",
          not early and af.stop_evt.is_set() and 0.5 <= dt < 2.5, (early, dt))
    af = af_stub("web")
    t0 = time.time()
    af.stop(join=0)
    check("grace: a plugin already in place -> stopped at once", af.stop_evt.is_set() and time.time() - t0 < 0.5)
    plug.unlink()
    af = af_stub("binary-reverse-engineering")
    af.stop(join=0)
    check("grace: never for a non-web lane", af.stop_evt.is_set())
    with patched({(orchestrate, "WEB_AF_PLUGIN_GRACE"): 0.6}):
        af = af_stub("web")
        t0 = time.time()
        af.stop(join=0)
        af.stop_evt.wait(5)
        af.stop(join=0)   # a second stop after the grace: no second grace
        check("grace: no promote -> stopped when the grace runs out, once",
              af.stop_evt.is_set() and 0.5 <= time.time() - t0 < 2.0 and af._grace_ran, time.time() - t0)
        af = af_stub("web")
        af._grace_ran, af._grace_until = True, time.time() + 0.6   # a grace running on another thread
        af.stop(join=0)
        check("grace: stop() during a running grace defers to it", not af.stop_evt.is_set())

if __name__ == "__main__":
    print(f"\n{'FAILED: ' + ', '.join(failures) if failures else 'all passed'}")
    sys.exit(1 if failures else 0)
