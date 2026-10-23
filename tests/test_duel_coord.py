#!/usr/bin/env python3
"""Offline self-test for the 2026-10-15 SOTA-gap features (no GM calls, no real workers):

  - duel (hctf/duel.py): solver-dir override, mirror depth, prompt rewrite, case copy (hard-linked artifacts, real
    expected.json), adopt_into, single snapshot verification + ready handoff, generalize green -> adopt
  - retrieval (hctf/retrieval.py): tokenizer, IDF query + lane bonus, reuse_plan(rank=...) keeps the newest solver
  - coordinator (hctf/coordinator.py): trace/GM digests, stall gating, hint -> inbox, NONE -> nothing
  - workers: per-launch model/effort override, live-worker registry; hb_timed: sequential-solver detection

Run:  source bin/env.sh && python3 tests/test_duel_coord.py      (exit 0 = all pass)
"""
import json
import os
import sys
import tempfile
import threading
import time
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

os.environ.setdefault("HCTF_AUTO_EARLY", "0")   # D23 #2 auto-armed early event: covered by test_d23_postmortem
from hctf import coordinator, duel, inbox, paths, retrieval, solvers, workers  # noqa: E402
from hctf import hb_timed  # noqa: E402

PASS, FAIL = [], []


def check(name, cond):
    (PASS if cond else FAIL).append(name)
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}")


class FakeChain:
    def __init__(self, sdir, base="day99-x"):
        self.sdir, self.root, self.base, self.lane = sdir, sdir.parent, base, "warmups"
        self._gen_lock = threading.Lock()
        self._ready_snap = None

    def _worker_env(self, cid, stage):
        return {"HCTF_CHAL": cid, "HCTF_BASE": self.base, "HCTF_STAGE": stage, "HCTF_SOLVER_DIR": self.sdir,
                "HCTF_CHAL_DIR": Path("/tmp"), "HCTF_LANE": self.lane}


def t_override():
    print("solver_dir override")
    base = "day99-some-chal"
    with mock.patch.object(paths, "challenge_root", lambda cid: Path("/x") / paths.base_id(cid)):
        with mock.patch.dict(os.environ, {"HCTF_SOLVER_DIR_OVERRIDE": "/dd/solver", "HCTF_BASE": base}):
            check("override applies to the duel's own challenge (all modes)",
                  paths.solver_dir(base) == Path("/dd/solver") and paths.solver_dir(base + "/mastery") == Path("/dd/solver"))
            check("override ignored for another challenge", paths.solver_dir("day99-other") == Path("/x/day99-other/solver"))
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("HCTF_SOLVER_DIR_OVERRIDE", None)
            check("no override -> challenge solver", paths.solver_dir(base) == Path("/x") / base / "solver")


def t_duel_files():
    print("duel: mirror, render, copy, adopt")
    sdir = paths.CHALLENGES / "day99" / "warmups-test-duel" / "solver"
    m = duel._mirror(sdir, "single")
    g = duel._mirror(sdir, "generalize")
    check("mirror keeps the solver depth (parents[3] == ROOT)",
          m.parents[3] == paths.ROOT and g.parents[3] == paths.ROOT and sdir.parents[3] == paths.ROOT and m != g)
    ch = FakeChain(sdir)
    d = duel.Duel(ch, "day99-x", "single", f"solver at `{sdir.relative_to(paths.ROOT)}` and {sdir}", 60, cases=False)
    txt = d._render()
    check("prompt rewritten to the duel dir + note appended",
          str(sdir.relative_to(paths.ROOT)) + "`" not in txt.split("## You are the DUEL worker")[0]
          and str(m.relative_to(paths.ROOT)) in txt and "## You are the DUEL worker" in txt)
    with tempfile.TemporaryDirectory(dir=paths.ROOT / ".run") as td:
        src = Path(td) / "c" / "solver"
        (src / "cases" / "k" / "artifacts").mkdir(parents=True)
        (src / "solve.py").write_text("print(1)\n")
        (src / "helper.py").write_text("x = 1\n")
        (src / "cases" / "k" / "expected.json").write_text("{}")
        (src / "cases" / "k" / "artifacts" / "a.bin").write_bytes(b"A" * 10)
        dst = Path(td) / "d" / "solver"
        duel._copy_solver(src, dst, cases=True)
        a1, a2 = src / "cases/k/artifacts/a.bin", dst / "cases/k/artifacts/a.bin"
        e1, e2 = src / "cases/k/expected.json", dst / "cases/k/expected.json"
        check("case artifacts hard-linked", a1.stat().st_ino == a2.stat().st_ino)
        check("expected.json is a real copy", e1.stat().st_ino != e2.stat().st_ino and e2.read_text() == "{}")
        dst2 = Path(td) / "e" / "solver"
        duel._copy_solver(src, dst2, cases=False)
        check("single copy has no cases/", (dst2 / "solve.py").exists() and not (dst2 / "cases").exists())
        # adopt: duel changed solve.py, dropped helper.py, added new.py; live cases untouched
        (dst / "solve.py").write_text("print(2)\n")
        (dst / "helper.py").unlink()
        (dst / "new.py").write_text("y = 2\n")
        (dst / "cases" / "k" / "expected.json").write_text('{"tampered": 1}')
        d2 = duel.Duel(FakeChain(src), "c", "generalize", "", 60, cases=True)
        d2.ddir = dst
        d2.adopt_into(src, log=lambda *_: None)
        check("adopt copies code, drops removed .py, keeps live cases",
              (src / "solve.py").read_text() == "print(2)\n" and not (src / "helper.py").exists()
              and (src / "new.py").exists() and e1.read_text() == "{}")


