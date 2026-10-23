#!/usr/bin/env python3
"""Offline self-test for hctf/hostguard.py (one harness copy busy per host; 10-22: rehearsal validation run beside main's
`prebuild --parallel`, load 37-50, every timing invalid). Never touches real /proc: every scan goes through an
injected fake process lister; harness copies are temp dirs (hctf/ + bin/env.sh); no real run/prebuild is spawned.
- classify: run vs prebuild vs ignored (feed/why/dash/solver-run, --stop/--list/--recover/--help, pgrep/grep/echo)
- chain shells: day.sh setsid launch, post-run prebuild chains (bash -c and systemd bash -lc 'cd ..; ..')
- root resolution: cwd, cwd walk-up, symlinked copy, PYTHONPATH/HCTF_ROOT env, parent shell `cd`, unresolvable
- other_copies excludes the own root (+ unresolved), own pid and its ancestors are ignored, shell+child dedupe
- CLI: check exit codes 0/1 (+ the OTHER line format bin/preflight.sh parses), stop-other-prebuilds (cwd/env/argv of
  `prebuild --stop`, chain shell SIGTERM first, runs untouched), load

Run:  source bin/env.sh && python3 tests/test_hostguard.py      (exit 0 = all pass)
"""
import io
import os
import shutil
import signal
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from hctf import hostguard as hg  # noqa: E402

failures = []


def check(name, cond, detail=""):
    print(("ok  " if cond else "FAIL ") + name + ("" if cond else f"  -- {detail}"))
    if not cond:
        failures.append(name)


def kind(argv):
    c = hg.classify(argv)
    return None if c is None else (c[0] + ("/shell" if c[1] else ""))


PY = "/home/u/huntress-2026/.venv/bin/python3"

# ------------------------------------------------------------------ 1. classification
CASES = [
    (["python3", "-m", "hctf.cli", "run", "--day", "22", "--local", "5", "--wait-release"], "run"),
    ([PY, "-m", "hctf.cli", "prebuild", "--parallel", "--n", "8"], "prebuild"),
    (["python3", "-u", "-m", "hctf.cli", "run", "--day", "3"], "run"),
    (["python3", "-X", "dev", "-W", "ignore", "-m", "hctf.cli", "prebuild", "--lane", "warmups"], "prebuild"),
    (["/bin/sh", "/home/u/huntress-2026/bin/hctf", "run", "--day", "5"], "run"),          # the bin/hctf wrapper
    (["timeout", "600", "python3", "-m", "hctf.cli", "run", "--day", "3"], "run"),
    (["python3", "-m", "hctf.cli", "feed", "--day", "22"], None),
    (["python3", "-m", "hctf.cli", "why", "warmups-day-22-x"], None),
    (["python3", "-m", "hctf.cli", "dash"], None),
    (["python3", "-m", "hctf.cli", "solver-run", "x"], None),
    (["python3", "-m", "hctf.cli", "postrun", "--day", "22"], None),
    (["python3", "-m", "hctf.cli", "prebuild", "--stop"], None),
    (["timeout", "60", "python3", "-m", "hctf.cli", "prebuild", "--stop"], None),
    (["python3", "-m", "hctf.cli", "prebuild", "--list"], None),
    (["python3", "-m", "hctf.cli", "prebuild", "--recover"], None),
    (["python3", "-m", "hctf.cli", "run", "--help"], None),
    (["python3", "-m", "hctf.hostguard", "check"], None),
    (["python3", "-c", "import time", "-m", "hctf.cli", "run"], None),
    (["pgrep", "-f", "hctf.cli prebuild|hctf prebuild"], None),
    (["grep", "hctf", "run"], None),
    (["/bin/sh", "/home/u/huntress-2026/bin/hctf", "feed", "--day", "22"], None),
    # chain / launch shells
    (["bash", "-c", f"{PY} -m hctf.cli prebuild --lane warmups --n 3 ; {PY} -m hctf.cli prebuild --lane binary"],
     "prebuild/shell"),
    (["bash", "-lc", f"cd /home/u/huntress-2026 && source bin/env.sh >/dev/null 2>&1; {PY} -m hctf.cli prebuild "
      "--parallel --n 8 >> /home/u/huntress-2026/.run/prebuild/x.log 2>&1"], "prebuild/shell"),
    (["bash", "-c", "cd '/home/u/huntress-2026' && source bin/env.sh && echo $$ > '/x/day22.pid' && echo "
      "'[effort] global=high; per lane: warmups=high' > '/x/day22.log'; hctf run --day 22 --local 5 "
      ">> '/x/day22.log' 2>&1; { echo; echo \"$(date +%H:%M:%S) [postrun] coverage start\"; }"], "run/shell"),
    (["bash", "-c", "-l", "cd ~/huntress-2026 && hctf run --day 4"], "run/shell"),
    (["bash", "-c", "cd ~/huntress-2026 && hctf prebuild --stop"], None),
    (["bash", "-lc", "cd ~/huntress-2026 && source bin/env.sh && hctf feed --day 22"], None),
    (["bash", "-c", "echo 'hctf run --day 5'"], None),
    (["bash", "-c", "pgrep -f 'hctf run' && echo busy"], None),
    (["bash", "-c", "eval 'cd ~/huntress-2026 && hctf run --day 5' < /dev/null"], None),
    (["bash", "/home/u/huntress-2026/.run/day22.unit.sh"], None),                       # no -c: the child is matched
]
for argv, want in CASES:
    got = kind(argv)
    check(f"1 classify {' '.join(argv)[:90]!r} -> {want}", got == want, f"got {got}")

