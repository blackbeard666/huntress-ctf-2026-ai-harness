#!/usr/bin/env python3
"""Solver for this challenge -- harness skeleton. Fill in `answer()`; keep the I/O contract unchanged.

    solve.py --contract <contract.json> --artifacts <dir>   ->  prints {answer_id: value} as JSON on the last line

Runs on the Homebase VM inside a ~6-7 s window for EVERY Mastery set: stdlib + lib.* + pyzipper/pyelftools/pefile/
capstone/pycryptodome/androguard only, no subprocess to 7z/jadx/etc., all sets well under 1 s. Mastery questions name
their files like 'delivery 2: sample_02.apk' or 'evidence.zip -> member': `artifact_bytes()` resolves both (by sha256
pairing first, so same-named per-set deliveries never get mixed up)."""
import argparse
import base64
import re
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from lib.decode import decode_chunk  # noqa: E402
from lib.common import (container_by_sha, delivery_missing, find_artifact, group_by_set, load_contract,  # noqa: E402
                        normalize)

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


def answer(answer_id, question, data, contract):
    """Return the value for one answer_id from its artifact bytes (None = cannot answer). Derive everything from
    `data`; never hard-code a variant's values."""
    text = data.decode("utf-8", "replace") if isinstance(data, bytes) else str(data)
    lines = text.split("\n")
    numbered = [re.match(r"^(\d+)\t(.*)$", l.rstrip("\r"), re.S) for l in lines if l.strip()]
    if numbered and all(numbered):
        frags = sorted(((int(m.group(1)), m.group(2)) for m in numbered), key=lambda t: t[0])
        out = "".join(_chunk(f) for _, f in frags)
    else:
        out = _chunk(text.strip())
    return _slug(out)


_B64URL = re.compile(r"[A-Za-z0-9_-]+={0,2}")


def _b64url(f):
    """Day 11: unpadded URL-safe base64 (- and _ alphabet, no '='). None unless it decodes to printable text."""
    t = f.strip()
    if not _B64URL.fullmatch(t) or len(t.rstrip("=")) % 4 == 1:
        return None
    if re.fullmatch(r"(?:[0-9a-fA-F]{2})+", t) and "-" not in t and "_" not in t:
        return None  # hex: leave to decode_chunk
    if len(t) % 4 == 0 and "-" not in t and "_" not in t:
        return None  # plain strict base64: decode_chunk handles it
    try:
        b = base64.urlsafe_b64decode(t.rstrip("=") + "=" * (-len(t.rstrip("=")) % 4))
        s = b.decode("utf-8")
    except Exception:
        return None
    if s and all(c.isprintable() or c in "\t\n\r" for c in s):
        return s
    return None


def _chunk(f):
    v = _b64url(f)
    if v is not None:
        return v
    v = decode_chunk(f)
    return v if v is not None else f


def _slug(out):
    for line in reversed([l for l in out.splitlines() if l.strip()]):
        m = re.findall(r"[a-z]+-[a-z]+-[a-z]+-\d{2}", line)
        if m:
            return m[-1]
    m = re.findall(r"[a-z]+-[a-z]+-[a-z]+-\d{2}", out)
    return m[-1] if m else None


def fallback(answer_id, question, data, contract):
    """Called ONLY when answer() found nothing (None or an exception): a cheap generic second try for a variant shape
    the direct parse doesn't know (Time Trial / Mastery mutate the task) -- e.g. the lane lib's name-agnostic decoder
    over `data`, then a match against question["answer_format"]. None = give up on this field only."""
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
    out = {}
    if len(groups) >= 2 and os.environ.get("HCTF_SOLVER_PARALLEL", "1") != "0":
        # Mastery: every set runs inside ONE clock -- one forked process per set (the Homebase VM has 2 vCPUs; heavy
        # per-set work such as unzipping 31 MB deliveries halves). Same results as the sequential loop.
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