def t_duel_single_handoff():
    print("duel: single snapshot + ready handoff")
    with tempfile.TemporaryDirectory(dir=paths.ROOT / ".run") as td:
        sdir = Path(td) / "duel-day99" / "chal" / "solver"   # stands in for the duel dir
        sdir.mkdir(parents=True)
        (sdir / "solve.py").write_text("print(1)\n")
        old = time.time() - 10
        os.utime(sdir / "solve.py", (old, old))
        live = paths.CHALLENGES / "day99" / "warmups-test-duel" / "solver"   # never created: only its mirror path is used
        ch = FakeChain(live)
        ch.root = Path(td)
        d = duel.Duel(ch, "cid", "single", "", 60, cases=False)
        d.ddir = sdir
        d.thread = threading.Thread(target=lambda: d.stop_evt.wait(5))
        d.thread.start()
        ready, lock = threading.Event(), threading.Lock()
        with mock.patch.object(duel.cli, "is_complete", lambda c: True), \
                mock.patch.object(duel.cli, "load", lambda c, n: {"answer_ids": ["a"]}), \
                mock.patch.object(duel.timed, "latest_artifacts", lambda c: Path(td)), \
                mock.patch.object(duel.cli, "confirmed_answers", lambda c: {"a": "1"}), \
                mock.patch.object(duel.solvers, "run_solver", lambda s, c, a: ({"a": "1"}, None, 0.1)), \
                mock.patch.object(duel, "POLL", 0.05):
            t = threading.Thread(target=d.watch_single, args=(lambda: (ready, lock), lambda *_: None))
            t.start()
            ok = ready.wait(5)
            t.join(5)
        d.stop()
        check("verified duel snapshot sets ready + chain._ready_snap",
              ok and d.won and ch._ready_snap is not None and (ch._ready_snap / "solve.py").exists()
              and ch._ready_snap.parents[2] == Path(td))
        # wrong answers -> never ready
        d3 = duel.Duel(ch, "cid", "single", "", 60, cases=False)
        d3.ddir = sdir
        with mock.patch.object(duel.cli, "load", lambda c, n: {"answer_ids": ["a"]}), \
                mock.patch.object(duel.timed, "latest_artifacts", lambda c: Path(td)), \
                mock.patch.object(duel.cli, "confirmed_answers", lambda c: {"a": "1"}), \
                mock.patch.object(duel.solvers, "run_solver", lambda s, c, a: ({"a": "2"}, None, 0.1)):
            check("unverified snapshot is refused", d3.verified_snapshot(lambda *_: None) is None)


def t_duel_green():
    print("duel: generalize green")
    with tempfile.TemporaryDirectory(dir=paths.ROOT / ".run") as td:
        ddir = Path(td) / "solver"
        ddir.mkdir()
        (ddir / "solve.py").write_text("print(1)\n")
        ch = FakeChain(paths.CHALLENGES / "day99" / "warmups-test-duel" / "solver")
        d = duel.Duel(ch, "cid", "generalize", "", 60, cases=True)
        d.ddir = ddir
        d.copied.set()
        d.thread = threading.Thread(target=lambda: d.stop_evt.wait(10))
        d.thread.start()
        green = threading.Event()
        res = [{"case": "old", "ok": True, "seconds": 0.1}, {"case": "variant-x", "ok": True, "seconds": 0.1}]

        def edit_later():
            time.sleep(0.3)
            (ddir / "solve.py").write_text("print(2)\n")
            t = time.time() - 5
            os.utime(ddir / "solve.py", (t, t))
        threading.Thread(target=edit_later).start()
        with mock.patch.object(duel.solvers, "test_solver",
                               lambda s, timeout=None, cases=None: [r for r in res if cases is None or r["case"] in cases]):
            t = threading.Thread(target=d.watch_green, args=({"variant-x"}, {"old"}, False, set(), green,
                                                              lambda *_: None))
            t.start()
            ok = green.wait(8)
            t.join(5)
        d.stop()
        check("duel green sets the shared green event and marks the duel won", ok and d.won)


