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
import re
import struct
import zipfile
import json
import os
import sys
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


def _cd_names(data):
    """Member names as stored in the central directory (walked from the EOCD's cd offset), in CD order."""
    i = len(data)
    eo = None
    while True:
        i = data.rfind(b"PK\x05\x06", 0, i)
        if i < 0:
            break
        if i + 22 <= len(data):
            eo = i
            if i + 22 + struct.unpack_from("<H", data, i + 20)[0] == len(data):
                break
    names = []
    if eo is not None:
        n_tot, cd_size, cd_off = struct.unpack_from("<HII", data, eo + 10)
        p = cd_off if data[cd_off:cd_off + 4] == b"PK\x01\x02" else data.find(b"PK\x01\x02")
        while p >= 0 and data[p:p + 4] == b"PK\x01\x02" and p + 46 <= len(data):
            flags = struct.unpack_from("<H", data, p + 8)[0]
            nl, el, cl = struct.unpack_from("<HHH", data, p + 28)
            raw = data[p + 46:p + 46 + nl]
            names.append(raw.decode("utf-8") if flags & 0x800 else _dec(raw))
            p += 46 + nl + el + cl
    if not names:
        try:
            names = [x.filename for x in zipfile.ZipFile(io.BytesIO(data)).infolist()]
        except zipfile.BadZipFile:
            return None
    return json.dumps(names, separators=(",", ":"), ensure_ascii=False)


def _dec(raw):
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("cp437")


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
    if aid.endswith("zip-central-directory-member-names"):
        return _cd_names(data)
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
    if aid.endswith("pe-address-of-entry-point-rva-hex"):
        return _pe_field(data, "entry")
    if aid.endswith("pe-image-base-hex"):
        return _pe_field(data, "imagebase")
    if aid.endswith("pe-optional-header-magic-u16-hex"):
        return _pe_field(data, "magic")
    if aid.endswith("elf-e-entry-hex") or aid.endswith("elf-entry-point-hex"):
        return _elf_entry(data)
    if aid.endswith("pe-coff-machine-u16-hex"):
        return _pe_machine(data)
    if aid.endswith("elf-e-machine-u16-hex"):
        if data[:4] != b"\x7fELF" or len(data) < 20:
            return "none"
        return "0x%04x" % struct.unpack_from("<H" if data[5] != 2 else ">H", data, 18)[0]
    return None


def _pe_machine(d):
    """COFF FileHeader.Machine: MZ -> e_lfanew -> 'PE\\0\\0' -> u16 LE. Decoys without a real PE header -> none."""
    if d[:2] != b"MZ" or len(d) < 0x40:
        return "none"
    o = struct.unpack_from("<I", d, 0x3C)[0]
    if o + 6 > len(d) or d[o:o + 4] != b"PE\0\0":
        return "none"
    return "0x%04x" % struct.unpack_from("<H", d, o + 4)[0]


def _pe_opt(d):
    """Offset of the PE OptionalHeader (MZ -> e_lfanew -> 'PE\\0\\0' + 24), or None when the header is absent."""
    if d[:2] != b"MZ" or len(d) < 0x40:
        return None
    o = struct.unpack_from("<I", d, 0x3C)[0]
    if o + 24 + 20 > len(d) or d[o:o + 4] != b"PE\0\0":
        return None
    return o + 24


def _pe_field(d, field):
    o = _pe_opt(d)
    if o is None:
        return "none"
    magic = struct.unpack_from("<H", d, o)[0]
    if field == "entry":
        return "0x%08x" % struct.unpack_from("<I", d, o + 16)[0]
    if field == "imagebase":
        return ("0x%016x" % struct.unpack_from("<Q", d, o + 24)[0]) if magic == 0x20B else ("0x%08x" % struct.unpack_from("<I", d, o + 28)[0])
    if field == "magic":
        return "0x%04x" % magic
    return None


def _elf_entry(d):
    if d[:4] != b"\x7fELF" or len(d) < 0x40:
        return "none"
    e = "<" if d[5] != 2 else ">"
    return ("0x%016x" % struct.unpack_from(e + "Q", d, 24)[0]) if d[4] == 2 else ("0x%08x" % struct.unpack_from(e + "I", d, 24)[0])


def fallback(answer_id, question, data, contract):
    """Called ONLY when answer() found nothing (None or an exception): a cheap generic second try for a variant shape
    the direct parse doesn't know (Time Trial / Mastery mutate the task) -- e.g. the lane lib's name-agnostic decoder
    over `data`, then a match against question["answer_format"]. None = give up on this field only."""
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
