#!/usr/bin/env python3
"""Solver for this challenge -- harness skeleton. Fill in `answer()`; keep the I/O contract unchanged.

    solve.py --contract <contract.json> --artifacts <dir>   ->  prints {answer_id: value} as JSON on the last line

Runs on the Homebase VM inside a ~6-7 s window for EVERY Mastery set: stdlib + lib.* + pyzipper/pyelftools/pefile/
capstone/pycryptodome/androguard only, no subprocess to 7z/jadx/etc., all sets well under 1 s. Mastery questions name
their files like 'delivery 2: sample_02.apk' or 'evidence.zip -> member': `artifact_bytes()` resolves both (by sha256
pairing first, so same-named per-set deliveries never get mixed up)."""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
import io, re, zipfile  # noqa: E402
from lib.common import container_by_sha, delivery_missing, find_artifact, load_contract, normalize  # noqa: E402

_cache = {}
ANS = re.compile(r"ANS-[0-9A-F]{16}(?![0-9A-Fa-f])")


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
    from lib.android import decode_payload
    if not data:
        return None
    z = zipfile.ZipFile(io.BytesIO(data))
    for n in z.namelist():
        if not n.endswith("huntress_puzzle.json"):
            continue
        pz = json.loads(z.read(n).decode("utf-8", "replace"))
        codec, key, d = str(pz.get("codec", "")).lower(), pz.get("key"), pz.get("data")
        cands = []
        if isinstance(pz.get("parts"), list):
            parts, order = pz["parts"], pz.get("order") or list(range(len(pz["parts"])))
            slot = [None] * len(parts)
            for i, o in enumerate(order):
                if 0 <= o < len(parts):
                    slot[o] = parts[i]
            cands += ["".join(x for x in slot if x is not None), "".join(parts[o] for o in order if 0 <= o < len(parts))]
        if isinstance(d, str):
            try:
                cands.append(decode_payload(codec, d, key))
            except Exception:  # noqa: BLE001
                pass
        for c in cands:
            m = ANS.search(c or "")
            if m:
                return m.group(0)
    return None


def fallback(answer_id, question, data, contract):
    """Called ONLY when answer() found nothing (None or an exception): a cheap generic second try for a variant shape
    the direct parse doesn't know (Time Trial / Mastery mutate the task) -- e.g. the lane lib's name-agnostic decoder
    over `data`, then a match against question["answer_format"]. None = give up on this field only."""
    if not data:
        return None
    z = zipfile.ZipFile(io.BytesIO(data))
    for n in z.namelist():  # answer moved out of the puzzle json: literal token in any member (dex string pool etc.)
        m = ANS.search(z.read(n).decode("latin-1"))
        if m:
            return m.group(0)
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--contract", required=True)
    ap.add_argument("--artifacts", required=True)
    a = ap.parse_args()
    contract, pairs = load_contract(a.contract)
    out = {}
    for aid, q in pairs:
        data = artifact_bytes(a.artifacts, contract, q.get("artifact") or "")
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
    print(json.dumps(out))


if __name__ == "__main__":
    main()
