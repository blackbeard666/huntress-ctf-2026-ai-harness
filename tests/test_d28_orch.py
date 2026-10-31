"""D28 post-mortem orchestrator items (reference/D28_POSTMORTEM.md #1 #2 #4 #5 #6 #9 #11 #14 + the hardlink-corruption
fix), offline: fakes only -- no GM, no LLM, no live target.

 #1  answer-first on the prior-solver dry run's RESIDUAL (392 ids, 31 empty -> eligible), sharded by dNN_ family
 #2  the READY warm worker gets its go at the download mark; triage / prior note follow via the inbox; sub-marks
 #4  cross-format check: a field answered on the single's ELF member but EMPTY on a PE member of the same family
 #5  a live TT pass no longer waits for the generalize's transactional judgement (background; reject applied later)
 #6  off-path work waits while the chain's timed pre-start downloads; download concurrency knob
 #9  a web kick answered prerequisite_required keeps no once-per-chain claim
 #11 lane-aware baseline case timeout (web >= 20 s)
 #14 the first web TT waits (bounded) for a codify worker still writing the plugin
 hardlinks: safe_place never writes into an existing (hardlinked) dst; stage_prior_cases skips today's case names

Run:  source bin/env.sh && .venv/bin/python tests/test_d28_orch.py      (exit 0 = all pass)
"""
import contextlib
import inspect
import json
import os
import shutil
import sys
import tempfile
import threading
import time
import zipfile
from concurrent.futures import Future
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ["HCTF_ANSWER_FIRST"] = "1"
from hctf import cli, duel, inbox, orchestrate  # noqa: E402

failures = []


def check(name, cond, detail=""):
    print(("ok  " if cond else "FAIL ") + name + ("" if cond else f"  -- {str(detail)[:600]}"))
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


TD = Path(tempfile.mkdtemp(prefix="d28orch-", dir=str(ROOT / ".run")))
said = []
QUIET = {(orchestrate, "say"): lambda *a, **k: said.append(a[0] if a else "")}


def bare_chain(lane="binary-reverse-engineering", base="binary-reverse-engineering-day-28-x", chal="binary-x"):
    ch = orchestrate.Chain.__new__(orchestrate.Chain)
    ch.lane, ch.base, ch.name = lane, base, chal
    ch.entries = {"single_solve": {"id": base}, "time_trial": {"id": f"{base}/time_trial"},
                  "mastery": {"id": f"{base}/mastery"}}
    ch.root = TD / "challenges" / "day28" / chal
    ch.sdir = ch.root / "solver"
    ch.sdir.mkdir(parents=True, exist_ok=True)
    return ch


# ------------------------------------------------------------------ hardlink corruption (coordinator item)
hl = TD / "hl"
(hl / "src" / "artifacts").mkdir(parents=True)
(hl / "other").mkdir()
(hl / "dst" / "artifacts").mkdir(parents=True)
(hl / "src" / "artifacts" / "evidence.zip").write_bytes(b"PRIOR-DAY BYTES")
(hl / "other" / "evidence.zip").write_bytes(b"TODAY BYTES (shared inode with the rehearsal tree)")
os.link(hl / "other" / "evidence.zip", hl / "dst" / "artifacts" / "evidence.zip")   # dst is a hardlink of `other`
(hl / "src" / "contract.json").write_text('{"prior": 1}')
(hl / "other" / "contract.json").write_text('{"today": 1}')
os.link(hl / "other" / "contract.json", hl / "dst" / "contract.json")
shutil.copytree(hl / "src", hl / "dst", dirs_exist_ok=True, copy_function=orchestrate._link_or_copy)
check("hardlink: copy over an existing hardlinked artifact leaves the OTHER link's bytes untouched",
      (hl / "other" / "evidence.zip").read_bytes() == b"TODAY BYTES (shared inode with the rehearsal tree)",
      (hl / "other" / "evidence.zip").read_bytes())
check("hardlink: ... and the dst now carries src's bytes (replaced, via a new inode)",
      (hl / "dst" / "artifacts" / "evidence.zip").read_bytes() == b"PRIOR-DAY BYTES"
      and os.stat(hl / "dst" / "artifacts" / "evidence.zip").st_ino == os.stat(hl / "src" / "artifacts" / "evidence.zip").st_ino)
check("hardlink: a non-artifact file over an existing hardlinked dst is replaced, the other link untouched",
      (hl / "other" / "contract.json").read_text() == '{"today": 1}' and (hl / "dst" / "contract.json").read_text() == '{"prior": 1}')
check("hardlink: no temp files left behind", not list((hl / "dst").rglob(".*place-*")), list((hl / "dst").rglob("*")))
orchestrate.safe_place(hl / "src" / "artifacts" / "evidence.zip", hl / "dst" / "artifacts" / "evidence.zip")
check("hardlink: same inode already -> no-op", (hl / "dst" / "artifacts" / "evidence.zip").read_bytes() == b"PRIOR-DAY BYTES")
# duel's copy and today_probe's helper use the same rule
(hl / "duelsrc" / "cases" / "c1" / "artifacts").mkdir(parents=True)
(hl / "duelsrc" / "cases" / "c1" / "artifacts" / "a.bin").write_bytes(b"A")
from hctf import today_probe  # noqa: E402
(hl / "tp_other").write_bytes(b"KEEP")
os.link(hl / "tp_other", hl / "tp_dst")
(hl / "tp_src").write_bytes(b"NEW")
today_probe._link_or_copy(hl / "tp_src", hl / "tp_dst")
check("hardlink: today_probe._link_or_copy over an existing hardlinked dst keeps the other link",
      (hl / "tp_other").read_bytes() == b"KEEP" and (hl / "tp_dst").read_bytes() == b"NEW")
