"""Contract-drift watcher: after a run ends with unsolved modes, re-fetch their contracts on a timer and resume the chain
the moment the GM rewrites one of its questions in place.

D17 binary: two open-vocab `hcfg_storage` fields could not be answered; the organizers rewrote them into an enum ~4 h
after the drop, in the same attempt and without notice. The run had long finished and nothing was watching -- the fix
was found only because a human said so. `start_watch` (at "all chains finished", only when a mode is unsolved)
starts `hctf drift --day N --watch`: every HCTF_DRIFT_INTERVAL s until HCTF_DRIFT_UNTIL (default 20:15, before the next
drop's warm-up) it diffs each unsolved mode's questions (cli.contract_drift) and, on a change, runs
`hctf run --day N --only <chain>` with no post-run (HCTF_RATCHET=0), its output appended to the day log.
"""
import datetime
import json
import os
import shlex
import shutil
import subprocess
import sys
import time

from . import cli, paths
from .paths import ROOT

ENABLED = os.environ.get("HCTF_DRIFT_WATCH", "1") != "0"
INTERVAL = float(os.environ.get("HCTF_DRIFT_INTERVAL", "600"))
UNTIL = os.environ.get("HCTF_DRIFT_UNTIL", "20:15")
RESUME_LOCAL = int(os.environ.get("HCTF_DRIFT_RESUME_LOCAL", "3"))
SYSTEMD = os.environ.get("HCTF_DRIFT_SYSTEMD", "1") != "0"


def _tag(day):
    return f"day{int(day):02d}"


def unsolved(day):
    """[(chain base id, mode id)] of every mode of `day` with a saved contract that the GM has not marked solved."""
    from . import webtarget
    out = []
    for p in sorted(paths.CHALLENGES.glob(f"{_tag(day)}/*/meta.json")):
        meta = cli.load_json(p) or {}
        if webtarget.is_live_lane(meta.get("lane")):
            continue   # web: a resume = a new live target behind a serial driver's back (one per team) -- never
        ids = meta.get("ids") or {}
        base = ids.get("single_solve") or next((paths.base_id(v) for v in ids.values() if v), None)
        for mode in paths.MODES:
            cid = ids.get(mode)
            if not cid or not (cli.load(cid, "start.json") or cli.load(cid, "contract.json")):
                continue
            if not cli.gm_solved(cid):
                out.append((base, cid))
    return out


def deadline(until=UNTIL, now=None):
    """Epoch seconds of the next HH:MM (local) at least 30 min away (a run ending at 21:09 watches until tomorrow)."""
    now = now or datetime.datetime.now()
    h, m = (int(x) for x in until.split(":"))
    t = now.replace(hour=h, minute=m, second=0, microsecond=0)
    if t <= now + datetime.timedelta(minutes=30):
        t += datetime.timedelta(days=1)
    return t.timestamp()


def resume(day, base, log=print):
    """Re-run one chain on the rewritten contract (no post-run); output appended to the day log. Returns the exit code."""
    dlog = ROOT / ".run" / f"{_tag(day)}.log"
    env = dict(os.environ, HCTF_RATCHET="0", HCTF_DRIFT_WATCH="0", HCTF_DRIFT_RESUME="1")
    with open(dlog, "a") as fh:
        fh.write(f"{time.strftime('%H:%M:%S')} [drift] resuming {base} on its rewritten contract\n")
        fh.flush()
        r = subprocess.run([sys.executable, "-m", "hctf.cli", "run", "--day", str(day), "--only", base,
                            "--local", str(RESUME_LOCAL)], cwd=ROOT, env=env, stdout=fh, stderr=subprocess.STDOUT)
    log(f"[drift] resume of {base} exited {r.returncode}")
    return r.returncode


