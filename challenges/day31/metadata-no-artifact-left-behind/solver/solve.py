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
from lib import solverrt  # noqa: E402  -- partial-emit on deadline (cumulative-lane upgrade)

FAST_INDEX = os.environ.get("HCTF_META_FAST_INDEX", "1") != "0"   # per-process member index (0 = find_artifact only)

_cache = {}
_index = {}
_ROOT = None   # artifacts dir of the running _solve_pairs (synthesis fields read sibling members)


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
    cbase = Path(container).name
    if not member:
        # a bare container ('evidence-03.zip') nested in the Mastery bundle: find_artifact's recursive branch returns
        # the FIRST entry of that name, but re-walks + inflates every member per set (D28-D30 Mastery, 12-14 sets:
        # 1.0-1.6 s lane solver, find_artifact 55% of it). Same answer from the index; a top-level file of that name
        # keeps find_artifact's bundle special cases (D7 evidence-01.zip = {evidence-01.zip, evidence-02.zip}).
        if any(p.name in (artifact, container, cbase) for p in iter_files(root)):
            return None
        for name, parent, load in _entries(root):
            if name == cbase:
                return load()
        return None
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


def _graph_texts(name, b):
    """Text payloads that can name a next artifact: script body, PNG tEXt/zTXt/iTXt, SQLite cell text, email
    (incl. base64 attachment parts), nested zip members. Each returned as str."""
    import base64
    import io
    import zlib
    out = []
    try:
        if b[:8] == b"\x89PNG\r\n\x1a\n":
            i = 8
            while i + 8 <= len(b):
                ln = int.from_bytes(b[i:i + 4], "big")
                ct = b[i + 4:i + 8]
                d = b[i + 8:i + 8 + ln]
                if ct == b"tEXt":
                    out.append(d.split(b"\0", 1)[-1].decode("latin-1"))
                elif ct == b"zTXt":
                    try:
                        out.append(zlib.decompress(d.split(b"\0", 1)[1][1:]).decode("latin-1"))
                    except Exception:  # noqa: BLE001
                        pass
                elif ct == b"iTXt":
                    k, _, r = d.partition(b"\0")
                    flag = r[:1]
                    r = r[2:].split(b"\0", 2)[-1]
                    try:
                        out.append((zlib.decompress(r) if flag == b"\x01" else r).decode("utf-8", "replace"))
                    except Exception:  # noqa: BLE001
                        pass
                elif ct == b"IEND":
                    break
                i += 12 + ln
            return out
        if b[:16] == b"SQLite format 3\0":
            import sqlite3
            con = sqlite3.connect(":memory:")
            try:
                con.deserialize(b)
            except Exception:  # noqa: BLE001
                import tempfile
                fd, tp = tempfile.mkstemp()
                os.write(fd, b)
                os.close(fd)
                con = sqlite3.connect(tp)
            for (tn,) in con.execute("select name from sqlite_master where type='table'").fetchall():
                for row in con.execute(f'select * from "{tn}"'):
                    out.extend(str(v) for v in row if isinstance(v, str))
            return out
        if b[:4] == b"PK\x03\x04":
            with zipfile.ZipFile(io.BytesIO(b)) as z:
                for n in z.namelist():
                    try:
                        out.append(z.read(n).decode("utf-8", "replace"))
                    except Exception:  # noqa: BLE001
                        pass
            return out
    except Exception:  # noqa: BLE001
        return out
    t = b.decode("utf-8", "replace")
    out.append(t)
    if re.search(r"(?im)^content-transfer-encoding:\s*base64", t):
        for blk in re.findall(r"(?m)(?:^[A-Za-z0-9+/=]{8,}\r?\n?)+", t):
            try:
                out.append(base64.b64decode(re.sub(r"\s", "", blk), validate=True).decode("utf-8", "replace"))
            except Exception:  # noqa: BLE001
                pass
    return out