check("hardlink: duel's link_or_copy delegates to orchestrate.safe_place",
      "safe_place" in inspect.getsource(duel._copy_solver) if hasattr(duel, "_copy_solver") else False)

# stage_prior_cases: a prior-day case never overwrites today's same-named case
prior = TD / "prior" / "solver"
(prior / "cases" / "single_solve" / "artifacts").mkdir(parents=True)
(prior / "cases" / "single_solve" / "artifacts" / "evidence.zip").write_bytes(b"YESTERDAY")
(prior / "cases" / "single_solve" / "expected.json").write_text('{"a": "yesterday"}')
(prior / "cases" / "auto-mastery-aaaa" / "artifacts").mkdir(parents=True)
(prior / "cases" / "auto-mastery-aaaa" / "artifacts" / "evidence.zip").write_bytes(b"M")
today = TD / "today" / "solver"
(today / "cases" / "single_solve" / "artifacts").mkdir(parents=True)
(today / "cases" / "single_solve" / "artifacts" / "evidence.zip").write_bytes(b"TODAY")
(today / "cases" / "single_solve" / "expected.json").write_text('{"a": "today"}')
with patched(QUIET):
    orchestrate.stage_prior_cases(prior, today)
check("stage_prior_cases: today's single_solve case is kept (bytes + expected)",
      (today / "cases" / "single_solve" / "artifacts" / "evidence.zip").read_bytes() == b"TODAY"
      and json.loads((today / "cases" / "single_solve" / "expected.json").read_text()) == {"a": "today"})
check("stage_prior_cases: ... and the prior's case dirs new to today are copied (artifacts hardlinked)",
      (today / "cases" / "auto-mastery-aaaa" / "artifacts" / "evidence.zip").read_bytes() == b"M"
      and os.stat(today / "cases" / "auto-mastery-aaaa" / "artifacts" / "evidence.zip").st_nlink >= 2)
check("stage_prior_cases: the prior's own case is untouched",
      (prior / "cases" / "single_solve" / "artifacts" / "evidence.zip").read_bytes() == b"YESTERDAY")

# ------------------------------------------------------------------ #1 answer-first residual + shards
ids = ([f"d{d:02d}_analysis_f{i}" for d in range(1, 28) for i in range(14)] + [f"d28_new_{i}" for i in range(14)])[:392]
residual = [a for a in ids if a.startswith(("d10_", "d17_", "d28_"))][:31]
check("#1 af_shard_count: <= SHARD_MIN residual = one worker, 31 = up to SHARDS",
      orchestrate.af_shard_count(12) == 1 and orchestrate.af_shard_count(31) == orchestrate.AF_SHARDS,
      (orchestrate.af_shard_count(12), orchestrate.af_shard_count(31)))
sh = orchestrate.shard_fields(residual, 3)
check("#1 shard_fields: 3 shards covering every residual id exactly once",
      len(sh) == 3 and sorted(a for s_ in sh for a in s_) == sorted(residual), sh)
check("#1 shard_fields: a family stays in one shard when it fits an even share",
      all(len({orchestrate._family_prefix(a) for a in s_}) >= 1 for s_ in sh)
      and sum(1 for s_ in sh if any(a.startswith("d28_") for a in s_)) == 1, sh)
check("#1 _family_prefix: dNN_ / setN_dNN_ / no prefix",
      (orchestrate._family_prefix("d10_analysis_section_count"), orchestrate._family_prefix("set3_d07_x"),
       orchestrate._family_prefix("flag")) == ("d10", "d07", "today"))

AF = TD / "af"
CDIR = AF / "chal" / "single_solve"
CDIR.mkdir(parents=True)
CID = "binary-reverse-engineering-day-28-af"
start = {"attempt_id": "att-28", "answer_ids": ids,
         "questions": [{"id": a, "question": f"q {a}", "artifact": "evidence.zip", "answer_format": {"kind": "integer"}}
                       for a in ids]}
(CDIR / "start.json").write_text(json.dumps(start))
(CDIR / "triage.md").write_text("# triage\n\n## STATUS\n- evidence.zip\n")
(CDIR / "artifacts" / "1").mkdir(parents=True)
(CDIR / "artifacts" / "latest").symlink_to(CDIR / "artifacts" / "1")
calls, lock = [], threading.Lock()


def fake_run_worker(cid, stage, prompt, timeout, urgent=False, prefer_homebase=False, stop=None, warm=None,
                    warm_task=None, env_extra=None, force_local=False):
    with lock:
        calls.append({"stage": stage, "env": dict(env_extra or {}), "prompt": prompt, "stop": stop})
    stop.wait(8)
    return 0


dry = Future()
dry.set_result({"seconds": 1.5, "timed_out": False, "error": "", "answered": 392 - len(residual), "total": 392,
                "empty": residual[:15], "empty_all": residual})