def t_retrieval():
    print("retrieval")
    toks = retrieval.tokens("The AutoIt script drops a PyInstaller EXE; answer the d09-pe-001 field 0xdeadbeefcafe")
    check("tokenizer keeps rare terms, drops stopwords/day ids/hex",
          {"autoit", "pyinstaller", "exe"} <= toks and "the" not in toks and not any(t.startswith("d09") for t in toks)
          and "deadbeefcafe" not in toks)
    rows = [{"day": "day01", "dir": "a", "lane": "script-analysis", "tokens": ["autoit", "script", "drops", "exe"],
             "summary": [], "solver": "challenges/day01/a/solver", "notes": ""},
            {"day": "day02", "dir": "b", "lane": "binary-reverse-engineering", "tokens": ["elf", "rust", "exe"],
             "summary": [], "solver": "challenges/day02/b/solver", "notes": ""},
            {"day": "day03", "dir": "c", "lane": "script-analysis", "tokens": ["powershell", "base64"],
             "summary": [], "solver": "challenges/day03/c/solver", "notes": ""}]
    with mock.patch.object(retrieval, "rows", lambda: rows):
        hits = retrieval.query({"autoit", "exe", "script"}, lane="script-analysis", k=3)
        check("most similar first", hits and hits[0][1]["dir"] == "a")
        check("own challenge excluded", all(r["dir"] != "a" for _, r in
                                            retrieval.query({"autoit", "exe"}, exclude=("a",), k=3)))
        check("nothing similar -> no hits", retrieval.query({"zzzz"}, k=3) == [])
    # reuse_plan(rank=...): newest always kept, the other slot goes to the most similar
    dirs = [Path(f"/s/day{n:02d}/x{n}/solver") for n in (5, 6, 7, 8)]
    rank = {dirs[0].resolve(): 0.9}
    seen = []
    with mock.patch.object(solvers, "all_solver_dirs", lambda: dirs), \
            mock.patch.object(solvers, "lane_solver_dirs", lambda lane: []), \
            mock.patch.object(solvers, "_lane_of", lambda p: "warmups"), \
            mock.patch.object(solvers, "run_solver", lambda s, c, a, t: (seen.append(s) or ({}, None, 0.0))):
        solvers.reuse_plan({"answer_ids": ["q"]}, Path("/a"), "warmups", limit=2, by_question=False, rank=rank)
    check("rank picks newest + most similar", sorted(seen) == sorted([dirs[3], dirs[0]]))


