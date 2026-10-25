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
_CONTRACT_PATH = None


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


import gzip
import io
import re
import tarfile
import urllib.parse
import urllib.request
import zipfile

PROOF_RE = re.compile(rb"proof_[A-Za-z0-9_\-]{6,}|flag\{[^}\s]{1,200}\}")
BACKUP_RE = re.compile(r"\.(bak|old|orig|save|swp|tmp|backup|zip|tar|tgz|gz|7z|sql|json|env|txt|log|yml|yaml|conf|cfg|ini)"
                       r"(\.[a-z0-9]+)?$|~$|backup|snapshot|archive|dump|env", re.I)


def _targets(contract):
    """{target id: url} from the contract, else from the mode dir's start/status envelopes."""
    out = {}
    bodies = [contract]
    d = Path(_CONTRACT_PATH).parent if _CONTRACT_PATH else None
    if d is not None:
        for name in ("status.json", "start.json"):
            try:
                bodies.append(json.loads((d / name).read_text()))
            except Exception:  # noqa: BLE001
                pass
    for b in bodies:
        for t in (b or {}).get("targets") or []:
            if isinstance(t, dict) and t.get("url"):
                out.setdefault(str(t.get("id")), t["url"])
    return out


def _get(url, limit=4 << 20):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (hctf solver)"})
        with urllib.request.urlopen(req, timeout=6) as r:
            return r.read(limit)
    except Exception:  # noqa: BLE001
        return None


def _unpack(b):
    """Search texts of a body: itself plus members of zip / gzip / tar archives."""
    out = [b]
    try:
        if b[:2] == b"PK":
            from lib.common import read_member
            z = zipfile.ZipFile(io.BytesIO(b))
            for n in z.namelist():
                try:
                    out.append(z.read(n))
                except RuntimeError:
                    try:
                        out.append(read_member(io.BytesIO(b), n))
                    except Exception:  # noqa: BLE001
                        pass
        elif b[:2] == b"\x1f\x8b":
            g = gzip.decompress(b)
            out.append(g)
            if len(g) > 262 and g[257:262] == b"ustar":
                b = g
        if len(b) > 262 and b[257:262] == b"ustar":
            with tarfile.open(fileobj=io.BytesIO(b)) as t:
                for m in t.getmembers():
                    if m.isfile():
                        out.append(t.extractfile(m).read())
    except Exception:  # noqa: BLE001
        pass
    return out


def _proof(b):
    for blob in _unpack(b or b""):
        m = PROOF_RE.search(blob)
        if m:
            return m.group(0).decode("latin-1")
    return None


def _links(base, body):
    hrefs = re.findall(rb"""(?:href|src)\s*=\s*["']([^"'#]+)""", body or b"")
    return [urllib.parse.urljoin(base, h.decode("latin-1")) for h in hrefs]


def crawl(url):
    """Follow what the site itself discloses: robots.txt Disallow paths and sitemap -> directory indexes -> backup
    files. A proof is the first `proof_...` token found in a leaked file (archives unpacked)."""
    base = url if url.endswith("/") else url + "/"
    host = urllib.parse.urlsplit(base).netloc
    robots = _get(urllib.parse.urljoin(base, "/robots.txt")) or b""
    paths = re.findall(rb"(?im)^\s*(?:dis)?allow\s*:\s*(\S+)", robots)
    paths += re.findall(rb"(?im)^\s*sitemap\s*:\s*(\S+)", robots)
    queue = [urllib.parse.urljoin(base, p.decode("latin-1").replace("*", "")) for p in paths if p.strip() != b"/"]
    home = _get(base) or b""
    # html comments / links on the home page that point at backups
    queue += [u for u in _links(base, home) if BACKUP_RE.search(urllib.parse.urlsplit(u).path)]
    seen, found = {base}, []
    while queue and len(seen) < 40:
        u = queue.pop(0)
        if u in seen or urllib.parse.urlsplit(u).netloc != host:
            continue
        seen.add(u)
        body = _get(u)
        if not body:
            continue
        p = _proof(body)
        if p:
            return p
        if b"<a " in body or b"<loc>" in body:
            for v in _links(u, body) + [x.decode("latin-1") for x in re.findall(rb"<loc>\s*([^<\s]+)", body)]:
                if v not in seen and v.startswith(base.rstrip("/")) and urllib.parse.urlsplit(v).path not in ("", "/") \
                        and not v.endswith((".css", ".svg", ".png", ".jpg", ".ico", ".woff2")):
                    queue.append(v)
    return _proof(home)


def answer(answer_id, question, data, contract):
    """Return the value for one answer_id from its artifact bytes (None = cannot answer). Derive everything from
    `data`; never hard-code a variant's values."""
    if data:
        p = _proof(data)
        if p:
            return p
    targets = _targets(contract)
    art = (question.get("artifact") or "").strip()
    url = targets.get(art)
    if url is None:
        m = re.search(r"(\d+)", art) or re.search(r"(\d+)$", answer_id)
        ids = [k for k in targets if m and re.search(rf"\b{m.group(1)}$", k)]
        url = targets[ids[0]] if ids else (next(iter(targets.values())) if len(targets) == 1 else None)
    if url is None:
        m = re.search(r"https?://\S+", question.get("question", "") + " " + art)
        url = m.group(0) if m else None
    return crawl(url) if url else None


def fallback(answer_id, question, data, contract):
    """Called ONLY when answer() found nothing (None or an exception): a cheap generic second try for a variant shape
    the direct parse doesn't know (Time Trial / Mastery mutate the task) -- e.g. the lane lib's name-agnostic decoder
    over `data`, then a match against question["answer_format"]. None = give up on this field only."""
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
    global _CONTRACT_PATH
    _CONTRACT_PATH = a.contract
    contract, pairs = load_contract(a.contract)
    groups = group_by_set(pairs)
    out = {}
    if len(groups) >= 2 and os.environ.get("HCTF_SOLVER_PARALLEL", "1") != "0":
        # Mastery: every set runs inside ONE clock -- one forked process per set (the Homebase VM has 2 vCPUs; heavy
        # per-set work such as unzipping 31 MB deliveries halves). Same results as the sequential loop.
        import multiprocessing as mp
        from concurrent.futures import ProcessPoolExecutor
        try:
            from lib.solverrt import max_procs   # HCTF_SOLVER_MAX_PROCS: the harness's small-pool rehearsal
            with ProcessPoolExecutor(max_workers=max_procs(len(groups)),
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
