"""D31 warmups Mastery speed: today's codec registered as a KNOWN day once the Single is GM-verified, offline: real
D29/D30 GM bytes, fakes for the harness -- no GM, no LLM, no Homebase.

 C1 lib: "tonight" simulated with HCTF_CODEC_MAX_DAY=<day-1> (the day's codec unknown to lib) on the REAL Mastery case:
    with HCTF_WARMUPS_TODAY (codec name, as the harness passes it, and "<day>:<case>" = infer at import) every set
    decodes positionally -> all correct, fast (< 2 s for D30's 148 sets; ~30 s+ through _unknown_line_cands without)
 C2 the real previous-day solver on the real D30 Mastery case via solvers.run_solver with the registration env: 148/148
 C3 never registered: a wrong codec, an unknown name, a name not built from known codecs, a tampered slug, a day that
    already has a codec, the kill switch -- DAYS untouched
 C4 harness: prepare_warmups_today publishes only for a warmups chain whose cases/single_solve IS today's verified
    Single (contract = single_solve/start.json, expected = its confirmed answers): a prestaged yesterday's case, another
    lane, the kill switch -> nothing; run_solver / the local timed runner / the lib racer pass the env to warmups runs
    only; the orchestrator hook runs for warmups only; today_probe.today_codec reuses the verified codec

Run:  source bin/env.sh && python3 tests/test_d31_codec.py      (exit 0 = all pass)
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import zipfile
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

os.environ["HCTF_CODEC_MAX_DAY"] = "29"          # in-process lib = the night of D30 (url%xx-twice unknown)
os.environ.pop("HCTF_WARMUPS_TODAY", None)
os.environ.pop("HCTF_WARMUPS_REGISTER_TODAY", None)
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from hctf import libracer, orchestrate as orch, procgov, solvers, today_probe as TP, workers  # noqa: E402
from lib import warmups_codecs as W  # noqa: E402

PY = str(ROOT / ".venv" / "bin" / "python") if (ROOT / ".venv" / "bin" / "python").exists() else sys.executable
D30 = ROOT / "challenges" / "day30" / "warmups-percent-percent"
D30_MASTERY = D30 / "solver" / "cases" / "mastery-67adc0ee"
D29 = ROOT / "challenges" / "day29" / "warmups-rotten-base"
D29_MASTERY = D29 / "solver" / "cases" / "auto-mastery-a1db777c"
D29_SOLVER = D29 / "solver"
D30_CODEC = "stack:url%xx>url%xx"
TMPROOT = Path(tempfile.mkdtemp(prefix="t31c-", dir=ROOT / ".run"))


def fake_chal(chal_src, day, lane="warmups", tamper=None, prestaged=False):
    """A dayNN/<lane>-x tree under .run/ from a real chain's single_solve/{start,confirmed}.json + bytes:
    solver/cases/single_solve as ensure_case_and_test saves it (prestaged: yesterday's contract instead)."""
    chal = TMPROOT / f"t{time.time_ns()}" / f"day{day:02d}" / f"{lane}-sim"
    (chal / "single_solve").mkdir(parents=True)
    start = json.loads((chal_src / "single_solve" / "start.json").read_text())
    conf = json.loads((chal_src / "single_solve" / "confirmed.json").read_text())
    (chal / "single_solve" / "start.json").write_text(json.dumps(start))
    (chal / "single_solve" / "confirmed.json").write_text(json.dumps(conf))
    (chal / "meta.json").write_text(json.dumps({"lane": lane, "name": start.get("name")}))
    case = chal / "solver" / "cases" / "single_solve"
    (case / "artifacts").mkdir(parents=True)
    art = chal_src / "single_solve" / "artifacts" / "latest"
    for f in art.iterdir():
        if f.is_file():
            shutil.copy2(f, case / "artifacts" / f.name)
    contract = dict(start, attempt_id="yesterday") if prestaged else start
    expected = dict(conf[start["attempt_id"]])
    if tamper:
        expected = {k: tamper for k in expected}
    (case / "contract.json").write_text(json.dumps(contract))
    (case / "expected.json").write_text(json.dumps(expected))
    return chal


def lib_run(code, env):
    e = dict(os.environ, PYTHONPATH=str(ROOT), **env)
    r = subprocess.run([PY, "-I", "-c", f"import sys; sys.path.insert(0, {str(ROOT)!r})\n" + code],
                       capture_output=True, text=True, env=e, timeout=600)
    assert r.returncode == 0, r.stderr[-2000:]
    return json.loads(r.stdout.strip().splitlines()[-1])


DECODE_ALL = """
import json, time, zipfile
from lib import warmups_codecs as W, decode
case = {case!r}
exp = json.load(open(case + "/expected.json"))
contract = json.load(open(case + "/contract.json"))
z = zipfile.ZipFile(case + "/artifacts/" + [f for f in sorted(__import__("os").listdir(case + "/artifacts"))
                                              if not f.startswith(".")][0])
names = {{n.rsplit("/", 1)[-1]: n for n in z.namelist()}}
t0 = time.time(); ok = n = 0
for i in range(1, len(contract["answer_ids"]) + 1):
    out = decode.decode_chunked(z.read(names["blob-%02d.txt" % i]).decode()) or ""
    n += 1
    ok += out.rstrip().endswith(exp["set%d.message" % i])
print(json.dumps({{"reg": W.TODAY_REGISTERED, "ok": ok, "n": n, "s": round(time.time() - t0, 2)}}))
"""


def c1():
    single30 = fake_chal(D30, 30) / "solver" / "cases" / "single_solve"
    for label, val in (("codec", json.dumps({"day": 30, "case": str(single30), "codec": D30_CODEC})),
                       ("infer", f"30:{single30}")):
        r = lib_run(DECODE_ALL.format(case=str(D30_MASTERY)),
                    {"HCTF_CODEC_MAX_DAY": "29", "HCTF_WARMUPS_TODAY": val})
        assert r["reg"] == D30_CODEC and r["ok"] == r["n"] == 148, (label, r)
        assert r["s"] < 2.0, (label, r)
        print(f"ok  C1 D30 ({label}): `{r['reg']}` registered as day 30 -> {r['ok']}/{r['n']} sets in {r['s']}s")
    # a second real day: D29 (rot13 over base64) the night of D29
    if D29_MASTERY.is_dir():
        single29 = fake_chal(D29, 29) / "solver" / "cases" / "single_solve"
        r = lib_run(DECODE_ALL.format(case=str(D29_MASTERY)),
                    {"HCTF_CODEC_MAX_DAY": "28", "HCTF_WARMUPS_TODAY": f"29:{single29}"})
        assert r["reg"] and r["ok"] == r["n"] == 143 and r["s"] < 2.0, r
        print(f"ok  C1 D29 (infer): `{r['reg']}` registered as day 29 -> {r['ok']}/{r['n']} sets in {r['s']}s")


def c2():
    single30 = fake_chal(D30, 30) / "solver" / "cases" / "single_solve"
    contract = json.loads((D30_MASTERY / "contract.json").read_text())
    expected = json.loads((D30_MASTERY / "expected.json").read_text())
    env = {"HCTF_CODEC_MAX_DAY": "29",
           "HCTF_WARMUPS_TODAY": json.dumps({"day": 30, "case": str(single30), "codec": D30_CODEC})}
    env.update(solvers.small_pool_env(contract))
    # a copy of yesterday's solver at <ROOT>/<x>/dayNN/<chal>/solver: its `parents[4]` sys.path root = THIS tree's lib
    sdir = ROOT / f".t31c-{time.time_ns()}" / "day30" / "warmups-sim" / "solver"
    try:
        sdir.mkdir(parents=True)
        for f in D29_SOLVER.glob("*.py"):
            shutil.copy2(f, sdir / f.name)
        got, err, dt = solvers.run_solver(sdir, contract, D30_MASTERY / "artifacts", 120, env_extra=env)
    finally:
        shutil.rmtree(sdir.parents[2], ignore_errors=True)
    ok = sum(got.get(k) == v for k, v in expected.items())
    assert not err and ok == len(expected) == 148, (err, ok, dt)
    assert dt < 15, dt   # ~1-3 s (interpreter + 2-proc pool); ~30-110 s on this box without the registration
    print(f"ok  C2 D29 solver + registration on the real D30 Mastery (2-proc pool): {ok}/148 in {dt:.1f}s")


def c3():
    single30 = fake_chal(D30, 30) / "solver" / "cases" / "single_solve"
    n0 = len(W.DAYS)
    assert W.day_codec(30) is None
    for bad in ("stack:url%xx", "rot13", "nope", "stack:url%xx>nope", "affine3,5", "subst", ""):
        assert W.today_codec_spec(30, single30, name=bad) is None, bad
        assert W.register_today(30, single30, name=bad) is None, bad
    tampered = fake_chal(D30, 30, tamper="wrong-slug-words-99") / "solver" / "cases" / "single_solve"
    assert W.register_today(30, tampered, name=D30_CODEC) is None
    assert W.register_today(30, tampered) is None            # inferred, but the verified slug doesn't come back
    assert W.register_today(29, single30, name="rot13-b64") is None   # day 29 already has a codec
    assert W.register_today(30, TMPROOT / "missing", name=D30_CODEC) is None
    with mock.patch.dict(os.environ, {"HCTF_WARMUPS_REGISTER_TODAY": "0"}):
        assert W.register_today(30, single30, name=D30_CODEC) is None
        assert W.register_today_env(json.dumps({"day": 30, "case": str(single30), "codec": D30_CODEC})) is None
    assert W.register_today_env("garbage") is None and W.register_today_env("{bad json") is None
    assert len(W.DAYS) == n0 and W.day_codec(30) is None
    # the verified one registers, then a second call is a no-op
    assert W.today_codec_spec(30, single30, name=D30_CODEC)[0] == D30_CODEC
    print("ok  C3 wrong / unknown / unbuildable codec, tampered slug, known day, missing case, kill switch, bad env "
          "-> never registered (DAYS untouched)")


def c4():
    solvers._WTODAY.clear()
    solvers._WTODAY_CACHE.clear()
    # another lane / a prestaged yesterday's case / kill switch -> nothing published
    other = fake_chal(D30, 30, lane="binary-reverse-engineering")
    assert solvers.prepare_warmups_today(other / "solver") is None and not solvers._WTODAY
    stale = fake_chal(D30, 30, prestaged=True)
    assert solvers.prepare_warmups_today(stale / "solver") is None and not solvers._WTODAY
    chal = fake_chal(D30, 30)
    sdir = chal / "solver"
    with mock.patch.dict(os.environ, {"HCTF_WARMUPS_REGISTER_TODAY": "0"}):
        assert solvers.prepare_warmups_today(sdir) is None and not solvers._WTODAY
    t0 = time.time()
    spec = solvers.prepare_warmups_today(sdir, hints=("Percent Percent",))
    assert spec and spec[0] == D30_CODEC, spec
    t_inf = time.time() - t0
    t0 = time.time()
    assert solvers.prepare_warmups_today(sdir) is spec and time.time() - t0 < 0.1   # cached
    env = solvers.warmups_today_env(sdir)
    v = json.loads(env["HCTF_WARMUPS_TODAY"])
    assert v["day"] == 30 and v["codec"] == D30_CODEC and Path(v["case"]).is_dir()
    assert solvers.warmups_today_env(other / "solver") == {} and solvers.warmups_today_env(lane="web") == {}
    with mock.patch.dict(os.environ, {"HCTF_WARMUPS_REGISTER_TODAY": "0"}):
        assert solvers.warmups_today_env(sdir) == {}
    # today_probe.today_codec: the same verified codec (no second inference)
    with mock.patch.object(W, "infer_case", side_effect=AssertionError("re-inferred")):
        name, enc = TP.today_codec(sdir)
    assert name == D30_CODEC and enc("Ni") == "%25%34%65%25%36%39"
    # run_solver: a warmups solver sees it, another lane's doesn't
    probe = "import json, os\nprint(json.dumps({'v': os.environ.get('HCTF_WARMUPS_TODAY', '')}))\n"
    (sdir / "solve.py").write_text(probe)
    (other / "solver" / "solve.py").write_text(probe)
    c = {"answer_ids": ["v"], "questions": [{"id": "v"}]}
    got, err, _ = solvers.run_solver(sdir, c, sdir, 30)
    assert not err and json.loads(got["v"])["codec"] == D30_CODEC, (got, err)
    got, err, _ = solvers.run_solver(other / "solver", c, other / "solver", 30)
    assert not err and got["v"] == "", got
    # the local timed runner (hb_timed spawn) and the lib racer subprocess
    seen = []

    def fake_run(cmd, **kw):
        seen.append(kw.get("env") or {})
        return subprocess.CompletedProcess(cmd, 0, '{"result": "correct"}\n', "")
    with mock.patch.object(workers, "timed_env", lambda cid: {}), mock.patch.object(procgov, "run", fake_run):
        workers.run_timed(sdir, "warmups-day-30/mastery")
        workers.run_timed(other / "solver", "binary-day-30/mastery")
        libracer.decode_candidates("warmups", sdir / "c.json", sdir, ["v"], timeout=5)
        libracer.decode_candidates("web", sdir / "c.json", sdir, ["v"], timeout=5)
    assert [("HCTF_WARMUPS_TODAY" in e) for e in seen] == [True, False, True, False], [list(e)[:3] for e in seen]
    # the orchestrator hook: warmups only, once
    solvers._WTODAY.clear()
    solvers._WTODAY_CACHE.clear()
    said = []
    with mock.patch.object(orch, "say", said.append):
        fake = SimpleNamespace(lane="binary-reverse-engineering", base="binary-day-30", sdir=other / "solver", name="x")
        orch.Chain._start_warmups_today(fake)
        assert not hasattr(fake, "_wtoday_fut")
        fake = SimpleNamespace(lane="warmups", base="warmups-day-30", sdir=sdir, name="Percent Percent")
        orch.Chain._start_warmups_today(fake)
        assert fake._wtoday_fut.result(timeout=60)[0] == D30_CODEC
        orch.Chain._start_warmups_today(fake)   # once per chain
        from concurrent.futures import Future
        pend = SimpleNamespace(_wtoday_fut=Future())
        t0 = time.time()
        orch.Chain._await_warmups_today(pend, "warmups-day-30/mastery", timeout=0.2)   # bounded, never raises
        assert 0.15 < time.time() - t0 < 2 and any("still running" in s for s in said)
        orch.Chain._await_warmups_today(SimpleNamespace(), "warmups-day-30/mastery")   # no registration started
    assert sum("registered as a known day" in s for s in said) == 1, said
    assert "HCTF_WARMUPS_TODAY" in solvers.warmups_today_env(sdir)
    solvers._WTODAY.clear()
    print(f"ok  C4 harness: published for today's verified warmups Single only ({t_inf:.2f}s inference, cached); "
          "run_solver / local timed runner / lib racer pass it to warmups runs only; orchestrator hook warmups-only, "
          "once; today-probe reuses the verified codec")


try:
    c3()
    c4()
    c1()
    c2()
finally:
    shutil.rmtree(TMPROOT, ignore_errors=True)
print("ALL PASS")