chain = SimpleNamespace(lane="binary-reverse-engineering", base=CID, sdir=AF / "chal" / "solver", root=AF / "chal",
                        run_worker=fake_run_worker, _dry_fut=dry, _deliver_note=lambda *a, **k: None)
chain.sdir.mkdir(parents=True, exist_ok=True)
with patched({**QUIET, (cli, "cdir"): lambda cid: CDIR, (orchestrate.timed, "latest_artifacts"): lambda cid: CDIR / "artifacts" / "1",
              (orchestrate, "ANSWER_FIRST_RACE_WAIT"): 0.0}):
    ok_all, why_all = orchestrate.answer_first_eligible("binary-reverse-engineering", 392)
    check("#1 (D28 refusal) 392 fields is over the cap", not ok_all and "cap" in why_all, why_all)
    af = orchestrate.AnswerFirst(chain, CID)
    fields, rwhy = af._residual()
    check("#1 _residual = the dry run's full empty list (empty_all), not every id", fields == residual and "residual" in rwhy,
          (len(fields), rwhy))
    (CDIR / "confirmed.json").write_text(json.dumps({"att-28": {residual[0]: "1"}}))
    fields2, _ = af._residual()
    check("#1 _residual drops ids the GM already confirmed", fields2 == residual[1:], len(fields2))
    (CDIR / "confirmed.json").unlink()
    # truncated list (no empty_all) -> the full residual is re-derived by one prior-solver run
    dry2 = Future()
    dry2.set_result({"seconds": 1.5, "timed_out": False, "error": "", "answered": 392 - len(residual), "total": 392,
                     "empty": residual[:15]})
    chain._dry_fut, chain._dry_prior = dry2, AF / "prior"
    with patched({(orchestrate.solvers, "run_solver"):
                  lambda sdir, c, art, timeout=0, background=None: ({a: "1" for a in ids if a not in residual}, None, 1.0)}):
        fields3, _ = af._residual()
    check("#1 a truncated dry-run list is completed by a re-run (diagnostic only)", fields3 == residual, len(fields3))
    chain._dry_fut = dry
    af.start(race_done=None)
    for _ in range(50):
        if len(calls) >= 3:
            break
        time.sleep(0.1)
    pools = sorted(c["env"].get("HCTF_LOG_POOL") for c in calls)
    check("#1 31 residual fields -> 3 parallel answer-first shards (distinct log pools)",
          pools == ["answer-first", "answer-first-2", "answer-first-3"], (pools, said[-4:]))
    lf = json.loads((CDIR / ".live_fields.json").read_text())
    check("#1 .live_fields.json = the residual (stop gate), not all 392 ids", lf["fields"] == residual, len(lf["fields"]))
    per = [json.loads(p.read_text())["fields"] for p in sorted(CDIR.glob(".live_fields-af*.json"))]
    check("#1 per-shard field files (HCTF_LIVE_FIELDS_FILE) partition the residual",
          len(per) == 3 and sorted(a for x in per for a in x) == sorted(residual)
          and all(c["env"].get("HCTF_LIVE_FIELDS_FILE") for c in calls), per)
    mine = {c["env"]["HCTF_LOG_POOL"]: c for c in calls}
    s1 = json.loads((CDIR / ".live_fields-af1.json").read_text())["fields"]
    p1 = mine["answer-first"]["prompt"]
    check("#1 each shard's prompt lists ONLY its own fields + the shard / residual notes",
          all(f"`{a}`" in p1 for a in s1) and not any(f"`{a}`" in p1 for a in residual if a not in s1)
          and "PARALLEL SHARD 1/3" in p1 and "RESIDUAL ONLY" in p1 and "`d01_analysis_f0`" not in p1, p1[-900:])
    check("#1 shards run at the answer-first effort (medium: user rule exception)",
          all(c["env"].get("HCTF_X_EFFORT") == (orchestrate.AF_SHARD_EFFORT or orchestrate.ANSWER_FIRST_EFFORT) for c in calls))
    # a shard whose own fields are all confirmed is ended; the others keep going
    (CDIR / "confirmed.json").write_text(json.dumps({"att-28": {a: "1" for a in s1}}))
    time.sleep(2.0)
    nn = [t_ for t_ in inbox.texts(CDIR) if "already CONFIRMED" in t_]
    check("#1 residual fields confirmed by another source -> a live-* narrowing note (LiveAnswer.narrow rule)",
          nn and all(a in nn[-1] for a in s1[:3]),
          inbox.texts(CDIR)[-2:])
    check("#1 a shard is ended once ITS fields are confirmed (the others run on)",
          mine["answer-first"]["stop"].is_set() and not mine["answer-first-2"]["stop"].is_set(),
          [c["stop"].is_set() for c in calls])
    af.stop_evt.set()
    af.done.wait(10)
    check("#1 stop_evt ends every shard; the concurrency slots are released",
          all(c["stop"].is_set() for c in calls) and not any(k.startswith(CID) for k in orchestrate._af_live),
          orchestrate._af_live)
    (CDIR / "confirmed.json").unlink()
    # kill switch: HCTF_AF_RESIDUAL=0 -> every id (and the 80-field cap refuses it, as on D28)
    calls.clear()
    with patched({(orchestrate, "AF_RESIDUAL"): False}):
        af0 = orchestrate.AnswerFirst(chain, CID)
        af0._run(None)
    check("#1 kill switch HCTF_AF_RESIDUAL=0: the old all-ids refusal", not calls
          and any("392 fields" in s for s in said[-3:]), said[-3:])
    # small residual -> one worker, no shard files
    for p in CDIR.glob(".live_fields-af*.json"):
        p.unlink()
    dry_s = Future()
    dry_s.set_result({"timed_out": False, "error": "", "answered": 389, "total": 392, "empty": residual[:3]})
    chain._dry_fut = dry_s
    calls.clear()
    af1 = orchestrate.AnswerFirst(chain, CID)
    threading.Timer(1.0, af1.stop_evt.set).start()
    af1._run(None)
    check("#1 3-field residual -> ONE answer-first worker on those 3 fields",
          len(calls) == 1 and calls[0]["env"]["HCTF_LOG_POOL"] == "answer-first"
          and json.loads((CDIR / ".live_fields.json").read_text())["fields"] == residual[:3]
          and not list(CDIR.glob(".live_fields-af*.json")), [c["env"] for c in calls])
