#!/usr/bin/env python3
"""Solver for this challenge -- harness skeleton. Fill in `answer()`; keep the I/O contract unchanged.

    solve.py --contract <contract.json> --artifacts <dir>   ->  prints {answer_id: value} as JSON on the last line

Runs on the Homebase VM inside a ~6-7 s window for EVERY Mastery set: stdlib + lib.* + pyzipper/pyelftools/pefile/
capstone/pycryptodome/androguard only, no subprocess to 7z/jadx/etc., all sets well under 1 s. Mastery questions name
their files like 'delivery 2: sample_02.apk' or 'evidence.zip -> member': `artifact_bytes()` resolves both (by sha256
pairing first, so same-named per-set deliveries never get mixed up)."""
import argparse
import base64
import codecs
import io
import re
import zipfile
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from lib.common import container_by_sha, delivery_missing, find_artifact, load_contract, normalize  # noqa: E402

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


ANS_RE = re.compile(r"ANS-[0-9A-F]{16}")


def _decode(p):
    """Decode a huntress.mobile.puzzle.v1 object; yield candidates."""
    codec = str(p.get("codec", "")).lower()
    d = p.get("data", "")
    key = p.get("key", p.get("shift", 0))
    try:
        key = int(key)
    except (TypeError, ValueError):
        key = 0
    if codec in ("caesar", "shift", "rot"):
        for k in (key, -key):
            yield "".join(chr((ord(c) - k) % 0x110000) for c in d)
        # alphabet-only caesar fallback
        def rot(c, k):
            if c.isupper():
                return chr((ord(c) - 65 - k) % 26 + 65)
            if c.islower():
                return chr((ord(c) - 97 - k) % 26 + 97)
            return c
        yield "".join(rot(c, key) for c in d)
    elif codec == "plain":
        yield d
    elif codec == "reverse":
        yield d[::-1]
    elif codec == "base64":
        yield base64.b64decode(d).decode("latin1")
    elif codec == "base32":
        yield base64.b32decode(d).decode("latin1")
    elif codec == "hex":
        yield bytes.fromhex(d).decode("latin1")
    elif codec == "rot13":
        yield codecs.decode(d, "rot13")
    elif codec == "xor":
        yield bytes(b ^ (key & 0xFF) for b in base64.b64decode(d)).decode("latin1")
    elif codec == "split":
        parts, order = p.get("parts", []), p.get("order", [])
        out = [""] * len(parts)
        try:
            for i, o in enumerate(order):
                out[o] = parts[i]
            yield "".join(out)
        except (IndexError, TypeError):
            pass
        try:
            yield "".join(parts[o] for o in order)
        except (IndexError, TypeError):
            pass
    if isinstance(d, str):
        yield d


def answer(answer_id, question, data, contract):
    """Return the value for one answer_id from its artifact bytes (None = cannot answer). Derive everything from
    `data`; never hard-code a variant's values."""
    if not data:
        return None
    try:
        z = zipfile.ZipFile(io.BytesIO(data))
        names = z.namelist()
        pj = next((n for n in names if n.endswith("huntress_puzzle.json")), None)
        if pj:
            p = json.loads(z.read(pj))
            for cand in _decode(p):
                m = ANS_RE.fullmatch(cand.strip())
                if m:
                    return m.group(0)
    except Exception as e:  # noqa: BLE001
        print(f"{answer_id}: puzzle {e!r}", file=sys.stderr)
    from lib.android import extract_answer  # fallback chain (dex/resources)
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".apk") as f:
        f.write(data)
        f.flush()
        return extract_answer(f.name)


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
        if v is not None:
            out[aid] = normalize(v, q)
    print(json.dumps(out))


if __name__ == "__main__":
    main()
