"""Web-lane solver helpers: bounded HTTP, live-target resolution, /api/clues dispatch, a proof-wins probe
race, and the fast-exit contract (re-exported from lib.solverrt).

The web apps since D05 are one kit: `GET /api/clues` returns a JSON object naming `framework`,
`feature_route`, `secondary_route`, `current_role` PLUS exactly one concept-specific key that identifies
the vuln class (e.g. `session_hint` -> session fixation, `callback_nonce` -> reflected XSS,
`moderator_data_route` -> stored XSS). Dispatch on the KEY, never the word in the value (the documented
pitfall). Every solve ends with `emit_and_exit` so a lingering probe pool/poll loop can't hold the
process past the window.

LLM-first: this is plumbing (HTTP, target lookup, race, exit), not a solver. The per-class exploitation
logic lives in lib/web/handlers/*; the worker still writes/adapts those with standard tools.
"""
import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request

from lib.solverrt import emit_and_exit  # noqa: F401  -- re-exported: web solvers end main() with this

UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/124.0 Safari/537.36")
PROOF_RE = re.compile(r"proof_[0-9A-Za-z]{8,}")


def _budget_left(default):
    """Seconds remaining before HCTF_SOLVE_DEADLINE (minus a 0.4 s margin), clamped to `default`."""
    try:
        left = float(os.environ["HCTF_SOLVE_DEADLINE"]) - time.time() - 0.4
    except (KeyError, ValueError):
        return default
    return max(0.1, min(default, left))


def fetch(url, headers=None, timeout=6, data=None, method=None):
    """GET/POST with a browser UA and a bounded timeout (never exceeds the solve deadline). Returns
    (status, body, set_cookie_headers); (0, "", []) on any transport error (callers treat as a miss)."""
    h = {"User-Agent": UA, "Accept": "application/json, text/html;q=0.9, */*;q=0.8"}
    h.update(headers or {})
    body_bytes = None
    if data is not None:
        body_bytes = data if isinstance(data, (bytes, bytearray)) else urllib.parse.urlencode(data).encode()
        h.setdefault("Content-Type", "application/x-www-form-urlencoded")
    req = urllib.request.Request(url, data=body_bytes, headers=h, method=method)
    to = min(timeout, _budget_left(timeout))
    try:
        with urllib.request.urlopen(req, timeout=to) as r:
            return r.status, r.read(1 << 20).decode("utf-8", "replace"), r.headers.get_all("Set-Cookie") or []
    except urllib.error.HTTPError as e:
        return e.code, e.read(1 << 20).decode("utf-8", "replace"), e.headers.get_all("Set-Cookie") or []
    except Exception:  # noqa: BLE001 - a transport error is just a miss on this probe
        return 0, "", []


def target_url(question, contract):
    """The live target URL for a question's `artifact` ("Target N"), matched by id then by number, else the
    sole target. None when it can't be resolved."""
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


def base_of(question, contract):
    """target_url with a guaranteed trailing slash (for urljoin), or None."""
    u = target_url(question, contract)
    if not u:
        return None
    return u if u.endswith("/") else u + "/"


def proof(body):
    """Extract a proof_<hex> token from a response body (JSON `evidence` field first, then any match)."""
    try:
        j = json.loads(body)
    except (ValueError, TypeError):
        j = None
    if isinstance(j, dict):
        v = j.get("evidence")
        if isinstance(v, str) and PROOF_RE.search(v):
            return PROOF_RE.search(v).group()
    m = PROOF_RE.search(body or "")
    return m.group() if m else None


def clues(base):
    """Fetch and parse GET /api/clues. Returns (clues_dict, dispatch_key) where dispatch_key is the single
    concept-specific key (the one NOT in the common kit set) that names the vuln class, or None.
    Dispatch on the KEY, never the value."""
    _, body, _ = fetch(urllib.parse.urljoin(base, "/api/clues"))
    try:
        j = json.loads(body)
    except (ValueError, TypeError):
        j = {}
    if not isinstance(j, dict):
        j = {}
    return j, dispatch_key(j)


def dispatch_key(j):
    """The first clue key NOT in the common kit set (the concept-specific one), or None."""
    common = {"framework", "feature_route", "secondary_route", "current_role", "routes", "role",
              "username", "user", "message"}
    return next((k for k in (j if isinstance(j, dict) else {}) if k not in common), None)


def race(probes, budget=40):
    """Run each (name, fn) in a daemon thread; the first proof-shaped result wins. A non-proof value is kept
    as a last resort. Losers keep running detached -- the caller exits via emit_and_exit without joining
    them. Honors HCTF_SOLVE_DEADLINE."""
    import queue
    import sys
    import threading
    q = queue.Queue()

    def run(name, fn):
        try:
            v = fn()
        except Exception as e:  # noqa: BLE001
            print(f"probe {name}: {e!r}", file=sys.stderr)
            v = None
        q.put((name, v))

    probes = list(probes)
    for name, fn in probes:
        threading.Thread(target=run, args=(name, fn), daemon=True).start()
    end = time.time() + budget
    try:
        end = min(end, float(os.environ["HCTF_SOLVE_DEADLINE"]) - 0.4)
    except (KeyError, ValueError):
        pass
    best, left = None, len(probes)
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
