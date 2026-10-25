"""Run timeline from .run/dayNN.log: per chain, T+ seconds to each mode's pass, timed attempts, generalize cycles,
worker (LLM) time vs harness overhead. The per-run table every review used to assemble by hand (rehearsal Day 7 review).

    hctf timeline --day 7 [--log path]
"""
import re
from pathlib import Path

from .paths import ROOT, canonical_lane

LINE = re.compile(r"^(\d\d):(\d\d):(\d\d) \[([^\]]+)\] (.*)$")
MODES = ("single_solve", "time_trial", "mastery")
# Log lines that mean the Single Solve is CORRECT without the word CORRECT in them (feed + timeline + kpi share these).
# D20: an answer-first CORRECT ("single complete -> ending the answer-first worker") was missing here -> kpi said 20/21.
SINGLE_SOLVED = ("single complete -> ending the answer-first worker", "after worker: stopped at CORRECT",
                 "solved via GM issued_flag", "single CORRECT + solver verified", "after worker: complete=True",
                 "live-target lane: single CORRECT")


# Log lines that mean a TIMED mode (Time Trial / Mastery) passed without a `timed: {..."correct"}` line (feed + timeline +
# kpi + effort_report share these). D25: two web TTs passed by the live answer during the codify wait (`passed by the
# live answer after 19s of the codify wait`) and returned with no recognised line -> feed 22/24 / kpi web 7/9 while the
# GM had 24/24. orchestrate now also logs `result: correct (<how>)` at every such exit; the list keeps older logs right.
TIMED_PASSED = ("result: correct", "passed by the live-answer worker", "passed by the live answer",
                "passed during the online resolution", "passed by the parallel live answer",
                "the probe attempt itself passed the mode")


def timed_passed(msg):
    """A line saying the tagged timed mode passed (any route: runner, live answer, online resolution, probe)."""
    return msg.startswith(TIMED_PASSED)


def timed_correct(msg):
    """A `timed: {...}` line whose attempt the GM judged CORRECT (the moment the mode is solved)."""
    return msg.startswith("timed: {") and '"result": "correct"' in msg[:120]


def single_solved(msg, mode):
    return mode == "single_solve" and ("CORRECT" in msg or "reuse race WON" in msg or msg.startswith(SINGLE_SOLVED)
                                       or msg.startswith("already solved"))


CHAIN_TAG = re.compile(r"-day-\d+")   # a chain's base id (`warmups-day-24`, `web-exploitation-day-15-fetch-quest`)
# `[slot] <cid>: waited 3.2s for a local slot` (Pools) / `[<web cid>] web target slot acquired after 484s` (webtarget)
SLOT_WAIT = re.compile(r"^(\S+?): waited ([\d.]+)s for a (\w+) slot")
WEB_SLOT = re.compile(r"web target slot acquired after ([\d.]+)s")


def is_chain(base):
    """A chain = any tag carrying a `-day-NN` part. Only those: `[res]`, `[hof]`, `[postrun]`, `[train]`... used to count
    as chains ("7/16 chains complete" on D24)."""
    return bool(CHAIN_TAG.search(base or ""))


def lane_label(base):
    """The lane a chain is reported under: its GM lane (`script-analysis`), except web -- one lane, several chains a
    day (D21: three) -- which is `web:<slug>` (`web:fetch-quest`), so two web chains stay distinct everywhere."""
    lane = (base or "").split("-day-")[0]
    if canonical_lane(lane) != "web":
        return lane
    slug = re.sub(r"^.*?-day-\d+-?", "", base or "")
    return f"web:{slug}" if slug else "web"


def _split(cid):
    m = re.match(r"^(.*?)/(time_trial|mastery)$", cid)
    return (m.group(1), m.group(2)) if m else (cid, "single_solve")


def _chain(chains, base):
    return chains.setdefault(base, {"done": {}, "attempts": dict.fromkeys(MODES, 0), "workers": [], "open": {},
                                    "harvested": 0, "harvest_refused": 0, "slot_wait": 0.0})


