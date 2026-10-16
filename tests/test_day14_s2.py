"""Behavior checks for the Day 14 S2 work (warmups Mastery-mix probe + verified-green + failure recovery), offline: no GM,
no Homebase, no workers.

  D1 lib.warmups_codecs: exact day encoders (all 819 D13 GM lines), infer() today's codec (13/13 Singles), candidates
  D2 lib.decode: register_free registry (toy day-14 codec), strict morse/a1z26, zero output change on historic blobs
  D3 hctf.today_probe: D13 failure reproduced from D12's Mastery + D13's Single; probe < 5 s; adopt; unidentified
  D4 orchestrator consumption (Mastery only, bounded wait, misses -> diag), merge probe (K1)
  D5 verified-green: capture_variant on D13 attempt bd5589ea, test_solver feedback, _watch_green rules, guard
  E1/E2 bundle fallback, async profile, inline attempt bytes; every flag off -> old path

Run:  source bin/env.sh && python3 tests/test_day14_s2.py      (exit 0 = all pass)
"""
import base64
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import zipfile
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "hctf"))
from hctf import cli, hb_daemon, orchestrate as orch, solvers, timed, today_probe as TP, workers  # noqa: E402
from lib import decode, warmups_codecs as W  # noqa: E402
from lib.common import iter_entries  # noqa: E402

CH = ROOT / "challenges"
S12 = CH / "day12" / "warmups-back-at-you" / "solver"
S13 = CH / "day13" / "warmups-opposite-day" / "solver"
D12M = S12 / "cases" / "auto-mastery-a5b5e87c"
D13M = S13 / "cases" / "auto-mastery-d1a77831"
ATT13 = CH / "day13" / "warmups-opposite-day" / "mastery" / "attempts" / "bd5589ea"
TMPD = Path(tempfile.mkdtemp(prefix="t14s2-", dir=ROOT / ".run"))


def members(case):
    f = next((case / "artifacts").iterdir())
    with zipfile.ZipFile(f) as z:
        return {n: z.read(n).decode() for n in z.namelist()}


def fake_chal(day, lane="warmups", name="x"):
    """tmp/dayNN/<lane>-x/{meta.json, solver/cases/} (today_probe reads the day from the dir names)."""
    chal = TMPD / f"day{day:02d}" / f"{lane}-{name}"
    (chal / "solver" / "cases").mkdir(parents=True, exist_ok=True)
    (chal / "meta.json").write_text(json.dumps({"lane": lane, "name": name}))
    return chal / "solver"


# ---------------------------------------------------------------------------------------------------------------- D1
n = ok = 0
for blob in members(D13M).values():
    for ln in blob.split("\n"):
        k, frag = ln.split("\t", 1)
        _name, enc, dec, _free = W.day_codec(int(k))
        n += 1
        ok += enc(dec(frag)) == frag
assert (n, ok) == (819, 819), (n, ok)
print("ok  D1 encoders: all 819 lines of D13 auto-mastery-d1a77831 reproduced byte for byte from their decoding")

want = ["base64", "rot13", "hex", "binary8", "decimal", "octal3", "url%xx", "html&#n;", "json\\u", "base32",
        "base64url-nopad", "reverse", "atbash"]
got = []
for d in sorted(CH.glob("day*/warmups-*")):
    if int(d.parent.name[3:]) <= 13:
        got.append((W.infer_case(d / "solver" / "cases" / "single_solve") or ("?",))[0])
assert got == want, got
print("ok  D1 infer: 13/13 Singles D1-D13 identified as their day's codec (E(plaintext) == blob)")

plain = W.SENTENCE.format(slug="handy-candle-quartz-31")
for name, fn in (("rot47", W.rot47), ("morse", W.morse_enc), ("a1z26", W.a1z26_enc), ("rail3", lambda s: W.rail_enc(s, 3)),
                 ("affine5,8", lambda s: W.affine(s, 5, 8)), ("base58", W.b58_enc), ("qwerty-right", lambda s: W.qwerty_shift(s, 1)),
                 ("base64(reverse)", lambda s: base64.b64encode(s[::-1].encode()).decode()), ("wordrev", W.wordrev)):
    r = W.infer(plain, fn(plain))
    assert r and r[1](plain) == fn(plain), (name, r and r[0])
r = W.infer(plain, W.vigenere(plain, "opposite"), hints=["Opposite Day"])
assert r and r[0] == "vigenere:opposite", r
r = W.infer(plain, W.vigenere(plain, "zebrafish"))       # no key hint: the fixed sentence is a crib (prebuild
assert r and r[0] == "vigenere:zebrafish" and r[1](plain) == W.vigenere(plain, "zebrafish"), r   # crib-polyalpha-key, 10-16)
sub = dict(zip("abcdefghijklmnopqrstuvwxyz", "qwertyuiopasdfghjklzxcvbnm"))
r = W.infer(plain, "".join(sub.get(c, c) for c in plain))
assert r and r[0] == "subst", r
print("ok  D1 candidates: rot47/morse/a1z26/rail/affine/base58/qwerty/chained/vigenere(title)/learned substitution inferred")