# ------------------------------------------------------------------ fixtures: two harness copies on disk
TMP = Path(tempfile.mkdtemp(prefix="hostguard-test-"))
try:
    MAIN, ALT, NOWHERE = TMP / "main", TMP / "alt", TMP / "nowhere"
    for r in (MAIN, ALT):
        (r / "hctf").mkdir(parents=True)
        (r / "bin").mkdir()
        (r / "bin" / "env.sh").write_text("")
    (MAIN / "challenges" / "day22" / "x").mkdir(parents=True)
    NOWHERE.mkdir()
    (TMP / "halfcopy" / "hctf").mkdir(parents=True)                    # hctf/ without bin/env.sh: not a copy
    LINK = TMP / "alt-link"
    LINK.symlink_to(ALT)
    M, A = os.path.realpath(MAIN), os.path.realpath(ALT)
    # TMP may sit inside this repo (TMPDIR=.run/tmp): only the fixture copies count as harness copies here, so a
    # walk-up from an "unresolvable" fixture dir cannot land on the real checkout
    _real_is_root = hg.is_root
    hg.is_root = lambda d: os.path.realpath(d).startswith(os.path.realpath(TMP) + os.sep) and _real_is_root(d)

    def P(pid, argv, cwd=None, ppid=1, **kw):
        return dict(pid=pid, ppid=ppid, argv=argv, cwd=None if cwd is None else str(cwd), **kw)

    RUN = ["python3", "-m", "hctf.cli", "run", "--day", "22", "--local", "5"]
    PB = [PY, "-m", "hctf.cli", "prebuild", "--parallel"]

    # ------------------------------------------------------------------ 2. root resolution
    procs = [
        P(10, ["systemd", "--user"], "/"),
        P(100, RUN, MAIN, ppid=10),                                                  # cwd = the root
        P(101, PB, MAIN / "challenges" / "day22" / "x", ppid=10),                   # cwd walk-up
        P(102, PB, LINK, ppid=10),                                                   # symlinked copy -> real path
        P(103, RUN, NOWHERE, ppid=10, env={"PYTHONPATH": f"{ALT}:/usr/lib/x"}),     # bin/hctf wrapper's PYTHONPATH
        P(104, RUN, "/", ppid=10, env={"HCTF_ROOT": str(MAIN)}),                    # env.sh's HCTF_ROOT
        P(110, ["bash", "-c", f"cd '{ALT}' && source bin/env.sh && exec timeout 99 sleep 1"], None, ppid=10),
        P(111, ["timeout", "99", "sleep", "1"], None, ppid=110),
        P(112, RUN, None, ppid=111),                                                 # grandparent shell's `cd`
        P(120, ["bash", "-lc", f"cd {MAIN} && source bin/env.sh; {PY} -m hctf.cli prebuild --lane warmups"], None,
          ppid=10),                                                                  # chain shell: its own `cd`
        P(130, RUN, NOWHERE, ppid=10),                                               # unresolvable
        P(131, RUN, TMP / "halfcopy", ppid=10),                                      # hctf/ alone is not a copy
        P(140, ["python3", "-m", "hctf.cli", "feed", "--day", "22"], MAIN, ppid=10),  # ignored
    ]
    hp = {p["pid"]: p for p in hg.harness_procs(lambda: procs, self_pid=99999)}
    roots = {pid: p["root"] for pid, p in hp.items()}
    check("2 root: cwd == root", roots.get(100) == M, roots)
    check("2 root: cwd below the root walks up", roots.get(101) == M, roots)
    check("2 root: symlinked copy resolves to its real path", roots.get(102) == A, roots)
    check("2 root: PYTHONPATH (bin/hctf wrapper) when the cwd is not a copy", roots.get(103) == A, roots)
    check("2 root: HCTF_ROOT (bin/env.sh) when cwd + PYTHONPATH fail", roots.get(104) == M, roots)
    check("2 root: a grandparent shell's `cd <dir>` (through a timeout wrapper)", roots.get(112) == A, roots)
    check("2 root: a chain shell's own `cd <dir>`", roots.get(120) == M, roots)
    check("2 root: unresolvable -> None", 130 in hp and roots.get(130) is None, roots)
    check("2 root: hctf/ without bin/env.sh is not a harness copy", roots.get(131) is None, roots)
    check("2 kinds: feed ignored; run/prebuild/shell kinds set",
          140 not in hp and hp[100]["kind"] == "run" and hp[101]["kind"] == "prebuild"
          and hp[120]["kind"] == "prebuild" and hp[120]["shell"] and not hp[100]["shell"], hp.keys())
    _home = os.environ.get("HOME")
    os.environ["HOME"] = str(TMP)
    try:
        exp = (hg.root_of("~/main"), hg.root_of("$HOME/alt"), hg.root_of("${HOME}/main/challenges"))
    finally:
        os.environ["HOME"] = _home or ""
    check("2 root_of: '~' / $HOME / ${HOME} (a `cd ~/huntress-2026` in a shell)", exp == (M, A, M), exp)
    check("2 root_of: ' (deleted)' cwd suffix; relative / empty -> None",
          hg.root_of(f"{MAIN} (deleted)") == M and hg.root_of("relative/dir") is None
          and hg.root_of(None) is None)

    # ------------------------------------------------------------------ 3. other_copies
    oc_main = {p["pid"] for p in hg.other_copies(str(MAIN), list(hp.values()))}
    oc_alt = {p["pid"] for p in hg.other_copies(str(ALT), list(hp.values()))}
    oc_link = {p["pid"] for p in hg.other_copies(str(LINK), list(hp.values()))}
    check("3 other_copies(main) = the rehearsal copy's procs only (no own, no unresolved)", oc_main == {102, 103, 112}, oc_main)
    check("3 other_copies(alt) = main's procs only", oc_alt == {100, 101, 104, 120}, oc_alt)
    check("3 other_copies(<symlink to the rehearsal copy>) == other_copies(alt)", oc_link == oc_alt, oc_link)
    check("3 other_copies(<subdir of main>) walks the given root up too",
          {p["pid"] for p in hg.other_copies(str(MAIN / "challenges"), list(hp.values()))} == oc_main)
    check("3 other_copies with a lister (no procs given)",
          {p["pid"] for p in hg.other_copies(str(MAIN), proc_lister=lambda: procs, self_pid=99999)} == oc_main)

    # ------------------------------------------------------------------ 4. own pid + ancestors ignored
    anc = [
        P(1, ["init"], "/", ppid=0),
        P(500, ["bash", "-c", f"cd {ALT} && hctf run --day 22"], ALT, ppid=1),     # grandparent: rehearsal run shell
        P(501, RUN, ALT, ppid=500),                                                  # parent: rehearsal run
        P(502, ["python3", "-m", "hctf.hostguard", "check"], ALT, ppid=501),        # us
        P(600, RUN, MAIN, ppid=1),                                                   # unrelated main run
    ]
    got = {p["pid"] for p in hg.harness_procs(lambda: anc, self_pid=502)}
    check("4 own pid and its ancestors are never reported", got == {600}, got)
    got = {p["pid"] for p in hg.harness_procs(lambda: anc, self_pid=99999)}
    check("4 ... but are reported for anyone else", got == {500, 501, 600}, got)
    check("4 leaves(): a launch shell whose python child is listed is dropped",
          {p["pid"] for p in hg.leaves(hg.harness_procs(lambda: anc, self_pid=99999))} == {501, 600})

    # ------------------------------------------------------------------ 5. CLI check
    def cli(args, lister, **kw):
        out = io.StringIO()
        rc = hg.main(args, proc_lister=lister, self_pid=99999, out=out, settle=0, **kw)
        return rc, out.getvalue()

    busy = [P(1, ["init"], "/", ppid=0), P(200, RUN, ALT), P(201, PB, MAIN)]
    rc, out = cli(["check", "--root", str(MAIN)], lambda: busy)
    check("5 check: another copy's run -> exit 1", rc == 1, (rc, out))
    check("5 check: one `OTHER <kind> pid=<pid> root=<root> cmd=..` line per other-copy proc",
          out.splitlines() == [f"OTHER run pid=200 root={A} cmd={' '.join(RUN)}"], out)
    rc, out = cli(["check", "--root", str(ALT)], lambda: busy)
    check("5 check from the rehearsal copy: main's prebuild -> exit 1", rc == 1 and out.startswith("OTHER prebuild pid=201 "), out)
    rc, out = cli(["check", "--root", str(MAIN)], lambda: [P(1, ["init"], "/", ppid=0), P(201, PB, MAIN)])
    check("5 check: own-copy prebuild only -> exit 0", rc == 0 and out.startswith("ok:"), (rc, out))
    rc, out = cli(["check", "--root", str(MAIN)], lambda: [P(1, ["init"], "/", ppid=0), P(130, RUN, NOWHERE)])
    check("5 check: an unresolved-root run is not counted -> exit 0", rc == 0, (rc, out))
    rc, out = cli(["check", "--root", str(MAIN)], lambda: [
        P(1, ["init"], "/", ppid=0), P(300, ["bash", "-c", f"cd {ALT} && hctf run --day 9"], ALT, ppid=1),
        P(301, RUN, ALT, ppid=300)])
    check("5 check: launch shell + its python child = ONE line", rc == 1 and len(out.splitlines()) == 1
          and "pid=301" in out, out)

    def boom():
        raise RuntimeError("no /proc")
    rc, out = cli(["check", "--root", str(MAIN)], boom)
    check("5 check: the guard failing exits 3 (unknown), never 1 (busy)", rc == 3, (rc, out))

    # ------------------------------------------------------------------ 6. CLI stop-other-prebuilds
    state = {"stopped": False}
    calls, kills = [], []
    chain = P(401, ["bash", "-lc", f"cd {ALT} && source bin/env.sh; {PY} -m hctf.cli prebuild --lane warmups ; "
                    f"{PY} -m hctf.cli prebuild --lane binary"], ALT, ppid=1)

    def lister():
        base = [P(1, ["init"], "/", ppid=0), P(400, RUN, ALT, ppid=1), P(410, PB, MAIN, ppid=1)]
        if not state["stopped"]:
            base += [chain, P(402, PB, ALT, ppid=401)]
        return base

    def runner(cmd, **kw):
        calls.append((cmd, kw))
        state["stopped"] = True
        return SimpleNamespace(returncode=0, stdout="[prebuild] stopping batch pid 402\n", stderr="")

    rc, out = cli(["stop-other-prebuilds", "--root", str(MAIN)], lister, runner=runner,
                  killer=lambda pid, sig: kills.append((pid, sig)))
    check("6 stop: exactly one `prebuild --stop`, for the other copy", len(calls) == 1, calls)
    if calls:
        cmd, kw = calls[0]
        check("6 stop: argv = timeout 120 <this python> -m hctf.cli prebuild --stop",
              cmd == ["timeout", "120", sys.executable, "-m", "hctf.cli", "prebuild", "--stop"], cmd)
        check("6 stop: cwd=<that root>, PYTHONPATH=<that root> (no `source`)",
              kw.get("cwd") == A and kw.get("env", {}).get("PYTHONPATH") == A
              and kw["env"].get("HCTF_ROOT") == A, kw.get("cwd"))
    check("6 stop: the other copy's chain shell gets SIGTERM first (not the batch, not runs, not own prebuild)",
          kills == [(401, signal.SIGTERM)], kills)
    check("6 stop: exit 0 when nothing is left; the run is untouched", rc == 0 and "stopping the prebuild" in out
          and "400" not in "".join(str(c) for c in calls), (rc, out))

    calls.clear(), kills.clear()
    state["stopped"] = False
    rc, out = cli(["stop-other-prebuilds", "--root", str(ALT)], lister, runner=runner,
                  killer=lambda pid, sig: kills.append((pid, sig)))
    check("6 stop from the rehearsal copy: stops MAIN's prebuild, never the rehearsal copy's own",
          len(calls) == 1 and calls[0][1]["cwd"] == M and kills == [], (calls, kills))

    calls.clear()
    rc, out = cli(["stop-other-prebuilds", "--root", str(MAIN)],
                  lambda: [P(1, ["init"], "/", ppid=0), P(400, RUN, ALT), P(410, PB, MAIN)], runner=runner)
    check("6 stop: no other-copy prebuild -> nothing run, exit 0 (another copy's RUN is not a prebuild)",
          rc == 0 and calls == [] and "no other" in out, (rc, out, calls))

    stuck = [P(1, ["init"], "/", ppid=0), P(402, PB, ALT, ppid=1)]
    rc, out = cli(["stop-other-prebuilds", "--root", str(MAIN)], lambda: stuck,
                  runner=lambda cmd, **kw: SimpleNamespace(returncode=124, stdout="", stderr="timeout"))
    check("6 stop: a prebuild still alive after --stop -> exit 1 + `still alive: OTHER prebuild ..`",
          rc == 1 and "still alive: OTHER prebuild pid=402" in out, (rc, out))

    # ------------------------------------------------------------------ 7. load
    l5, n = hg.host_load()
    check("7 host_load = (float load5, int nproc >= 1)", isinstance(l5, float) and isinstance(n, int) and n >= 1)
    rc, out = cli(["load"], None)
    check("7 load CLI prints load5=<x> nproc=<n>", rc == 0 and out.startswith("load5=") and " nproc=" in out, out)
finally:
    shutil.rmtree(TMP, ignore_errors=True)

if failures:
    print(f"\n{len(failures)} FAILED: {failures}")
    sys.exit(1)
print("\nall hostguard checks passed")
