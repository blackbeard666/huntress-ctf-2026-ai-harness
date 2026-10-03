#!/usr/bin/env python3
"""Solver: Day 01 mobile-android "Exported Trust".

Concept: the APK has an exported deep-link Activity (huntressNN://.../unlock) that,
when invoked, attaches an embedded client credential plus a `proof` to a backend
`.../evidence` endpoint. The `proof` the app sends is the decoded value of
assets/huntress_puzzle.json, and the backend's returned evidence code equals that
value (confirmed ANS-<16 hex>). So the answer for each case is the decoded puzzle
`data` field. Everything is derived from the APK bytes; nothing is hard-coded.

Variant axes handled: package suffix, case reference, APK filename, Mastery sets,
and the puzzle `codec` (plain/base64/hex/rot13/reverse) in case a variant encodes it.
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

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from lib.common import load_contract, find_artifact, normalize  # noqa: E402

ANS_RE = re.compile(r"ANS-[0-9A-Fa-f]{16}")


def decode_payload(codec, data):
    """Decode the puzzle `data` field per its declared codec; fall back to plain."""
    codec = (codec or "plain").strip().lower()
    try:
        if codec in ("plain", "", "none", "raw", "identity"):
            return data
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
    except Exception as e:  # noqa: BLE001
        print(f"[warn] codec {codec!r} failed: {e}; using raw", file=sys.stderr)
    return data


def extract_answer(apk_bytes):
    """Read assets/huntress_puzzle.json from the APK and return the decoded ANS- code."""
    with zipfile.ZipFile(io.BytesIO(apk_bytes)) as z:
        name = next((n for n in z.namelist()
                     if n.endswith("huntress_puzzle.json")), None)
        if not name:
            raise ValueError("puzzle asset not found in APK")
        puzzle = json.loads(z.read(name).decode("utf-8", "replace"))
    value = decode_payload(puzzle.get("codec"), puzzle.get("data", ""))
    m = ANS_RE.search(value)
    if m:
        return m.group(0).upper()
    # If decoding didn't surface the pattern, return the trimmed decoded value.
    return value.strip()


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
        qtext = q.get("question", "")
        # Only handle the exported-trust / evidence-code concept.
        if "evidence" not in qtext.lower() and "exported" not in qtext.lower():
            continue
        try:
            apk = find_artifact(args.artifacts, q["artifact"])
            ans = extract_answer(apk)
            out[aid] = normalize(ans, q)
        except Exception as e:  # noqa: BLE001
            print(f"[error] {aid}: {e}", file=sys.stderr)

    print(json.dumps(out))


if __name__ == "__main__":
    main()