def t_coordinator():
    print("coordinator")
    with tempfile.TemporaryDirectory(dir=paths.ROOT / ".run") as td:
        cd = Path(td)
        log = cd / "worker-single-local-x.log"
        evs = [{"type": "assistant", "message": {"content": [{"type": "text", "text": "Trying base64 on blob"},
                                                             {"type": "tool_use", "name": "Bash",
                                                              "input": {"command": "python3 dec.py"}}]}},
               {"type": "user", "message": {"content": [{"type": "tool_result", "content": "garbage output"}]}}]
        log.write_text("\n".join(json.dumps(e) for e in evs) + "\n")
        dig = coordinator.trace_digest(log)
        check("trace digest has thoughts, calls, results",
              "THINKS: Trying base64" in dig and "CALLS Bash: python3 dec.py" in dig and "RESULT: garbage" in dig)
        (cd / "submissions.jsonl").write_text(json.dumps({"kind": "incorrect", "answers": {"f": "x"}}) + "\n")
        check("gm digest lists rejected submits", "incorrect" in coordinator.gm_digest(cd))
        w = {"log": log, "start": time.time() - 3600, "cid": "day99-c", "stage": "single", "lane": "warmups",
             "base": "day99-c", "chal_dir": cd, "duel": False}
        posted = []
        with mock.patch.object(coordinator.workers, "live_workers", lambda: [w]), \
                mock.patch.object(coordinator, "_accepted", lambda cid: 3), \
                mock.patch.object(coordinator.cli, "is_complete", lambda cid: False), \
                mock.patch.object(coordinator, "_triage", lambda cid: "(t)"), \
                mock.patch.object(coordinator, "LOG", cd / "coord.jsonl"), \
                mock.patch.object(coordinator, "ask", lambda p: (posted.append(p) or "Try XOR with the key in set1.", 0.01)):
            c = coordinator.Coordinator(log=lambda *_: None)
            c.tick()          # first sight: progress clock starts at worker start (an hour ago) -> stalled -> review
            for _ in range(50):
                if not c.busy:
                    break
                time.sleep(0.05)
            msgs = inbox.texts(cd)
            check("stalled worker gets one hint in its inbox", len(posted) == 1 and msgs and "XOR" in msgs[-1])
            c.tick()
            time.sleep(0.2)
            check("GAP holds the next hint back", len(posted) == 1)
        inbox.reset(cd)
        w2 = dict(w, log=cd / "other.log", start=time.time() - 60)
        with mock.patch.object(coordinator.workers, "live_workers", lambda: [w2]), \
                mock.patch.object(coordinator, "_accepted", lambda cid: 0), \
                mock.patch.object(coordinator, "ask", lambda p: (posted.append(p) or "x", 0.0)):
            coordinator.Coordinator(log=lambda *_: None).tick()
            time.sleep(0.2)
            check("young worker is never reviewed", len(posted) == 1)
        w3 = dict(w, log=cd / "third.log")
        with mock.patch.object(coordinator.workers, "live_workers", lambda: [w3]), \
                mock.patch.object(coordinator, "_accepted", lambda cid: 0), \
                mock.patch.object(coordinator.cli, "is_complete", lambda cid: False), \
                mock.patch.object(coordinator, "_triage", lambda cid: "(t)"), \
                mock.patch.object(coordinator, "LOG", cd / "coord.jsonl"), \
                mock.patch.object(coordinator, "ask", lambda p: ("NONE", 0.0)):
            c = coordinator.Coordinator(log=lambda *_: None)
            c.tick()
            for _ in range(50):
                if not c.busy:
                    break
                time.sleep(0.05)
            check("NONE posts nothing", inbox.texts(cd) == [])


def t_workers():
    print("workers / hb_timed")
    cmd = workers._worker_cmd("single", "warmups", "p", model="m-x", effort="low")
    check("model/effort override", cmd[cmd.index("--model") + 1] == "m-x" and cmd[cmd.index("--effort") + 1] == "low")
    cmd = workers._worker_cmd("single", "warmups", "p")
    check("default model/effort unchanged", cmd[cmd.index("--model") + 1] == workers.worker_model("warmups"))
    k = workers._live_add("/tmp/l.log", {"HCTF_CHAL": "c", "HCTF_STAGE": "single", "HCTF_DUEL": "1"})
    check("live registry add", any(w["cid"] == "c" and w["duel"] for w in workers.live_workers()))
    workers._live_drop(k)
    check("live registry drop", not any(w["cid"] == "c" for w in workers.live_workers()))
    with tempfile.TemporaryDirectory() as td:
        (Path(td) / "solve.py").write_text("for s in sets: solve(s)\n")
        seq = hb_timed._sequential_solver(Path(td) / "solve.py")
        (Path(td) / "par.py").write_text("from lib.common import group_by_set\n")
        par = hb_timed._sequential_solver(Path(td) / "solve.py")
    check("sequential solver detected; group_by_set anywhere in the dir = parallel", seq and not par)


