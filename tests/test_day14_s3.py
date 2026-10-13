"""Day 14 prep, stream S3 (offline: no GM / no Homebase / no real LLM workers): lane solver dirs, prebuild worker
plumbing (no GM token, secrets/ hidden, 40 turns), the prebuild gate + transactional revert with STUB workers, the
budget/deadline math, the post-run hook, bin/day.sh stop, the metadata lane seed, fair_run overlays.

Run:  source bin/env.sh && python3 tests/test_day14_s3.py      (exit 0 = all pass)
"""
import inspect
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
for k in ("HCTF_META_MAX_DAY", "HCTF_META_LANE_SOLVER", "HCTF_LANE_SOLVERS"):
    os.environ.pop(k, None)
from hctf import orchestrate, paths, prebuild, solvers, workers  # noqa: E402

LANE = paths.CHALLENGES / "_lane" / "metadata-forensics" / "solver"

# 1) lane solver dirs + flags
assert paths.lane_solver_dirs("metadata-forensics") == [LANE]
assert paths.lane_solver_dirs("binary-reverse-engineering") == [] and paths.lane_solver_dirs("warmups") == []
os.environ["HCTF_META_LANE_SOLVER"] = "0"
assert paths.lane_solver_dirs("metadata-forensics") == []
del os.environ["HCTF_META_LANE_SOLVER"]
os.environ["HCTF_LANE_SOLVERS"] = "warmups"
assert paths.lane_solver_dirs("metadata-forensics") == []
del os.environ["HCTF_LANE_SOLVERS"]
assert LANE not in paths.all_solver_dirs()          # question index / compound checks never see it
assert not subprocess.run(["git", "check-ignore", "-q", str(LANE / "solve.py")], cwd=ROOT).returncode == 0, \
    "challenges/_lane is gitignored"
print("ok  lane_solver_dirs: metadata on by default; HCTF_META_LANE_SOLVER=0 / HCTF_LANE_SOLVERS off; not gitignored")

# 2) prebuild worker plumbing
assert workers._max_turns("prebuild") == 40 and "prebuild" in workers.NO_GM_STAGES
os.environ["HUNTRESS_GM_TOKEN"] = "tok-should-vanish"
try:
    assert "HUNTRESS_GM_TOKEN" not in workers._worker_env({"HCTF_STAGE": "prebuild"})
    assert workers._worker_env({"HCTF_STAGE": "single"})["HUNTRESS_GM_TOKEN"] == "tok-should-vanish"
finally:
    del os.environ["HUNTRESS_GM_TOKEN"]
made = not (ROOT / "secrets").exists()
(ROOT / "secrets").mkdir(exist_ok=True)
try:
    sec = (ROOT / "secrets").resolve()
    hid = [h.resolve() for h in workers.sandbox_hidden_paths("prebuild")]
    assert any(sec == h or h in sec.parents for h in hid), hid          # masked itself or inside a masked dir
    assert sec not in [h.resolve() for h in workers.sandbox_hidden_paths("single")]
    if shutil.which("bwrap") and workers.WORKER_SANDBOX:
        cmd = workers.sandboxed(["bash", "-c", f"ls -A {ROOT / 'secrets'}/ 2>/dev/null | wc -l"], "prebuild")
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        assert r.returncode == 0 and r.stdout.strip() == "0", (r.stdout, r.stderr[-300:])   # empty inside the sandbox
finally:
    if made:
        (ROOT / "secrets").rmdir()
print("ok  prebuild workers: 40 turns, no GM token in env, secrets/ masked (bwrap tmpfs) -- other stages unchanged")

# 3) AST allowlist: NEW disallowed imports / banned calls only
with tempfile.TemporaryDirectory() as d:
    f = Path(d) / "m.py"
    f.write_text("import struct, zlib\nfrom lib.meta.spell import Hex\nimport pefile\n")
    assert prebuild.ast_problems(f) == []
    f.write_text("import struct\nimport subprocess\nfrom socket import socket\nimport ctypes\nx = eval('1')\nopen('x')\n")
    probs = " ".join(prebuild.ast_problems(f))
    for w in ("subprocess", "socket", "ctypes", "eval", "open"):
        assert w in probs, (w, probs)
    f.write_text("import subprocess\nimport os\nos.system('x')\n")
    assert prebuild.ast_problems(f, before_src="import subprocess\nimport os\nos.system('y')\n") == []   # pre-existing
    f.write_text("import urllib.request\nimport urllib.parse\n")
    assert [p for p in prebuild.ast_problems(f) if "urllib.request" in p] and not [p for p in prebuild.ast_problems(f)
                                                                                  if "urllib.parse" in p]
