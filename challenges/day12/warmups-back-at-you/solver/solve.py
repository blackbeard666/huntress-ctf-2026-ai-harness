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
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from lib.decode import decode_chunk, decode_chunked  # noqa: E402
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
    if not data:
        return None
    text = data.decode("utf-8", "replace")
    if re.match(r"\s*\d{1,3}\t", text):
        return _chunked_slug(text)
    dec = decode_chunk(text.strip())
    if dec and "\\u" in dec or (dec and dec.lstrip().startswith('"')):
        try:
            dec = json.loads(dec) if dec.strip().startswith('"') else json.loads('"' + dec + '"')
        except Exception:  # noqa: BLE001
            pass
    # Day 12 "Back at You": the whole message is reversed (before or after the encoding)
    return _slug(dec) or (_slug(dec[::-1]) if dec else None)


def _chunked_slug(text):
    """Numbered fragments (`NN<TAB>frag`), one encoding per line. Day 12 adds a REVERSED line (Mastery line 12 =
    '89-enud-t' -> 't-dune-98'), which decode_chunk misreads as rot-N. Decode each line once, add reversal readings
    (raw reversed, decoded-then-reversed, reversed-then-decoded) and swap them in only if the plain join has no
    slug; among slug-bearing joins keep the most English-like one."""
    from lib.decode import _CHUNK, _bigram
    rows = []
    for ln in text.splitlines():
        m = _CHUNK.match(ln.rstrip("\r\n"))
        if m:
            rows.append((int(m.group(1)), m.group(2)))
    rows.sort(key=lambda r: r[0])
    prim = [decode_chunk(p) for _, p in rows]
    v = _slug("".join(prim))
    if v and _tail_slug("".join(prim)):
        return v
    # Reading priority: a plain reversed fragment ('69-enud-m' -> 'm-dune-96') beats a decoded-then-reversed one,
    # which beats reversed-then-decoded (decode_chunk rot-N-shifts plain text: 'm-dune-96' -> 'd-ulev-96').
    best = None
    for i, (_, p) in enumerate(rows):
        for pri, c in enumerate((p[::-1], prim[i][::-1], decode_chunk(p[::-1]))):
            if c is None or c == prim[i]:
                continue
            msg = "".join(prim[:i] + [c] + prim[i + 1:])
            if _tail_slug(msg):
                key = (-pri, _bigram(msg))
                if best is None or key > best[0]:
                    best = (key, msg)
    return _slug(best[1]) if best else v


def _tail_slug(msg):
    """The decoded message ends in a whole slug (not one glued onto a mis-decoded fragment)."""
    return re.search(r"(?:^|[\s:])" + SLUG.pattern + r"\W*$", msg.strip()) is not None


def _slug(dec):
    if not dec:
        return None
    lines = [ln for ln in dec.splitlines() if ln.strip()]
    for ln in reversed(lines):
        m = SLUG.findall(ln)
        if m:
            return m[-1]
    return None


SLUG = re.compile(r"\b[a-z]+-[a-z]+-[a-z]+-\d{2}\b")


def fallback(answer_id, question, data, contract):
    """Called ONLY when answer() found nothing (None or an exception): a cheap generic second try for a variant shape
    the direct parse doesn't know (Time Trial / Mastery mutate the task) -- e.g. the lane lib's name-agnostic decoder
    over `data`, then a match against question["answer_format"]. None = give up on this field only."""
    if not data:
        return None
    from lib.decode import peel
    try:
        out = peel(data, lambda t: SLUG.search(t or ""))
        return _slug(out[0] if isinstance(out, tuple) else out)
    except Exception:  # noqa: BLE001
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
            with ProcessPoolExecutor(max_workers=min(len(groups), os.cpu_count() or 2),
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
