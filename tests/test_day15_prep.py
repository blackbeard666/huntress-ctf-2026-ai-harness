"""Behavior checks for the Day 15 prep (Day 14 review fixes), offline: no GM, no Homebase, no workers.

  W1 lib.decode positional-first decode_chunked: every verified warmups Mastery/Single blob D1-D14 decodes to its slug
  W2 seeded random Mastery sets (GM vocabulary, GM-like 7/8 cuts): 0 misses on 14 known lines; 0 misses with an
     unregistered codec on line 15 (rot47 / swapcase / per-word reversal / base58)
  W3 D14 set22 (the one empty field of attempt 18c3893f): positional, joint-only and decode_candidates all get it
  W4 a codec swap on lines 12/13 (an unseen mutation) is never accepted as a positional reading; flag off -> joint path

Run:  source bin/env.sh && python3 tests/test_day15_prep.py      (exit 0 = all pass)
"""
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from hctf import solvers, today_probe as TP  # noqa: E402
from lib import decode, slug, warmups_codecs as W  # noqa: E402
from unittest import mock  # noqa: E402
from hctf import hb_timed as H  # noqa: E402
import os  # noqa: E402
from lib import meta  # noqa: E402
from lib.common import find_artifact  # noqa: E402
import shutil  # noqa: E402
import tempfile  # noqa: E402
from hctf import orchestrate as orch, workers  # noqa: E402
from hctf import timed  # noqa: E402
import threading  # noqa: E402
import time  # noqa: E402


def blobs():
    """(case dir, answer id, blob text, slug) for every distinct verified numbered warmups blob."""
    seen = set()
    for case in sorted(ROOT.glob("challenges/day*/warmups-*/solver/cases/*")):
        if not (case / "expected.json").exists() or not (case / "contract.json").exists():
            continue
        exp = json.loads((case / "expected.json").read_text())
        contract = json.loads((case / "contract.json").read_text())
        try:
            _c, members = TP._members(case)
        except OSError:
            continue
        for aid, q in solvers.paired_questions(contract):
            raw = members.get(Path(str(q.get("artifact") or "").split("->")[0].strip()).name)
            val = exp.get(aid)
            if raw is None or not isinstance(val, str) or (raw, val) in seen:
                continue
            text = raw.decode("utf-8", "replace")
            if decode._rows(text) is None:
                continue
            seen.add((raw, val))
            yield case, aid, text, val


HAVE_D14 = (ROOT / "challenges/day14/warmups-seven-steps/solver/cases").is_dir()   # main only (alt never played D14)

# ---------------------------------------------------------------------------------------------------------------- W1
n = bad = 0
for case, aid, text, val in blobs():
    n += 1
    if not (decode.decode_chunked(text) or "").rstrip().endswith(val):
        bad += 1
        print("MISS", case, aid, val)
assert n >= 290 and bad == 0, (n, bad)
print(f"ok  W1 decode_chunked: {n}/{n} verified numbered warmups blobs D1-D14 end in their GM slug")

# ---------------------------------------------------------------------------------------------------------------- W2
WORDS = sorted(slug.vocab())
EXTRA = {"rot47": lambda s: "".join(chr(33 + (ord(c) - 33 + 47) % 94) if 33 <= ord(c) <= 126 else c for c in s),
         "swapcase": str.swapcase, "wordrev": W.wordrev,
         "base58": next(c[1] for c in W.CANDIDATES if c[0] == "base58")}


def sim(n_sets, n_lines, seed, today=None):
    rng = random.Random(seed)
    miss = []
    for _ in range(n_sets):
        s = "-".join(rng.choice(WORDS) for _ in range(3)) + f"-{rng.randint(10, 99)}"
        sentence = decode.TEMPLATE + s
        base, extra = divmod(len(sentence), n_lines)
        sizes = [base + 1] * extra + [base] * (n_lines - extra)
        rng.shuffle(sizes)
        cuts, pos = [], 0
        for z in sizes[:-1]:
            pos += z
            cuts.append(pos)
        parts = [sentence[a:b] for a, b in zip([0] + cuts, cuts + [len(sentence)])]
        lines = []
        for k, piece in enumerate(parts, 1):
            dc = W.day_codec(k)
            lines.append(f"{k:02d}\t{(dc[1] if dc else EXTRA[today])(piece)}")
        if not (decode.decode_chunked("\n".join(lines) + "\n") or "").rstrip().endswith(s):
            miss.append(s)
    return miss


