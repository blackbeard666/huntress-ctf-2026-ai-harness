#!/usr/bin/env python3
"""Solver: Day 05 mobile-android "Backup Spill".

Concept: the APK (allowBackup="true", "backup-admitted SharedPreferences") has an
exported deep-link ChallengeActivity that relays `answer`/`case_id` as `proof` to a
device-loopback backend .../evidence endpoint with an embedded client_secret. The
proof is the decoded assets/huntress_puzzle.json value, and the backend's returned
answer code equals it (confirmed ANS-<16 hex>). Everything is derived from the bytes.

Puzzle codecs: split (`parts` + `order`, where order[i] is the output slot of
parts[i]; the other reading parts[order[i]] is tried too), xor (base64 + key),
base64/base32/hex/rot13/reverse/plain; lib.decode.peel is the fallback.
"""
import base64
import binascii
import codecs
import io
import json
import re
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
from lib.common import load_contract, find_artifact, normalize  # noqa: E402

ANS_RE = re.compile(r"ANS-[0-9A-Fa-f]{16}")


def _key_bytes(key):
    if key is None:
        return b"\x00"
    if isinstance(key, int):
        return bytes([key & 0xFF])
    s = str(key)
    if re.fullmatch(r"\d+", s):
        return bytes([int(s) & 0xFF])
    return s.encode("utf-8") or b"\x00"


def _decode_text(codec, data, key=None):
    codec = (codec or "plain").strip().lower()
    if codec in ("plain", "", "none", "raw", "identity", "split"):
        return data
    if codec == "xor":
        raw = base64.b64decode(data)
        k = _key_bytes(key)
        return bytes(b ^ k[i % len(k)] for i, b in enumerate(raw)).decode("utf-8", "replace")
    if codec in ("base64", "b64"):
        return base64.b64decode(data).decode("utf-8", "replace")
    if codec in ("base32", "b32"):
        return base64.b32decode(data).decode("utf-8", "replace")
    if codec in ("hex", "base16"):
        return binascii.unhexlify(data.strip()).decode("utf-8", "replace")
    if codec in ("rot13", "rot-13"):
        return codecs.decode(data, "rot13")
    if codec in ("reverse", "reversed"):
        return data[::-1]
    return data


def _split_candidates(parts, order):
    """Yield assemblies of `parts` under both readings of `order`."""
    parts = [str(p) for p in parts]
    n = len(parts)
    if order and sorted(int(o) for o in order) == list(range(n)):
        order = [int(o) for o in order]
        slots = [None] * n
        for i, o in enumerate(order):  # order[i] = output position of parts[i]
            slots[o] = parts[i]
        yield "".join(slots)
        yield "".join(parts[o] for o in order)  # order[i] = index of i-th piece
    yield "".join(parts)
    yield "".join(reversed(parts))


def candidates(puzzle):
    codec = puzzle.get("codec")
    key = puzzle.get("key")
    raws = []
    if isinstance(puzzle.get("parts"), list) and puzzle["parts"]:
        raws.extend(_split_candidates(puzzle["parts"], puzzle.get("order")))
    if puzzle.get("data"):
        raws.append(puzzle["data"])
    for raw in raws:
        yield raw
        try:
            yield _decode_text(codec, raw, key)
        except Exception as e:  # noqa: BLE001
            print(f"[warn] codec {codec!r} failed: {e}", file=sys.stderr)


def extract_answer(apk_bytes):
    with zipfile.ZipFile(io.BytesIO(apk_bytes)) as z:
        name = next((n for n in z.namelist() if n.endswith("huntress_puzzle.json")), None)
        if not name:
            raise ValueError("puzzle asset not found in APK")
        puzzle = json.loads(z.read(name).decode("utf-8", "replace"))
    seen = []
    for c in candidates(puzzle):
        m = ANS_RE.fullmatch(c.strip())
        if m:
            return m.group(0).upper()
        seen.append(c)
    for c in seen:  # looser: ANS- code embedded in surrounding text
        m = ANS_RE.search(c)
        if m:
            return m.group(0).upper()
    try:
        from lib.decode import peel
        for c in seen:
            got = peel(c.encode() if isinstance(c, str) else c, lambda t: ANS_RE.search(t))
            if got and got[0]:
                return ANS_RE.search(got[0]).group(0).upper()
    except Exception as e:  # noqa: BLE001
        print(f"[warn] peel failed: {e}", file=sys.stderr)
    raise ValueError(f"no ANS- code derivable from puzzle {puzzle!r}")


def locate_apk(root, artifact):
    try:
        return find_artifact(root, artifact)
    except FileNotFoundError:
        bare = re.sub(r"^\s*delivery\s*\d+\s*:\s*", "", artifact, flags=re.I)
        if bare == artifact:
            raise
        return find_artifact(root, bare)


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--contract", required=True)
    ap.add_argument("--artifacts", required=True)
    args = ap.parse_args()

    _contract, pairs = load_contract(args.contract)
    out = {}
    for aid, q in pairs:
        if not q:
            continue
        if not str(q.get("artifact", "")).lower().endswith(".apk") and "ANS-" not in str(q.get("answer_format", "")):
            continue
        try:
            out[aid] = normalize(extract_answer(locate_apk(args.artifacts, q["artifact"])), q)
        except Exception as e:  # noqa: BLE001
            print(f"[error] {aid}: {e}", file=sys.stderr)
    print(json.dumps(out))


if __name__ == "__main__":
    main()