def t_replay_fixes():
    print("rehearsal D13 replay fixes")
    from hctf import orchestrate as orch
    check("label-only: expansion/control labels",
          orch.label_only_failure([("batch-dropper-expansion", "delayed"), ("vbscript-benign-control", "direct")]))
    check("not label-only: a decoded value among them",
          not orch.label_only_failure([("batch-dropper-expansion", "x"), ("set1.message", "abc")]))
    check("not label-only: nothing wrong", not orch.label_only_failure([]))
    # untimed/resume -> Homebase when it is up; local fallback on exec_error
    calls = []
    with mock.patch.object(workers, "_homebase_ready", lambda log=None: True), \
            mock.patch.object(workers, "AUTO_HOMEBASE", True), \
            mock.patch.object(workers.remote, "gm_transport", lambda: "local"), \
            mock.patch.object(workers, "run_hb_timed", lambda s, c, op, timeout, on_event=None:
                              (calls.append(("hb", op)) or {"result": "correct"})), \
            mock.patch.object(workers, "run_timed", lambda s, c, op, timeout: (calls.append(("local", op)) or
                                                                              {"result": "correct"})):
        r = workers.run_timed_auto(Path("/s"), "x/time_trial", op="untimed", log=lambda *_: None)
        check("untimed routed to Homebase when ready", calls == [("hb", "untimed")] and r["routed"] == "homebase (untimed)")
    calls.clear()
    with mock.patch.object(workers, "_homebase_ready", lambda log=None: True), \
            mock.patch.object(workers, "AUTO_HOMEBASE", True), \
            mock.patch.object(workers.remote, "gm_transport", lambda: "local"), \
            mock.patch.object(workers, "run_hb_timed", lambda s, c, op, timeout, on_event=None:
                              (calls.append(("hb", op)) or {"result": "exec_error", "detail": "x"})), \
            mock.patch.object(workers, "run_timed", lambda s, c, op, timeout: (calls.append(("local", op)) or
                                                                              {"result": "incorrect"})):
        r = workers.run_timed_auto(Path("/s"), "x/time_trial", op="resume", log=lambda *_: None)
        check("Homebase exec_error -> local fallback", calls == [("hb", "resume"), ("local", "resume")]
              and r["routed"] == "local (untimed)")
    # _localize: a one-field set judged incorrect is not re-submitted
    subs = []
    with mock.patch.object(hb_timed, "_submit", lambda cid, ans, body, out: (subs.append(ans) or {"result": "incorrect"})), \
            mock.patch.object(hb_timed, "_vocab", lambda: {}), \
            mock.patch.object(hb_timed, "_playbook_alts", lambda a, v: []), \
            mock.patch.object(hb_timed, "_deadline_left", lambda b: None):
        out = {}
        groups = {"set1": {"set1.message": {}}, "set2": {"set2.message": {}}}
        hb_timed._localize("c", {"set1.message": "a", "set2.message": "b"}, groups,
                           {"set1": {"result": "incorrect"}, "set2": {"result": "correct"}}, {}, out)
    check("one-field incorrect set -> wrong without a re-submit",
          subs == [] and out["wrong"] == [["set1.message", "a"]] and out["verified"] == {"set2.message": "b"})
    # duel wakes on the race event instead of waiting the full delay
    sdir = paths.CHALLENGES / "day99" / "warmups-test-duel" / "solver"
    d = duel.Duel(FakeChain(sdir), "c", "single", "", 60, cases=False)
    d.ddir = None   # the body logs + returns right after the wait: only the timing is under test
    wake, t0, seen = threading.Event(), time.time(), []
    d.ddir = Path("/nonexistent/x/y/solver")
    with mock.patch.object(duel, "_reserve", lambda k: (seen.append(time.time() - t0) or False)):
        wake.set()
        d.start(delay=15, skip=lambda: False, log=lambda *_: None, wake=wake)
        d.thread.join(5)
    check("duel wakes on the race event (<1 s, not 15 s)", seen and seen[0] < 1.0)
    # coordinator: generalize digest + edit-based stall
    with tempfile.TemporaryDirectory(dir=paths.ROOT / ".run") as td:
        cd = Path(td)
        (cd / "last_timed.json").write_text(json.dumps({"attempt_id": "96dad658-x", "result": "incorrect",
                                                        "verified": {"a": 1}, "wrong": [["f-expansion", "delayed"]],
                                                        "fixed": {"f-expansion": "percent"}}))
        dig = coordinator.gm_digest(cd)
        check("generalize digest shows GM-accepted label", "f-expansion" in dig and "'percent'" in dig)
        sd = cd / "solver"
        sd.mkdir()
        (sd / "solve.py").write_text("x")
        w = {"log": cd / "g.log", "start": time.time() - 600, "cid": "c/time_trial", "stage": "generalize",
             "lane": "script-analysis", "base": "c", "chal_dir": cd, "solver_dir": sd, "duel": False}
        asked = []
        with mock.patch.object(coordinator.workers, "live_workers", lambda: [w]), \
                mock.patch.object(coordinator, "_triage", lambda cid: "(t)"), \
                mock.patch.object(coordinator, "LOG", cd / "coord.jsonl"), \
                mock.patch.object(coordinator, "ask", lambda p: (asked.append(p) or "NONE", 0.0)):
            c = coordinator.Coordinator(log=lambda *_: None)
            c.tick()     # solve.py just edited -> not stalled
            time.sleep(0.2)
            check("generalize that just edited its solver is not reviewed", asked == [])
            old = time.time() - 400
            os.utime(sd / "solve.py", (old, old))
            c.tick()
            for _ in range(50):
                if not c.busy:
                    break
                time.sleep(0.05)
            check("generalize with no edit for 3+ min is reviewed (digest included)",
                  len(asked) == 1 and "GM accepted 'percent'" in asked[0])


