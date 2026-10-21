"""Run timeline from .run/dayNN.log: per chain, T+ seconds to each mode's pass, timed attempts, generalize cycles,
worker (LLM) time vs harness overhead. The per-run table every review used to assemble by hand (rehearsal Day 7 review).

    hctf timeline --day 7 [--log path]
"""
import re
from pathlib import Path

from .paths import ROOT

LINE = re.compile(r"^(\d\d):(\d\d):(\d\d) \[([^\]]+)\] (.*)$")
MODES = ("single_solve", "time_trial", "mastery")
# Log lines that mean the Single Solve is CORRECT without the word CORRECT in them (feed + timeline + kpi share these).
# D20: an answer-first CORRECT ("single complete -> ending the answer-first worker") was missing here -> kpi said 20/21.
SINGLE_SOLVED = ("single complete -> ending the answer-first worker", "after worker: stopped at CORRECT",
                 "solved via GM issued_flag", "single CORRECT + solver verified", "after worker: complete=True",
                 "live-target lane: single CORRECT")


def timed_correct(msg):
    """A `timed: {...}` line whose attempt the GM judged CORRECT (the moment the mode is solved)."""
    return msg.startswith("timed: {") and '"result": "correct"' in msg[:120]


def single_solved(msg, mode):
    return mode == "single_solve" and ("CORRECT" in msg or "reuse race WON" in msg or msg.startswith(SINGLE_SOLVED)
                                       or msg.startswith("already solved"))


def _split(cid):
    m = re.match(r"^(.*?)/(time_trial|mastery)$", cid)
    return (m.group(1), m.group(2)) if m else (cid, "single_solve")


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
        if tag in ("homebase", "ratchet", "attack-coverage", "warm", "run"):
            continue
        base, mode = _split(tag)
        c = chains.setdefault(base, {"done": {}, "attempts": dict.fromkeys(MODES, 0), "workers": [], "open": {},
                                     "harvested": 0, "harvest_refused": 0})
        if single_solved(msg, mode) and "single_solve" not in c["done"]:
            c["done"]["single_solve"] = t
        if (msg.startswith("result: correct") or msg.startswith("passed by the live-answer worker")) \
                and mode not in c["done"]:
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


def report(day=None, log=None):
    path = Path(log) if log else ROOT / ".run" / f"day{int(day):02d}.log"
    t0, chains = parse(path.read_text(errors="replace").splitlines())
    if t0 is None:
        return f"no timestamped lines in {path}"
    rows = [f"timeline {path.name} (T0 = first event)",
            f"{'chain':44} {'single':>7} {'TT':>6} {'Mastery':>8} {'att TT/M':>9} {'gen n/s':>8} {'LLM s':>6} "
            f"{'other s':>7} {'harvest':>8}"]
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
        other = (end - llm) if end is not None else None
        harv = f"{c['harvested']}" + (f" ({c['harvest_refused']} ref)" if c["harvest_refused"] else "")
        rows.append(f"{base[:44]:44} {fmt('single_solve'):>7} {fmt('time_trial'):>6} {fmt('mastery'):>8} "
                    f"{c['attempts']['time_trial']:>4}/{c['attempts']['mastery']:<4} {len(gens):>3}/{sum(gens):<4} "
                    f"{llm:>6} {other if other is not None else '-':>7} {harv:>8}")
    complete = sum(1 for b in chains if len(chains[b]["done"]) == len(MODES))
    rows.append(f"{complete}/{len(chains)} chains complete; last pass T+{max(ends) if ends else '-'} s "
                "(LLM = worker wall time on that chain; other = harness/GM time on its critical path)")
    return "\n".join(rows)