# ---------------------------------------------------------------------------------------------------------------- D2
seen, blobs, blob_day = set(), [], []
for d in sorted(CH.glob("day*/warmups-*")):
    roots = [c / "artifacts" for c in (d / "solver" / "cases").glob("*/")]
    for r in roots:
        for name, load, _ in iter_entries(r):
            try:
                b = load()
            except Exception:  # noqa: BLE001
                continue
            if b[:2] == b"PK" or name.endswith(".json"):
                continue
            h = hashlib.sha1(b).hexdigest()
            if h not in seen:
                seen.add(h)
                blobs.append(b.decode("utf-8", "replace"))
                blob_day.append(int(d.parent.name[3:]))


def decode_all(max_day=99):
    out = []
    for text, day in zip(blobs, blob_day):
        if day > max_day:
            continue
        out.append(decode.decode_chunked(text))
        out.append(decode.decode_chunk(text.strip()))
        out += [decode.decode_chunk(m.group(2)) for m in map(decode._CHUNK.match, text.splitlines()) if m]
    return out


# Historic = days before the newest codec rule: D16's MORSE-HEX (lib/decode.py, `_max_day() >= 16`) changes D16 blobs
# on purpose, so the zero-change sweep stops at D15.
HISTORIC_MAX = 15
# the pre-change behaviour: every new flag off and the speculative entries removed
saved_free = list(decode._FREE)
with mock.patch.object(decode, "STRICT_EXTRA", False), mock.patch.object(decode, "SPECULATIVE_FREE", False):
    decode._FREE[:] = [e for e in saved_free if e[1] is not None]
    t0 = time.time()
    old = decode_all(HISTORIC_MAX)
    decode._FREE[:] = saved_free
new_out = decode_all(HISTORIC_MAX)
assert len(blobs) > 300 and old == new_out, (len(blobs), sum(a != b for a, b in zip(old, new_out)))
print(f"ok  D2 historic sweep: {len(blobs)} distinct warmups blobs (whole, chunked, every line) decode identically with "
      "strict morse/a1z26 + speculative free codecs on")

assert decode.decode_chunk(W.morse_enc("nice work!")) == "NICE WORK!"          # uppercase, as the generic path had
assert decode.decode_chunk(W.a1z26_enc("nice work")) == "nice work"
print("ok  D2 strict branches: morse and a1z26 fragments decode")

# toy day-14 free-text codec: rot13 of the swapped case. 14-line blob = D13's 63 verified sets + toy line 14.
toy_enc = lambda s: W.rot(s.swapcase(), 13)                                      # noqa: E731
s14 = fake_chal(14, name="toy")
toy_cases = TP.synth(s14, toy_enc, "toy", base=D13M, variants=("even",), out_dir=TMPD / "toy")
assert toy_cases, "toy synth"
exp = json.loads((toy_cases[0] / "expected.json").read_text())
contract = json.loads((toy_cases[0] / "contract.json").read_text())
mem = members(toy_cases[0])
assert all(len(v.split("\n")) == 14 for v in mem.values())


def toy_right():
    return sum((decode.decode_chunked(mem[q["artifact"]]) or "").rstrip().endswith(exp[q["id"]])
               for q in contract["questions"])


# the toy stands in for day 14, so D14's real confirmed free codec (caesar7) is off while it is scored
decode._FREE[:] = [e for e in saved_free if e[1] is None or e[1] < 14]
try:
    before = toy_right()
    decode.register_free("toy", 14, lambda p: [W.rot(p, 13).swapcase()])
    after = toy_right()
    decode._FREE[:] = saved_free
    decode.register_free("toy", 14, lambda p: [W.rot(p, 13).swapcase()])
    reg_out = decode_all(13)     # D14 blobs are 14 lines: the toy day-14 codec competes there by design
finally:
    decode._FREE[:] = saved_free
assert after == 63 and before < 63, (before, after)
assert reg_out == decode_all(13)
print(f"ok  D2 register_free: toy day-14 codec -> 14-line blobs {before}/63 -> {after}/63, every historic blob unchanged")

