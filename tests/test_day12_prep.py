"""Behavior checks for the Day 12 prep (Day 11 post-mortem): hardlinked prior cases/ artifacts, single `start` via
Homebase, NEW-today ids in the prior-solver dry run, ratchet proposals minus earlier days' carry-overs
(offline: no GM / no Homebase / no workers).

Run:  source bin/env.sh && python3 tests/test_day12_prep.py      (exit 0 = all pass)
"""
import json
import subprocess as _sp
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace as _NS

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "hctf"))
from hctf import orchestrate, remote, solvers  # noqa: E402

# 1) prior cases/: artifacts hardlinked (same inode), JSON copied (own inode); a re-saved case never writes through
with tempfile.TemporaryDirectory() as d:
    prior, sdir = Path(d) / "prior", Path(d) / "today" / "solver"
    case = prior / "cases" / "auto-mastery-1"
    (case / "artifacts").mkdir(parents=True)
    (case / "artifacts" / "evidence.zip").write_bytes(b"PK" + b"\0" * 64)
    (case / "contract.json").write_text('{"answer_ids": ["a"]}')
    (case / "expected.json").write_text('{"a": "1"}')
    (prior / "solve.py").write_text("print(1)\n")
    orchestrate.stage_prior_solver(prior, sdir, cases=False)
    orchestrate.stage_prior_cases(prior, sdir)
    new = sdir / "cases" / "auto-mastery-1"
    assert (new / "artifacts" / "evidence.zip").stat().st_ino == (case / "artifacts" / "evidence.zip").stat().st_ino
    for f in ("contract.json", "expected.json"):
        assert (new / f).stat().st_ino != (case / f).stat().st_ino, f
    assert (sdir / "solve.py").stat().st_ino != (prior / "solve.py").stat().st_ino
    (new / "expected.json").write_text('{"a": "2"}')                       # in-place JSON edit stays local
    solvers.add_case(sdir, "auto-mastery-1", {"answer_ids": ["a"]}, new / "artifacts", {"a": "3"})
    assert (case / "expected.json").read_text() == '{"a": "1"}'
    assert (case / "artifacts" / "evidence.zip").read_bytes() == b"PK" + b"\0" * 64
    orchestrate.stage_prior_cases(prior, sdir)                             # re-stage over existing files: no crash
print("ok  prior cases/: artifacts hardlinked, contract/expected/code copied; re-saving a case leaves the prior day intact")

# 2) single `start` via Homebase: marker + envelope -> homebase; no marker -> public; started-then-lost -> public too
#    (start resumes the running attempt, unlike a submit); download/status never go via HB
_orun, _oal, _oloc = remote.subprocess.run, remote._master_alive, remote._gm_local
remote._master_alive = lambda: True
local_calls = []
remote._gm_local = lambda args, timeout: (local_calls.append(args), {"http": 200, "body": {"attempt_id": "x"}})[1]
try:
    remote.subprocess.run = lambda *a, **k: _NS(returncode=0, stdout='{"http": 200, "body": {"attempt_id": "x"}}\n',
                                                stderr="HCTF-EXEC\n")
    env = remote.gm("start", "c")
    assert env["transport"] == "homebase" and not local_calls, (env, local_calls)
    remote.subprocess.run = lambda *a, **k: _NS(returncode=255, stdout="", stderr="ssh: connect refused\n")
    remote.gm("start", "c")
    assert local_calls == [("start", "c")], local_calls
    local_calls.clear()
    remote.subprocess.run = lambda *a, **k: _NS(returncode=255, stdout="", stderr="HCTF-EXEC\nconnection reset\n")
    remote.gm("start", "c")
    assert local_calls == [("start", "c")], local_calls
    local_calls.clear()
    remote.subprocess.run = lambda *a, **k: (_ for _ in ()).throw(AssertionError("must not go via HB"))
    remote.gm("download", "cap", "/tmp/x")
    remote.gm("status", "c")
    assert local_calls == [("download", "cap", "/tmp/x"), ("status", "c")], local_calls
    local_calls.clear()
    remote.START_VIA_HB = False
    remote.gm("start", "c")
    assert local_calls == [("start", "c")]
finally:
    remote.subprocess.run, remote._master_alive, remote._gm_local = _orun, _oal, _oloc
    remote.START_VIA_HB = True
print("ok  single start via Homebase: proxy when the master is up; any failure -> public start; download/status local")