m = sim(1500, 14, 101)
assert not m, m[:5]
for i, today in enumerate(EXTRA):
    m = sim(300, 15, 200 + i, today)
    assert not m, (today, m[:5])
print("ok  W2 random Mastery sets: 1500 x 14 known lines + 4 x 300 x 15 lines with an unregistered line-15 codec, 0 misses")

# ---------------------------------------------------------------------------------------------------------------- W3
if HAVE_D14:
    # set22 is not in auto-mastery-18c3893f (only its 67 GM-accepted answers); the untimed retry served the same blob
    hit = [b for b in blobs() if "day14/warmups" in str(b[0]) and b[3] == "groovy-puzzle-turtle-60"]
    assert hit, "D14 set22 blob missing"
    _c, _a, t22, v22 = hit[0]
    rows = decode._rows(t22)
    assert decode._positional_ok(rows).rstrip().endswith(v22)
    assert decode._joint_free(rows).rstrip().endswith(v22)          # vocabulary rank alone also fixes it
    cands = decode.decode_candidates(t22)
    assert cands and cands[0].rstrip().endswith(v22), cands
    print("ok  W3 D14 set22: positional, joint-only (vocabulary rank) and decode_candidates[0] all give " + v22)
else:
    print("skip W3: no challenges/day14 data in this copy")

# ---------------------------------------------------------------------------------------------------------------- W4
if HAVE_D14:
    swapped = 0
    for case, aid, text, val in blobs():
        rows = decode._rows(text)
        if len(rows) < 13 or "day1" not in str(case):
            continue
        plain = [W.day_codec(k)[2](f) for k, f in rows]
        mut = list(rows)
        mut[11] = (12, W.day_codec(13)[1](plain[11]))
        mut[12] = (13, W.day_codec(12)[1](plain[12]))
        if W.day_codec(13)[1](plain[11]) == rows[11][1]:
            continue
        pos = decode._positional_ok(mut)
        assert pos is None or pos.rstrip().endswith(val), (case, aid, pos[-40:])
        swapped += 1
    assert swapped > 100, swapped
    decode.POSITIONAL = False
    try:
        assert decode._positional(decode._rows(t22)) == []
        assert (decode.decode_chunked(t22) or "").rstrip().endswith(v22)
    finally:
        decode.POSITIONAL = True
    print(f"ok  W4 codec swap on lines 12/13: no garbled positional reading accepted on {swapped} sets; "
          "HCTF_DECODE_POSITIONAL=0 -> joint path")
else:
    print("skip W4: no challenges/day14 data in this copy")

# ---------------------------------------------------------------------------------------------------------------- W5
if HAVE_D14:
    vcase = ROOT / "challenges/day14/warmups-seven-steps/solver/cases/variant-mastery-18c3893f"
    vc = json.loads((vcase / "contract.json").read_text())
    qmap = H._paired(vc.get("answer_ids") or [q["id"] for q in vc["questions"]], vc["questions"])
    posts = []


    def fake_post(p, timeout=None):
        posts.append(p)
        ok = p["answers"].get("set22.message") == "groovy-puzzle-turtle-60"
        return {"result": "correct" if ok else "incorrect", "remaining": 0 if ok else 1}


    out = {"result": "solver_incomplete", "missing": ["set22.message"], "verified": {"set1.message": "x"}}
    with mock.patch.object(H, "_post", fake_post), mock.patch.object(H, "_deadline_left", lambda b: 20.0):
        H._fill_missing("warmups-day-14", ["set22.message"], qmap, vcase / "artifacts", {}, out)
    assert out["result"] == "correct" and "missing" not in out and len(posts) == 1, out
    assert out["verified"] == {"set1.message": "x", "set22.message": "groovy-puzzle-turtle-60"}
    posts.clear()
    out = {"result": "solver_incomplete"}
    with mock.patch.object(H, "_post", fake_post), mock.patch.object(H, "_deadline_left", lambda b: 1.0):
        H._fill_missing("warmups-day-14", ["set22.message"], qmap, vcase / "artifacts", {}, out)
    assert out["result"] == "solver_incomplete" and not posts, (out, posts)      # clock nearly gone: no submit
    with mock.patch.object(H, "_post", fake_post):
        H._fill_missing("x", ["set1.n"], {"set1.n": {"artifact": "blob-01.txt", "answer_format": "an integer"}},
                        vcase / "artifacts", {}, out)
    assert out["result"] == "solver_incomplete" and not posts                  # not a slug question: never guessed
    print("ok  W5 hb_timed in-window fill: D14 set22 completed in 1 submit; no submit under 1.5 s left or for non-slugs")
