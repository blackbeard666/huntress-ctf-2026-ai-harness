"""Live progress FEED: one short, flushed line per milestone of a run, streamed from its log.

The day log is hundreds of noisy lines and `hctf watch` is a full-screen board, so nobody following a run from another
session (the orchestrator's Monitor, a reviewer's terminal) saw "binary Mastery solved, 9/15 at T+1:12" as it happened
(rehearsal D13 replays: the old grep|cut monitor buffered everything until the run ended).

    hctf feed --day 15                 follow .run/day15.log until "all chains finished"
    hctf feed --log PATH [--from-start] [--no-follow]

Lines:  T+1:03 ✅ script TT solved (in-attempt fix) [7/15]   ·   T+0:41 ⏳ metadata TT blocked -> generalize (+duel)
        T+1:55 🟢 metadata generalize accepted (42s)   ·   T+0:58 🤝 warmups duel won the single   ·   T+3:10 💬 hint ...
        T+2:00 · 12/15 solved · working: script Mastery (generalize 1:12)        (heartbeat, every 60 s while running)
"""
import json
import re
import sys
import time
from pathlib import Path

from .paths import ROOT
from .timeline import LINE, _split

LANES = (("warmups", "warmups"), ("metadata-forensics", "metadata"), ("script-analysis", "script"),
         ("binary-reverse-engineering", "binary"), ("mobile-android", "mobile"), ("welcome", "welcome"))
MODE_SHORT = {"single_solve": "single", "time_trial": "TT", "mastery": "Mastery"}
CHAINS = re.compile(r"(\d+) chains \((\d+) challenge modes\)")


def lane_of(base):
    for prefix, short in LANES:
        if base.startswith(prefix):
            return short
    return base.split("-day-")[0][:16]


def _secs(h, m, s):
    return int(h) * 3600 + int(m) * 60 + int(s)


def _fmt(sec):
    sec = max(0, int(sec))
    return f"{sec // 60}:{sec % 60:02d}"


