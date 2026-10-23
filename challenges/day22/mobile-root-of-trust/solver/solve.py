#!/usr/bin/env python3
"""Solver for this challenge -- harness skeleton. Fill in `answer()`; keep the I/O contract unchanged.

    solve.py --contract <contract.json> --artifacts <dir>   ->  prints {answer_id: value} as JSON on the last line

Runs on the Homebase VM inside a ~6-7 s window for EVERY Mastery set: stdlib + lib.* + pyzipper/pyelftools/pefile/
capstone/pycryptodome/androguard only, no subprocess to 7z/jadx/etc., all sets well under 1 s. Mastery questions name
their files like 'delivery 2: sample_02.apk' or 'evidence.zip -> member': `artifact_bytes()` resolves both (by sha256
pairing first, so same-named per-set deliveries never get mixed up)."""
import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from lib.common import (container_by_sha, delivery_missing, find_artifact, group_by_set, load_contract,  # noqa: E402
                        normalize)
from lib import solverrt  # noqa: E402  -- partial-emit on deadline (cumulative-lane upgrade)
from lib.android import dex_strings, puzzle_candidates, raw_entry_scan  # noqa: E402
import io  # noqa: E402
import re  # noqa: E402

ANS = re.compile(r"ANS-[0-9A-F]{16}")

_cache = {}


def artifact_bytes(root, contract, artifact):
    """Bytes for a question's `artifact` string (cached per artifact)."""
    if artifact in _cache:
        return _cache[artifact]
    container, _, member = (x.strip() for x in artifact.partition("->"))
    data = None
    p = container_by_sha(root, contract, container)
    if p is not None and not member:
        data = p.read_bytes()
    elif not delivery_missing(root, contract, container):
        for cand in (artifact, container.split(": ", 1)[-1] + (f" -> {member}" if member else "")):
            try:
                data = find_artifact(root, cand)
                break
            except FileNotFoundError:
                continue
    _cache[artifact] = data
    return data


def _indexed(data):
    """d17 `indexed` codec: data chars + order[]; order[i] is the output slot of data[i] (else the inverse reading)."""
    import json, zipfile
    try:
        z = zipfile.ZipFile(io.BytesIO(data))
    except Exception:  # noqa: BLE001
        return None
    for n in z.namelist():
        if not n.endswith('.json'):
            continue
        try:
            j = json.loads(z.read(n))
        except Exception:  # noqa: BLE001
            continue
        d, o = j.get('data'), j.get('order')
        if not isinstance(d, str) or not isinstance(o, list) or len(o) != len(d):
            continue
        try:
            r = [''] * len(d)
            for i, c in enumerate(d):
                r[o[i]] = c
            cands = [''.join(r), ''.join(d[k] for k in o)]
        except Exception:  # noqa: BLE001
            continue
        for c in cands:
            m = ANS.fullmatch(c)
            if m:
                return m.group(0)
    return None


def answer(answer_id, question, data, contract):
    """Return the value for one answer_id from its artifact bytes (None = cannot answer). Derive everything from
    `data`; never hard-code a variant's values."""
    if not data:
        return None
    v = _indexed(data)
    if v:
        return v
    for cand in puzzle_candidates(io.BytesIO(data)):
        m = ANS.search(cand)
        if m:
            return m.group(0)
    return None


def fallback(answer_id, question, data, contract):
    """Called ONLY when answer() found nothing (None or an exception): a cheap generic second try for a variant shape
    the direct parse doesn't know (Time Trial / Mastery mutate the task) -- e.g. the lane lib's name-agnostic decoder
    over `data`, then a match against question["answer_format"]. None = give up on this field only."""
    if not data:
        return None
    for fn in (raw_entry_scan, dex_strings):
        try:
            for cand in fn(io.BytesIO(data)) or ():
                m = ANS.search(str(cand))
                if m:
                    return m.group(0)
        except Exception:  # noqa: BLE001
            continue
    return None


def _solve_pairs(job):
    """Answer one group of (answer_id, question) pairs -- a whole Mastery set, or the whole contract."""
    root, contract, pairs = job
    out = {}
    for aid, q in pairs:
        data = artifact_bytes(root, contract, q.get("artifact") or "")
        try:
            v = answer(aid, q, data, contract)
        except Exception as e:  # noqa: BLE001 - one bad field must not sink the other answers
            print(f"{aid}: {e!r}", file=sys.stderr)
            v = None
        if v is None:
            try:
                v = fallback(aid, q, data, contract)
            except Exception as e:  # noqa: BLE001
                print(f"{aid}: fallback {e!r}", file=sys.stderr)
        if v is not None:
            out[aid] = normalize(v, q)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--contract", required=True)
    ap.add_argument("--artifacts", required=True)
    a = ap.parse_args()
    contract, pairs = load_contract(a.contract)
    groups = group_by_set(pairs)
    # out/pool are shared with the deadline watchdog: if the solve runs past HCTF_SOLVE_DEADLINE, whatever has been
    # collected so far is printed (a partial the untimed runner finishes in-attempt) instead of being SIGKILLed with no
    # output (which scores exec_error and forces a blocking generalize). run_sets merges each Mastery set as it finishes
    # (one forked process per set), then emit_and_exit prints once, kills any lingering pool/probe child, and os._exit(0).
    out, pool = {}, []
    solverrt.arm_deadline(out, pool)
    jobs = [(a.artifacts, contract, g) for g in groups.values()] if len(groups) >= 2 else [(a.artifacts, contract, pairs)]
    solverrt.run_sets(jobs, _solve_pairs, out, pool)
    solverrt.emit_and_exit(out, pool)


if __name__ == "__main__":
    main()