def graph_execution_chain(b):
    """D31 graph.execution_chain_artifact_ids: members of the case zip each name their successor (script
    Invoke-Item/Start-Process/& '.\\x', SQLite launch_queue.target, PNG tEXt next=, email route attachment, nested zip
    run.txt `execute x`). An edge counts only if its quotes MATCH (mismatched-quote script = decoy edge that would close
    a cycle). Chain = root (in-degree 0) -> ... -> terminal (PNG `done ...` / no successor); prefer the path ending on a
    `done` marker, then the longest. Decoys form a CLOSED CYCLE (no in-degree-0 member). GM-confirmed D31 single: [birch-bd18, nectar-1767, bramble-e622, orchard-e5bc]."""
    import io
    mem = {}
    with zipfile.ZipFile(io.BytesIO(b)) as z:
        for n in z.namelist():
            if n.endswith("/"):
                continue
            base = n.rsplit("/", 1)[-1]
            if base.lower() in ("delivery-manifest.json", "manifest.json"):
                continue
            try:
                mem[base] = z.read(n)
            except Exception:  # noqa: BLE001
                mem[base] = b""
    names = sorted(mem, key=len, reverse=True)
    edges, done = {}, set()
    for src in mem:
        succ = []
        for t in _graph_texts(src, mem[src]):
            if re.search(r"(?i)\bdone\b", t):
                done.add(src)
            for n in names:
                if n == src:
                    continue
                for m in re.finditer(r"(?<![\w.-])" + re.escape(n) + r"(?![\w-])", t):
                    i = m.start()
                    while i > 0 and t[i - 1] in "\\/.":
                        i -= 1
                    q1 = t[i - 1] if i > 0 else ""
                    q2 = t[m.end()] if m.end() < len(t) else ""
                    # D31 Mastery: quote style is NOT a decoy signal (mismatched quotes occur on real chain edges
                    # and on decoy-cycle edges alike). The decoy is a closed cycle; the chain starts at the in-degree-0 root.
                    if n not in succ:
                        succ.append(n)
        edges[src] = succ
    indeg = {n: 0 for n in mem}
    for s_, ss in edges.items():
        for d in ss:
            indeg[d] += 1
    roots = [n for n in mem if indeg[n] == 0 and edges[n]] or list(mem)
    best = None
    for r in sorted(roots):
        path, cur = [r], r
        while edges.get(cur):
            nxt = next((x for x in edges[cur] if x not in path), None)
            if nxt is None:
                break
            path.append(nxt)
            cur = nxt
        key = (path[-1] in done, len(path))
        if best is None or key > best[0]:
            best = (key, path)
    return json.dumps(best[1], separators=(",", ":")) if best else None


def local_answer(answer_id, question, data, contract):
    """TODAY's new field (the worker adds it here; None = not today's). Derive it from `data`; never hard-code."""
    if re.search(r"graph[-_.]execution[-_]chain", answer_id) and data:
        return graph_execution_chain(data)
    return None


def synthesis_answer(answer_id, question, contract):
    """D15-D19 TT/Mastery `metadata-day-NN-synthesis-<algo>-order` (GM-confirmed every day; lib.knowledge
    METADATA_SYNTHESIS_DIGEST_ORDER): the question's `Files: [...]` siblings of the artifact's own container ordered by
    full-file digest. Lives HERE, not in lib.meta.answer: it needs the sibling members, which the per-field call lacks
    (D19: the seed won the single, then the TT and Mastery each blocked on this one field -> two live answers, ~60 s)."""
    sm = re.search(r"synthesis-(md5|sha1|sha256|sha512)-order$", answer_id.lower())
    if not sm or _ROOT is None:
        return None
    from lib.meta.synthesis import digest_order
    container = ((question or {}).get("artifact") or "").partition("->")[0].strip()
    return digest_order(question, lambda n: artifact_bytes(
        _ROOT, contract, f"{container} -> {n}" if container else n, n), sm.group(1))


def answer(answer_id, question, data, contract):
    v = local_answer(answer_id, question, data, contract)
    if v is not None:
        return v
    v = synthesis_answer(answer_id, question, contract)
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
    global _ROOT
    _ROOT = root
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
    # out/pool are shared with the deadline watchdog: if the solve runs past HCTF_SOLVE_DEADLINE, whatever has been
    # collected so far is printed (a partial the untimed runner finishes in-attempt) instead of being SIGKILLed with no
    # output (which scores exec_error and forces a blocking generalize). run_sets merges each Mastery set as it finishes
    # (one forked process per set), then emit_and_exit prints once, kills any lingering pool/probe child, and os._exit(0).
    out, pool = {}, []
    solverrt.arm_deadline(out, pool)
    jobs = [(a.artifacts, contract, g) for g in groups.values()] if len(groups) >= 2 else [(a.artifacts, contract, pairs)]
    if len(jobs) >= 2:
        # build the per-process caches ONCE before the fork pool: every forked set otherwise rebuilt lib.meta's id
        # patterns (~0.3 s) and the member index (inflating the whole bundle) itself -- 14x on a D30 Mastery
        meta._id_patterns()
        if FAST_INDEX:
            try:
                _entries(a.artifacts)
            except Exception:  # noqa: BLE001 - a set builds its own index as before
                pass
    solverrt.run_sets(jobs, _solve_pairs, out, pool)
    solverrt.emit_and_exit(out, pool)


if __name__ == "__main__":
    main()