def t_label_scout():
    print("label scouting")
    from hctf import orchestrate as orch, scout
    check("label scouting is OFF by default", orch.LABEL_SCOUT_ROUNDS == 0 or os.environ.get("HCTF_LABEL_SCOUT_ROUNDS"))
    orch.LABEL_SCOUT_ROUNDS = 2   # the mechanism itself (env-enabled) is still tested below
    ch = orch.Chain.__new__(orch.Chain)
    ch.base, ch.sdir = "x", Path("/s")
    calls = []

    def fake_scout(cid, sdir, rounds, clean, log):
        calls.append(rounds)
        return {"rounds": [{}, {}], "last_correct": False, "fixed": {"b-expansion": "percent"},
                "unresolved": [("c-expansion", "delayed")]}
    with mock.patch.object(scout, "scout", fake_scout), mock.patch.object(orch, "set_state", lambda *a, **k: None), \
            mock.patch.object(orch.timed, "last_result", lambda cid: {"attempts_remaining": 30}), \
            mock.patch.object(orch.cli, "is_complete", lambda cid: False), mock.patch.object(orch, "say", lambda *a: None):
        wrong, fixed = [("a-expansion", "delayed")], {}
        r = ch._label_scout("x/time_trial", "time_trial", wrong, fixed)
        check("label-only TT failure scouts, merges fixed + unresolved", not r and calls == [orch.LABEL_SCOUT_ROUNDS]
              and fixed == {"b-expansion": "percent"} and ("c-expansion", "delayed") in wrong)
        r2 = ch._label_scout("x/time_trial", "time_trial", [("a-expansion", "delayed")], {})
        check("only once per mode per run", not r2 and len(calls) == 1)
        check("never on Mastery", not ch._label_scout("x/mastery", "mastery", [("a-expansion", "d")], {}) and len(calls) == 1)
        check("not for a decoded-value failure",
              not ch._label_scout("y/time_trial", "time_trial", [("set1.message", "x")], {}) and len(calls) == 1)
    with mock.patch.object(scout, "scout", fake_scout), mock.patch.object(orch, "set_state", lambda *a, **k: None), \
            mock.patch.object(orch.timed, "last_result", lambda cid: {"attempts_remaining": 3}), \
            mock.patch.object(orch, "say", lambda *a: None):
        check("skipped below the attempt floor",
              not ch._label_scout("z/time_trial", "time_trial", [("a-expansion", "d")], {}) and len(calls) == 1)
    with mock.patch.object(scout, "scout", lambda *a, **k: {"rounds": [{}], "last_correct": True}), \
            mock.patch.object(orch, "set_state", lambda *a, **k: None), \
            mock.patch.object(orch, "record_timed_case", lambda cid, sdir: None), \
            mock.patch.object(orch.timed, "last_result", lambda cid: {"attempts_remaining": 30}), \
            mock.patch.object(orch, "say", lambda *a: None):
        check("a passing scout round passes the mode",
              ch._label_scout("w/time_trial", "time_trial", [("a-expansion", "d")], {}) is True)