# ---------------------------------------------------------------------------------------------------------------- D3
t0 = time.time()
cases = TP.synth(S13, W.atbash, "atbash", base=D12M, out_dir=TMPD / "d13", variants=("even", "edge"))
assert {c.name for c in cases} == {"compound-today-d13-even", "compound-today-d13-edge"}, cases
# default variants also add the random-slug GM-cut cases (D15 prep: D14 set22 needed a slug the base never had)
assert len(TP.synth(S13, W.atbash, "atbash", base=D12M, out_dir=TMPD / "d13r")) == 2 + TP.RANDOM_CASES
for c in cases:
    mem = members(c)
    contract = json.loads((c / "contract.json").read_text())
    exp = json.loads((c / "expected.json").read_text())
    truth = json.loads((c / "truth.json").read_text())
    assert len(exp) == 58 and truth["today"]["codec"] == "atbash" and not truth["skipped"]
    per = joint = 0
    for q in contract["questions"]:
        text = mem[q["artifact"]]
        rows = [decode._CHUNK.match(x).groups() for x in text.splitlines()]
        assert len(rows) == 13
        per += "".join(decode.decode_chunk(p) for _, p in rows).rstrip().endswith(exp[q["id"]])
        joint += (decode.decode_chunked(text) or "").rstrip().endswith(exp[q["id"]])
    assert per <= 50 and joint == 58, (c.name, per, joint)
    r12 = TP._run(S12, c, 60)
    assert r12["correct"] < 58 and not r12["error"], (c.name, r12["correct"])
    if c.name.endswith("even"):
        r13 = TP._run(S13, c, 60)
        assert r13["correct"] == 58, r13["correct"]
print("ok  D3 reproduction: D12 Mastery + D13 codec -> per-line join <=50/58, decode_chunked 58/58, D12 solver misses, "
      "D13 solver passes (even cuts)")

t0 = time.time()
res = TP.probe(S13, deadline=time.time() + 30, out_dir=TMPD / "probe13")
dt = time.time() - t0
assert dt < 5 and res["codec"] == "atbash" and res["base_ok"], (dt, res["status"])
# finding: the final D13 solver's own `_joint` misses one edge-cut set that lib.decode.decode_chunked gets
assert res["status"] == "miss" and "compound-today-d13-edge" in [Path(p).name for p in res["hard"]], res["hard"]
assert "compound-today-d13-even" not in [Path(p).name for p in res["hard"]], res["hard"]
txt = TP.summary(res)
assert "atbash" in txt and "line 13" in txt and "register_free" in txt, txt
adopt_dir = fake_chal(13, name="adopt")
assert TP.adopt(adopt_dir, res) == len(res["hard"])
ad = adopt_dir / "cases" / "compound-today-d13-edge"
assert (ad / "expected.json").exists() and (ad / "truth.json").exists() and (ad / "contract.json").exists()
print(f"ok  D3 probe: {dt:.2f}s, D13 solver passes even cuts but misses 1 edge-cut set (adopted with expected + truth)")

unk = fake_chal(14, name="unknown")
(unk / "cases" / "single_solve" / "artifacts").mkdir(parents=True)
slug = "brisk-otter-maple-14"
_k = b"k3y!Zq9#Lm2@P"   # keyed Vigenere is no longer "unknown": the fixed sentence is a crib (crib-polyalpha-key, 10-16)
(unk / "cases" / "single_solve" / "artifacts" / "blob.txt").write_text(base64.b64encode(bytes(
    b ^ _k[i % len(_k)] for i, b in enumerate(W.SENTENCE.format(slug=slug).encode()))).decode())
(unk / "cases" / "single_solve" / "contract.json").write_text(json.dumps(
    {"answer_ids": ["message"], "questions": [{"id": "message", "artifact": "blob.txt"}], "prompt": "Mystery"}))
(unk / "cases" / "single_solve" / "expected.json").write_text(json.dumps({"message": slug}))
ures = TP.probe(unk, out_dir=TMPD / "unk")
assert ures["status"] == "unidentified" and not ures["hard"] and not (TMPD / "unk").exists(), ures
assert "could not be identified" in TP.summary(ures)
print("ok  D3 unknown codec -> 'unidentified', no cases")

# ---------------------------------------------------------------------------------------------------------------- D4


def bare_chain(**kw):
    c = object.__new__(orch.Chain)
    c.base, c.pools, c.gov, c.only_modes = "warmups-day-13", None, mock.Mock(allow_timed=lambda: True), None
    c.lane, c.name, c.sdir, c.root = "warmups", "t", S13, TMPD
    c.__dict__.update(kw)
    return c


