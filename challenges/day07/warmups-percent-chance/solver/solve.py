#!/usr/bin/env python3
"""Solver for this challenge -- harness skeleton. Fill in `answer()`; keep the I/O contract unchanged.

    solve.py --contract <contract.json> --artifacts <dir>   ->  prints {answer_id: value} as JSON on the last line

Runs on the Homebase VM inside a ~6-7 s window for EVERY Mastery set: stdlib + lib.* + pyzipper/pyelftools/pefile/
capstone/pycryptodome/androguard only, no subprocess to 7z/jadx/etc., all sets well under 1 s. Mastery questions name
their files like 'delivery 2: sample_02.apk' or 'evidence.zip -> member': `artifact_bytes()` resolves both (by sha256
pairing first, so same-named per-set deliveries never get mixed up)."""
import argparse
import base64
import binascii
import codecs
import json
import re
import urllib.parse
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


SLUG = re.compile(r"[a-z]+-[a-z]+-[a-z]+-\d{2}")


def _printable(t):
    return t is not None and all(32 <= ord(c) < 127 or c in "\r\n\t" for c in t)


def _letters(t):
    return sum(c.isalpha() or c == " " for c in t) / max(len(t), 1)


def decode_frag(f):
    """One fragment -> plaintext, encoding detected from its alphabet (b64/rot13/hex/binary/decimal/octal/url)."""
    s = f.strip()
    if re.search(r"%[0-9A-Fa-f]{2}", s):
        return urllib.parse.unquote(s)
    toks = s.split()
    if toks and all(re.fullmatch(r"[01]{8}", t) for t in toks):
        return "".join(chr(int(t, 2)) for t in toks)
    if toks and all(t.isdigit() for t in toks) and len(toks) > 1 or re.fullmatch(r"\d{2,3}", s):
        cands = []
        if all(re.fullmatch(r"[0-7]{3}", t) for t in toks):
            cands.append((any(t[0] == "0" for t in toks), "".join(chr(int(t, 8)) for t in toks)))
        cands.append((False, "".join(chr(int(t)) for t in toks) if all(int(t) < 0x110000 for t in toks) else None))
        cands = [(z, t) for z, t in cands if _printable(t)]
        if cands:
            return max(cands, key=lambda c: (c[0], _letters(c[1])))[1]
    if re.fullmatch(r"(?:[0-9a-fA-F]{2})+", s):
        try:
            t = binascii.unhexlify(s).decode()
            if _printable(t):
                return t
        except (ValueError, UnicodeDecodeError):
            pass
    if re.fullmatch(r"[A-Za-z0-9+/]+={0,2}", s) and len(s) % 4 == 0:
        try:
            t = base64.b64decode(s, validate=True).decode()
            if _printable(t):
                return t
        except (ValueError, UnicodeDecodeError):
            pass
    return codecs.decode(f, "rot13")


def answer(answer_id, question, data, contract):
    """Return the value for one answer_id from its artifact bytes (None = cannot answer). Derive everything from
    `data`; never hard-code a variant's values."""
    text = data.decode("utf-8", "replace").strip("\r\n")
    lines = [ln for ln in text.splitlines() if ln.strip()]
    numbered = [re.match(r"(\d+)\t(.*)$", ln) for ln in lines]
    if lines and all(numbered):
        plain = "".join(decode_frag(m.group(2)) for m in sorted(numbered, key=lambda m: int(m.group(1))))
    else:
        plain = decode_frag(text)
    last = [ln for ln in plain.splitlines() if ln.strip()][-1]
    hits = SLUG.findall(last) or SLUG.findall(plain)
    return hits[-1] if hits else None


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