else:
    print("skip W5: no challenges/day14 data in this copy")

# ---------------------------------------------------------------------------------------------------------------- M1
if HAVE_D14:
    mcase = ROOT / "challenges/day14/metadata-the-shortcut-home/solver/cases/single_solve"
    mc, mexp = json.loads((mcase / "contract.json").read_text()), json.loads((mcase / "expected.json").read_text())
    mq = mc["questions"][0]
    mdata = find_artifact(mcase / "artifacts", mq["artifact"])
    os.environ["HCTF_META_MAX_DAY"] = "14"      # the morning-of-D14 view: no verified lnk entry yet
    try:
        assert meta.lookup("lnk", "target_path_windows") == (None, None)
        ext, _p, used = meta.resolve("lnk", "target_path_windows")
        assert used == "target_path" and ext.tier == meta.SPECULATIVE, (ext, used)
        assert meta.answer(mq["id"], mq, mdata) == (mexp[mq["id"]], meta.SPECULATIVE), meta.answer(mq["id"], mq, mdata)
        meta.ALIASES = False
        assert meta.answer(mq["id"], mq, mdata) == (None, None)
    finally:
        meta.ALIASES = True
        del os.environ["HCTF_META_MAX_DAY"]
    assert meta.answer(mq["id"], mq, mdata) == (mexp[mq["id"]], meta.VERIFIED)     # today: the verified D14 extractor
    assert meta.resolve("lnk", "no_such_field")[0] is None and meta.resolve("pe", "image_base_hex_text")[2] == "image_base_hex"
    assert meta.resolve("pe", "coff_machine_u16_hex")[0].tier == meta.VERIFIED       # exact keys keep their tier
    print("ok  M1 lib.meta.resolve: D14 lnk.target_path_windows -> prebuilt target_path (speculative) = the GM answer "
          "with the D14 verified entry hidden; HCTF_META_ALIASES=0 -> no answer")
else:
    print("skip M1: no challenges/day14 data in this copy")