said = []
with mock.patch.object(orch, "say", said.append), \
        mock.patch.object(orch, "today_probe", lambda sdir, seconds=30, kind="codec": dict(res, kind=kind)):
    sd = fake_chal(13, name="consume")
    (sd / "solve.py").write_text("")
    ch2 = bare_chain(sdir=sd)
    ch2._start_today_pre("warmups-day-13")
    ch2._mut_late_done = ch2._cmp_late_done = True
    ch2._fam_pre_fut = None
    with mock.patch.object(ch2, "_family_pre_result", lambda wait=True: ("", [])):
        tt = ch2._late_probes("warmups-day-13/time_trial", wait=True)
        ma = ch2._late_probes("warmups-day-13/mastery", wait=False)
        again = ch2._late_probes("warmups-day-13/mastery", wait=True)
assert tt == {} and "compound_today" in ma and again == {}, (tt, ma, again)
assert (sd / "cases" / "compound-today-d13-edge" / "truth.json").exists()
print("ok  D4 consumption: never before the Time Trial; before Mastery even with wait=False; consumed once")

slow = threading.Event()


def slow_probe(sdir, seconds=30, kind="codec"):
    slow.wait(10)
    return {"status": "clean", "kind": kind}


with mock.patch.object(orch, "say", lambda m: None), mock.patch.object(orch, "today_probe", slow_probe), \
        mock.patch.object(orch, "TODAY_PROBE_WAIT", 0.3):
    ch = bare_chain(sdir=fake_chal(13, name="slow"))
    (ch.sdir / "solve.py").write_text("")
    ch._start_today_pre("x")
    t0 = time.time()
    first = ch._today_pre_result("x/mastery")
    waited = time.time() - t0
    pending = not getattr(ch, "_today_done", False)
    slow.set()
    time.sleep(0.2)
    second = ch._today_pre_result("x/mastery")
assert first == {} and second == {} and 0.25 < waited < 1.5 and pending and ch._today_done, (waited, pending)
with mock.patch.object(orch, "TODAY_PROBE", False), mock.patch.object(orch, "TODAY_MERGE_PROBE", False):
    ch = bare_chain(sdir=S13)
    ch._start_today_pre("x")
    assert ch._today_fut is None and ch._today_pre_result("x/mastery") == {}
print("ok  D4 bounded wait: a running probe holds Mastery <= HCTF_TODAY_PROBE_WAIT and stays pending; flags off -> no probe")

# generalize prompt carries the compound_today block (rendered prompt captured, worker stubbed)
captured = {}


def gen_with(diag, sdir=None, **patches):
    ch = bare_chain(sdir=sdir or fake_chal(13, name="gen"), root=TMPD / "genroot")
    (ch.root).mkdir(exist_ok=True)
    ch._pre_res, ch._baseline = [], set()
    launched = {}

    def run_worker(cid, stage, prompt, timeout, stop=None, **k):
        launched["t"], launched["prompt"] = time.time(), prompt

    ch.run_worker = run_worker
    ch._snapshot_solver = lambda: None
    ch._accept_or_restore = lambda cid: None
    ps = [mock.patch.object(orch, "say", lambda m: None), mock.patch.object(orch, "set_state", lambda *a, **k: None),
          mock.patch.object(orch, "ensure_case_and_test", lambda *a, **k: (True, None)),
          mock.patch.object(orch.solvers, "test_solver", lambda *a, **k: []),
          mock.patch.object(orch.timed, "last_result", lambda cid: {}),
          mock.patch.object(orch.remote, "gm_transport", lambda: "local"),
          mock.patch.object(orch.cli, "cdir", lambda cid: TMPD / "gencdir"),
          mock.patch.object(orch, "ROOT", TMPD)]
    ps += [mock.patch.object(orch, k, v) for k, v in patches.items()]
    (TMPD / "gencdir").mkdir(exist_ok=True)
    for p in ps:
        p.start()
    try:
        t0 = time.time()
        ch.generalize("warmups-day-13/mastery", wrong=None, fixed=None, diag=diag)
    finally:
        for p in ps:
            p.stop()
    return launched, t0


launched, _ = gen_with({"compound_today": TP.summary(res)})
assert "TODAY'S CODEC IN A MASTERY MIX" in launched["prompt"] and "compound-today-d13-edge" in launched["prompt"]
print("ok  D4 generalize prompt: compound-today block with the per-line truth")