src_single = inspect.getsource(orchestrate.Chain._single)
check("#1 the launch site no longer refuses on len(af.ids) when a dry run exists",
      "AF_RESIDUAL" in src_single and "_dry_fut" in src_single)

# ------------------------------------------------------------------ #2 go at the download mark
ch2 = bare_chain(lane="binary-reverse-engineering", base="binary-reverse-engineering-day-28-go", chal="binary-go")
GO = TD / "go"
(GO / "artifacts" / "1").mkdir(parents=True)
(GO / "start.json").write_text(json.dumps({"attempt_id": "a1", "answer_ids": ["x"]}))


class FakeWarm:
    def __init__(self):
        self.sent, self.cancelled = [], False
        self.log, self.p, self.out, self.started = GO / "w.log", None, None, time.time()

    def alive(self):
        return True

    def send_task(self, text):
        self.sent.append(text)

    def cancel(self):
        self.cancelled = True


warm = FakeWarm()
ch2._warm = warm
ch2._go_lock, ch2._go_sent, ch2._go_pending = threading.Lock(), False, ["EARLY NOTE"]
ch2._chain_t0 = time.time() - 24.0
staged = Future()
staged.set_result(ch2.sdir)
with patched({**QUIET, (cli, "cdir"): lambda cid: GO, (orchestrate.timed, "latest_artifacts"): lambda cid: GO / "artifacts" / "1",
              (orchestrate, "prior_solver_dir"): lambda lane, sdir: TD / "prior" / "solver"}):
    st = ch2._early_go("binary-reverse-engineering-day-28-go", False, staged, {"answer_ids": ["x"]})
    st["evt"].wait(5)
    check("#2 the READY warm worker got its go at the download mark (staged solver awaited first)",
          st["ok"] and len(warm.sent) == 1 and warm.sent[0].startswith("GO.") and "ALREADY copied" in warm.sent[0]
          and "EARLY NOTE" in warm.sent[0], (st, warm.sent[:1]))
    check("#2 ... after which late facts go to the inbox (go_sent)", ch2._go_sent and ch2._go_pending == [])
    posted = []
    with patched({(inbox, "post"): lambda d, text, key="": posted.append((key, text))}):
        ch2._deliver_note("binary-reverse-engineering-day-28-go", "DRY RUN late", key="dry-run")
    check("#2 a late dry-run note goes to the worker's inbox", posted == [("dry-run", "DRY RUN late")], posted)
    # no warm worker / welcome / no body -> no early go (the old path)
    ch2._warm = None
    check("#2 no warm worker -> no early go", ch2._early_go("c", False, staged, {"x": 1}) is None)
    ch2._warm = warm
    check("#2 welcome / body None -> no early go",
          ch2._early_go("c", True, staged, {"x": 1}) is None and ch2._early_go("c", False, staged, None) is None)
    with patched({(orchestrate, "GO_AT_DL"): False}):
        check("#2 kill switch HCTF_GO_AT_DL=0", ch2._early_go("c", False, staged, {"x": 1}) is None)
    # a staging copy that does not finish in time -> no early go, normal path
    ch2._go_sent = False
    slow = Future()
    with patched({(orchestrate, "GO_AT_DL_STAGE_WAIT"): 0.2}):
        st2 = ch2._early_go("c", False, slow, {"x": 1})
        st2["evt"].wait(3)
    check("#2 staging not done in time -> no early go (go_sent stays False)", st2["ok"] is False and not ch2._go_sent, st2)
sw = orchestrate._SentWarm(warm)
n0 = len(warm.sent)
sw.send_task("SECOND GO")
check("#2 _SentWarm: run_local's send_task is a no-op; everything else delegates",
      len(warm.sent) == n0 and sw.alive() and sw.log == warm.log)
src = inspect.getsource(orchestrate.Chain._single)
check("#2 _single: staging + the early go come BEFORE the tool prefetch / dry run / race start",
      src.index("self._early_go(") < src.index("self._tool_prefetch(cid, (body or {}))") < src.index("self._start_prior_dry_run(cid)"))
