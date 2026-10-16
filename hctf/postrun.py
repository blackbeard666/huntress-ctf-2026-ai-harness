"""Post-run phases: visible, persisted, resumable.

D16: after "all chains finished" the post-run ran ratchet -> technique logs -> speed-harden, then a machine-wide OOM
killed WSL mid speed-harden. Nothing said which phase it was in, `hctf feed` had already exited, train / prebuild /
coverage never ran, and the binary chain was left `generalizing` with an unrestored snapshot.

Every phase is wrapped in phase(): `HH:MM:SS [postrun] <phase> start` / `... done (Ns)` / `... FAILED (...)` in the day
log (the feed follows them) + .run/dayNN.postrun.json. `hctf postrun --day N [--from PHASE]` re-runs the remaining
phases after a crash; it first restores what a killed run leaves behind (recover()).
"""
import contextlib
import json
import os
import shutil
import subprocess
import sys
import time

from .paths import CHALLENGES, ROOT

PHASES = ("ratchet", "speed-harden", "train", "prebuild", "coverage")


def state_path(day):
    return ROOT / ".run" / f"day{int(day):02d}.postrun.json"


def load(day):
    try:
        return json.loads(state_path(day).read_text())
    except (OSError, ValueError):
        return {"phases": {}}


def _save(day, st):
    p = state_path(day)
    tmp = p.with_name(p.name + f".{os.getpid()}.tmp")
    tmp.write_text(json.dumps(st, indent=2))
    os.replace(tmp, p)


def _say(msg):
    from . import orchestrate
    orchestrate.say(msg)


@contextlib.contextmanager
def phase(day, name, log=None):
    """Mark one post-run phase (start / done / FAILED) in the log + the state file. Exceptions propagate."""
    log = log or _say
    st = load(day)
    st.setdefault("phases", {})[name] = {"start": time.strftime("%H:%M:%S"), "status": "running"}
    st["current"], st["pid"] = name, os.getpid()
    _save(day, st)
    log(f"[postrun] {name} start")
    t0 = time.time()
    status = "done"
    try:
        yield
    except BaseException as e:
        status = f"FAILED ({type(e).__name__}: {str(e)[:120]})"
        raise
    finally:
        st = load(day)
        st.setdefault("phases", {})[name] = {**st["phases"].get(name, {}), "end": time.strftime("%H:%M:%S"),
                                             "seconds": round(time.time() - t0), "status": status.split(" ")[0]}
        st["current"] = None
        _save(day, st)
        log(f"[postrun] {name} {status} ({time.time() - t0:.0f}s)")


def finished(day, log=None):
    """The run's own post-run is over (day.sh appends coverage + `post-run finished` after it)."""
    (log or _say)("[postrun] run phases done")


def recover(day, log=None):
    """Undo what a killed post-run leaves: a challenge solver mid-generalize (.generalize-snapshot -> restored, chain
    stage reset), and a lib ratchet that never finished (.run/ratchet-lib-dayNN still on disk -> lib/ + tests/
    restored). Never touches a chain while a run of this day is alive. Returns the list of actions."""
    log = log or _say
    tag = f"day{int(day):02d}"
    acts = []
    if run_alive(day):
        log(f"[postrun] {tag}: a run is still alive -- recovery skipped")
        return acts
    for snap in sorted((CHALLENGES / tag).glob("*/.generalize-snapshot")):
        root = snap.parent
        sdir = root / "solver"
        rejected = root / ".generalize-rejected"
        shutil.rmtree(rejected, ignore_errors=True)
        if sdir.exists():
            shutil.move(str(sdir), str(rejected))
        shutil.move(str(snap), str(sdir))
        try:
            ch = json.loads((root / "chain.json").read_text())
            if str(ch.get("stage", "")).endswith((":generalizing", ":solving")):
                from . import cli
                ids = (json.loads((root / "meta.json").read_text()).get("ids") or {}).values()
                ch["stage"] = "done" if ids and all(cli.gm_solved(i) for i in ids) else "interrupted"
                ch["worker"] = None
                (root / "chain.json").write_text(json.dumps(ch, indent=2))
        except (OSError, ValueError):
            pass
        acts.append(f"restored {sdir.relative_to(ROOT)} from its interrupted generalize "
                    f"(worker's copy in {rejected.relative_to(ROOT)})")
    lib_snap, tests_snap = ROOT / ".run" / f"ratchet-lib-{tag}", ROOT / ".run" / f"ratchet-tests-{tag}"
    if lib_snap.exists():
        shutil.rmtree(ROOT / "lib", ignore_errors=True)
        shutil.copytree(lib_snap, ROOT / "lib")
        shutil.rmtree(lib_snap, ignore_errors=True)
        acts.append("restored lib/ from the unfinished ratchet's snapshot")
        if tests_snap.exists():
            from . import orchestrate
            orchestrate._restore_tests(tests_snap)
            shutil.rmtree(tests_snap, ignore_errors=True)
            acts.append("restored tests/ from the unfinished ratchet's snapshot")
    for a in acts:
        log(f"[postrun] {tag}: {a}")
    return acts


def run_alive(day):
    """Is this day's run process (bin/day.sh pid file) still alive?"""
    p = ROOT / ".run" / f"day{int(day):02d}.pid"
    try:
        pid = int(p.read_text().strip())
        os.kill(pid, 0)
        return pid != os.getpid()
    except (OSError, ValueError):
        return False


def _coverage(day, log):
    for argv, tag in (([sys.executable, "-m", "lib.refs.coverage", str(day)], "attack-coverage"),
                      ([sys.executable, "-m", "hctf.toolchain", "report", "--day", str(day)], "tool-gaps")):
        r = subprocess.run(argv, cwd=ROOT, capture_output=True, text=True, timeout=600)
        for ln in (r.stdout + r.stderr).splitlines():
            log(f"[{tag}] {ln}")


def run_phases(day, start="ratchet", log=None):
    """Run the post-run phases from `start` (inclusive), each marked; a failing phase is logged and the next runs."""
    from . import orchestrate
    log = log or _say
    i = PHASES.index(start)
    for name in PHASES[i:]:
        try:
            with phase(day, name, log):
                if name == "ratchet":
                    orchestrate.ratchet_lib(day)
                elif name == "speed-harden":
                    orchestrate.speed_harden(day=day)
                elif name == "train":
                    from . import train
                    train.run(day, log=log)
                elif name == "prebuild":
                    from . import prebuild
                    prebuild.launch_background(day, log=log)
                elif name == "coverage":
                    _coverage(day, log)
        except Exception as e:  # noqa: BLE001 - one phase never stops the next
            log(f"[postrun] {name}: {type(e).__name__}: {str(e)[:200]}")
    log("post-run finished")
