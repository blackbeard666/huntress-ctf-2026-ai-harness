#!/usr/bin/env python3
"""Metadata-forensics LANE solver: every GM-verified field family D1..today through lib.meta (+ speculative breadth).

    solve.py --contract <contract.json> --artifacts <dir>   ->  prints {answer_id: value} as JSON on the last line

The harness RACES it beside the LLM worker (reuse race; `_day_key` 999 = always tried first); it never blocks the
worker. A field is "confident" only when lib.meta's entry for it is GM-verified (hctf/solvers.py _known_ids).
Seeded into a day's solver dir (HCTF_LANE_SEED_LANES): the worker adds ONLY today's new field in `local_answer()`;
the post-run ratchet folds it into lib/meta.

Runs on the Homebase VM inside a ~6-7 s window for EVERY Mastery set: stdlib + lib.* + pyzipper/pyelftools/pefile/
capstone/pycryptodome/androguard only, no subprocess, all sets well under 1 s. Also runs from the race snapshot copy
(.run/spec-dayNN/<chal>-race/solver/solve.py): parents[4] is the project root at every one of these depths."""
import argparse
import json
import os
import re
import sys
import time
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from lib import meta  # noqa: E402
from lib.common import (_zip_open, _zip_read, container_by_sha, delivery_missing, find_artifact,  # noqa: E402
                        find_artifact_hinted, group_by_set, iter_files, load_contract, normalize, read_member)

FAST_INDEX = os.environ.get("HCTF_META_FAST_INDEX", "1") != "0"   # per-process member index (0 = find_artifact only)

_cache = {}
_index = {}


def _once(load):
    memo = []
    return lambda: memo[0] if memo else (memo.append(load()) or memo[0])


def _entries(root):
    """[(name, parent, loader)] of every file under root and every (nested) zip member, in find_artifact's order, built
    ONCE per process; a member is decompressed only when it is a zip (2-byte peek) or asked for. find_artifact re-walks
    and inflates every member per question: D9 Mastery (65 ids, 5 sets) spent 0.9 of 1.2 s there."""
    root = str(root)
    if root in _index:
        return _index[root]
    out = []

    def walk(name, load, parent, depth, peek):
        load = _once(load)
        out.append((name, parent, load))
        if depth >= 4:
            return
        try:
            if peek() != b"PK":
                return
            z = _zip_open(load())
        except Exception:  # noqa: BLE001 - unreadable member: a leaf
            return
        if z is None:
            return
        for n in z.namelist():
            if n.endswith("/"):
                continue

            def pk(z=z, n=n):
                try:
                    with z.open(n) as f:
                        return f.read(2)
                except Exception:  # noqa: BLE001 - encrypted: the password-aware full read
                    return _zip_read(z, n)[:2]
            walk(Path(n).name, (lambda z=z, n=n: _zip_read(z, n)), name, depth + 1, pk)

    for p in iter_files(root):
        walk(p.name, p.read_bytes, None, 0, (lambda p=p: p.open("rb").read(2)))
    _index[root] = out
    return out


def _fast_member(root, artifact):
    """'container -> member' bytes via the per-process index (same precedence as lib.common.find_artifact: a top-level
    file named like the container, then the member whose parent is the container, then any same-named member).
    None -> fall back to find_artifact (odd shapes)."""
    container, _, member = (x.strip() for x in artifact.partition("->"))
    if not member:
        return None
    cbase = Path(container).name
    for p in iter_files(root):
        if p.name in (artifact, container, cbase):
            if not zipfile.is_zipfile(p):
                return None
            try:
                return read_member(p, member)
            except KeyError:
                continue
    target, loose = Path(member).name, None
    for name, parent, load in _entries(root):
        if name != target:
            continue
        if parent == cbase:
            return load()
        loose = loose or load
    return loose() if loose else None


def artifact_bytes(root, contract, artifact, hint=""):
    """Bytes for a question's `artifact` string (cached per artifact): sha256 pairing first (same-named per-set
    deliveries), then by name; a member the question names but the archive lacks -> the member matching `hint`."""
    key = (artifact, hint)
    if key in _cache:
        return _cache[key]
    container, _, member = (x.strip() for x in artifact.partition("->"))
    data = None
    p = container_by_sha(root, contract, container)
    if p is not None and not member:
        data = p.read_bytes()
    elif not delivery_missing(root, contract, container):
        for cand in (artifact, container.split(": ", 1)[-1] + (f" -> {member}" if member else "")):
            try:
                data = _fast_member(root, cand) if FAST_INDEX else None
                data = data if data is not None else find_artifact(root, cand)
                break
            except (FileNotFoundError, KeyError):
                continue
        if data is None and artifact and hint:
            try:   # stale question text vs the real archive (D2 TT: question says roster.csv, the zip holds readme.exe)
                data = find_artifact_hinted(root, artifact, hint)[0]
            except (FileNotFoundError, KeyError):
                pass
    _cache[key] = data
    return data


