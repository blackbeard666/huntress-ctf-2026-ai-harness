"""Parallel group testing: which answers of a rejected batch does the GM reject?

A GM "incorrect" on a multi-field submit names nothing; an "accepted" banks every field in it. So the wrong fields are
found by submitting groups: an accepted group is clean (and banked), a rejected one holds >= 1 wrong field and is
halved. D16 script single: the old bisect probed ONE group at a time, and its family key split 1095 fields into ~1000
one-field families -> 55 sequential submits, 4:04 of the day's 6-min critical path. The GM judges concurrent submits in
parallel (12 at once: 3.3 s wall vs 1.9 s for one, no 429), so each WAVE probes every open group at once:

  wave 1   the batch cut into ~TARGET contiguous groups (ids ordered by family, so a family stays together)
  wave k   every group that failed in wave k-1, cut into max(2, conc / failing groups) parts, all probed together
  unjudged (rate_limited / empty / transport): probed again once in the next wave, never counted as wrong
  already_solved: stop at once (the attempt is CORRECT)

Concurrency adapts (user-approved 2026-10-16): starts at HCTF_PROBE_CONC (12); a wave with any rate-limited probe
halves it (>= 2) and sleeps a short jittered backoff; each clean wave adds 2 back, up to the start value.

probe(group: dict) -> "ok" | "bad" | "solved" | "rate" | None (None = unjudged for another reason).
"""
import os
import random
import re
import threading
import time
from concurrent.futures import ThreadPoolExecutor

from . import ratebucket

CONC = max(1, int(os.environ.get("HCTF_PROBE_CONC", "12")))
CONC_MIN = 2
TARGET_GROUPS = int(os.environ.get("HCTF_PROBE_GROUPS", str(CONC)))   # wave 1 = one round at full concurrency
UNJUDGED_RETRIES = 1
SINGLES_MAX = int(os.environ.get("HCTF_PROBE_SINGLES_MAX", "6"))


def family(aid):
    """Coarse family key: optional set prefix + the first id token (resource-scenario -> resource; set2.batch-x -> set2.batch)."""
    m = re.match(r"((?:set\d+\.|slot\d+\.)?[A-Za-z0-9]+)", aid)
    return m.group(1) if m else aid


def initial_groups(answers, target=None, families=True):
    """Cut answers into <= target contiguous groups, ids ordered by family (stable within a family)."""
    ids = list(answers)
    if not ids:
        return []
    if families:
        order = {}
        for a in ids:
            order.setdefault(family(a), len(order))
        ids.sort(key=lambda a: order[family(a)])
    n = len(ids)
    # ~8 fields per group, 2..TARGET groups: a 1095-field batch is cut in 12 (one round at full concurrency), an
    # 11-field speculative remainder in 2 (not 11 one-field probes)
    target = max(1, min(n, target or max(2, min(TARGET_GROUPS, n // 8))))
    size = -(-n // target)
    return [{a: answers[a] for a in ids[i:i + size]} for i in range(0, n, size)]


def find_rejected(probe, answers, budget=None, conc=None, groups=None, families=True, whole_known_bad=True,
                  log=None, stop=None):
    """-> (rejected ids set, stats dict). `budget`: max probes (None = unbounded). `stop()`: True ends early (e.g. the
    worker took over). whole_known_bad: the caller already saw the whole batch rejected (no probe of it again)."""
    t0 = time.time()
    cmax = max(1, conc or CONC)
    c = ratebucket.wave_width(cmax, CONC_MIN)   # start narrow if another worker is already being throttled
    stats = {"probes": 0, "waves": 0, "rate_limited": 0, "unjudged": 0, "solved": False, "conc_min": c,
             "seconds": 0.0, "unjudged_fields": 0, "unjudged_ids": []}
    bad, unjudged_left = set(), []
    if not answers:
        return bad, stats
    if len(answers) == 1 and whole_known_bad:
        return set(answers), stats
    todo = [(g, 0) for g in (groups or initial_groups(answers, families=families))]
    lock = threading.Lock()

    def budget_left():
        return None if budget is None else budget - stats["probes"]

    while todo:
        if stop and stop():
            stats["stopped"] = True
            unjudged_left += [g for g, _ in todo]
            break
        if budget is not None and budget_left() <= 0:
            unjudged_left += [g for g, _ in todo]
            break
        stats["waves"] += 1
        wave, todo = todo, []
        if budget is not None:
            wave, rest = wave[:budget_left()], wave[budget_left():]
            unjudged_left += [g for g, _ in rest]
        results = [None] * len(wave)

        def one(i):
            g = wave[i][0]
            with lock:
                stats["probes"] += 1
            try:
                results[i] = probe(g)
            except Exception:  # noqa: BLE001 - a transport error judged nothing
                results[i] = None
        with ThreadPoolExecutor(max_workers=max(1, min(c, len(wave)))) as ex:
            list(ex.map(one, range(len(wave))))
        rate = False
        # k-ary split: the failing groups share the next wave's slots (rehearsal fair D16: halving took 7 waves x ~9 s over
        # the public GM for 5 wrong fields of 1095; splitting 12-way finds them in ~3 at the same 12 in flight)
        n_bad = sum(1 for r in results if r == "bad")
        parts = max(2, min(cmax, c) // max(1, n_bad))
        for (g, tries), r in zip(wave, results):
            if r == "solved":
                stats["solved"] = True
                todo = []
                break
            if r == "ok":
                continue
            if r == "bad":
                if len(g) == 1:
                    bad.update(g)
                else:
                    ks = list(g)
                    # a small failing group goes straight to one-field probes (2 more halving waves cost more than
                    # the few extra probes)
                    k = len(ks) if len(ks) <= SINGLES_MAX else min(len(ks), parts)
                    size = -(-len(ks) // k)
                    todo += [({x: g[x] for x in ks[i:i + size]}, 0) for i in range(0, len(ks), size)]
                continue
            # unjudged: rate-limited or other -- retry once next wave, never call it wrong
            if r == "rate":
                rate = True
                stats["rate_limited"] += 1
            else:
                stats["unjudged"] += 1
            if tries < UNJUDGED_RETRIES:
                todo.append((g, tries + 1))
            else:
                unjudged_left.append(g)
        if stats["solved"]:
            break
        if rate:
            c = max(CONC_MIN, c // 2)
            stats["conc_min"] = min(stats["conc_min"], c)
            time.sleep(1.0 + random.random())
        else:
            c = min(ratebucket.wave_width(cmax, CONC_MIN), c + 2)   # add back, but stay narrow under run-wide pressure
        if log:
            log(f"grouptest wave {stats['waves']}: {len(wave)} probe(s), {len(bad)} rejected so far, "
                f"{len(todo)} open, conc {c}")
    stats["unjudged_fields"] = sum(len(g) for g in unjudged_left)
    stats["unjudged_ids"] = [a for g in unjudged_left for a in g]
    stats["seconds"] = round(time.time() - t0, 2)
    return bad, stats