# K1 merge probe: clean on real solvers (no false alarms D4-D13 metadata/binary/script/mobile: see the report), a miss
# when a solver can't take the merged shape
mres = TP.merge_probe(CH / "day13" / "mobile-keystore-misuse" / "solver", out_dir=TMPD / "merge")
assert mres["status"] == "clean", mres["status"]
mc = TMPD / "merge" / "compound-merge-d13"
mct = json.loads((mc / "contract.json").read_text())
assert mct["answer_ids"][-1] == "set4.answer" and "delivery 4: keystore_misuse.apk" in mct["questions"][-1]["artifact"]
assert (mc / "artifacts" / "delivery 4: keystore_misuse.apk").exists()
toy = fake_chal(13, lane="mobile-android", name="toymerge")
shutil.copytree(CH / "day13" / "mobile-keystore-misuse" / "solver" / "cases" / "single_solve", toy / "cases" / "single_solve")
base12 = TP.base_case(toy)                     # real D12 mobile auto-mastery (earlier day, same lane)
assert base12 is not None and "day12" in str(base12)
single_exp = json.loads((toy / "cases" / "single_solve" / "expected.json").read_text())
(toy / "answers.json").write_text(json.dumps({**json.loads((base12 / "expected.json").read_text()), **single_exp,
                                              **{f"set4.{k}": v for k, v in single_exp.items()}}))
(toy / "solve.py").write_text(
    "import json,sys,re\nc=json.load(open(sys.argv[sys.argv.index('--contract')+1]))\n"
    "sets={re.match(r'set(\\d+)',a).group(1) for a in c['answer_ids'] if a.startswith('set')}\n"
    "assert len(sets)<=3, 'one family per contract'\n"
    "a=json.load(open('answers.json'))\nprint(json.dumps({k:a[k] for k in c['answer_ids'] if k in a}))\n")
tres = TP.merge_probe(toy, out_dir=TMPD / "toymerge")
assert tres["status"] == "miss" and "one family per contract" in (tres["results"][0]["error"] or ""), tres["status"]
assert "merged" in TP.merge_summary(tres)
print("ok  K1 merge probe: real D13 mobile solver clean (set 4 = Single under 'delivery 4:'); a one-family solver -> miss")

# ---------------------------------------------------------------------------------------------------------------- D5
cv = fake_chal(13, name="capture")
art = TMPD / "capart"
art.mkdir()
shutil.copy2(ATT13 / "blob-01.txt", art / "blob-01.txt")
c13 = json.loads((ATT13 / "contract.json").read_text())
last13 = json.loads((ATT13 / "last_timed.json").read_text())
with mock.patch.object(orch.cli, "load", lambda cid, f: c13), mock.patch.object(orch.timed, "artifacts_for", lambda cid, c: art), \
        mock.patch.object(orch.timed, "last_result", lambda cid: last13), \
        mock.patch.object(orch.cli, "confirmed_answers", lambda cid: {}):
    case = orch.capture_variant("warmups-day-13/mastery", cv)
exp = json.loads((case / "expected.json").read_text())
fb = json.loads((case / "gm_feedback.json").read_text())
assert case.name == "variant-mastery-bd5589ea" and len(exp) == 39 and len(fb["rejected"]) == 20 and fb["require_complete"]
assert all(exp.get(a) != v[0] for a, v in fb["rejected"].items())
with mock.patch.object(orch, "VERIFIED_GREEN", False), mock.patch.object(orch.cli, "load", lambda cid, f: c13), \
        mock.patch.object(orch.timed, "artifacts_for", lambda cid, c: art), \
        mock.patch.object(orch.timed, "last_result", lambda cid: last13), \
        mock.patch.object(orch.cli, "confirmed_answers", lambda cid: {}):
    case_off = orch.capture_variant("warmups-day-13/mastery", fake_chal(13, name="captureoff"))
assert json.loads((case_off / "expected.json").read_text()) == {} and not (case_off / "gm_feedback.json").exists()
print("ok  D5 capture_variant: D13 bd5589ea -> 39 GM-verified answers + 20 rejected values (require_complete); flag off -> {}")

# test_solver: the real D13 solver passes it; rejected hit / incomplete -> not ok
shutil.copy2(S13 / "solve.py", cv / "solve.py")
r = {x["case"]: x for x in solvers.test_solver(cv)}["variant-mastery-bd5589ea"]
assert r["ok"] and r["verified_n"] == 39 and r["rejected_hits"] == 0 and r["answered"] == 63 and not r["fully_verified"], r
bad_a, bad_v = next(iter(fb["rejected"].items()))
tsd = fake_chal(13, name="tsolver")
shutil.copytree(case, tsd / "cases" / case.name)
full = {**{a: "x-y-z-11" for a in c13["answer_ids"]}, **exp}
(tsd / "out.json").write_text(json.dumps(dict(full, **{bad_a: bad_v[0]})))
(tsd / "solve.py").write_text("import json;print(json.dumps(json.load(open('out.json'))))\n")
r = solvers.test_solver(tsd)[0]
assert not r["ok"] and r["rejected_hits"] == 1 and not r["diff"], r
(tsd / "out.json").write_text(json.dumps({k: v for k, v in full.items() if k != "set11.message"}))
r = solvers.test_solver(tsd)[0]
assert not r["ok"] and r["answered"] == 62 and r["rejected_hits"] == 0, r
(tsd / "out.json").write_text(json.dumps(full))
assert solvers.test_solver(tsd)[0]["ok"]
with mock.patch.object(solvers, "VERIFIED_GREEN", False):
    (tsd / "out.json").write_text(json.dumps(dict(full, **{bad_a: bad_v[0]})))
    assert solvers.test_solver(tsd)[0]["ok"]