check("#2 _single: an early go keeps the inbox (no reset) and posts the follow-up (go-late)",
      "if not early_ok:" in src and 'key="go-late"' in src and "_SentWarm(warm)" in src)
ch2._pre_t = {"dl": 100.0, "stage": 100.2, "tp": 101.0, "dry": 117.0, "race": 117.1, "flag": 117.1, "tri0": 117.2,
              "tri1": 118.0}
ch2._chain_t0 = 76.0
split = ch2._prelude_split()
check("#2 pre-triage sub-marks name each step (dry-run start 16.0s here)",
      "pre-triage:" in split and "dry-run start 16.0s" in split and "tool-prefetch 0.8s" in split and "staging 0.2s" in split,
      split)
check("#2 shadow / duel / answer-first start beside the worker launch (LAUNCH_PREP_ASYNC)",
      "LAUNCH_PREP_ASYNC" in src and "target=side_workers" in src and "prep_thr.join" in src)

# ------------------------------------------------------------------ #4 cross-format check
XF = TD / "xf" / "solver"
(XF / "cases").mkdir(parents=True)
(XF / "solve.py").write_text('''import argparse, json, zipfile, os
ap = argparse.ArgumentParser(); ap.add_argument("--contract"); ap.add_argument("--artifacts"); a = ap.parse_args()
c = json.load(open(a.contract)); z = zipfile.ZipFile(os.path.join(a.artifacts, "evidence.zip"))
names = z.namelist(); out = {}
for i in c["answer_ids"]:
    fam = i.split("_")[0]
    mem = next((n for n in names if n.startswith(fam + "--")), None)
    if mem is None:
        continue
    if i.endswith("_sha"):
        out[i] = "ab"
    elif i.endswith("_section_count") and z.read(mem)[:4] == b"\\x7fELF":
        out[i] = "12"           # ELF-only handler (the D28 bug)
print(json.dumps(out))
''')


def mk_case(name, members, ids, expected):
    d = XF / "cases" / name
    (d / "artifacts").mkdir(parents=True)
    with zipfile.ZipFile(d / "artifacts" / "evidence.zip", "w") as z:
        for n, data in members.items():
            z.writestr(n, data)
    (d / "contract.json").write_text(json.dumps({"answer_ids": ids, "questions": [{"id": i, "artifact": "evidence.zip"}
                                                                                  for i in ids]}))
    (d / "expected.json").write_text(json.dumps(expected))


ELF, PE = b"\x7fELF" + b"\0" * 60, b"MZ" + b"\0" * 62
mk_case("single_solve", {"d10--sample.elf": ELF, "d11--x.elf": ELF}, ["d10_sha", "d10_section_count", "d11_sha"],
        {"d10_sha": "ab", "d10_section_count": "12", "d11_sha": "ab"})
mk_case("auto-time_trial-pe", {"d10--sample.exe": PE, "d11--x.elf": ELF}, ["d10_sha", "d11_sha"],
        {"d10_sha": "ab", "d11_sha": "ab"})
mk_case("auto-mastery-elf", {"d10--sample.elf": ELF}, ["d10_sha"], {"d10_sha": "ab"})
with patched(QUIET):
    txt, xcases, summ = orchestrate.xfmt_probe(XF, budget=30, out_dir=TD / "xf" / "out")
check("#4 cross-format check flags the field answered on ELF but EMPTY on the PE member of the same family",
      "d10_section_count" in txt and "pe" in txt and len(xcases) == 1 and summ["flagged"] == 1, (txt, summ))
c0 = json.loads((xcases[0] / "contract.json").read_text()) if xcases else {}
check("#4 the xfmt-* case is an unverified fill case on exactly the flagged field, bytes hardlinked",
      xcases and xcases[0].name.startswith("xfmt-d10-") and c0.get("answer_ids") == ["d10_section_count"]
      and json.loads((xcases[0] / "expected.json").read_text()) == {}
      and os.stat(xcases[0] / "artifacts" / "evidence.zip").st_ino
      == os.stat(XF / "cases" / "auto-time_trial-pe" / "artifacts" / "evidence.zip").st_ino, c0)
check("#4 the corpus' own case files are untouched (read-only probe)",
      json.loads((XF / "cases" / "auto-time_trial-pe" / "expected.json").read_text()) == {"d10_sha": "ab", "d11_sha": "ab"})
check("#4 same-format members are not flagged (d11 is ELF everywhere)", "d11" not in txt, txt)
# _late_probes: untimed evidence -> held for the failure generalize (no pre-TT generalize); clocked -> pre-TT diag
ch4 = bare_chain(chal="binary-xf")
ch4.sdir = XF
fut = Future()
fut.set_result((txt, xcases, summ))
adopted = []
base_late = {(orchestrate.Chain, "_handoff_join"): lambda self, why: None,
             (orchestrate.Chain, "_family_pre_result"): lambda self, wait=True: ("", []),
             (orchestrate.Chain, "_mutation_pre_result"): lambda self, wait=True: ("", []),
             (orchestrate.Chain, "_compound_pre_result"): lambda self, wait=True: ("", []),
             (orchestrate.Chain, "_adopt_xfmt_cases"): lambda self, cds: adopted.extend(cds) or len(cds)}