# ---------------------------------------------------------------------------------------------------------------- R1
if HAVE_D14:
    tmp = Path(tempfile.mkdtemp(prefix="t15r-", dir=ROOT / ".run"))
    GATE_T = "test_day7_fixes.py"


    def ratchet_case(gate_rule):
        """Run orchestrate.ratchet(14) in a scratch ROOT (copies of lib/ + tests/): the mocked lib worker adds a lib line and
        REWRITES the first assert of tests/test_day7_fixes.py; the mocked gate decides by `gate_rule(tests text, lib text)`."""
        root = tmp / f"r{len(list(tmp.iterdir()))}"
        (root / ".run").mkdir(parents=True)
        shutil.copytree(ROOT / "lib", root / "lib", ignore=shutil.ignore_patterns("__pycache__"))
        shutil.copytree(ROOT / "tests", root / "tests", ignore=shutil.ignore_patterns("__pycache__", "data"))
        (root / "challenges").symlink_to(ROOT / "challenges")      # read-only use: digest + proposals (workers mocked)
        orig = (root / "tests" / GATE_T).read_text()
        calls, said = [], []

        def fake_run(cd, stage, prompt, env, timeout, **kw):
            calls.append((stage, env.get("HCTF_LANE")))
            if stage == "ratchet":
                with open(root / "lib" / "decode.py", "a") as f:
                    f.write("\n# ratchet edit\n")
                t = (root / "tests" / GATE_T).read_text()
                i = t.index("assert ")
                (root / "tests" / GATE_T).write_text(t[:i] + "assert True  # weakened\n" + t[i:].split("\n", 1)[1])
                assert "Digest" in prompt and "warmups-seven-steps [warmups]" in prompt and "TECHNIQUE LOGS" not in prompt
            else:
                assert stage == "ratchet_log" and "reference/techniques/" in prompt
            return 0, str(cd / f"worker-{stage}.log")
        gate = lambda tag: gate_rule((root / "tests" / GATE_T).read_text(), (root / "lib" / "decode.py").read_text())  # noqa: E731
        with mock.patch.object(orch, "ROOT", root), mock.patch.object(orch.paths, "CHALLENGES", root / "challenges"), \
                mock.patch.object(workers, "run_local", fake_run), \
                mock.patch.object(orch, "ratchet_gate", gate), mock.patch.object(orch, "SPEED_HARDEN", False), \
                mock.patch.object(orch, "say", said.append):
            orch.ratchet(14)
        return root, orig, calls, said


    # A) gate green with the ORIGINAL assertion -> originals restored, lib edit kept
    root, orig, calls, said = ratchet_case(lambda t, lib: True)
    assert (root / "tests" / GATE_T).read_text() == orig and "# ratchet edit" in (root / "lib" / "decode.py").read_text()
    assert any("ORIGINAL tests" in s for s in said) and (root / ".run" / "ratchet-tests-day14.patch").exists(), said
    assert sorted(l for s, l in calls if s == "ratchet_log") == ["binary-reverse-engineering", "metadata-forensics",
                                                                  "mobile-android", "script-analysis", "warmups"], calls
    # B) the lib edit needs the modified assertion -> kept, flagged !!! for review
    root, orig, calls, said = ratchet_case(lambda t, lib: "# weakened" in t)
    assert "# weakened" in (root / "tests" / GATE_T).read_text() and any(s.startswith("!!! [ratchet]") for s in said), said
    # C) gate red either way -> lib/ AND tests/ reverted
    root, orig, calls, said = ratchet_case(lambda t, lib: False)
    assert (root / "tests" / GATE_T).read_text() == orig and "# ratchet edit" not in (root / "lib" / "decode.py").read_text()
    assert any("REVERTED lib/ + tests/" in s for s in said), said
    shutil.rmtree(tmp, ignore_errors=True)
    print("ok  R1 ratchet split: 5 per-lane technique-log workers beside one lib worker (digest, no log step); a rewritten "
          "gate assertion -> originals tried first, kept only flagged '!!!', revert restores lib/ + tests/")
else:
    print("skip R1: no challenges/day14 data in this copy")

# ---------------------------------------------------------------------------------------------------------------- T1
ch = object.__new__(orch.Chain)
ch.base, ch.entries, ch.sdir = "b", {"mastery": {"id": "b/mastery"}}, ROOT / ".run"
ch.gov = type("G", (), {"allow_timed": lambda self: True})()
ch._pre_attempt_done = True
calls, said = [], []


def stage_run(results, prev):
    it = iter(results)
    with mock.patch.object(orch, "set_state", lambda *a, **k: None), \
            mock.patch.object(orch, "record_timed_case", lambda *a, **k: None), \
            mock.patch.object(orch, "say", said.append), \
            mock.patch.object(orch.cli, "is_complete", lambda cid: False), \
            mock.patch.object(orch.cli, "gm_solved", lambda cid: False), \
            mock.patch.object(timed, "last_result", lambda cid: prev), \
            mock.patch.object(timed, "seconds_left", lambda p: 0), \
            mock.patch.object(orch.time, "sleep", lambda s: None), \
            mock.patch.object(orch.Chain, "_mastery_speed_gate", lambda self, cid: None), \
            mock.patch.object(orch.Chain, "generalize", lambda self, *a, **k: None), \
            mock.patch.object(timed, "run", lambda cid, sdir, log=None, **k: (calls.append(k.get("op", "start")),
                                                                               next(it))[1]):
        return ch.timed_stage("mastery")


# D14 warmups: the previous start said attempts_remaining 0 -> the first call is already untimed (no refused retry)
assert stage_run(["correct"], {"attempt_id": "a", "attempts_remaining": 0, "result": "solver_incomplete"}) is True
assert calls == ["untimed"] and any("0 fresh attempts left" in s for s in said), (calls, said)
calls.clear()
assert stage_run(["correct"], {"attempt_id": "a", "attempts_remaining": 7, "result": "solver_incomplete"}) is True
assert calls == ["retry"], calls                    # attempts left: a normal timed retry
calls.clear()
orch.SKIP_DOOMED_RETRY = False
try:
    assert stage_run(["error:exhausted", "correct"], {"attempt_id": "a", "attempts_remaining": 0}) is True
    assert calls == ["retry", "untimed"], calls     # flag off: the old refused-retry path