print("ok  AST gate: subprocess/socket/ctypes/os/urllib.request + eval/open flagged; pre-existing imports tolerated")

# 4) budget + deadline
saved_rm = workers.read_metrics
try:
    workers.read_metrics = lambda: []
    assert prebuild.budget_for(3) == min(prebuild.BUDGET_CAP, round(prebuild.DEFAULT_COST * 3 * 1.2, 2))
    workers.read_metrics = lambda: [{"stage": "prebuild", "cost_usd": c} for c in (1.0, 2.0, 3.0, 4.0)] + \
        [{"stage": "single", "cost_usd": 99.0}]
    assert prebuild.budget_for(2) == round(4.0 * 2 * 1.2, 2), prebuild.budget_for(2)   # p75 of prebuild rows only
    workers.read_metrics = lambda: [{"stage": "prebuild", "cost_usd": 50.0}]
    assert prebuild.budget_for(3) == prebuild.BUDGET_CAP
finally:
    workers.read_metrics = saved_rm
now = datetime(2026, 10, 14, 0, 30)
assert prebuild.default_deadline(now) == datetime(2026, 10, 14, 20, 30)
assert prebuild.next_drop(datetime(2026, 10, 14, 21, 5)) == datetime(2026, 10, 15, 21, 0)
assert prebuild.parse_deadline("20:30", datetime(2026, 10, 14, 22, 0)) == datetime(2026, 10, 15, 20, 30)
print("ok  budget = n x p75(metrics prebuild cost) x 1.2, capped; deadline = next 21:00 drop - 30 min")

# 5) the gate + transactional revert with STUB workers (temp state/lock/snapshot; real lib/ restored by the harness)
tmp = Path(tempfile.mkdtemp(prefix="s3pb-", dir=paths.TMP))
saved = {k: getattr(prebuild, k) for k in ("STATE", "LOCK", "SNAP", "LOGDIR")}
saved_gate = orchestrate.RATCHET_GATE
cfg_saved = dict(prebuild.LANES["metadata-forensics"])
prebuild.STATE, prebuild.LOCK, prebuild.SNAP, prebuild.LOGDIR = (tmp / "state.json", tmp / "lock", tmp / "snap",
                                                                   tmp / "logs")
orchestrate.RATCHET_GATE = ()
prebuild.LANES["metadata-forensics"]["gate"] = ()        # fixtures + structure are still checked (fresh interpreter)
MOD = ROOT / "lib" / "meta" / "prebuilt" / "zzstub.py"
FIX = ROOT / "tests" / "data" / "meta_fixtures" / "zzstub"
EVIL = ROOT / "hctf" / "zz_evil_stub.py"
GOOD = '''"""stub prebuilt module (test)"""
import struct

FIELDS = {("zzstub", "header_count"): "header_count"}


def header_count(data, ctx):
    if data is None:
        return None
    if data[:4] != b"ZZST":
        return "none"
    return struct.unpack_from("<H", data, 4)[0]
'''


def write_good():
    MOD.write_text(GOOD)
    FIX.mkdir(parents=True, exist_ok=True)
    (FIX / "a.bin").write_bytes(b"ZZST" + (7).to_bytes(2, "little"))
    (FIX / "a.json").write_text(json.dumps({"field": "zzstub.header_count", "expected": "7", "generator_cmd": "printf",
                                            "oracle_cmd": "xxd -s 4 -l 2"}))
    (FIX / "decoy.bin").write_bytes(b"NOPE\x07\x00")
    (FIX / "decoy.json").write_text(json.dumps({"field": "zzstub.header_count", "expected": "none", "decoy": True,
                                                "generator_cmd": "printf", "oracle_cmd": "head -c4"}))


def stub(action):
    def runner(chal_dir, stage, prompt, env, timeout, stop):
        assert stage == "prebuild" and env["HCTF_PREBUILD"] == "1" and env["HCTF_STAGE"] == "prebuild"
        assert "zz-target" in prompt and "lib/meta/prebuilt/" in prompt and "FIELDS" in prompt, prompt[:300]
        action(stop)
        chal_dir.mkdir(parents=True, exist_ok=True)
        log = chal_dir / "worker-stub.log"
        log.write_text("")
        return 0, log
    return runner


