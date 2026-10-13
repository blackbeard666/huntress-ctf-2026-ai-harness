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


import re
import struct

_GUID = re.compile(rb"\{?([0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12})\}?")


def cfb_streams(b):
    """Stdlib OLE/CFB reader -> {decoded stream name: bytes} (MSI names de-mangled; tables keep the '!' prefix)."""
    if b[:8] != bytes.fromhex("d0cf11e0a1b11ae1"):
        return None
    ss = 1 << struct.unpack_from("<H", b, 0x1E)[0]
    mss = 1 << struct.unpack_from("<H", b, 0x20)[0]
    nfat, dir0, cutoff, mf0, nmf, dif0, ndif = struct.unpack_from("<IIIIIII", b, 0x2C)[0:1] + \
        struct.unpack_from("<I", b, 0x30) + struct.unpack_from("<IIIII", b, 0x38)
    sec = lambda n: b[512 + n * ss: 512 + (n + 1) * ss]
    difat = list(struct.unpack_from("<109I", b, 0x4C))
    d = dif0
    while ndif and d < 0xFFFFFFFA:
        e = struct.unpack("<%dI" % (ss // 4), sec(d))
        difat += e[:-1]
        d = e[-1]
        ndif -= 1
    fat = []
    for f in difat[:nfat]:
        fat += struct.unpack("<%dI" % (ss // 4), sec(f))

    def chain(start, tbl, get):
        out, n, seen = [], start, set()
        while n < 0xFFFFFFFA and n < len(tbl) and n not in seen:
            seen.add(n)
            out.append(get(n))
            n = tbl[n]
        return b"".join(out)
    dirb = chain(dir0, fat, sec)
    minifat = list(struct.unpack("<%dI" % (len(x) // 4), x)) if (x := chain(mf0, fat, sec)) else []
    ents = []
    for i in range(0, len(dirb) - 127, 128):
        nl, typ = struct.unpack_from("<HB", dirb, i + 64)
        start, size = struct.unpack_from("<II", dirb, i + 116)
        ents.append((dirb[i:i + max(nl - 2, 0)].decode("utf-16le", "replace"), typ, start, size))
    mini = chain(ents[0][2], fat, sec) if ents and ents[0][1] == 5 else b""
    out = {}
    for name, typ, start, size in ents:
        if typ != 2:
            continue
        if size < cutoff:
            data = chain(start, minifat, lambda n: mini[n * mss:(n + 1) * mss])[:size]
        else:
            data = chain(start, fat, sec)[:size]
        out[msi_name(name)] = data
    return out


def msi_name(n):
    m = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz._"
    r = []
    for ch in n:
        c = ord(ch)
        if c == 0x4840:
            r.append("!")
        elif 0x4800 <= c < 0x4840:
            r.append(m[c - 0x4800])
        elif 0x3800 <= c < 0x4800:
            c -= 0x3800
            r.append(m[c & 0x3F] + m[(c >> 6) & 0x3F])
        else:
            r.append(ch)
    return "".join(r)


def msi_property(b, prop):
    st = cfb_streams(b)
    if not st:
        return None
    pool, sdata = st.get("!_StringPool"), st.get("!_StringData")
    tbl = st.get("!Property")
    if pool is None or sdata is None or tbl is None:
        return None
    cp, = struct.unpack_from("<I", pool, 0)
    w = 3 if cp & 0x80000000 else 2
    enc = {1252: "cp1252", 65001: "utf-8"}.get(cp & 0xFFFF, "cp1252")
    strs, off, i, ents = [None], 0, 0, struct.unpack("<%dH" % (len(pool) // 2 - 2), pool[4:4 + (len(pool) // 4 - 1) * 4])
    while i + 1 < len(ents):
        ln, refs = ents[i], ents[i + 1]
        if ln == 0 and refs and i + 3 < len(ents):
            ln = ents[i + 2] + (refs << 16)
            i += 4
        else:
            i += 2
        strs.append(sdata[off:off + ln].decode(enc, "replace"))
        off += ln
    rows = len(tbl) // (2 * w)
    rd = lambda o: int.from_bytes(tbl[o:o + w], "little")
    for r in range(rows):
        k, v = rd(r * w), rd((rows + r) * w)
        if 0 < k < len(strs) and strs[k] == prop and 0 < v < len(strs):
            return strs[v]
    return None


def _guid(v):
    """MSI stores GUIDs braced+uppercase; the GM accepts the braced form (GM-confirmed D13, bare form rejected)."""
    m = _GUID.search(v.encode() if isinstance(v, str) else v)
    return "{%s}" % m.group(1).decode().upper() if m else None


def answer(answer_id, question, data, contract):
    """Return the value for one answer_id from its artifact bytes (None = cannot answer). Derive everything from
    `data`; never hard-code a variant's values."""
    if data is None:
        return None
    tail = answer_id.split(".")[-1].lower()
    m = re.search(r"msi-(.+?)(?:-guid)?$", tail.split("-msi-", 1)[-1] if "-msi-" in tail else tail)
    field = (m.group(1) if m else "product-code").replace("-", "").lower()
    names = {"productcode": "ProductCode", "upgradecode": "UpgradeCode", "productversion": "ProductVersion",
             "productname": "ProductName", "manufacturer": "Manufacturer", "productlanguage": "ProductLanguage"}
    prop = names.get(field, field)
    v = msi_property(data, prop)
    if v is None:
        return None
    return _guid(v) if "guid" in tail else v


def fallback(answer_id, question, data, contract):
    """Called ONLY when answer() found nothing (None or an exception): a cheap generic second try for a variant shape
    the direct parse doesn't know (Time Trial / Mastery mutate the task) -- e.g. the lane lib's name-agnostic decoder
    over `data`, then a match against question["answer_format"]. None = give up on this field only."""
    if data and "product-code" in answer_id:
        m = re.search(rb"ProductCode(\{[0-9A-Fa-f-]{36}\})", data)
        return _guid(m.group(1)) if m else None
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