with patched({**QUIET, **base_late, (orchestrate.Chain, "_untimed_evidence"): lambda self: True}):
    ch4._xfmt_fut, ch4._late_held = fut, None
    pre = ch4._late_probes("binary-reverse-engineering-day-28-x/time_trial", wait=False)
check("#4 no clock: the gap is HELD for a failure generalize, not a pre-TT generalize",
      "xfmt_pre" not in pre and "xfmt_pre" in (ch4._late_held or {}) and adopted, (pre, ch4._late_held))
with patched({**QUIET, **base_late, (orchestrate.Chain, "_untimed_evidence"): lambda self: False}):
    ch4._xfmt_fut, ch4._late_held, ch4._xfmt_late_done = fut, None, False
    pre = ch4._late_probes("binary-reverse-engineering-day-28-x/time_trial", wait=False)
check("#4 clocked TT: the gap feeds the pre-TT harden diag", "xfmt_pre" in pre, pre)
check("#4 the generalize prompt renders the xfmt_pre diag", "CROSS-FORMAT GAP" in inspect.getsource(orchestrate.Chain))
check("#4 started beside the mutation probe (single's final solver), lane-gated",
      "_start_xfmt_pre" in inspect.getsource(orchestrate.Chain._start_mutation_pre)
      and "binary-reverse-engineering" in orchestrate.XFMT_LANES)

# ------------------------------------------------------------------ #5 background post-live accept
ch5 = bare_chain(chal="binary-acc")
(ch5.sdir / "cases" / "c1").mkdir(parents=True, exist_ok=True)
(ch5.sdir / "solve.py").write_text("# edited by the generalize worker\n")
snap = ch5._snap_dir()
shutil.copytree(ch5.sdir, snap)
(snap / "solve.py").write_text("# pre-worker\n")


class FakeGB:
    def __init__(self, res, delay=0.0):
        self.res, self.delay, self.cancelled = res, delay, False

    def join(self):
        time.sleep(self.delay)
        return self.res

    def cancel(self):
        self.cancelled = True


replays = []


def fake_test_solver(sdir, timeout=None, **k):
    replays.append((str(sdir), timeout))
    time.sleep(0.3)
    return [{"case": "c1", "ok": FAKE_OK[0]}]


FAKE_OK = [True]
env5 = {**QUIET, (orchestrate.solvers, "test_solver"): fake_test_solver,
        (orchestrate.Chain, "_prefetch_mastery_start"): lambda self: None,
        (orchestrate.procgov, "bg_wrap"): lambda fn, on=True, owner_tag=None: fn}
with patched(env5):
    ch5._gen_base = FakeGB([{"case": "c1", "ok": True}], delay=1.0)
    t0 = time.time()
    ch5._accept_after_live("binary-reverse-engineering-day-28-x/time_trial", "time_trial")
    dt = time.time() - t0
    check("#5 a live TT pass returns at once (judgement in the background)", dt < 0.5 and snap.exists(), f"{dt:.2f}s")
    check("#5 ... Mastery's start applies only a FINISHED verdict (never waits)",
          ch5._live_accept_join("the mastery start", wait=0) is None and snap.exists())
    v = ch5._live_accept_join("the chain's end", wait=10)
    check("#5 accepted edits: the snapshot is dropped, the edited solver stays",
          v == "accept" and not snap.exists() and "edited" in (ch5.sdir / "solve.py").read_text(), v)
    # reject: applied on the chain thread; a case recorded after the pass is carried into the restored solver
    shutil.copytree(ch5.sdir, snap)
    (snap / "solve.py").write_text("# pre-worker\n")
    FAKE_OK[0] = False
    ch5._gen_base = FakeGB([{"case": "c1", "ok": True}])
    ch5._accept_after_live("binary-reverse-engineering-day-28-x/time_trial", "time_trial")
    time.sleep(0.05)
    (ch5.sdir / "cases" / "auto-mastery-new").mkdir()
    (ch5.sdir / "cases" / "auto-mastery-new" / "expected.json").write_text("{}")
    ch5._live_accept["done"].wait(5)
    check("#5 a reject is NOT applied by the background thread (the next mode's runner may be reading the dir)",
          "edited" in (ch5.sdir / "solve.py").read_text() and snap.exists())
    v = ch5._live_accept_join("a new generalize")
    check("#5 ... it is applied at the chain's next safe point: pre-worker solver restored",
          v == "reject" and "pre-worker" in (ch5.sdir / "solve.py").read_text() and not snap.exists(), v)
    check("#5 ... keeping the case the next mode recorded meanwhile",
          (ch5.sdir / "cases" / "auto-mastery-new" / "expected.json").exists())
    # a judgement still running when a generalize needs the snapshot -> abandoned, known-good restored
    shutil.copytree(ch5.sdir, snap)
    (ch5.sdir / "solve.py").write_text("# edited again\n")
    FAKE_OK[0] = True
    gb = FakeGB([{"case": "c1", "ok": True}], delay=3.0)
    ch5._gen_base = gb
    ch5._accept_after_live("binary-reverse-engineering-day-28-x/time_trial", "time_trial")
    v = ch5._live_accept_join("a new generalize", wait=0.3)
    check("#5 judgement still running at a new generalize -> abandoned, pre-worker solver restored",
          v == "reject" and gb.cancelled and "pre-worker" in (ch5.sdir / "solve.py").read_text(), v)
    with patched({(orchestrate, "LIVE_ACCEPT_BG"): False}):
        shutil.copytree(ch5.sdir, snap)
        (ch5.sdir / "solve.py").write_text("# edited once more\n")
        called = []
        with patched({(orchestrate.Chain, "_accept_or_restore"): lambda self, cid, case_timeout=None: called.append(1)}):
            ch5._accept_after_live("x/time_trial", "time_trial")
        check("#5 kill switch HCTF_LIVE_ACCEPT_BG=0: the old synchronous accept", called == [1])
        shutil.rmtree(snap, ignore_errors=True)
