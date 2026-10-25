#!/usr/bin/env python3
"""Solver for this challenge -- harness skeleton. Fill in `answer()`; keep the I/O contract unchanged.

    solve.py --contract <contract.json> --artifacts <dir>   ->  prints {answer_id: value} as JSON on the last line

Runs on the Homebase VM inside a ~6-7 s window for EVERY Mastery set: stdlib + lib.* + pyzipper/pyelftools/pefile/
capstone/pycryptodome/androguard only, no subprocess to 7z/jadx/etc., all sets well under 1 s. Mastery questions name
their files like 'delivery 2: sample_02.apk' or 'evidence.zip -> member': `artifact_bytes()` resolves both (by sha256
pairing first, so same-named per-set deliveries never get mixed up)."""
import re
import argparse
import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
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
    text = data.decode("utf-8", "replace") if isinstance(data, bytes) else data
    if re.match(r"\s*\d{2}\t", text):  # Mastery: numbered lines, line k in day k's encoding (D15 = ROT47)
        m = _slug(decode.decode_chunked(text))
        if m:  # direct per-line decode hit: skip the costly joint-ranked search (60 s on 83 sets)
            return m
        m = _slug(_rail_lines(text))
        if m:
            return m
        cands = []
        try:
            cands += decode.decode_candidates(text, 5)
        except Exception:  # noqa: BLE001
            pass
    else:
        cands = [_hex_utf16(text), _railfence_best(text.strip("\r\n")), _baconhex(text), _morsehex(text), _rot47(text.strip())]
        try:
            cands.append(decode.decode_chunk(text.strip()))
        except Exception:  # noqa: BLE001
            pass
    for c in cands:
        m = _slug(c)
        if m:
            return m
    return None


def _hex_utf16(t):
    """D19: hex of UTF-16 bytes (BOM fffe/feff, or BOM-less alternating NULs)."""
    t = re.sub(r"\s+", "", t)
    if not re.fullmatch(r"(?:[0-9a-fA-F]{2})+", t):
        return None
    b = bytes.fromhex(t)
    for enc in (("utf-16",) if b[:2] in (b"\xff\xfe", b"\xfe\xff") else ("utf-16-le", "utf-16-be")):
        try:
            r = b.decode(enc)
        except Exception:  # noqa: BLE001
            continue
        if r.isprintable() or "\n" in r:
            return r
    return None


def _rail_dec(c, r, off=0):
    """D18: rail-fence (zigzag) decrypt with r rails, start offset off."""
    n = len(c)
    cyc = 2 * (r - 1)
    pat = [(p if p < r else cyc - p) for p in ((i + off) % cyc for i in range(n))]
    idx = sorted(range(n), key=lambda i: (pat[i], i))
    out = [""] * n
    for k, i in enumerate(idx):
        out[i] = c[k]
    return "".join(out)


def _railfence_best(t):
    """D18 "Three rails": anagram of the crib sentence -> rail fence. Prefer 3 rails, offset 0; then others."""
    if not t or len(t) < 4:
        return None
    tries = [(3, 0)] + [(r, o) for r in range(2, 12) for o in range(2 * (r - 1)) if (r, o) != (3, 0)]
    for r, o in tries:
        if r >= len(t):
            break
        d = _rail_dec(t, r, o)
        if re.search(r"Master:\s*[a-z]+-[a-z]+-[a-z]+-\d{2}\s*$", d):
            return d
    return None


def _rail_lines(text):
    """Mastery fallback: decode each numbered line by decode_chunk, but rail-fence (3 rails) any one line."""
    rows = [re.match(r"\s*(\d+)\t(.*)$", ln) for ln in text.splitlines()]
    rows = sorted((int(m.group(1)), m.group(2)) for m in rows if m)
    base = []
    for _, f in rows:
        try:
            base.append(decode.decode_chunk(f) or "")
        except Exception:  # noqa: BLE001
            base.append("")
    for i, (_, f) in enumerate(rows):
        for r, o in ((3, 0), (2, 0), (3, 1), (3, 2), (3, 3)):
            if r >= len(f):
                continue
            cand = "".join(base[:i]) + _rail_dec(f, r, o) + "".join(base[i + 1:])
            if _slug(cand):
                return cand
    return None


def _morsehex(s):
    """D16: Morse code whose symbols are hex digits of the UTF-8 text (or plain Morse text)."""
    t = s.strip().strip('"')
    if not t or not re.fullmatch(r"[.\-/ \t\r\n]+", t) or not re.search(r"[.\-]", t):
        return None
    try:
        from lib.ciphers import morse_decode
        m = morse_decode(t)
    except Exception:  # noqa: BLE001
        return None
    h = re.sub(r"\s", "", m or "")
    if re.fullmatch(r"(?:[0-9A-Fa-f]{2})+", h):
        try:
            return bytes.fromhex(h).decode("utf-8")
        except Exception:  # noqa: BLE001
            pass
    return m.lower() if m else None


def _baconhex(s):
    """D17: Baconian 5-symbol a/b groups; each group's index (a=0, b=1) is one hex nibble of the UTF-8 text
    ("Sixteen guests"). Groups >= 16 -> plain Bacon letters (26-letter, else 24-letter I=J/U=V alphabet)."""
    t = s.strip().strip('"')
    if not t or not re.fullmatch(r"[abAB\s]+", t):
        return None
    bits = re.sub(r"\s", "", t).lower().replace("a", "0").replace("b", "1")
    if not bits or len(bits) % 5:
        return None
    vals = [int(bits[i:i + 5], 2) for i in range(0, len(bits), 5)]
    if max(vals) < 16 and len(vals) % 2 == 0:
        try:
            return bytes.fromhex("".join("%x" % v for v in vals)).decode("utf-8")
        except Exception:  # noqa: BLE001
            pass
    a26 = "abcdefghijklmnopqrstuvwxyz"
    if max(vals) < 26:
        return "".join(a26[v] for v in vals)
    return None


def _rot47(s):
    return "".join(chr(33 + (ord(ch) - 33 + 47) % 94) if 33 <= ord(ch) <= 126 else ch for ch in s)


def _slug(c):
    if isinstance(c, (list, tuple)):
        c = c[0] if c and isinstance(c[0], str) else (c[1] if len(c) > 1 and isinstance(c[1], str) else "")
    if not isinstance(c, str):
        return None
    lines = [l for l in c.splitlines() if l.strip()]
    if not lines:
        return None
    m = re.search(r"([a-z]+(?:-[a-z]+){2}-\d{2})\s*$", lines[-1])
    return m.group(1) if m else None


try:
    from lib import decode
    decode.register_free("rot47", 15, lambda p: [_rot47(p)])
    decode.register_free("morsehex", 16, lambda p: [x for x in [_morsehex(p)] if x])
    decode.register_free("baconhex", 17, lambda p: [x for x in [_baconhex(p)] if x])
except Exception:  # noqa: BLE001
    decode = None


def fallback(answer_id, question, data, contract):
    """Called ONLY when answer() found nothing (None or an exception): a cheap generic second try for a variant shape
    the direct parse doesn't know (Time Trial / Mastery mutate the task) -- e.g. the lane lib's name-agnostic decoder
    over `data`, then a match against question["answer_format"]. None = give up on this field only."""
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