print("ok  D5 test_solver: real D13 solver ok (39 verified, 0 rejected, 63/63); rejected hit / empty field -> not ok; "
      "flag off -> old rule")

# _watch_green rules


def watch(targets, fill, results, flag=True, seconds=6):
    c = bare_chain(sdir=TMPD, root=TMPD)
    seq = iter([{"solve.py": 1.0}])
    c._solver_mtimes = lambda: next(seq, {"solve.py": 2.0})
    green, done = threading.Event(), threading.Event()
    with mock.patch.object(orch.solvers, "test_solver", lambda *a, **k: results), \
            mock.patch.object(orch, "say", lambda m: None), mock.patch.object(orch.time, "time", lambda: 10 ** 6), \
            mock.patch.object(orch, "VERIFIED_GREEN", flag):
        t = threading.Thread(target=orch.Chain._watch_green, args=(c, targets, {"old"}, False, green, done, fill))
        t.start()
        green.wait(seconds)
        done.set()
        t.join(5)
    return green.is_set()


filled = [{"case": "var", "ok": False, "unverified": True, "answered": 5, "total": 5, "seconds": 0.1},
          {"case": "old", "ok": True, "seconds": 0.1}]
assert not watch(set(), {"var"}, filled, seconds=4.5)
assert watch({"compound-today-d14-even"}, {"var"}, filled + [{"case": "compound-today-d14-even", "ok": True, "seconds": 0.1}])
assert watch(set(), {"var"}, filled, flag=False)
print("ok  D5 _watch_green: fill-only never ends the worker; + a passing GM-verified target -> green; flag off -> old")

# expected/feedback guard
gch = bare_chain(sdir=cv)
snap = gch._expected_snapshot()
(case / "gm_feedback.json").write_text("{}")
(case / "expected.json").write_text("{}")
(cv / "cases" / "single_solve").mkdir(exist_ok=True)
with mock.patch.object(orch, "say", lambda m: None):
    gch._restore_expected("c", snap)
assert json.loads((case / "gm_feedback.json").read_text()) == fb and len(json.loads((case / "expected.json").read_text())) == 39
(case / "gm_feedback.json").unlink()
snap = gch._expected_snapshot()
(case / "gm_feedback.json").write_text('{"rejected": {}}')
with mock.patch.object(orch, "say", lambda m: None):
    gch._restore_expected("c", snap)
assert not (case / "gm_feedback.json").exists()
print("ok  D5 guard: worker edits to gm_feedback.json restored, worker-made ones removed")

# ---------------------------------------------------------------------------------------------------------------- E1
blob = (ATT13 / "blob-01.txt").read_bytes()
assert hashlib.sha256(blob).hexdigest() == c13["sha256"]
listing = f"{len(blob)}\tblob-01.txt\n{(ATT13 / 'contract.json').stat().st_size}\tcontract.json\n10\tresult.json\n"
srcs = {"blob-01.txt": blob, "contract.json": (ATT13 / "contract.json").read_bytes(), "result.json": b"{}"}
fetched = []


def fake_fetch(rpath, dst, size, streams=4):
    fetched.append(Path(rpath).name)
    Path(dst).write_bytes(srcs[Path(rpath).name])


res13 = {"result": "solver_incomplete", "missing": last13["missing"], "partial_wrong": last13["partial_wrong"],
         "attempt_id": last13["attempt_id"]}
with mock.patch.object(workers.remote, "ssh", lambda *a, **k: subprocess.CompletedProcess(a, 0, listing, "")), \
        mock.patch.object(workers.remote, "fetch_file", fake_fetch):
    got = workers.scoped_pull(res13, "warmups_day_13_mastery", TMPD / "pull")
    assert got == ["blob-01.txt"] and fetched[-1] == "blob-01.txt" and (TMPD / "pull" / "blob-01.txt").read_bytes() == blob
    with mock.patch.object(workers, "BUNDLE_FALLBACK", False):
        try:
            workers.scoped_pull(res13, "warmups_day_13_mastery", TMPD / "pull2")
            raise AssertionError("no fallback expected")
        except RuntimeError as e:
            assert "no failing-set delivery" in str(e)
print("ok  E1 bundle fallback: D13 Mastery (one zip, no artifacts[]) -> ['blob-01.txt'] sha-checked; flag off -> old error")