check("#5 the safe points join the judgement (generalize, accept, bg-generalize take, chain end)",
      all("_live_accept_join" in inspect.getsource(f) for f in
          (orchestrate.Chain.generalize, orchestrate.Chain._accept_or_restore, orchestrate.Chain._bg_gen_take,
           orchestrate.Chain._run_modes, orchestrate.Chain.timed_stage)))

# ------------------------------------------------------------------ #6 off-path work deferred during a timed download
ch6 = bare_chain(chal="binary-dl", base="binary-reverse-engineering-day-28-dl")
other = bare_chain(chal="binary-dl2", base="script-analysis-day-28-dl2")
with patched(QUIET):
    check("#6 nothing downloading -> no wait", ch6._offpath_wait("x") == 0.0 or ch6._offpath_wait("x") < 0.05)
    done_at = {}

    def dl():
        with ch6._timed_download("mastery"):
            time.sleep(0.8)
        done_at["t"] = time.time()
    threading.Thread(target=dl).start()
    time.sleep(0.1)
    t0 = time.time()
    waited = ch6._offpath_wait("background baseline")
    check("#6 off-path work waits until the chain's Mastery bytes are in", 0.5 < waited < 2.0 and time.time() >= done_at.get("t", 1e18) - 0.05,
          waited)
    threading.Thread(target=dl).start()
    time.sleep(0.1)
    check("#6 work for the downloading mode itself never waits", ch6._offpath_wait("mastery's own", mode="mastery") < 0.05)
    check("#6 another chain's download does not hold this chain (scope chain)", other._offpath_wait("x") < 0.05)
    stop = threading.Event()
    threading.Timer(0.2, stop.set).start()
    check("#6 a stop event ends the wait", ch6._offpath_wait("duel", stop) < 0.6)
    time.sleep(0.9)
    with patched({(orchestrate, "OFFPATH_DL_GATE"): False}):
        threading.Thread(target=dl).start()
        time.sleep(0.1)
        check("#6 kill switch HCTF_OFFPATH_DL_GATE=0", ch6._offpath_wait("x") == 0.0)
    time.sleep(0.9)
check("#6 the pre-start download concurrency is HCTF_PRESTART_DL_WORKERS (default 16 since D31: one wave) and marks the download",
      orchestrate.PRESTART_DL_WORKERS == int(os.environ.get("HCTF_PRESTART_DL_WORKERS", "16"))
      and "_prestart_dl_width()" in inspect.getsource(orchestrate.Chain._prefetch_mode_start)   # D31: via the 429-aware width
      and "PRESTART_DL_WORKERS" in inspect.getsource(orchestrate._prestart_dl_width)
      and "_timed_download(mode)" in inspect.getsource(orchestrate.Chain._prefetch_mode_start))
check("#6 gated: generalize baseline replay, background baseline, duel / background-generalize starts, post-live accept",
      "self.gate(" in inspect.getsource(orchestrate.GenBaseline._run)
      and "_offpath(self" in inspect.getsource(orchestrate.Chain._start_baseline_pre)
      and "_offpath_wait" in inspect.getsource(duel.Duel.start)
      and "_offpath(self" in inspect.getsource(orchestrate.Chain._start_live_accept))

# ------------------------------------------------------------------ #9 web kick not consumed on prerequisite_required
ch9 = bare_chain(lane="web", base="web-exploitation-day-24-fail-open-friday", chal="web-fail-open")
complete = {"single": False, "tt": False}
starts = []


def fake_call(cid, op, *a, **k):
    starts.append((cid, op))
    if cid.endswith("/time_trial"):
        return {"http": 200, "body": {"result": "preparing" if complete["single"] else "prerequisite_required"}}
    return {"http": 200, "body": {"result": "preparing" if complete["tt"] else "prerequisite_required"}}


def is_complete(cid):
    return complete["tt"] if cid.endswith("/time_trial") else complete["single"] if "/" not in cid else False


env9 = {**QUIET, (cli, "call"): fake_call, (cli, "is_complete"): is_complete,
        (orchestrate.time, "sleep"): lambda s: None, (orchestrate, "WEB_READY_POLL_MAX"): 0.0}
