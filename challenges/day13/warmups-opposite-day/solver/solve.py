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
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
import lib.decode as _dec  # noqa: E402
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


SLUG = re.compile(r"[a-z]+-[a-z]+-[a-z]+-\d{2}")
_CH = re.compile(r"^(\d+)\t(.*)$")


def _atbash(s):
    return "".join(chr(219 - ord(c)) if "a" <= c <= "z" else chr(155 - ord(c)) if "A" <= c <= "Z" else c for c in s)


def _chunk(p, k=None):
    """decode_chunk + Atbash (Day 13 "Opposite Day": a<->z mirror, digits/punctuation kept). Atbash competes only
    with free-text results (rot-N / reversal of the raw line); line 13 of a numbered blob leans Atbash."""
    d = _dec.decode_chunk(p)
    t = p.strip()
    if not re.search(r"[A-Za-z]", t):
        return d
    free = d is not None and (d.strip() == t[::-1] or any(d == _dec._rot(p, n) for n in range(26)))
    if not free:
        return d
    a = _atbash(p)
    if re.fullmatch(r"\d{2,}-[A-Za-z][A-Za-z-]*", t):  # reversed slug tail (Day 12) -- unless it's line 13
        return a if k == 13 else d
    bonus = 0.6 if k == 13 else (-0.6 if k in (2, 12) else 0.0)
    return a if _dec._bigram(a) + bonus > _dec._bigram(d) else d


def _is_free(p):
    """A letter-bearing fragment no strict codec claims: decode_chunk fell through to rot-N / reversal."""
    t = p.strip()
    if not re.search(r"[A-Za-z]", t):
        return False
    d = _dec.decode_chunk(p)
    return d is not None and (d.strip() == t[::-1] or any(d == _dec._rot(p, n) for n in range(26)))


def _joint(rows):
    """Mastery line k = day k's encoding; the free-text days are rot-N (D2), reversal (D12) and Atbash (D13), each
    used ONCE per blob. Decode by alphabet, not position: try every assignment of those transforms to the free
    lines (reversal offered only to a blob of >= 12 lines, Atbash >= 13) and keep the one whose joined text ends in
    a slug, then reads most like English. Per-line guessing put Atbash on '-tliuq-d' (-> 'd-quilt-')."""
    kmax = max(k for k, _ in rows)
    free = [i for i, (_, p) in enumerate(rows) if _is_free(p)]
    if not free or len(free) > 4:
        return None
    fixed = [_dec.decode_chunk(p) if i not in free else None for i, (_, p) in enumerate(rows)]
    if any(x is None for i, x in enumerate(fixed) if i not in free):
        return None
    tf = [("rot", None)] + ([("rev", None)] if kmax >= 12 else []) + ([("atb", None)] if kmax >= 13 else [])
    import itertools

    def cand(name, p):
        if name == "rev":
            return [p.strip()[::-1] if p.strip() == p else p[::-1]]
        if name == "atb":
            return [_atbash(p)]
        return [_dec._best_rot(p)] + ([_dec._rot(p, 13)] if _dec._rot(p, 13) != _dec._best_rot(p) else [])

    best = None
    names = [n for n, _ in tf]
    for combo in itertools.product(names, repeat=len(free)):
        if len(set(combo)) < len(combo):
            continue
        for picks in itertools.product(*(cand(n, rows[i][1]) for n, i in zip(combo, free))):
            parts = list(fixed)
            for i, v in zip(free, picks):
                parts[i] = v
            text = "".join(parts)
            last = [ln for ln in text.splitlines() if ln.strip()]
            ok = bool(last) and re.search(SLUG.pattern + r"\s*$", last[-1]) is not None
            sc = (ok, _dec._bigram(text))
            if best is None or sc > best[0]:
                best = (sc, text)
    return best[1] if best and best[0][0] else None


def _decode_text(txt):
    rows = []
    for ln in txt.splitlines():
        m = _CH.match(ln.rstrip("\r\n"))
        if m:
            rows.append((int(m.group(1)), m.group(2)))
        elif ln.strip():
            rows = None
            break
    if rows and len(rows) >= 2:
        rows.sort(key=lambda r: r[0])
        j = _joint(rows)
        if j is not None:
            return j
        return "".join(_chunk(p, k) for k, p in rows)
    return _chunk(txt)


def _slug(text):
    if not text:
        return None
    lines = [ln for ln in text.splitlines() if ln.strip()]
    for ln in reversed(lines):
        m = SLUG.findall(ln)
        if m:
            return m[-1]
    m = SLUG.findall(text)
    return m[-1] if m else None


def answer(answer_id, question, data, contract):
    """Return the value for one answer_id from its artifact bytes (None = cannot answer). Derive everything from
    `data`; never hard-code a variant's values."""
    if not data:
        return None
    if data[:4] == b"PK\x03\x04":
        return None
    txt = data.decode("utf-8", "replace")
    return _slug(_decode_text(txt))


def fallback(answer_id, question, data, contract):
    """Called ONLY when answer() found nothing (None or an exception): a cheap generic second try for a variant shape
    the direct parse doesn't know (Time Trial / Mastery mutate the task) -- e.g. the lane lib's name-agnostic decoder
    over `data`, then a match against question["answer_format"]. None = give up on this field only."""
    if not data:
        return None
    txt = data.decode("utf-8", "replace")
    for cand in (_dec.decode_chunked(txt), _dec.decode_chunk(txt), _atbash(txt), txt[::-1]):
        v = _slug(cand)
        if v:
            return v
    return None


def _past_deadline():
    """The timed runner's HCTF_SOLVE_DEADLINE (epoch) has passed: print the answers found so far instead."""
    try:
        return time.time() > float(os.environ["HCTF_SOLVE_DEADLINE"])
    except (KeyError, ValueError):
        return False


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
        if v is None and not _past_deadline():   # in-window: never let a fallback search eat the kill margin
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