def parse(lines):
    """-> (t0_seconds, {base: info}). Times are seconds since midnight, unwrapped across midnight."""
    t0, last, wrap = None, None, 0
    chains = {}
    for raw in lines:
        m = LINE.match(raw.rstrip("\n"))
        if not m:
            continue
        t = int(m.group(1)) * 3600 + int(m.group(2)) * 60 + int(m.group(3)) + wrap
        if last is not None and t < last - 3600:  # crossed midnight
            wrap += 86400
            t += 86400
        last = t
        if t0 is None:
            t0 = t
        tag, msg = m.group(4), m.group(5)
        if tag == "slot":
            sw = SLOT_WAIT.match(msg)
            if sw and is_chain(sw.group(1)):
                c = _chain(chains, _split(sw.group(1))[0])
                c["slot_wait"] += float(sw.group(2))
            continue
        if tag in ("homebase", "ratchet", "attack-coverage", "warm", "run", "shapes"):
            continue
        base, mode = _split(tag)
        if not is_chain(base):
            continue
        c = _chain(chains, base)
        c.setdefault("first", t)   # the chain's launch (its first log line)
        sw = WEB_SLOT.search(msg)
        if sw:
            c["slot_wait"] += float(sw.group(1))
        if single_solved(msg, mode) and "single_solve" not in c["done"]:
            c["done"]["single_solve"] = t
        if timed_passed(msg) and mode not in c["done"]:
            c["done"][mode] = t   # a live-answer pass returns from timed_stage without a `result: correct` line
        if msg.startswith("timed: "):
            c["attempts"][mode] += 1
            if timed_correct(msg) and mode not in c["done"]:
                c["done"][mode] = t   # the GM's CORRECT: `result: correct` follows only after the case is saved (D20
                                      # script Mastery: 24 s later for its 6645-answer case)
        w = re.match(r"(\w+) worker -> (\S+)", msg)
        if w:
            c["open"][(mode, w.group(1))] = t
        w = re.match(r"(\w+) worker exit", msg)
        if w and (mode, w.group(1)) in c["open"]:
            c["workers"].append((mode, w.group(1), c["open"].pop((mode, w.group(1))), t))
        if re.match(r"harvest: variant-", msg):
            c["harvested"] += 1
        if "harvest: start refused" in msg:
            c["harvest_refused"] += 1
    return t0, chains


RELEASE = re.compile(r"^(\d\d):(\d\d):(\d\d) \d+ chains \(\d+ challenge modes\)")


def _anchor(lines, first, t0_hms=None):
    """(T0 seconds, label): an explicit HH:MM:SS (e.g. the 21:00:00 drop), else the run's release line (the chains
    launch), else the first event. D22 post-mortem P3: with `--wait` the first event is the arm ~49 min before the drop,
    so every T+ read +2927 s -- score runs per phase from the drop."""
    def secs(h, m, s):
        t = int(h) * 3600 + int(m) * 60 + int(s)
        return t + 86400 if t < first - 43200 else t   # a T0 after midnight relative to a pre-midnight first event
    if t0_hms:
        h, m, s = (t0_hms.split(":") + ["0", "0"])[:3]
        return secs(h, m, s), f"T0 = {t0_hms}"
    for raw in lines:
        r = RELEASE.match(raw)
        if r:
            return secs(*r.groups()), "T0 = release (chains launched)"
    return first, "T0 = first event"


def report(day=None, log=None, t0=None):
    path = Path(log) if log else ROOT / ".run" / f"day{int(day):02d}.log"
    lines = path.read_text(errors="replace").splitlines()
    first, chains = parse(lines)
    if first is None:
        return f"no timestamped lines in {path}"
    t0, label = _anchor(lines, first, t0)
    rows = [f"timeline {path.name} ({label})",
            f"{'chain':44} {'single':>7} {'TT':>6} {'Mastery':>8} {'->TT':>5} {'->M':>5} {'att TT/M':>9} {'gen n/s':>8} "
            f"{'LLM s':>6} {'other s':>7} {'harvest':>8}"]
    ends = []
    for base in sorted(chains, key=lambda b: max(chains[b]["done"].values(), default=10 ** 9)):
        c = chains[base]
        done = {m: c["done"][m] - t0 for m in c["done"]}
        end = max(done.values(), default=None)
        if end is not None and len(done) == len(MODES):
            ends.append(end)
        llm = sum(b - a for _, _, a, b in c["workers"])
        gens = [(b - a) for _, stage, a, b in c["workers"] if stage == "generalize"]
        fmt = lambda m: f"{done[m]}" if m in done else "-"  # noqa: E731
        dlt = lambda a, b: f"{done[b] - done[a]}" if a in done and b in done else "-"  # noqa: E731
        other = (end - llm) if end is not None else None
        harv = f"{c['harvested']}" + (f" ({c['harvest_refused']} ref)" if c["harvest_refused"] else "")
        rows.append(f"{base[:44]:44} {fmt('single_solve'):>7} {fmt('time_trial'):>6} {fmt('mastery'):>8} "
                    f"{dlt('single_solve', 'time_trial'):>5} {dlt('time_trial', 'mastery'):>5} "
                    f"{c['attempts']['time_trial']:>4}/{c['attempts']['mastery']:<4} {len(gens):>3}/{sum(gens):<4} "
                    f"{llm:>6} {other if other is not None else '-':>7} {harv:>8}")
    complete = sum(1 for b in chains if len(chains[b]["done"]) == len(MODES))
    rows.append(f"{complete}/{len(chains)} chains complete; last pass T+{max(ends) if ends else '-'} s "
                "(LLM = worker wall time on that chain; other = harness/GM time on its critical path)")
    return "\n".join(rows)