def t_generalize_speed():
    print("faster generalize")
    from hctf import orchestrate as orch
    # label table from baseline results + expected.json
    with tempfile.TemporaryDirectory(dir=paths.ROOT / ".run") as td:
        sd = Path(td)
        for name, exp in (("auto-a", {"x-dropper-expansion": "percent", "x-relay-expansion": "delayed"}),
                          ("auto-b", {"y-dropper-expansion": "percent", "y-msg": "hello"})):
            (sd / "cases" / name).mkdir(parents=True)
            (sd / "cases" / name / "expected.json").write_text(json.dumps(exp))
        res = [{"case": "auto-a", "diff": {"x-dropper-expansion": {"expected": "percent", "got": "delayed"}}},
               {"case": "auto-b", "diff": {"y-dropper-expansion": {"expected": "percent", "got": "delayed"},
                                           "y-msg": {"expected": "hello", "got": "x"}}}]
        t = orch.label_table(sd, res, [("z-dropper-expansion", "delayed")])
        check("label table: GM distribution + grouped disagreements, label families only",
              "percent x2, delayed x1" in t and "GM percent <- solver delayed  (2)" in t and "y-msg" not in t)
        # test_solver(cases=...) filters by name / glob (no contract -> one() would raise; filter first)
        (sd / "cases" / "variant-z").mkdir()
        seen = []
        with mock.patch.object(solvers, "run_solver", lambda s, c, a, t: (seen.append(a.parent.name) or ({}, None, 0.0))):
            for n in ("auto-a", "auto-b", "variant-z"):
                (sd / "cases" / n / "contract.json").write_text("{}")
            solvers.test_solver(sd, cases=["variant-*"])
        check("test_solver(cases=glob) runs only matching cases", seen == ["variant-z"])
    # solver-test --case parses
    from hctf import cli
    import argparse
    with mock.patch.object(sys, "argv", ["hctf", "solver-test", "b", "--case", "variant-*", "--case", "auto-x",
                                         "--timeout", "20"]):
        ap_seen = {}
        with mock.patch.object(cli, "c_solver_test", lambda a: ap_seen.update(vars(a)) or 0):
            try:
                cli.main()
            except SystemExit:
                pass
    check("solver-test --case/--timeout parse", ap_seen.get("case") == ["variant-*", "auto-x"] and ap_seen.get("timeout") == 20)
    # targets_pass gates the full suite
    with mock.patch.object(solvers, "test_solver", lambda s, timeout=8, cases=None:
                           [{"case": "v", "ok": False}] if cases else []):
        check("targets_pass false while the target fails", not solvers.targets_pass(Path("/x"), {"v"}))
    with mock.patch.object(solvers, "test_solver", lambda s, timeout=8, cases=None:
                           [{"case": "v", "ok": True}]):
        check("targets_pass true once it passes", solvers.targets_pass(Path("/x"), {"v"}))
    # inline payload round trip (zlib)
    import base64
    import zlib
    with tempfile.TemporaryDirectory() as td:
        blob = b'{"questions": [' + b'{"q": "same text"},' * 2000 + b'{}]}'
        got = workers.write_inline({"contract.json": "z:" + base64.b64encode(zlib.compress(blob)).decode(),
                                    "evidence.zip": base64.b64encode(b"PK..").decode()}, Path(td))
        check("inline z: payload decompresses; plain still works",
              (Path(td) / "contract.json").read_bytes() == blob and (Path(td) / "evidence.zip").read_bytes() == b"PK.."
              and got == ["evidence.zip"])