class Feed:
    def __init__(self):
        self.t0 = None
        self.now = None
        self.total = None
        self.solved = set()          # (base, mode)
        self.activity = {}           # base -> (what, mode, since_secs)
        self.gen_start = {}          # base -> secs
        self.in_attempt = set()      # (base, mode) passed by in-attempt correction
        self.done = False

    def _t(self):
        return f"T+{_fmt((self.now or 0) - (self.t0 or self.now or 0))}"

    def _solve(self, base, mode, note=""):
        if (base, mode) in self.solved:
            return []
        self.solved.add((base, mode))
        self.activity.pop(base, None) if mode == "mastery" else None
        tot = f"/{self.total}" if self.total else ""
        return [f"{self._t()} ✅ {lane_of(base)} {MODE_SHORT[mode]} solved{note} [{len(self.solved)}{tot}]"]

    def process(self, line):
        """One log line -> [feed messages]."""
        line = line.rstrip("\n")
        out = []
        m = LINE.match(line)
        if not m:
            tm = re.match(r"^(\d\d):(\d\d):(\d\d) (.*)$", line)
            if tm:
                self.now = _secs(*tm.groups()[:3])
                msg = tm.group(4)
                c = CHAINS.search(msg)
                if c:
                    self.total = int(c.group(2))
                    self.t0 = self.now          # T+ counts from the run's start (after any release wait)
                    out.append(f"{self._t()} ▶ run started: {c.group(1)} chains, {c.group(2)} modes")
                elif msg.startswith("all chains finished"):
                    self.done = True
                    out.append(self.summary())
                elif "!!!" in msg:
                    out.append(f"{self._t()} ⚠ {msg[:200]}")
            elif "!!!" in line:
                out.append(f"⚠ {line[:200]}")
            return out
        h, mi, s, tag, msg = m.groups()
        self.now = _secs(h, mi, s)
        if self.t0 is None:
            self.t0 = self.now
        if "!!!" in line:
            out.append(f"{self._t()} ⚠ {msg[:200]}")
        if tag in ("homebase", "coord", "hof", "capture", "effort", "prebuild", "ratchet"):
            return out
        base, mode = _split(tag)
        lane = lane_of(base)
        ms = MODE_SHORT.get(mode, mode)
        if msg.startswith("timed: {"):
            try:
                d = json.loads(msg[len("timed: "):])
            except ValueError:
                d = {}
            if str(d.get("result", "")).lower() == "correct" and d.get("resubmit_fixed"):
                self.in_attempt.add((base, mode))
            return out
        if msg.startswith("result: correct"):
            out += self._solve(base, mode, " (in-attempt fix)" if (base, mode) in self.in_attempt else "")
        elif msg.startswith("result: blocked"):
            self.activity[base] = (f"{ms} blocked", mode, self.now)
            out.append(f"{self._t()} ⏳ {lane} {ms} blocked")
        elif msg.startswith("result: error") or msg.startswith("result: expired"):
            out.append(f"{self._t()} ⚠ {lane} {ms} {msg[len('result: '):][:80]}")
        elif "reuse race WON" in msg:
            out += self._solve(base, "single_solve", " (reuse race)")
        elif msg.startswith("after worker: stopped at CORRECT") or msg.startswith("solved via GM issued_flag") or \
                (msg.startswith("already solved") and mode == "single_solve"):
            out += self._solve(base, "single_solve")
        elif msg.startswith("single worker ->"):
            self.activity[base] = ("single (LLM)", "single_solve", self.now)
        elif msg.startswith("generalize worker ->"):
            self.gen_start[base] = self.now
            self.activity[base] = (f"{ms} generalize", mode, self.now)
            out.append(f"{self._t()} 🔧 {lane} {ms} generalize started")
        elif msg.startswith("duel generalize worker ->"):
            out.append(f"{self._t()} ➕ {lane} {ms} duel generalize started")
        elif msg.startswith("duel single worker ->"):
            out.append(f"{self._t()} ➕ {lane} duel single started")
        elif msg.startswith("generalize accepted") or msg.startswith("generalize REJECTED"):
            took = self.now - self.gen_start.pop(base, self.now)
            ok = msg.startswith("generalize accepted")
            out.append(f"{self._t()} {'🟢' if ok else '🔴'} {lane} generalize {'accepted' if ok else 'REJECTED'} "
                       f"({took}s)")
        elif "duel reached a verified solver first" in msg:
            out.append(f"{self._t()} 🤝 {lane} duel won the single")
        elif "duel generalize green first" in msg:
            out.append(f"{self._t()} 🤝 {lane} duel won the generalize")
        elif msg.startswith("coordinator hint"):
            out.append(f"{self._t()} 💬 {lane} {ms} hint: {msg.split(':', 1)[-1].strip()[:140]}")
        elif "single:help" in msg or msg.startswith("HELP") or "HELP.md" in msg:
            out.append(f"{self._t()} 🆘 {lane} {ms} asked for help: {msg[:120]}")
        return out

    def heartbeat(self):
        tot = f"/{self.total}" if self.total else ""
        work = []
        for base, (what, mode, since) in sorted(self.activity.items()):
            if (base, mode) in self.solved and "generalize" not in what:
                continue
            work.append(f"{lane_of(base)} {what} {_fmt((self.now or since) - since)}")
        return (f"{self._t()} · {len(self.solved)}{tot} solved" + (" · working: " + ", ".join(work) if work else ""))

    def summary(self):
        tot = f"/{self.total}" if self.total else ""
        missing = ""
        if self.total and len(self.solved) < self.total:
            missing = " -- NOT all solved (see `hctf dash` / `hctf why`)"
        return f"{self._t()} 🏁 all chains finished: {len(self.solved)}{tot} solved{missing}"


def parse_lines(lines):
    """All feed messages for a finished log (tests / --from-start --no-follow)."""
    f = Feed()
    out = []
    for ln in lines:
        out += f.process(ln)
    return out


def follow(path, from_start=False, follow_=True, heartbeat=60.0, poll=0.5):
    path = Path(path)
    for _ in range(int(3600 / poll)):           # the day log appears at launch
        if path.exists():
            break
        time.sleep(poll)
    f = Feed()
    say = lambda s: print(s, flush=True)  # noqa: E731
    with open(path, errors="replace") as fh:
        for ln in fh:                           # history: state always, messages only with --from-start
            msgs = f.process(ln)
            if from_start:
                for s in msgs:
                    say(s)
        if not from_start:
            say(f"(following {path.name}) " + f.heartbeat())
        if f.done or not follow_:
            return 0
        last_hb, buf = time.time(), ""
        while True:
            chunk = fh.readline()
            if chunk:
                buf += chunk
                if not buf.endswith("\n"):
                    continue
                for s in f.process(buf):
                    say(s)
                buf = ""
                if f.done:
                    return 0
                continue
            if time.time() - last_hb >= heartbeat:
                last_hb = time.time()
                if f.now is not None:
                    # advance the clock to wall time for the heartbeat (log timestamps are local HH:MM:SS)
                    lt = time.localtime()
                    f.now = max(f.now, lt.tm_hour * 3600 + lt.tm_min * 60 + lt.tm_sec)
                say(f.heartbeat())
            time.sleep(poll)


def main(day=None, log=None, from_start=False, follow_=True, heartbeat=60.0):
    path = Path(log) if log else ROOT / ".run" / f"day{int(day):02d}.log"
    return follow(path, from_start=from_start, follow_=follow_, heartbeat=heartbeat)


if __name__ == "__main__":
    sys.exit(main(log=sys.argv[1], from_start=True))