finally:
    orch.SKIP_DOOMED_RETRY = True
print("ok  T1 timed_stage: previous start reported 0 attempts left -> untimed at once (no refused retry); "
      "HCTF_SKIP_DOOMED_RETRY=0 -> old path")

# ---------------------------------------------------------------------------------------------------------------- C1
ev = threading.Event()
t = threading.Thread(target=ev.wait, daemon=True)
timed._captures.append(t)
t.start()
assert timed.join_captures(0.2) == 1
said.clear()
threading.Timer(0.3, ev.set).start()
with mock.patch.object(orch, "say", said.append):
    orch._join_captures("day99")
assert timed.join_captures(0) == 0 and any("all captured" in s for s in said), said
timed._captures.remove(t)
src = __import__("inspect").getsource(orch.run)
assert "_join_captures(" in src and "_join_captures(tag)" in __import__("inspect").getsource(orch.ratchet)
print("ok  C1 background pass captures tracked + joined before speed-harden and before the run exits")

# ---------------------------------------------------------------------------------------------------------------- G1
# rehearsal fair D14 findings: the single-speed gate re-times once alone; the today-probe stops after a stage-1 miss (no
# ~20 CPU-s random draw at the drop); warmups Mastery waits up to TODAY_PROBE_WAIT for the codec probe.
said.clear()
g = object.__new__(orch.Chain)
g.sdir = ROOT / ".run"
with mock.patch.object(orch, "say", said.append), \
        mock.patch.object(orch.solvers, "run_solver", lambda *a, **k: ({}, None, 0.4)):
    g._note_single_speed("x", 6.7, rerun=("d", {}, "a"))
assert g._single_slow is None and any("re-timed alone 0.4s" in s for s in said), said
with mock.patch.object(orch, "say", said.append), \
        mock.patch.object(orch.solvers, "run_solver", lambda *a, **k: ({}, None, 5.9)):
    g._note_single_speed("x", 6.7, rerun=("d", {}, "a"))
assert g._single_slow == 5.9, g._single_slow                        # still slow alone -> flagged (best timing)
ran = []


def fake_tp_run(sdir, case, timeout):
    ran.append(Path(case).name)
    bad = Path(case).name.endswith("-edge")
    return {"case": Path(case).name, "path": str(case), "expected": 1, "correct": 0 if bad else 1,
            "wrong": {"a": {}} if bad else {}, "error": None, "seconds": 0.1}


fake_base = tmp_b = Path(tempfile.mkdtemp(prefix="t15g-", dir=ROOT / ".run"))
made_variants = []


def fake_synth(sdir, enc, name, base=None, variants=(), out_dir=None, seed=None, salt=0):
    made_variants.extend(variants)
    return [tmp_b / f"compound-today-d99-{v}" for v in variants]


with mock.patch.object(TP, "today_codec", lambda sdir: ("toy", str.upper)), \
        mock.patch.object(TP, "base_case", lambda sdir: tmp_b / "base"), \
        mock.patch.object(TP, "synth", fake_synth), mock.patch.object(TP, "_run", fake_tp_run):
    r = TP.probe(tmp_b)
assert r["status"] == "miss" and not any(v.startswith("random") for v in made_variants), made_variants
assert ran[0] == "base" and set(ran[1:]) == {"compound-today-d99-even", "compound-today-d99-edge"}, ran
shutil.rmtree(tmp_b, ignore_errors=True)
assert orch.TODAY_PROBE_WAIT >= 20 and orch.TODAY_MERGE_WAIT <= 10
print("ok  G1 speed gate re-times alone (6.7 -> 0.4 s: no speed generalize); probe stage 1 miss -> no random draw; "
      f"codec probe wait {orch.TODAY_PROBE_WAIT:g}s, merge {orch.TODAY_MERGE_WAIT:g}s")
print("ALL PASS")