def run_stub(action):
    return prebuild.run("metadata-forensics", n=1, only=["zz-target"], budget_usd=5, log=lambda m: None,
                        runner=stub(action), deadline=datetime.now().replace(year=datetime.now().year + 1))


def clean():
    MOD.unlink(missing_ok=True)
    shutil.rmtree(FIX, ignore_errors=True)
    EVIL.unlink(missing_ok=True)


try:
    clean()
    # a) good module + 2 fixtures (1 decoy) -> kept
    r = run_stub(lambda stop: write_good())
    assert r and r[0]["ok"], r
    assert MOD.exists() and not prebuild.SNAP.exists() and not prebuild.LOCK.exists()
    st = json.loads(prebuild.STATE.read_text())["metadata-forensics:zz-target"]
    assert st["ok"] and st["attempts"] == 1
    clean()
    # b) writes outside the allowlist + a subprocess import -> everything reverted
    def evil(stop):
        write_good()
        MOD.write_text(GOOD.replace("import struct", "import struct\nimport subprocess"))
        EVIL.write_text("x = 1\n")
    r = run_stub(evil)
    assert r and not r[0]["ok"], r
    why = " ".join(r[0]["reasons"])
    assert "allowlist" in why and "hctf/zz_evil_stub.py" in why and "subprocess" in why, why
    assert not MOD.exists() and not FIX.exists() and not EVIL.exists(), "revert left files behind"
    # c) a key that is already verified -> conflict -> reverted
    r = run_stub(lambda stop: (write_good(), MOD.write_text(GOOD.replace(
        '{("zzstub", "header_count"): "header_count"}',
        '{("zzstub", "header_count"): "header_count", ("msi", "product_code_guid"): "header_count"}'))))
    assert r and not r[0]["ok"] and "conflict" in " ".join(r[0]["reasons"]) and not MOD.exists(), r
    # d) a fixture whose expected disagrees with the extractor -> reverted
    def wrong(stop):
        write_good()
        (FIX / "a.json").write_text(json.dumps({"field": "zzstub.header_count", "expected": "8",
                                                "generator_cmd": "printf", "oracle_cmd": "xxd"}))
    r = run_stub(wrong)
    assert r and not r[0]["ok"] and "expected '8'" in " ".join(r[0]["reasons"]) and not MOD.exists(), r
    # e) one fixture only / no decoy / oracle = lib.meta -> reverted
    def thin(stop):
        write_good()
        (FIX / "decoy.json").unlink()
        (FIX / "a.json").write_text(json.dumps({"field": "zzstub.header_count", "expected": "7",
                                                "generator_cmd": "printf", "oracle_cmd": "python3 -m lib.meta"}))
    r = run_stub(thin)
    why = " ".join(r[0]["reasons"])
    assert not r[0]["ok"] and ">= 2 fixtures" in why and "decoy" in why and "independent" in why, why
    # f) nothing written -> not kept; g) stopped mid-target -> snapshot restored, batch ends
    r = run_stub(lambda stop: None)
    assert not r[0]["ok"] and "no change" in r[0]["reasons"][0]
    r = run_stub(lambda stop: (write_good(), stop.set()))
    assert r[0]["reasons"] == ["stopped"] and not MOD.exists() and not FIX.exists()
    # h) attempts cap: the target failed MAX_ATTEMPTS+ times -> skipped by the ranked pending() (not when named)
    cfg = prebuild.LANES["metadata-forensics"]
    tgt = tmp / "targets.json"
    tgt.write_text(json.dumps({"targets": [{"id": "zz-target", "fmt": "zzstub", "fields": ["header_count"]},
                                           {"id": "zz-2", "fmt": "msi", "fields": ["product_code_guid"]}]}))
    cfg_t = dict(cfg, targets=str(tgt.relative_to(ROOT)))
    assert [t["id"] for t in prebuild.pending("metadata-forensics", cfg_t, 5)] == [], "failed + done targets skipped"
    assert [t["id"] for t in prebuild.pending("metadata-forensics", cfg_t, 5, only=["zz-target"])] == ["zz-target"]
    # i) lock: a live holder blocks a second batch
    prebuild.LOCK.write_text(json.dumps({"pid": os.getppid()}))
    assert prebuild.run("metadata-forensics", n=1, only=["zz-target"], log=lambda m: None,
                        runner=stub(lambda s: write_good())) == []
    prebuild.LOCK.unlink()
