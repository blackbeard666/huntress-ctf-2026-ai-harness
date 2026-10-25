#!/usr/bin/env python3
"""Metadata-forensics LANE solver: every GM-verified field family D1..today through lib.meta (+ speculative breadth).

    solve.py --contract <contract.json> --artifacts <dir>   ->  prints {answer_id: value} as JSON on the last line

The harness RACES it beside the LLM worker (reuse race; `_day_key` 999 = always tried first); it never blocks the
worker. A field is "confident" only when lib.meta's entry for it is GM-verified (hctf/solvers.py _known_ids).
Seeded into a day's solver dir (HCTF_LANE_SEED_LANES): the worker adds ONLY today's new field in `local_answer()`;
the post-run ratchet folds it into lib/meta.

Runs on the Homebase VM inside a ~6-7 s window for EVERY Mastery set: stdlib + lib.* + pyzipper/pyelftools/pefile/
capstone/pycryptodome/androguard only, no subprocess, all sets well under 1 s. Also runs from the race snapshot copy
(.run/spec-dayNN/<chal>-race/solver/solve.py): parents[4] is the project root at every one of these depths."""
import argparse
import json
import os
import re
import sys
import time
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from lib import meta  # noqa: E402
from lib.common import (_zip_open, _zip_read, container_by_sha, delivery_missing, find_artifact,  # noqa: E402
                        find_artifact_hinted, group_by_set, iter_files, load_contract, normalize, read_member)

FAST_INDEX = os.environ.get("HCTF_META_FAST_INDEX", "1") != "0"   # per-process member index (0 = find_artifact only)

_cache = {}
_index = {}
_ROOT = None   # artifacts dir of the running _solve_pairs (synthesis fields read sibling members)


def _once(load):
    memo = []
    return lambda: memo[0] if memo else (memo.append(load()) or memo[0])


def _entries(root):
    """[(name, parent, loader)] of every file under root and every (nested) zip member, in find_artifact's order, built
    ONCE per process; a member is decompressed only when it is a zip (2-byte peek) or asked for. find_artifact re-walks
    and inflates every member per question: D9 Mastery (65 ids, 5 sets) spent 0.9 of 1.2 s there."""
    root = str(root)
    if root in _index:
        return _index[root]
    out = []

    def walk(name, load, parent, depth, peek):
        load = _once(load)
        out.append((name, parent, load))
        if depth >= 4:
            return
        try:
            if peek() != b"PK":
                return
            z = _zip_open(load())
        except Exception:  # noqa: BLE001 - unreadable member: a leaf
            return
        if z is None:
            return
        for n in z.namelist():
            if n.endswith("/"):
                continue

            def pk(z=z, n=n):
                try:
                    with z.open(n) as f:
                        return f.read(2)
                except Exception:  # noqa: BLE001 - encrypted: the password-aware full read
                    return _zip_read(z, n)[:2]
            walk(Path(n).name, (lambda z=z, n=n: _zip_read(z, n)), name, depth + 1, pk)

    for p in iter_files(root):
        walk(p.name, p.read_bytes, None, 0, (lambda p=p: p.open("rb").read(2)))
    _index[root] = out
    return out


def _fast_member(root, artifact):
    """'container -> member' bytes via the per-process index (same precedence as lib.common.find_artifact: a top-level
    file named like the container, then the member whose parent is the container, then any same-named member).
    None -> fall back to find_artifact (odd shapes)."""
    container, _, member = (x.strip() for x in artifact.partition("->"))
    if not member:
        return None
    cbase = Path(container).name
    for p in iter_files(root):
        if p.name in (artifact, container, cbase):
            if not zipfile.is_zipfile(p):
                return None
            try:
                return read_member(p, member)
            except KeyError:
                continue
    target, loose = Path(member).name, None
    for name, parent, load in _entries(root):
        if name != target:
            continue
        if parent == cbase:
            return load()
        loose = loose or load
    return loose() if loose else None


