#!/usr/bin/env python3
"""Solver: Day 04 mobile-android "Pending Intent Relay".

Concept: the APK has an exported deep-link Activity (ChallengeActivity) that, when
invoked, relays the incoming intent's `answer`/`proof` to a backend
`.../evidence` endpoint along with an embedded client_secret. The `proof` the app
sends is the decoded value of assets/huntress_puzzle.json, and the backend's
returned evidence code equals that value (confirmed ANS-<16 hex>). The backend URL
is the device loopback (127.0.0.1) and is not a live network service, so the answer
is simply the decoded puzzle value. Everything is derived from the APK bytes.

Variant axes handled: package suffix, case reference, APK filename, Mastery sets,
and the puzzle `codec` (xor with `key`, plus plain/base64/hex/rot13/reverse).
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


def _as_bytes(data, codec):
    """Return the raw bytes of the `data` field before any xor is applied."""
    codec = (codec or "plain").strip().lower()
    if codec in ("base64", "b64", "xor"):  # xor payloads are base64-wrapped
        return base64.b64decode(data)
    if codec in ("base32", "b32"):
        return base64.b32decode(data)
    if codec in ("hex", "base16"):
        return binascii.unhexlify(data.strip())
    return data.encode("utf-8") if isinstance(data, str) else data


def decode_payload(codec, data, key=None):
    """Decode the puzzle `data` field per its declared codec; fall back to plain."""
    codec = (codec or "plain").strip().lower()
    try:
        if codec in ("plain", "", "none", "raw", "identity"):
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
    except Exception as e:  # noqa: BLE001
        print(f"[warn] codec {codec!r} failed: {e}; using raw", file=sys.stderr)
    return data


def _key_bytes(key):
    """Normalize a puzzle key (int, numeric string, or string) to key bytes."""
    if key is None:
        return b"\x00"
    if isinstance(key, int):
        return bytes([key & 0xFF])
    s = str(key)
    if re.fullmatch(r"\d+", s):
        return bytes([int(s) & 0xFF])
    return s.encode("utf-8") or b"\x00"


def extract_answer(apk_bytes):
    """Read assets/huntress_puzzle.json from the APK and return the decoded ANS- code."""
    with zipfile.ZipFile(io.BytesIO(apk_bytes)) as z:
        name = next((n for n in z.namelist()
                     if n.endswith("huntress_puzzle.json")), None)
        if not name:
            raise ValueError("puzzle asset not found in APK")
        puzzle = json.loads(z.read(name).decode("utf-8", "replace"))
    value = decode_payload(puzzle.get("codec"), puzzle.get("data", ""), puzzle.get("key"))
    m = ANS_RE.search(value)
    if m:
        return m.group(0).upper()
    return value.strip()


def locate_apk(root, artifact):
    """find_artifact, retrying without a Mastery 'delivery N:' label prefix."""
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
            apk = locate_apk(args.artifacts, q["artifact"])
            ans = extract_answer(apk)
            out[aid] = normalize(ans, q)
        except Exception as e:  # noqa: BLE001
            print(f"[error] {aid}: {e}", file=sys.stderr)

    print(json.dumps(out))


if __name__ == "__main__":
    main()
