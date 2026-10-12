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


import hashlib  # noqa: E402
import re  # noqa: E402
import struct  # noqa: E402
import uuid  # noqa: E402


def _pe(data):
    """(e_lfanew, opt_off, sections[(va, vsize, raw, rawsize)], is_pe32plus) or None."""
    if not data or data[:2] != b"MZ" or len(data) < 0x40:
        return None
    lf = struct.unpack_from("<I", data, 0x3C)[0]
    if data[lf:lf + 4] != b"PE\0\0":
        return None
    nsec, = struct.unpack_from("<H", data, lf + 6)
    optsz, = struct.unpack_from("<H", data, lf + 20)
    opt = lf + 24
    plus = struct.unpack_from("<H", data, opt)[0] == 0x20B
    secs = []
    for i in range(nsec):
        o = opt + optsz + 40 * i
        vsize, va, rsize, raw = struct.unpack_from("<IIII", data, o + 8)
        secs.append((va, vsize, raw, rsize))
    return lf, opt, secs, plus


def _rva2off(secs, rva):
    for va, vs, raw, rs in secs:
        if va <= rva < va + max(vs, rs):
            return rva - va + raw
    return rva


def _cli_metadata(data):
    """Return (metadata_root_offset, {stream_name: (off, size)}) of a .NET PE, or None."""
    pe = _pe(data)
    if not pe:
        return None
    lf, opt, secs, plus = pe
    dd = opt + (112 if plus else 96)
    cli_rva, cli_sz = struct.unpack_from("<II", data, dd + 14 * 8)
    if not cli_rva:
        return None
    c = _rva2off(secs, cli_rva)
    md_rva, md_sz = struct.unpack_from("<II", data, c + 8)
    m = _rva2off(secs, md_rva)
    if data[m:m + 4] != b"BSJB":
        return None
    vlen, = struct.unpack_from("<I", data, m + 12)
    p = m + 16 + vlen
    nstreams, = struct.unpack_from("<H", data, p + 2)
    p += 4
    streams = {}
    for _ in range(nstreams):
        off, size = struct.unpack_from("<II", data, p)
        e = data.index(b"\0", p + 8)
        name = data[p + 8:e].decode("latin-1")
        p = (e + 4) & ~3
        streams[name] = (m + off, size)
    return m, streams


def dotnet_mvid(data):
    md = _cli_metadata(data)
    if not md:
        return None
    _, st = md
    tbl = st.get("#~") or st.get("#-")
    gh = st.get("#GUID")
    if not tbl or not gh:
        return None
    t = tbl[0]
    heap_sizes = data[t + 6]
    valid, = struct.unpack_from("<Q", data, t + 8)
    if not valid & 1:
        return None
    rows_at = t + 24
    p = rows_at + 4 * bin(valid).count("1")
    if heap_sizes & 0x20:  # extra data (#- uncompressed)
        p += 4
    sidx = 4 if heap_sizes & 1 else 2
    gidx = 4 if heap_sizes & 2 else 2
    p += 2 + sidx  # Generation, Name
    g, = struct.unpack_from("<I" if gidx == 4 else "<H", data, p)
    if not g:
        return None
    o = gh[0] + (g - 1) * 16
    return str(uuid.UUID(bytes_le=bytes(data[o:o + 16])))


def _key(answer_id):
    return re.sub(r"[^a-z0-9]", "", answer_id.rsplit(".", 1)[-1].lower())


def answer(answer_id, question, data, contract):
    """Return the value for one answer_id from its artifact bytes (None = cannot answer). Derive everything from
    `data`; never hard-code a variant's values."""
    if data is None:
        return None
    k = _key(answer_id)
    art = (question.get("artifact") or "").split("->")[-1].strip()
    if "mvid" in k:
        return dotnet_mvid(data)
    if k.endswith("filename") and "version" not in k:
        return art.split("/")[-1] or None
    if k.endswith("sizebytes"):
        return len(data)
    for h in ("sha256", "sha1", "md5"):
        if k.endswith(h):
            return hashlib.new(h, data).hexdigest()
    m = re.search(r"magicprefixhex(\d+)$", k)
    if m:
        return data[:int(m.group(1))].hex()
    if k.endswith("bompresent"):
        return "true" if data[:3] == b"\xef\xbb\xbf" else "false"
    pe = _pe(data)
    if k.endswith("coffmachineu16hex"):
        return "0x%04x" % struct.unpack_from("<H", data, pe[0] + 4)[0] if pe else "none"
    if k.endswith("addressofentrypointrvahex"):
        return "0x%08x" % struct.unpack_from("<I", data, pe[1] + 16)[0] if pe else "none"
    if "version" in k and pe:
        import pefile
        want = re.sub(r"^.*pe(version)?", "", k)
        x = pefile.PE(data=data, fast_load=True)
        x.parse_data_directories(directories=[pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_RESOURCE"]])
        for fi in getattr(x, "FileInfo", []) or []:
            for e in fi:
                for stt in getattr(e, "StringTable", []) or []:
                    for kk, vv in stt.entries.items():
                        if kk.decode("latin-1").lower() == want:
                            return vv.decode("utf-8", "replace")
    return None


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