finally:
    clean()
    prebuild.LANES["metadata-forensics"].clear()
    prebuild.LANES["metadata-forensics"].update(cfg_saved)
    orchestrate.RATCHET_GATE = saved_gate
    for k, v in saved.items():
        setattr(prebuild, k, v)
    shutil.rmtree(tmp, ignore_errors=True)
assert not subprocess.run(["git", "status", "--porcelain", "--", "lib", "hctf/zz_evil_stub.py"], cwd=ROOT,
                          capture_output=True, text=True).stdout.strip().count("zz"), "stub residue in the tree"
print("ok  prebuild gate (stub workers): good module kept; outside-allowlist / subprocess / verified-key conflict / "
      "wrong fixture / thin fixtures / no-op / stop -> lib + tests/data + hctf restored; attempts cap; lock")

# 6) stop(): SIGTERM the lock holder, SIGKILL HCTF_PREBUILD=1 processes, recover the snapshot
tmp = Path(tempfile.mkdtemp(prefix="s3stop-", dir=paths.TMP))
saved = {k: getattr(prebuild, k) for k in ("LOCK", "SNAP")}
prebuild.LOCK, prebuild.SNAP = tmp / "lock", tmp / "snap"
try:
    batch = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(60)"])
    worker = subprocess.Popen(["sleep", "60"], env=dict(os.environ, HCTF_PREBUILD="1"))
    prebuild.LOCK.write_text(json.dumps({"pid": batch.pid}))
    assert prebuild.lock_holder() == batch.pid and worker.pid in prebuild._worker_pids()
    t0 = time.time()
    assert prebuild.stop(log=lambda m: None, grace=3) is True
    assert batch.wait(5) is not None and worker.wait(5) is not None and time.time() - t0 < 10
    assert not prebuild.LOCK.exists() and prebuild.lock_holder() is None
    assert prebuild.stop(log=lambda m: None) is False          # nothing running: instant no-op
finally:
    for p in (batch, worker):
        if p.poll() is None:
            p.kill()
    for k, v in saved.items():
        setattr(prebuild, k, v)
    shutil.rmtree(tmp, ignore_errors=True)
day_sh = (ROOT / "bin" / "day.sh").read_text()
assert "hctf.cli prebuild --stop" in day_sh and day_sh.index("prebuild --stop") < day_sh.index("# 3) Launch the sweep")
print("ok  prebuild --stop: batch SIGTERM, workers SIGKILL, lock cleared; bin/day.sh stops it before pre-flight")

# 7) post-run hook: launch_background command line, skips (lock held / too close to the drop), wired after ratchet
calls = []


class FakePopen:
    def __init__(self, cmd, **kw):
        calls.append((cmd, kw))


saved_dl = prebuild.default_deadline
try:
    prebuild.default_deadline = lambda now=None: datetime.now().replace(microsecond=0) + timedelta(hours=5)
    p = prebuild.launch_background(14, log=lambda m: None, popen=FakePopen)
    assert p is not None and len(calls) == 1
    cmd, kw = calls[0]
    assert "hctf.cli prebuild --lane metadata-forensics" in cmd[2] and "--budget-usd" in cmd[2] and "--deadline" in cmd[2]
    assert kw.get("start_new_session") is True
    prebuild.default_deadline = lambda now=None: datetime.now() + timedelta(minutes=5)
    assert prebuild.launch_background(14, log=lambda m: None, popen=FakePopen) is None and len(calls) == 1
finally:
    prebuild.default_deadline = saved_dl
src = inspect.getsource(orchestrate.run)
assert src.index("ratchet(day)") < src.index("launch_background(day") and orchestrate.PREBUILD_AFTER_RATCHET
assert "tests/test_meta_lane.py" in orchestrate.RATCHET_GATE
rp = (ROOT / "hctf" / "prompts" / "ratchet.md").read_text()
assert "PROMOTE" in rp and "lib/meta" in rp and "warmups_codecs" in rp and "test_meta_lane" in rp
assert orchestrate.prebuild.__doc__ and "ratchet()" in orchestrate.prebuild.__doc__
print("ok  post-run hook: detached `hctf prebuild` per lane after ratchet (budget + deadline args), skipped near the "
      "drop; ratchet prompt promotes prebuilt -> verified; test_meta_lane in RATCHET_GATE")

# 8) prompt render: registry + msi example + writable paths, no unreplaced placeholders
txt = prebuild._render("metadata-forensics", prebuild.LANES["metadata-forensics"],
                       {"id": "cab", "fmt": "cab", "fields": ["cfheader_folder_count"]}, 5.0, datetime(2026, 10, 14, 20, 30))