def check_once(day, do_resume=False, log=print):
    """One pass over the day's unsolved modes: {mode id: [changed answer ids]}; resumes changed chains if asked."""
    found, chains = {}, []
    for base, cid in unsolved(day):
        try:
            changed = cli.contract_drift(cid)
        except Exception as e:  # noqa: BLE001 - a check, never a failure
            log(f"[drift] {cid}: check failed ({type(e).__name__}: {str(e)[:120]})")
            continue
        if changed:
            found[cid] = changed
            log(f"[drift] DRIFT {cid}: the GM rewrote {len(changed)} question(s) in place ({', '.join(changed[:4])})")
            if base not in chains:
                chains.append(base)
    if do_resume:
        for base in chains:
            resume(day, base, log)
    return found


def watch(day, interval=INTERVAL, until=UNTIL, log=print):
    """Check every `interval` s until `until`; resume any chain whose contract the GM rewrote. Ends when all solved."""
    end = deadline(until)
    log(f"[drift] day {day}: watching unsolved modes every {interval:g}s until "
        f"{datetime.datetime.fromtimestamp(end):%a %H:%M}")
    while time.time() < end:
        todo = unsolved(day)
        if not todo:
            log(f"[drift] day {day}: every mode solved -- watch ends")
            return 0
        if not check_once(day, do_resume=True, log=log):
            log(f"[drift] day {day}: {len(todo)} unsolved mode(s), contracts unchanged")
        time.sleep(max(1.0, min(interval, end - time.time())))
    log(f"[drift] day {day}: deadline {until} reached -- watch ends")
    return 0


def _alive(pidfile):
    try:
        os.kill(int(pidfile.read_text().strip()), 0)
        return True
    except (OSError, ValueError):
        return False


def start_watch(day, log=print, popen=subprocess.Popen):
    """At "all chains finished": start the watcher for this day when a mode is unsolved (one per day). None if not."""
    if not ENABLED or os.environ.get("HCTF_DRIFT_RESUME"):
        return None
    pidfile = ROOT / ".run" / f"{_tag(day)}-drift.pid"
    if pidfile.exists() and _alive(pidfile):
        log(f"[drift] watcher for day {day} already running")
        return None
    todo = unsolved(day)
    if not todo:
        return None
    out = ROOT / ".run" / f"{_tag(day)}-drift.log"
    cmd = (f"{shlex.quote(sys.executable)} -m hctf.cli drift --day {int(day)} --watch "
           f"--interval {INTERVAL:g} --until {UNTIL}")
    script = (f"cd {shlex.quote(str(ROOT))} && source bin/env.sh >/dev/null 2>&1; echo $$ > {shlex.quote(str(pidfile))}; "
              f"exec {cmd} >> {shlex.quote(str(out))} 2>&1")
    if SYSTEMD and popen is subprocess.Popen and shutil.which("systemd-run"):
        unit = f"hctf-drift-{_tag(day)}-{time.strftime('%H%M%S')}"
        p = popen(["systemd-run", "--user", "--collect", "--unit", unit, "--working-directory", str(ROOT),
                   "bash", "-lc", script], cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        where = f"systemd user unit {unit}"
    else:
        p = popen(["bash", "-c", script], cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT,
                  start_new_session=True)
        where = "background process"
    names = sorted({cid for _b, cid in todo})
    log(f"[drift] {len(todo)} unsolved mode(s) ({', '.join(names[:3])}{'...' if len(names) > 3 else ''}): contract "
        f"watch every {INTERVAL:g}s until {UNTIL} ({where}) -> {out.relative_to(ROOT)}")
    return p


def status(day):
    """For `hctf drift --day N`: the watcher pid file + log tail (json-able)."""
    pidfile = ROOT / ".run" / f"{_tag(day)}-drift.pid"
    out = ROOT / ".run" / f"{_tag(day)}-drift.log"
    tail = out.read_text(errors="replace").splitlines()[-5:] if out.exists() else []
    return {"alive": pidfile.exists() and _alive(pidfile), "log": str(out), "tail": tail}


if __name__ == "__main__":
    print(json.dumps(status(sys.argv[1]), indent=2))