# 2b) ensure_started: a Homebase start whose PUBLIC download fails -> public re-start (same attempt) + refetch
from hctf import cli, timed  # noqa: E402
with tempfile.TemporaryDirectory() as d:
    calls, saved_files = [], {}
    o = (cli.call, cli.c_artifact, cli.save, cli.log, timed.latest_artifacts, remote._gm_local, cli.chal_lock)
    import contextlib
    cli.chal_lock = lambda cid: contextlib.nullcontext()
    cli.call = lambda cid, op, *a, **k: (calls.append(("hb", op)),
                                         {"http": 200, "transport": "homebase", "body": {"attempt_id": "A1", "download": "hb"}})[1]
    remote._gm_local = lambda args, timeout: (calls.append(("public", args[0])),
                                              {"http": 200, "body": {"attempt_id": "A1", "download": "pub"}})[1]
    cli.save = lambda cid, name, body: saved_files.__setitem__(name, body)
    cli.log = lambda cid, op, env: None
    timed.latest_artifacts = lambda cid: None
    def _art(a):
        calls.append(("download", saved_files["start.json"]["download"]))
        return 0 if saved_files["start.json"]["download"] == "pub" else 2
    cli.c_artifact = _art
    try:
        body, err = timed.ensure_started("c")
        assert calls == [("hb", "start"), ("download", "hb"), ("public", "start"), ("download", "pub")], calls
        assert body["attempt_id"] == "A1" and err is None and saved_files["start.json"]["download"] == "pub"
        calls.clear()
        cli.call = lambda cid, op, *a, **k: (calls.append(("hb", op)),
                                             {"http": 200, "transport": "homebase", "body": {"attempt_id": "A1", "download": "pub"}})[1]
        timed.ensure_started("c")
        assert calls == [("hb", "start"), ("download", "pub")], calls          # download fine -> no public re-start
    finally:
        cli.call, cli.c_artifact, cli.save, cli.log, timed.latest_artifacts, remote._gm_local, cli.chal_lock = o
print("ok  ensure_started: HB start + failed public download -> public re-start of the same attempt + refetch")

# 3) dry run: NEW-today ids (shape unseen in the prior cases) grouped by artifact; names only, never values
with tempfile.TemporaryDirectory() as d:
    prior = Path(d) / "solver"
    (prior / "cases" / "auto-1").mkdir(parents=True)
    (prior / "cases" / "auto-1" / "contract.json").write_text(json.dumps(
        {"answer_ids": ["set1.d09-fam-001-role", "d09-fam-002-role"]}))
    (prior / "solve.py").write_text("import json; print(json.dumps({'d09-fam-003-role': 'SECRET', 'new-ts-role': 'HIDDEN'}))\n")
    contract = {"answer_ids": ["d09-fam-003-role", "new-ts-role", "new-ts-attack"],
                "questions": [{"id": "d09-fam-003-role", "artifact": "evidence.zip -> old.js"},
                              {"id": "new-ts-role", "artifact": "evidence.zip -> launcher.ts"},
                              {"id": "new-ts-attack", "artifact": "evidence.zip -> launcher.ts"}]}
    art = Path(d) / "art"
    art.mkdir()
    known = orchestrate.prior_case_shapes(prior)
    assert known == {"d09-fam-N-role"}, known
    dd = solvers.dry_run_diagnostics(prior.resolve(), contract, art, 15, known=known, shape=orchestrate.field_shape)
    assert dd["new"] == 2 and dd["new_by_art"] == {"evidence.zip -> launcher.ts": ["new-ts-role", "new-ts-attack"]}, dd
    txt = solvers.render_dry_run(dd)
    assert "NEW today (2 ids" in txt and "`new-ts-attack`" in txt and "launcher.ts" in txt, txt
    assert "SECRET" not in txt and "HIDDEN" not in txt, txt
    assert orchestrate.prior_case_shapes(Path(d) / "nothing") is None   # no corpus -> no NEW section at all
    assert "NEW today" not in solvers.render_dry_run(
        solvers.dry_run_diagnostics(prior.resolve(), contract, art, 15, known=None))
print("ok  dry run: NEW-today ids by artifact (values withheld); no prior corpus -> no NEW section")