# async profile: the worker launches at once; profile.txt shows up interrupted
psd = fake_chal(13, name="prof")
(psd / "cases" / "single_solve" / "artifacts").mkdir(parents=True)
(psd / "cases" / "single_solve" / "contract.json").write_text(json.dumps({"answer_ids": ["message"]}))
(psd / "solve.py").write_text("import time\ndef spin():\n    t=time.time()\n    while time.time()-t<30: pass\nspin()\n")
sync_calls = []
launched, t0 = gen_with({"single_seconds": 30}, sdir=psd, PROFILE_SECONDS=1.5)
assert launched["t"] - t0 < 1.0 and "profile.txt" in launched["prompt"], launched["t"] - t0
pf = TMPD / "gencdir" / "profile.txt"
for _ in range(80):
    if pf.exists():
        break
    time.sleep(0.1)
assert pf.exists() and "INTERRUPTED" in pf.read_text() and "spin" in pf.read_text(), pf.exists() and pf.read_text()[:300]
with mock.patch.object(orch.solvers, "profile_solver", lambda *a, **k: sync_calls.append(a) or "cProfile of x"):
    launched, _ = gen_with({"single_seconds": 30}, sdir=psd, PROFILE_ASYNC=False)
assert sync_calls and "HOT PATH (harness-run profile" in launched["prompt"]
print("ok  E1 async profile: worker launched <1 s after generalize start, profile.txt (SIGINT at 1.5 s) names the hot "
      "loop; flag off -> synchronous profile in the prompt")

# ---------------------------------------------------------------------------------------------------------------- E2
hw = TMPD / "hw"
adir = hw / ".run" / "tmp-timed" / "warmups_day_13_mastery"
adir.mkdir(parents=True)
(adir / "contract.json").write_bytes(srcs["contract.json"])
(adir / "blob-01.txt").write_bytes(blob)
with mock.patch.object(hb_daemon, "HW", hw):
    inl = hb_daemon._inline_bytes("warmups-day-13/mastery", res13, 2_000_000)
    assert set(inl) == {"contract.json", "blob-01.txt"} and base64.b64decode(inl["blob-01.txt"]) == blob
    assert hb_daemon._inline_bytes("warmups-day-13/mastery", res13, 1000) is None                  # over the cap
    assert hb_daemon._inline_bytes("warmups-day-13/mastery", dict(res13, result="correct"), 2_000_000) is None
    assert hb_daemon._inline_bytes("warmups-day-13/mastery", res13, 0) is None                     # old client
    assert hb_daemon._inline_bytes("warmups-day-13/mastery", dict(res13, attempt_id="other"), 2_000_000) is None

calls = []


class FakeDaemon:
    def call(self, op, timeout=60, **kw):
        calls.append(kw)
        out = dict(res13)
        if kw.get("inline_max"):
            out["_inline"] = inl
        return {"result": out}


def no_remote(*a, **k):
    raise AssertionError("remote call on the inline path")


cid = "warmups-day-13/mastery"
local = ROOT / ".run" / "tmp-timed" / "warmups_day_13_mastery"
saved_local = TMPD / "saved-local"
if local.exists():
    shutil.copytree(local, saved_local)
try:
    with mock.patch.object(workers, "hb_daemon", lambda *a, **k: FakeDaemon()), \
            mock.patch.object(workers, "sync_homebase_base", lambda *a, **k: None), \
            mock.patch.object(workers, "push_hot_files", lambda *a, **k: None), \
            mock.patch.object(workers, "_solver_sig", lambda d: ("same",)), \
            mock.patch.dict(workers._pushed, {str(S13): ("same",)}), \
            mock.patch.object(workers, "timed_env", lambda cid: {}), \
            mock.patch.object(workers.remote, "ssh", no_remote), mock.patch.object(workers.remote, "fetch_file", no_remote), \
            mock.patch.object(workers.remote, "rsync_from", no_remote):
        out = workers.run_hb_timed(S13, cid)
        assert calls[-1].get("inline_max") == workers.INLINE_PULL_MAX and "_inline" not in out
        assert "inline from the daemon: blob-01.txt" in out["capture_note"], out.get("capture_note")
        assert (local / "blob-01.txt").read_bytes() == blob and (local / "contract.json").exists()
        with mock.patch.object(workers, "INLINE_PULL_MAX", 0), \
                mock.patch.object(workers, "scoped_pull", lambda *a, **k: ["pulled"]):
            out = workers.run_hb_timed(S13, cid)
        assert "inline_max" not in calls[-1] and out["capture_note"].startswith("scoped pull: pulled")
finally:
    shutil.rmtree(local, ignore_errors=True)
    if saved_local.exists():
        shutil.copytree(saved_local, local)
