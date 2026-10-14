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

# ---------------------------------------------------------------------------------------------------------------- W4
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

# ---------------------------------------------------------------------------------------------------------------- W5
from unittest import mock  # noqa: E402
from hctf import hb_timed as H  # noqa: E402
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
print("ALL PASS")