# 4) ratchet: a proposal bullet an earlier day of the same lane already carried is dropped; a new one is kept
with tempfile.TemporaryDirectory() as d:
    saved = orchestrate.paths.CHALLENGES
    orchestrate.paths.CHALLENGES = Path(d)
    try:
        def notes(day, name, lane, body):
            p = Path(d) / f"day{day:02d}" / name
            (p / "solver").mkdir(parents=True)
            (p / "meta.json").write_text(json.dumps({"lane": lane}))
            (p / "solver" / "NOTES.md").write_text(f"# x\n\n## Proposed lib additions\n{body}\n## Other\nz\n")
            return p / "solver" / "NOTES.md"
        old = "- `lib.common.gm_error_body`: detect a GM error JSON\n  saved in place of an artifact."
        notes(10, "scripting-a", "script-analysis", old)
        notes(10, "binary-b", "binary-reverse-engineering", "- `lib.x.only_binary`: helper")
        n = notes(11, "scripting-c", "script-analysis", old + "\n- `lib.codec`: NEW rep `rot47` (D11 confirmed)\n"
                  "- `lib.x.only_binary`: helper")
        fresh = orchestrate._new_proposals(n, 11)
        assert fresh == ["- `lib.codec`: NEW rep `rot47` (D11 confirmed)", "- `lib.x.only_binary`: helper"], fresh
        assert len(orchestrate._proposal_blocks(n)) == 3
    finally:
        orchestrate.paths.CHALLENGES = saved
print("ok  ratchet proposals: earlier same-lane carry-overs dropped (other lanes' don't count), new bullets kept")

# 5) web lane (not released yet): GM lane names normalized at `list` intake; persona/skill/helpers/technique log/triage
#    hints/cues all resolve for it, without changing any existing lane
from hctf import paths, toolchain, triage, workers  # noqa: E402
for raw, want in (("web", "web"), ("web-exploitation", "web"), ("Web-Application", "web"), ("mobile-android", "mobile-android"),
                  ("metadata-forensics", "metadata-forensics"), ("warmups", "warmups"), ("welcome", "welcome"), ("misc", "misc")):
    assert paths.canonical_lane(raw) == want, (raw, paths.canonical_lane(raw))
_og, _oreg = remote.gm, paths.register
seen = []
try:
    remote.gm = lambda *a, **k: {"http": 200, "body": {"challenges": [
        {"id": "web-day-12-x", "lane": "web-exploitation", "day": 12, "name": "X"},
        {"id": "warmups-day-12", "lane": "warmups", "day": 12, "name": "W"}]}}
    paths.register = lambda ch: seen.extend(ch)
    _olog = cli.log
    cli.log = lambda *a, **k: None
    body = cli.call(None, "list", "--day", "12")["body"]
    cli.log = _olog
finally:
    remote.gm, paths.register = _og, _oreg
assert body["challenges"][0]["lane"] == "web" and body["challenges"][0]["gm_lane"] == "web-exploitation"
assert body["challenges"][1]["lane"] == "warmups" and "gm_lane" not in body["challenges"][1]
assert seen[0]["lane"] == "web"
assert "web application" in workers.lane_persona("web")
sk = workers.lane_skill("web")
assert "# Scope" in sk and "hctf hb exec" in sk and "tshark" in sk and not sk.startswith("---"), sk[:200]
assert "lib.codec" in workers.lane_helpers("web")
assert "Recognition cues" in orchestrate.technique_log("web")
assert "pcap" in " ".join(triage._sig(b"\xd4\xc3\xb2\xa1" + b"\0" * 40))
assert "pcapng" in " ".join(triage._sig(b"\x0a\x0d\x0d\x0a" + b"\0" * 40))
har = '{"log": {"version": "1.2", "entries": [{"request": {"method": "GET"}, "response": {"status": 200}}]}}'
assert any("HAR" in x for x in triage._text_signals(har))
log = "\n".join(f'10.0.0.{i} - - [12/Oct/2026:10:00:0{i} +0000] "GET /a?id={i} HTTP/1.1" 200 12 "-" "curl/8"' for i in range(4))
assert any("access log" in x for x in triage._text_signals(log))
assert any("web shell" in x for x in triage._text_signals("<?php eval(gzinflate(base64_decode($_POST['x']))); ?>"))
assert any("JWT" in x for x in triage._text_signals("Cookie: t=eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJhZG1pbiJ9.sig"))
assert any("tshark" in x for x in toolchain.cues("Which packets in the capture...", cid="web-day-12-x"))
assert not any("tshark" in x for x in toolchain.cues("Which packets in the capture...", cid="mobile-android-day-12-x"))
print("ok  web lane: lane normalized at list intake (raw kept as gm_lane); persona/skill/lib.codec/technique log; "
      "pcap/HAR/access-log/web-shell/JWT triage hints; web cues only on web ids")

print("\nALL DAY-12 PREP CHECKS PASSED")