print("ok  E2 inline bytes: daemon attaches a failed attempt's files under the cap; client writes them and skips the "
      "pull; HCTF_INLINE_PULL_MAX=0 / old daemon -> pull as before")

# ---------------------------------------------------------------------------------------------------------------- K2
from hctf import hb_timed  # noqa: E402
evs = []
hb_timed._CTX.on_event, hb_timed._CTX.opts = evs.append, {"HCTF_EARLY_GENERALIZE": "1"}
hb_timed._event("solved", {"attempt_id": "a1", "missing": ["set1.x"], "cid": "c"}, result="solver_incomplete")
hb_timed._CTX.opts = {"HCTF_EARLY_GENERALIZE": "0"}
hb_timed._event("solved", {"attempt_id": "a2"})
hb_timed._CTX.on_event = hb_timed._CTX.opts = None
assert [e["attempt_id"] for e in evs] == ["a1"] and evs[0]["event"] == "solved" and evs[0]["missing"] == ["set1.x"]

cl = object.__new__(workers.HbDaemon)
got_ev, done_ev = [], threading.Event()
cl.pending, cl.events = {"r1": (done_ev, {})}, {"r1": lambda m: got_ev.append(m)}
cl.p = type("P", (), {"stdout": [json.dumps({"id": "r1", "event": "solved", "data": {"attempt_id": "a1"}}) + "\n",
                                 json.dumps({"id": "r1", "ok": True, "result": {"result": "solver_incomplete"}}) + "\n"]})()
cl._read()
time.sleep(0.2)
assert done_ev.is_set() and cl.pending == {} and cl.events == {} and got_ev and got_ev[0]["data"]["attempt_id"] == "a1"

ecv = fake_chal(13, name="early")
gen_calls = []
ch = bare_chain(sdir=ecv)
ch.generalize = lambda cid, wrong=None, fixed=None, diag=None: (gen_calls.append((wrong, diag)), time.sleep(0.5))
local = TMPD / "early-local"
local.mkdir()
shutil.copy2(ATT13 / "contract.json", local / "contract.json")
shutil.copy2(ATT13 / "blob-01.txt", local / "blob-01.txt")
lr = [{}]
with mock.patch.object(workers, "EARLY_GENERALIZE", True), mock.patch.object(orch.cli, "save", lambda *a: None), \
        mock.patch.object(orch.cli, "load", lambda cid, f: c13), mock.patch.object(orch.timed, "artifacts_for", lambda cid, c: local), \
        mock.patch.object(orch.timed, "last_result", lambda cid: lr[0]), \
        mock.patch.object(orch.cli, "confirmed_answers", lambda cid: {}), mock.patch.object(orch, "say", lambda m: None):
    kw = ch._early_kw("warmups-day-13/mastery")
    kw["on_event"]({"event": "solved", "local": str(local), "attempt_id": c13["attempt_id"], "missing": last13["missing"],
                    "result": "solver_incomplete"})
    vcase = ecv / "cases" / "variant-mastery-bd5589ea"
    assert json.loads((vcase / "expected.json").read_text()) == {} and not (vcase / "gm_feedback.json").exists()
    ch._exp_before = ch._expected_snapshot()
    lr[0] = last13                                         # the final result: verdicts arrive
    t0 = time.time()
    assert ch._early_join("warmups-day-13/mastery") is True
    assert ch._early_join("warmups-day-13/mastery") is False
assert gen_calls and gen_calls[0][0] == [(a, None) for a in last13["missing"]] and gen_calls[0][1]["early"]
assert len(json.loads((vcase / "expected.json").read_text())) == 39
assert len(json.loads((vcase / "gm_feedback.json").read_text())["rejected"]) == 20
assert ch._exp_before["variant-mastery-bd5589ea"] == (vcase / "expected.json").read_bytes()
with mock.patch.object(workers, "EARLY_GENERALIZE", False):
    assert bare_chain()._early_kw("x") == {}
# watcher: a fill case that turned verified mid-worker counts as a target (early on); off -> it stays fill-only
turned = [{"case": "var", "ok": True, "unverified": False, "answered": 5, "total": 5, "seconds": 0.1},
          {"case": "old", "ok": True, "seconds": 0.1}]
with mock.patch.object(workers, "EARLY_GENERALIZE", True):
    assert watch(set(), {"var"}, turned)
assert not watch(set(), {"var"}, turned, seconds=4.5)
print("ok  K2 early generalize (default OFF): hb_timed event -> daemon -> client callback; the worker starts on the "
      "variant before the verdicts; the final verdicts fold into its expected.json/gm_feedback.json + snapshot")

shutil.rmtree(TMPD, ignore_errors=True)
print("ALL PASS")
