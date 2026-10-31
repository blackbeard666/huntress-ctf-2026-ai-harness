#!/usr/bin/env python3
"""Mastery-scale bench for the script lane (prebuild mastery-scale-bench-30k). Offline, no network, no hctf.

  solver mode (default): take a recorded Mastery case (contract.json + artifacts/), append extra sets cloned from set1
  (`set1.` -> `setN.` ids, same members) up to --sets, run the day's solver.py on it (parallel, as in the window) and
  report wall time + loadavg, then a sequential cProfile run's top hot functions (tottime and lib/codec cumtime).

  codec mode (--codec): replicate the first --sample tests/data/script_fixtures sources --sets times with per-set ident/content
  mutations (no memo hits across sets, like real Mastery), time find_codecs + the answer-JSON serialisation of a
  --ids-per-set answer dict, and profile it. Pure stdlib + lib.codec.

Always record loadavg: host load swings the solve phase (D29 one-set TT 5.48 s vs D30 0.74 s on the same solver).
Usage: python3 tests/data/script_fixtures/mt_bench.py [--case DIR] [--solver solve.py] [--sets 15] [--codec]
"""
import argparse, cProfile, io, json, os, pstats, re, subprocess, sys, tempfile, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DEF_CASE = ROOT / "challenges/day30/scripting-spill-the-beans/solver/cases/auto-mastery-4d7b1061"
DEF_SOLVER = ROOT / "challenges/day30/scripting-spill-the-beans/solver/solve.py"


def load():
    return " ".join(f"{x:.2f}" for x in os.getloadavg())


def expand(contract, sets):
    qs, ids = contract["questions"], contract["answer_ids"]
    have = sorted({int(m.group(1)) for q in qs for m in [re.match(r"set(\d+)\.", q["id"])] if m})
    base = [q for q in qs if q["id"].startswith("set1.")]
    for n in range(max(have, default=0) + 1, sets + 1):
        for q in base:
            q2 = dict(q, id=f"set{n}." + q["id"][5:])
            qs.append(q2)
            ids.append(q2["id"])
    return contract


def top(prof, n=5, pat=None):
    s = io.StringIO()
    st = pstats.Stats(prof, stream=s)
    if pat:
        st.sort_stats("cumtime").print_stats(pat, n)
    else:
        st.sort_stats("tottime").print_stats(n)
    return "\n".join(l for l in s.getvalue().splitlines() if re.match(r"\s*\d", l))


def solver_mode(a):
    case, tmp = Path(a.case), Path(tempfile.mkdtemp(prefix="mtbench-", dir=os.environ.get("TMPDIR")))
    c = expand(json.loads((case / "contract.json").read_text()), a.sets)
    cpath = tmp / "contract.json"
    cpath.write_text(json.dumps(c))
    n = len(c["answer_ids"])
    print(f"case {case.name}: {a.sets} sets, {n} ids  (loadavg {load()}, {os.cpu_count()} cpus)")
    env = dict(os.environ)
    if a.procs:
        env["HCTF_SOLVER_MAX_PROCS"] = str(a.procs)
    for i in range(a.repeat):
        l0, t0 = load(), time.time()
        r = subprocess.run([sys.executable, a.solver, "--contract", str(cpath), "--artifacts", str(case / "artifacts")],
                           capture_output=True, text=True, env=env)
        dt = time.time() - t0
        got = json.loads(r.stdout or "{}") if r.returncode == 0 else {}
        print(f"  run {i + 1}: solve {dt:.2f} s, {len(got)}/{n} answered, rc {r.returncode}  (loadavg {l0} -> {load()})")
        t1 = time.time()
        json.dumps({"answers": got})
        print(f"  answer-JSON serialise: {time.time() - t1:.3f} s ({len(json.dumps(got)) / 1e6:.2f} MB)")
    exp = case / "expected.json"
    if exp.exists() and got:
        e = json.loads(exp.read_text())
        e = e.get("answers", e) if isinstance(e, dict) else e
        bad = [k for k, v in e.items() if k in got and str(got[k]) != str(v)]
        print(f"  vs expected.json (recorded sets): {len(bad)} mismatches of {sum(k in got for k in e)}")
    prof = tmp / "seq.prof"
    env["HCTF_SOLVER_PARALLEL"] = "0"
    subprocess.run([sys.executable, "-m", "cProfile", "-o", str(prof), a.solver, "--contract", str(cpath),
                    "--artifacts", str(case / "artifacts")], capture_output=True, env=env)
    if prof.exists():
        print("top hot functions (sequential CPU, tottime):\n" + top(str(prof), a.top))
        print("lib/codec.py (cumtime):\n" + top(str(prof), a.top, r"lib/codec\.py"))


def codec_mode(a):
    sys.path.insert(0, str(ROOT))
    from lib import codec
    d = Path(__file__).resolve().parent
    srcs = [p.read_text(errors="replace") for p in sorted(d.iterdir())
            if p.suffix not in (".json", ".py", ".sh", ".exe", ".apk", ".zip", ".gz") and p.is_file()
            and p.stat().st_size < 1 << 16][:a.sample]
    print(f"codec bench: {len(srcs)} fixture sources x {a.sets} sets  (loadavg {load()})")

    def run():
        n = 0
        for s in range(a.sets):
            tag = f"{s:02d}"
            for src in srcs:
                # per-set mutation: a set-unique comment line, so no content memo hit crosses sets
                codec.find_codecs(f"# set{tag}\n" + src)
                for m in codec._CODEC_RE.finditer(src):
                    codec.material_text(src, m.group("id"))
                n += 1
        return n
    pr = cProfile.Profile()
    l0, t0 = load(), time.time()
    pr.enable()
    n = run()
    pr.disable()
    dt = time.time() - t0
    print(f"  find_codecs x {n}: {dt:.2f} s ({dt / max(n, 1) * 1e3:.2f} ms each; loadavg {l0} -> {load()})")
    t1 = time.time()
    run_again = sum(len(codec.find_codecs(f"# set00\n" + src)) for src in srcs)
    print(f"  memo re-read of set 0 ({len(srcs)} texts, {run_again} codecs): {time.time() - t1:.3f} s")
    ans = {f"set{s}.lang-{i:06x}-field": f"https://x-{s}-{i}.example.invalid/stage" for s in range(1, a.sets + 1)
           for i in range(a.ids_per_set)}
    t2 = time.time()
    json.dumps({"answers": ans})
    print(f"  answer-JSON serialise ({len(ans)} ids): {time.time() - t2:.3f} s")
    prof = Path(tempfile.mkdtemp(prefix="mtbench-", dir=os.environ.get("TMPDIR"))) / "codec.prof"
    pr.dump_stats(str(prof))
    print("top hot functions (tottime):\n" + top(str(prof), a.top))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--case", default=str(DEF_CASE))
    ap.add_argument("--solver", default=str(DEF_SOLVER))
    ap.add_argument("--sets", type=int, default=15)
    ap.add_argument("--ids-per-set", type=int, default=2000)
    ap.add_argument("--procs", type=int, default=0, help="HCTF_SOLVER_MAX_PROCS (2 = Homebase VM rehearsal)")
    ap.add_argument("--repeat", type=int, default=1)
    ap.add_argument("--top", type=int, default=5)
    ap.add_argument("--codec", action="store_true")
    ap.add_argument("--sample", type=int, default=40, help="codec mode: first N fixture sources (find_codecs is up to 2 s each)")
    a = ap.parse_args()
    codec_mode(a) if a.codec else solver_mode(a)


if __name__ == "__main__":
    main()