for need in ("msi.product_code_guid: verified (GM-verified D13)", "def property_value", "`lib/meta/prebuilt/`",
             "cfheader_folder_count", "20:30", "python3 tests/test_meta_lane.py"):
    assert need in txt, need
for ph in ("{lane}", "{target}", "{brief}", "{registry}", "{example}", "{writable}", "{gate}", "{minutes}"):
    assert ph not in txt, ph
assert prebuild.enabled_lanes()[0] == "metadata-forensics"
print("ok  prebuild prompt renders (registry with tiers, verified MSI example, allowlist, gate, deadline)")

# 9) lane seed: metadata single starts from the lane solver; other lanes keep the skeleton
assert orchestrate.lane_seed_dir("metadata-forensics") == LANE
assert orchestrate.lane_seed_dir("binary-reverse-engineering") is None and orchestrate.lane_seed_dir("warmups") is None
saved_seed = orchestrate.LANE_SEED_LANES
orchestrate.LANE_SEED_LANES = set()
assert orchestrate.lane_seed_dir("metadata-forensics") is None
orchestrate.LANE_SEED_LANES = saved_seed
sd = paths.CHALLENGES / "day99" / "metadata-s3-seedtest" / "solver"
try:
    orchestrate.stage_prior_solver(LANE, sd, cases=False)
    assert (sd / "solve.py").read_bytes() == (LANE / "solve.py").read_bytes()
    note = orchestrate.lane_seed_note(LANE, sd)
    assert "local_answer()" in note and "challenges/day99/metadata-s3-seedtest/solver/solve.py" in note
    case = next(paths.CHALLENGES.glob("day12/metadata-*/solver/cases/single_solve"))
    got, err, _ = solvers.run_solver(sd, json.loads((case / "contract.json").read_text()), case / "artifacts")
    assert not err and got == json.loads((case / "expected.json").read_text()), (got, err)
finally:
    shutil.rmtree(sd.parent.parent, ignore_errors=True)
src = inspect.getsource(orchestrate.Chain)
assert "lane_seed_dir(self.lane)" in src and "self._lane_seed_note" in src
print("ok  lane seed: metadata solver dir seeded from challenges/_lane (runs at a dayNN depth), note names "
      "local_answer(); HCTF_LANE_SEED_LANES empty -> skeleton")

# 10) bin/fair_run.sh: directory overlays + _lane sync + HCTF_META_MAX_DAY (syntax + the overlay loop on a scratch repo)
fr = (ROOT / "bin" / "fair_run.sh").read_text()
assert subprocess.run(["bash", "-n", str(ROOT / "bin" / "fair_run.sh")]).returncode == 0
assert 'cat-file -t "HEAD:$f"' in fr and "challenges/_lane" in fr and "HCTF_META_MAX_DAY={day}" in fr
loop = fr[fr.index('for f in "${OVERLAYS[@]}"'):]
loop = loop[:loop.index("\ndone") + 5]
with tempfile.TemporaryDirectory() as d:
    main, alt = Path(d) / "main", Path(d) / "alt"
    (main / "lib" / "meta").mkdir(parents=True)
    (main / "lib" / "meta" / "a.py").write_text("A=1\n")
    (main / "lib" / "common.py").write_text("C=1\n")
    g = ["git", "-C", str(main), "-c", "user.email=t@t", "-c", "user.name=t"]
    subprocess.run(["git", "init", "-q", str(main)], check=True)
    subprocess.run(g + ["add", "-A"], check=True)
    subprocess.run(g + ["commit", "-qm", "x"], check=True)
    (alt / "lib" / "meta").mkdir(parents=True)
    (alt / "lib" / "meta" / "stale.py").write_text("S=1\n")
    script = f'set -euo pipefail\nMAIN={main}\nALT={alt}\nOVERLAYS=(lib/meta/ lib/common.py)\n{loop}\n'
    r = subprocess.run(["bash", "-c", script], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    assert (alt / "lib" / "meta" / "a.py").read_text() == "A=1\n" and not (alt / "lib" / "meta" / "stale.py").exists()
    assert (alt / "lib" / "common.py").read_text() == "C=1\n" and "overlay (HEAD, dir): lib/meta" in r.stdout
print("ok  fair_run.sh: overlays take files AND directories (replaced whole), challenges/_lane synced, "
      "HCTF_META_MAX_DAY=<day> in the env block")
print("all S3 checks passed")