def artifact_bytes(root, contract, artifact, hint=""):
    """Bytes for a question's `artifact` string (cached per artifact): sha256 pairing first (same-named per-set
    deliveries), then by name; a member the question names but the archive lacks -> the member matching `hint`."""
    key = (artifact, hint)
    if key in _cache:
        return _cache[key]
    container, _, member = (x.strip() for x in artifact.partition("->"))
    data = None
    p = container_by_sha(root, contract, container)
    if p is not None and not member:
        data = p.read_bytes()
    elif not delivery_missing(root, contract, container):
        for cand in (artifact, container.split(": ", 1)[-1] + (f" -> {member}" if member else "")):
            try:
                data = _fast_member(root, cand) if FAST_INDEX else None
                data = data if data is not None else find_artifact(root, cand)
                break
            except (FileNotFoundError, KeyError):
                continue
        if data is None and artifact and hint:
            try:   # stale question text vs the real archive (D2 TT: question says roster.csv, the zip holds readme.exe)
                data = find_artifact_hinted(root, artifact, hint)[0]
            except (FileNotFoundError, KeyError):
                pass
    _cache[key] = data
    return data


def _hint(answer_id):
    tail = re.sub(r"^(?:set|slot)[._-]?\d+[._-]", "", answer_id).split(".")[-1]
    return re.split(r"-(?:magic|sha256|sha1|md5|size|filename|text|d\d\d)\b", tail)[0]


def local_answer(answer_id, question, data, contract):
    """TODAY's new field (the worker adds it here; None = not today's). Derive it from `data`; never hard-code."""
    return None


def synthesis_answer(answer_id, question, contract):
    """D15-D19 TT/Mastery `metadata-day-NN-synthesis-<algo>-order` (GM-confirmed every day; lib.knowledge
    METADATA_SYNTHESIS_DIGEST_ORDER): the question's `Files: [...]` siblings of the artifact's own container ordered by
    full-file digest. Lives HERE, not in lib.meta.answer: it needs the sibling members, which the per-field call lacks
    (D19: the seed won the single, then the TT and Mastery each blocked on this one field -> two live answers, ~60 s)."""
    sm = re.search(r"synthesis-(md5|sha1|sha256|sha512)-order$", answer_id.lower())
    if not sm or _ROOT is None:
        return None
    from lib.meta.synthesis import digest_order
    container = ((question or {}).get("artifact") or "").partition("->")[0].strip()
    return digest_order(question, lambda n: artifact_bytes(
        _ROOT, contract, f"{container} -> {n}" if container else n, n), sm.group(1))


def answer(answer_id, question, data, contract):
    v = local_answer(answer_id, question, data, contract)
    if v is not None:
        return v
    v = synthesis_answer(answer_id, question, contract)
    if v is not None:
        return v
    v, _tier = meta.answer(answer_id, question, data)
    return v


def _past_deadline():
    """The timed runner's HCTF_SOLVE_DEADLINE (epoch) has passed: print the answers found so far instead."""
    try:
        return time.time() > float(os.environ["HCTF_SOLVE_DEADLINE"])
    except (KeyError, ValueError):
        return False


def _solve_pairs(job):
    """Answer one group of (answer_id, question) pairs -- a whole Mastery set, or the whole contract."""
    root, contract, pairs = job
    global _ROOT
    _ROOT = root
    out = {}
    for aid, q in pairs:
        if _past_deadline():
            break
        data = artifact_bytes(root, contract, q.get("artifact") or "", _hint(aid))
        try:
            v = answer(aid, q, data, contract)
        except Exception as e:  # noqa: BLE001 - one bad field must not sink the other answers
            print(f"{aid}: {e!r}", file=sys.stderr)
            v = None
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
    out = {}
    if len(groups) >= 2 and os.environ.get("HCTF_SOLVER_PARALLEL", "1") != "0":
        # Mastery: every set runs inside ONE clock -- one forked process per set. Same results as the sequential loop.
        import multiprocessing as mp
        from concurrent.futures import ProcessPoolExecutor
        try:
            from lib.solverrt import max_procs   # HCTF_SOLVER_MAX_PROCS: the harness's small-pool rehearsal
            with ProcessPoolExecutor(max_workers=max_procs(len(groups)),
                                     mp_context=mp.get_context("fork")) as ex:
                for part in ex.map(_solve_pairs, [(a.artifacts, contract, g) for g in groups.values()]):
                    out.update(part)
        except Exception as e:  # noqa: BLE001 - never lose a solve to the pool: fall back to sequential
            print(f"parallel sets failed ({e!r}); sequential", file=sys.stderr)
            out = _solve_pairs((a.artifacts, contract, pairs))
    else:
        out = _solve_pairs((a.artifacts, contract, pairs))
    print(json.dumps(out))


if __name__ == "__main__":
    main()
