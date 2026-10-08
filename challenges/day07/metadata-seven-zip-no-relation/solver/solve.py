#!/usr/bin/env python3
"""Solver for this challenge -- harness skeleton. Fill in `answer()`; keep the I/O contract unchanged.

    solve.py --contract <contract.json> --artifacts <dir>   ->  prints {answer_id: value} as JSON on the last line

Runs on the Homebase VM inside a ~6-7 s window for EVERY Mastery set: stdlib + lib.* + pyzipper/pyelftools/pefile/
capstone/pycryptodome/androguard only, no subprocess to 7z/jadx/etc., all sets well under 1 s. Mastery questions name
their files like 'delivery 2: sample_02.apk' or 'evidence.zip -> member': `artifact_bytes()` resolves both (by sha256
pairing first, so same-named per-set deliveries never get mixed up)."""
import argparse
import hashlib
import io
import json
import re
import struct
import zipfile
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


def _members(data, depth=0):
    """(name, bytes) of every non-zip member in archive order, recursing into nested zips."""
    try:
        z = zipfile.ZipFile(io.BytesIO(data))
    except zipfile.BadZipFile:
        return []
    out = []
    for i in z.infolist():
        if i.is_dir():
            continue
        b = z.read(i)
        if depth < 3 and i.filename.lower().endswith(".zip") and b[:2] == b"PK":
            out += _members(b, depth + 1)
        else:
            out.append((i.filename, b))
    return out


def _eocd_total(data):
    i = len(data)
    while True:
        i = data.rfind(b"PK\x05\x06", 0, i)
        if i < 0:
            return None
        if i + 22 <= len(data) and i + 22 + struct.unpack_from("<H", data, i + 20)[0] == len(data):
            return struct.unpack_from("<H", data, i + 10)[0]
        if data.rfind(b"PK\x05\x06", 0, i) < 0:
            return struct.unpack_from("<H", data, i + 10)[0]


def _jpeg_dims(d):
    if d[:2] != b"\xff\xd8":
        return "none"
    i = 2
    while i + 4 <= len(d):
        if d[i] != 0xFF:
            i += 1
            continue
        m = d[i + 1]
        if m == 0xFF:
            i += 1
            continue
        if m in (0xD8, 0x01) or 0xD0 <= m <= 0xD7:
            i += 2
            continue
        if m == 0xD9 or m == 0xDA:
            break
        ln = struct.unpack_from(">H", d, i + 2)[0]
        if 0xC0 <= m <= 0xCF and m not in (0xC4, 0xC8, 0xCC):
            h, w = struct.unpack_from(">HH", d, i + 5)
            return f"{w}x{h}"
        i += 2 + ln
    return "none"


def answer(answer_id, question, data, contract):
    """Return the value for one answer_id from its artifact bytes (None = cannot answer). Derive everything from
    `data`; never hard-code a variant's values."""
    if data is None:
        return None
    aid = answer_id.lower()
    if aid.endswith("-filename"):
        if data[:2] != b"PK":
            return None
        mem = [n for n, _ in _members(data)]
        stem = aid.split(".")[-1].rsplit("-filename", 1)[0]
        for pred in (lambda n: stem and stem in n.lower(), lambda n: "note" in n.lower(), lambda n: n.lower().endswith(".txt")):
            for n in mem:
                if pred(n.rsplit("/", 1)[-1]):
                    return n.rsplit("/", 1)[-1]
        return mem[0].rsplit("/", 1)[-1] if mem else None
    if aid.endswith("zip-eocd-total-entries"):
        return str(_eocd_total(data))
    if aid.endswith("-size-bytes"):
        return str(len(data))
    for h in ("md5", "sha1", "sha256"):
        if aid.endswith("-" + h):
            return hashlib.new(h, data).hexdigest()
    if aid.endswith("magic-prefix-hex-16"):
        return data[:16].hex()
    if aid.endswith("utf8-bom-present"):
        return "true" if data[:3] == b"\xef\xbb\xbf" else "false"
    if aid.endswith("utf16-bom-present"):
        return "true" if data[:2] in (b"\xff\xfe", b"\xfe\xff") else "false"
    if aid.endswith("jpeg-sof-dimensions-pixels"):
        return _jpeg_dims(data)
    if aid.endswith("png-ihdr-dimensions-pixels"):
        if data[:8] != b"\x89PNG\r\n\x1a\n" or data[12:16] != b"IHDR":
            return "none"
        w, h = struct.unpack_from(">II", data, 16)
        return f"{w}x{h}"
    if aid.endswith("pdf-header-version"):
        m = re.match(rb"%PDF-(\d+\.\d+)", data)
        return m.group(1).decode() if m else "none"
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
        if v is not None:
            out[aid] = normalize(v, q)
    print(json.dumps(out))


if __name__ == "__main__":
    main()