with patched(env9):
    ch9._web_tt_kick()   # WEB_PREPROVISION at chain start
    for _ in range(50):
        if any("not consumed" in s for s in said):
            break
        time.sleep(0.05)
    check("#9 pre-provision kick answered prerequisite_required -> the once-per-chain claim is released",
          getattr(ch9, "_web_kicked", None) is False and any("not consumed" in s for s in said), said[-3:])
    complete["single"] = True
    n0 = len(starts)
    ch9._web_tt_kick()   # the single's CORRECT
    for _ in range(50):
        if len(starts) > n0:
            break
        time.sleep(0.05)
    check("#9 ... so the kick at the single's CORRECT really requests the TT target",
          len(starts) == n0 + 1 and ch9._web_kicked is True, starts)
    n1 = len(starts)
    ch9._web_tt_kick()
    time.sleep(0.2)
    check("#9 a successful kick stays once-per-chain", len(starts) == n1)
    # Mastery kick before the TT's CORRECT -> released too
    ch9._web_mastery_kick()
    for _ in range(50):
        if getattr(ch9, "_web_m_kicked", True) is False:
            break
        time.sleep(0.05)
    check("#9 a Mastery kick ahead of the TT's CORRECT keeps no claim", ch9._web_m_kicked is False)
    complete["tt"] = True
    n2 = len(starts)
    ch9._web_mastery_kick()
    for _ in range(50):
        if len(starts) > n2:
            break
        time.sleep(0.05)
    check("#9 ... and the kick at the TT's CORRECT requests the Mastery target", len(starts) == n2 + 1 and ch9._web_m_kicked)
    with patched({(orchestrate, "WEB_KICK_RETRY_PREREQ"): False}):
        check("#9 kill switch HCTF_WEB_KICK_RETRY_PREREQ=0",
              orchestrate._kick_release_if_prereq(ch9, "_web_kicked", "prerequisite_required") is False)

# ------------------------------------------------------------------ #11 lane-aware baseline case timeout
check("#11 web baseline case timeout >= 20 s (race budget 12-14 s), other lanes keep 8 s",
      orchestrate.baseline_case_timeout("web") >= 20 and orchestrate.baseline_case_timeout("binary-reverse-engineering")
      == orchestrate.BASELINE_CASE_TIMEOUT)
check("#11 Chain._case_timeout + duel green watch are lane-aware",
      bare_chain(lane="web", chal="w11")._case_timeout() >= 20 and duel._green_timeout("web") >= 20
      and duel._green_timeout("warmups") == duel.GREEN_CASE_TIMEOUT)
check("#11 no Chain method replays with the bare BASELINE_CASE_TIMEOUT any more",
      "timeout=BASELINE_CASE_TIMEOUT" not in inspect.getsource(orchestrate.Chain)
      and "baseline_case_timeout(getattr(self, \"lane\", None))" in inspect.getsource(orchestrate.Chain._accept_after_live))
with patched({(orchestrate, "WEB_BASELINE_CASE_TIMEOUT"): 0.0}):
    check("#11 kill switch HCTF_WEB_BASELINE_CASE_TIMEOUT=0", orchestrate.baseline_case_timeout("web") == orchestrate.BASELINE_CASE_TIMEOUT)

# ------------------------------------------------------------------ #14 TT waits (bounded) for a pending codify
ch14 = bare_chain(lane="web", chal="web-cod")
plug = TD / "day28_web_cod.py"


class FakeCodify:
    def __init__(self, prelanded=False):
        self.plugin, self.t0, self.prelanded = plug, time.time() - 0.1, prelanded
        self.done = threading.Event()

    def landed(self, timeout=15):
        return self.plugin.exists() and self.plugin.stat().st_mtime >= self.t0


with patched({**QUIET, (orchestrate, "WEB_CODIFY_HOLD"): 0.0, (orchestrate, "WEB_CODIFY_PENDING_WAIT"): 3.0}):
    ch14._codify = FakeCodify()
    threading.Timer(0.6, lambda: plug.write_text("HANDLERS = {}\n")).start()
    t0 = time.time()
    ch14._codify_hold("web-x/time_trial")
    dt = time.time() - t0
    check("#14 a codify still writing the plugin holds the first TT until it lands (bounded)", 0.4 < dt < 2.0
          and any("landed after" in s for s in said[-3:]), (dt, said[-3:]))
    plug.unlink()
    ch14._codify = FakeCodify(prelanded=True)
    t0 = time.time()
    ch14._codify_hold("web-x/time_trial")
    check("#14 a hardening pass over a plugin already in place never holds", time.time() - t0 < 0.1)
    ch14._codify = FakeCodify()
    ch14._codify.done.set()
    t0 = time.time()
    ch14._codify_hold("web-x/time_trial")
    check("#14 a finished codify (no plugin) never holds", time.time() - t0 < 0.1)
    ch14._codify = FakeCodify()
    t0 = time.time()
    with patched({(orchestrate, "WEB_CODIFY_PENDING_WAIT"): 0.8}):
        ch14._codify_hold("web-x/time_trial")
    check("#14 the wait is capped at HCTF_WEB_CODIFY_PENDING_WAIT", 0.7 < time.time() - t0 < 1.6, time.time() - t0)
    with patched({(orchestrate, "WEB_CODIFY_PENDING_WAIT"): 0.0}):
        t0 = time.time()
        ch14._codify_hold("web-x/time_trial")
        check("#14 kill switch HCTF_WEB_CODIFY_PENDING_WAIT=0", time.time() - t0 < 0.1)

shutil.rmtree(TD, ignore_errors=True)
print(f"\n{'ALL PASS' if not failures else f'{len(failures)} FAILURE(S)'}")
sys.exit(1 if failures else 0)