def t_resubmit_fixed():
    print("resubmit-fixed (same attempt)")
    sent = []
    body = {"answer_ids": ["a-expansion", "b-url"]}
    with mock.patch.object(hb_timed, "_submit", lambda cid, ans, body, out: (sent.append(dict(ans)) or
                                                                           {"result": "CORRECT"})), \
            mock.patch.object(hb_timed, "_deadline_left", lambda b: None):
        out = {"result": "incorrect", "localize_complete": True, "wrong": [["a-expansion", "delayed"]],
               "fixed": {"a-expansion": "percent"}, "bad_sets": ["_"]}
        ok = hb_timed._resubmit_fixed("c", {"a-expansion": "delayed", "b-url": "u"}, body, out)
        check("all wrong fixed -> full corrected resubmit -> correct",
              ok and out["result"] == "correct" and sent == [{"a-expansion": "percent", "b-url": "u"}]
              and out["bad_sets"] == [] and out["verified"]["a-expansion"] == "percent")
        sent.clear()
        out = {"result": "incorrect", "localize_complete": True, "wrong": [["a-expansion", "delayed"], ["b-url", "u"]],
               "fixed": {"a-expansion": "percent"}}
        check("a wrong field without a fix -> no resubmit",
              not hb_timed._resubmit_fixed("c", {"a-expansion": "delayed", "b-url": "u"}, body, out) and sent == [])
        out = {"result": "incorrect", "localize_complete": False, "wrong": [["a-expansion", "delayed"]],
               "fixed": {"a-expansion": "percent"}}
        check("incomplete localization -> no resubmit",
              not hb_timed._resubmit_fixed("c", {"a-expansion": "delayed", "b-url": "u"}, body, out) and sent == [])
    # localize's own fix submit completed the attempt (GM CORRECT) -> passed, no resubmit
    subs = []
    verdicts = iter([{"result": "CORRECT"}])
    with mock.patch.object(hb_timed, "_submit", lambda cid, ans, body, out: (subs.append(dict(ans)) or next(verdicts))), \
            mock.patch.object(hb_timed, "_vocab", lambda: {"expansion": ["delayed", "percent"]}), \
            mock.patch.object(hb_timed, "_suffix", lambda aid: "expansion"), \
            mock.patch.object(hb_timed, "_playbook_alts", lambda a, v: []), \
            mock.patch.object(hb_timed, "_deadline_left", lambda b: None):
        out = {"result": "incorrect"}
        ans = {"a-expansion": "delayed", "b-url": "u"}
        hb_timed._localize("c", ans, {"_": {"a-expansion": {}}}, {"_": {"result": "incorrect"}}, body, out)
        n = len(subs)
        ok = hb_timed._resubmit_fixed("c", ans, body, out)
    check("a fix submit judged CORRECT = attempt completed -> passed without a resubmit",
          out.get("localize_completed_attempt") and ok and out["result"] == "correct" and len(subs) == n
          and out["resubmit_fixed"] == "completed_by_localize" and out["verified"]["a-expansion"] == "percent")
    # resubmit answered already_solved -> passed
    with mock.patch.object(hb_timed, "_submit", lambda *a, **k: {"result": "already_solved"}), \
            mock.patch.object(hb_timed, "_deadline_left", lambda b: None):
        out = {"result": "incorrect", "localize_complete": True, "wrong": [["a-expansion", "delayed"]],
               "fixed": {"a-expansion": "percent"}}
        check("resubmit already_solved -> correct",
              hb_timed._resubmit_fixed("c", {"a-expansion": "delayed", "b-url": "u"}, body, out)
              and out["result"] == "correct")
    with mock.patch.object(hb_timed, "_submit", lambda *a, **k: sent.append(1) or {"result": "CORRECT"}), \
            mock.patch.object(hb_timed, "_deadline_left", lambda b: 0.2):
        out = {"result": "incorrect", "localize_complete": True, "wrong": [["a-expansion", "delayed"]],
               "fixed": {"a-expansion": "percent"}}
        check("no clock left -> no resubmit",
              not hb_timed._resubmit_fixed("c", {"a-expansion": "d", "b-url": "u"}, body, out) and sent == [])


def t_parallel_localize():
    print("parallel localize")
    bad = {"set1.b-expansion", "set2.c-expansion", "set3.a-expansion"}
    answers, groups = {}, {}
    for s in ("set1", "set2", "set3"):
        groups[s] = {}
        for f in ("a-expansion", "b-expansion", "c-expansion", "d-url", "e-url", "f-url"):
            aid = f"{s}.{f}"
            answers[aid] = "delayed" if f.endswith("expansion") else "u"
            groups[s][aid] = {}

    def submit(cid, ans, body, out):
        time.sleep(0.05)
        if len(ans) == 1:
            (aid, v), = ans.items()
            if aid in bad:
                return {"result": "accepted", "remaining": 5} if v == "percent" else {"result": "incorrect"}
        return {"result": "incorrect"} if bad & set(ans) else {"result": "accepted", "remaining": 5}
    with mock.patch.object(hb_timed, "_submit", submit), \
            mock.patch.object(hb_timed, "_vocab", lambda: {"expansion": ["delayed", "percent"]}), \
            mock.patch.object(hb_timed, "_suffix", lambda aid: "expansion" if aid.endswith("expansion") else None), \
            mock.patch.object(hb_timed, "_playbook_alts", lambda a, v: []), \
            mock.patch.object(hb_timed, "_deadline_left", lambda b: None):
        out = {}
        t0 = time.time()
        hb_timed._localize("c", answers, groups, {s: {"result": "incorrect"} for s in groups}, {}, out)
        dt = time.time() - t0
    check("parallel localize finds + fixes every wrong field across sets, in set order",
          [w[0] for w in out["wrong"]] == ["set1.b-expansion", "set2.c-expansion", "set3.a-expansion"]
          and out["fixed"] == {a: "percent" for a in bad} and out["localize_complete"])
    check("sets localized concurrently (not one after another)", dt < 0.05 * 30, )


for fn in (t_override, t_duel_files, t_duel_single_handoff, t_duel_green, t_retrieval, t_coordinator, t_workers,
           t_replay_fixes, t_label_scout, t_generalize_speed, t_resubmit_fixed, t_parallel_localize):
    try:
        fn()
    except Exception as e:  # noqa: BLE001
        import traceback
        traceback.print_exc()
        check(f"{fn.__name__} raised {e!r}", False)
print(f"\n{len(PASS)} passed, {len(FAIL)} failed")
sys.exit(1 if FAIL else 0)