def _hint(answer_id):
    tail = re.sub(r"^(?:set|slot)[._-]?\d+[._-]", "", answer_id).split(".")[-1]
    return re.split(r"-(?:magic|sha256|sha1|md5|size|filename|text|d\d\d)\b", tail)[0]


def _cstr(b, off, wide=False):
    if wide:
        end = off
        while end + 1 < len(b) and b[end:end + 2] != b"\0\0":
            end += 2
        return b[off:end].decode("utf-16-le", "replace")
    end = b.find(b"\0", off)
    return b[off:end if end >= 0 else len(b)].decode("cp1252", "replace")


def _lnk_idlist_path(b, off, end):
    """Rebuild a filesystem path from the shell IDList: volume item ('/C:\\') + file-entry items (long name)."""
    parts = []
    while off + 2 <= end:
        n = int.from_bytes(b[off:off + 2], "little")
        if n < 2:
            break
        it = b[off:off + n]
        t = it[2] if len(it) > 2 else 0
        if t & 0x70 == 0x20 and len(it) > 3:          # volume / drive
            parts = [_cstr(it, 3).rstrip("\\")]
        elif t & 0x70 == 0x30 and len(it) > 14:       # file entry: short name, then beef0004 long name
            wide = bool(t & 0x04)
            name = _cstr(it, 14, wide)
            k = it.find(b"\x04\x00\xef\xbe")
            if k >= 4:
                ver = int.from_bytes(it[k - 2:k], "little")
                lo = k + 4 + 14 + (2 if ver >= 7 else 0) + (4 if ver >= 3 else 0) + (8 if ver >= 9 else 0)
                # extension block: size(2) ver(2) sig(4) ctime(4) atime(4) id(2) [unk 2 + mft 8 if ver>=7] [nameoff 2 if ver>=3] [4 if ver>=9]
                lo = k + 4 + 4 + 4 + 2 + (10 if ver >= 7 else 0) + (2 if ver >= 3 else 0) + (4 if ver >= 9 else 0)
                ln = _cstr(it, lo, True) if lo < len(it) else ""
                if ln:
                    name = ln
            parts.append(name)
        off += n
    return "\\".join(parts) if parts else None


def lnk_target_path(b):
    if len(b) < 0x4C or b[:4] != b"\x4c\0\0\0":
        return None
    flags = int.from_bytes(b[0x14:0x18], "little")
    off = 0x4C
    idl = None
    if flags & 1:
        n = int.from_bytes(b[off:off + 2], "little")
        idl = (off + 2, off + 2 + n)
        off += 2 + n
    if flags & 2 and off + 0x1C <= len(b):
        li = b[off:off + int.from_bytes(b[off:off + 4], "little")]
        hs = int.from_bytes(li[4:8], "little")
        lflags = int.from_bytes(li[8:12], "little")
        if lflags & 1:
            base = suf = ""
            if hs >= 0x24 and int.from_bytes(li[0x1C:0x20], "little"):
                base = _cstr(li, int.from_bytes(li[0x1C:0x20], "little"), True)
            else:
                base = _cstr(li, int.from_bytes(li[0x10:0x14], "little"))
            if hs >= 0x24 and int.from_bytes(li[0x20:0x24], "little"):
                suf = _cstr(li, int.from_bytes(li[0x20:0x24], "little"), True)
            else:
                so = int.from_bytes(li[0x18:0x1C], "little")
                suf = _cstr(li, so) if so else ""
            if base or suf:
                return base + ("\\" if base and suf and not base.endswith("\\") else "") + suf
    if idl:
        return _lnk_idlist_path(b, *idl)
    return None


def local_answer(answer_id, question, data, contract):
    """TODAY's new field (the worker adds it here; None = not today's). Derive it from `data`; never hard-code."""
    if re.search(r"lnk-target-path(-windows)?$", answer_id or "") and data:
        return lnk_target_path(data)
    return None


def answer(answer_id, question, data, contract):
    v = local_answer(answer_id, question, data, contract)
    if v is not None:
        return v
    v, _tier = meta.answer(answer_id, question, data)
    return v


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
        if _past_deadline():
            break
        data = artifact_bytes(root, contract, q.get("artifact") or "", _hint(aid))
        try:
            v = answer(aid, q, data, contract)
        except Exception as e:  # noqa: BLE001 - one bad field must not sink the other answers
            print(f"{aid}: {e!r}", file=sys.stderr)
            v = None
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
        # Mastery: every set runs inside ONE clock -- one forked process per set. Same results as the sequential loop.
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
