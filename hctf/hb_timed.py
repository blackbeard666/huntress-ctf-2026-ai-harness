#!/usr/bin/env python3
"""One-shot timed attempt: the whole start -> download -> solve -> submit path in one process.

Runs LOCALLY against the public GM (pairing token) by default — direct HTTPS is fast enough for the
~6s Time Trial windows, so no VM/SSH is needed. Still runs unchanged ON Homebase against the inside
proxy (set HUNTRESS_GAME_MASTER_URL) as a fallback. The solver must already be correct
(built/generalised offline); this just executes the clock-critical path as fast as possible.

Usage:  python3 hb_timed.py <challenge-id> <solver_dir_rel_to_HW> [--op start|retry]
Prints one JSON line: {result, remaining, deadline, elapsed, submitted, detail}.
"""
import argparse
import hashlib
import http.client
import json
import os
import re
import subprocess
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

def _load_ratebucket():
    """GM rate governor, imported however hb_timed was loaded (package, standalone script, or bare
    file-path module). Falls back to loading the sibling ratebucket.py by path. See gm.py for why."""
    try:
        from . import ratebucket as rb
        return rb
    except Exception:  # noqa: BLE001
        pass
    try:
        import ratebucket as rb
        return rb
    except Exception:  # noqa: BLE001
        pass
    try:
        import importlib.util
        p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ratebucket.py")
        spec = importlib.util.spec_from_file_location("hctf_ratebucket", p)
        rb = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(rb)
        return rb
    except Exception:  # noqa: BLE001
        return None


ratebucket = _load_ratebucket()

GM = os.environ.get("HUNTRESS_GAME_MASTER_URL", "https://2026.huntress.ctf.games")
HW = Path(__file__).resolve().parent.parent          # project root locally; ~/hw on Homebase
CAP_RE = re.compile(r"(?:/download/|[?&]capability=)([0-9a-f]{64})")  # Homebase proxy or public GM


class _Ctx(__import__("threading").local):
    """Per-attempt state. hb_daemon runs several attempts at once in one process (one thread each)."""
    lane = None
    opts = None
    on_event = None   # hb_daemon (HCTF_EARLY_GENERALIZE): callable(dict) for mid-attempt events
    solver_dir = None  # rel. to HW: the challenge dir next to it holds label_hints.json (shared by its modes)
    t0 = None          # this attempt's start (HCTF_RUNNER_BUDGET is relative to it)
    spawn = None       # D24 #1: {main, lock} s before _attempt (interpreter start + imports, mode-lock wait)


_CTX = _Ctx()


def _event(kind, out, slim=False, **extra):
    """Mid-attempt event to the daemon client (HCTF_EARLY_GENERALIZE=1 only): {"event": kind, attempt facts}. The
    orchestrator can start the offline generalize on the variant while this attempt still localizes in-window.
    slim: no `submitted` (D25 C4 per-set events: several per attempt, the answers can be ~2.6k fields)."""
    cb = _CTX.on_event
    path = os.environ.get("HCTF_EARLY_EVENT_FILE")   # local runs (a subprocess): the parent polls this file
    if (cb is None and not path) or _opt("HCTF_EARLY_GENERALIZE", "0") != "1":
        return
    keys = ("cid", "attempt_id", "window", "deadline", "phases", "missing") + (() if slim else ("submitted",))
    data = dict({k: out.get(k) for k in keys}, event=kind, **extra)
    if cb is not None:
        try:
            cb(data)
        except Exception:  # noqa: BLE001 - an event must never cost the attempt
            pass
    if path:
        try:   # every event, in order (the local poller reads this log; the single file below = the first-event compat)
            with open(path + "l", "a") as f:
                f.write(json.dumps({k: v for k, v in data.items() if k != "submitted"}) + "\n")
        except (OSError, TypeError, ValueError):
            pass
        try:
            tmp = path + ".tmp"
            with open(tmp, "w") as f:
                json.dump({k: v for k, v in data.items() if k != "submitted"}, f)
            os.replace(tmp, path)
        except (OSError, TypeError, ValueError):
            pass
_TOKEN = None    # set in-process by hb_daemon: the bearer lives in its memory only (never env / argv / disk)
SOLVER = None    # hb_daemon: callable(solve_path, args, env, timeout) -> obj with stdout/stderr/returncode (zygote fork)


def _opt(key, default=None):
    """A per-attempt knob: the attempt's opts (hb_daemon) first, then this process's environment."""
    o = _CTX.opts
    if o and key in o:
        return o[key]
    return os.environ.get(key, default)


def _run_solver(solve, contract, artifacts, timeout, env):
    """solve.py on (contract, artifacts): a warm zygote fork under hb_daemon, else a fresh interpreter. Exports
    HCTF_SOLVE_DEADLINE (epoch, a margin before the kill) so lib.decode.peel / the skeleton's fallback stop searching
    and print what they have: D12 warmups Mastery, a 60k-node peel fallback x 58 sets ran into the 28 s kill with 0
    answers out."""
    args = ["--contract", str(contract), "--artifacts", str(artifacts)]
    env = dict(os.environ if env is None else env)
    env["HCTF_SOLVE_DEADLINE"] = f"{time.time() + timeout - min(1.0, 0.25 * timeout):.3f}"
    if SOLVER is not None:
        return SOLVER(str(solve), args, env, timeout)
    return run_group([sys.executable, str(solve), *args], timeout=timeout, env=env)


def run_group(cmd, timeout, env=None, **kw):
    """subprocess.run(capture_output, text) in its own session; on timeout the WHOLE group is SIGKILLed (a solver's
    fork pool too -- D16: ~20 orphaned solve.py forks kept a 12-core host at load 27) and TimeoutExpired raised.
    Self-contained (this file also runs alone on Homebase)."""
    import signal
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env,
                         start_new_session=True, **kw)
    try:
        out, err = p.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(p.pid, signal.SIGKILL)
        except OSError:
            pass
        try:
            p.communicate(timeout=5)
        except (subprocess.TimeoutExpired, ValueError, OSError):
            pass
        raise
    try:
        os.killpg(p.pid, signal.SIGKILL)      # forks left behind after a normal exit
    except OSError:
        pass
    return subprocess.CompletedProcess(cmd, p.returncode, out, err)


def _token():
    """Pairing token for the public GM: env first, then the project-local secret (None in-network)."""
    if _TOKEN:
        return _TOKEN
    tok = os.environ.get("HUNTRESS_GM_TOKEN")
    if tok:
        return tok.strip()
    try:
        with open(HW / "secrets" / "gm_pairing_token") as f:
            return f.read().strip() or None
    except OSError:
        return None


def _auth(headers=None):
    headers = dict(headers or {})
    tok = _token()
    if tok:
        headers["Authorization"] = "Bearer " + tok
    return headers


class _Pool:
    """Keep-alive connections to the GM, opened (TCP+TLS) BEFORE the clock starts and reused for every in-window
    request. Measured from the rehearsal copy (no Homebase): each GM call costs ~1.5s of origin latency, and a fresh
    connection adds ~0.6s, occasionally a multi-second TLS spike (6.9s once) — fatal inside a 6-7s window when every
    download thread and the submit each opened their own urllib connection."""

    def __init__(self, url, size=6):
        import queue
        from urllib.parse import urlsplit
        u = urlsplit(url)
        self.https = u.scheme == "https"
        self.host, self.port = u.hostname, u.port
        self.path = u.path or "/"         # inside proxy: /huntress-ctf-proxy (never add a trailing slash)
        self.q = queue.LifoQueue()
        self.size, self._pending = size, 0
        first = int(os.environ.get("HCTF_GM_POOL_FIRST", "2"))
        if os.environ.get("HCTF_GM_POOL_LAZY", "1") != "0" and 0 < first < size:
            self._open_lazy(size, first)
            return
        with ThreadPoolExecutor(max_workers=size) as ex:
            for c in ex.map(lambda _: self._new(), range(size)):
                self.q.put(c)

    def _open_lazy(self, size, first):
        """D24 #3 (HCTF_GM_POOL_LAZY): return once `first` sockets are connected (or every connect has ended); the rest
        finish their TCP+TLS on daemon threads and join the pool as they come up. Building all 32 before returning put
        the slowest handshake (a 6.9 s TLS spike once) in front of every mode's start. Daemon threads, not an executor:
        an executor's workers are joined at interpreter exit, so a one-shot runner would wait on a stuck connect."""
        import threading
        lock, ev = threading.Lock(), threading.Event()
        st = {"done": 0, "up": 0}
        self._pending = size

        def one():
            c = None
            try:
                c = self._new()
                c._hctf_used = time.time()   # idle is counted from the end of the handshake
            except Exception:  # noqa: BLE001 - a request opens its own socket when the pool is empty
                c = None
            finally:
                with lock:
                    self._pending -= 1
                    st["done"] += 1
                    if c is not None:
                        self.q.put(c)
                        st["up"] += c.sock is not None
                    if st["up"] >= first or st["done"] >= size:
                        ev.set()
        for _ in range(size):
            threading.Thread(target=one, daemon=True, name="gm-pool-connect").start()
        ev.wait()

    def _new(self, connect=True):
        import http.client
        cls = http.client.HTTPSConnection if self.https else http.client.HTTPConnection
        c = cls(self.host, self.port, timeout=20)
        c._hctf_used = time.time()
        if connect:
            try:
                c.connect()
            except OSError:
                pass                      # will reconnect lazily on first use
        return c

    def fresh(self, want=8):
        """Before a clock: drop sockets idle past IDLE_MAX and pre-open fresh ones (TCP+TLS) up to `want`, in parallel.
        A one-shot process's pool was just built (no-op); hb_daemon's pool idles between attempts. Sockets a lazy pool is
        still connecting count toward `want`, and a pool smaller than `want` (adaptive size) is topped up to its size."""
        import queue
        want = min(want, getattr(self, "size", want))
        keep = []
        while True:
            try:
                c = self.q.get_nowait()
            except queue.Empty:
                break
            if time.time() - getattr(c, "_hctf_used", 0) <= self.IDLE_MAX and c.sock is not None:
                keep.append(c)
            else:
                c.close()
        need = max(0, want - len(keep) - getattr(self, "_pending", 0))
        if need:
            with ThreadPoolExecutor(max_workers=need) as ex:
                keep += list(ex.map(lambda _: self._new(), range(need)))
        for c in keep:
            self.q.put(c)
        return self

    IDLE_MAX = float(os.environ.get("HCTF_POOL_IDLE_MAX", "3"))   # s idle before reuse (D8: 3.5 s ok, 5.7 s dropped)
    # A no-resend call (submit) reuses a socket only if it carried a reply within this many s: localization waves keep
    # sockets hot (D16: every probe paid a fresh TCP+TLS, 30+ sockets left in CLOSE-WAIT); a socket idle through a solve
    # still gets a fresh connection (D8: RemoteDisconnected on an idle kept-alive socket lost the verdict).
    NORESEND_IDLE = float(os.environ.get("HCTF_POOL_NORESEND_IDLE", "0.25"))

    def request(self, method, query, body=None, headers=None, timeout=None):
        """-> (status, bytes). Reconnects once if the kept-alive socket was dropped. `timeout` (s): a hard per-call
        bound with NO resend -- used for the submit, which must not outlive the clock nor be POSTed twice."""
        import http.client
        c = self.q.get() if not self.q.empty() else self._new(connect=False)
        idle = time.time() - getattr(c, "_hctf_used", time.time())
        if idle > self.IDLE_MAX or (timeout is not None and (idle > self.NORESEND_IDLE or c.sock is None)):
            # Never reuse a kept-alive socket that sat idle (e.g. through the solve): the GM proxy closes it. Day 8
            # binary + script Mastery (8 s / 5.4 s solves): the no-resend submit got RemoteDisconnected, no verdict,
            # attempt lost three times. A no-resend call always gets a fresh connection (sub-ms on the inside proxy).
            c.close()
            c = self._new(connect=False)
        if timeout is not None:
            c.timeout = timeout
            if c.sock is not None:
                c.sock.settimeout(timeout)
        reused = c.sock is not None
        headers = dict(headers or {})
        if _opt("HCTF_GM_GZIP", "1") != "0" and "op=download" not in query and "op=artifact" not in query:
            headers["Accept-Encoding"] = "gzip"   # API replies only (script Mastery start body 3.2 MB -> ~100 KB)
        try:
            for retry in ((False,) if timeout is not None else (True, False)):
                try:
                    try:
                        c.request(method, self.path + query, body=body, headers=headers)
                    except (BrokenPipeError, ConnectionResetError):
                        if not reused:
                            raise
                        # a hot kept-alive socket the server had just closed: the request never went out (the SEND
                        # failed), so one fresh connection is safe even for a no-resend submit
                        c.close()
                        c = self._new(connect=False)
                        if timeout is not None:
                            c.timeout = timeout
                        c.request(method, self.path + query, body=body, headers=headers)
                    r = c.getresponse()
                    raw = r.read()
                    if str(r.getheader("Content-Encoding") or "").lower() == "gzip":
                        import gzip
                        raw = gzip.decompress(raw)
                    if ratebucket and (r.status == 429 or b"rate_limited" in (raw or b"")):
                        ratebucket.note_429()   # participate in the account-wide pressure signal
                    return r.status, raw
                except (http.client.HTTPException, ConnectionError, OSError):
                    c.close()
                    c = self._new(connect=False)
                    if not retry:
                        raise
        finally:
            if timeout is not None:
                c.timeout = 20
                if c.sock is not None:
                    c.sock.settimeout(20)
            c._hctf_used = time.time()
            self.q.put(c)


_POOL = None


_POOL_LOCK = __import__("threading").Lock()


def _pool():
    global _POOL
    with _POOL_LOCK:
        return _pool_locked()


def _pool_locked():
    global _POOL
    if _POOL is None:
        # Pre-open enough connections (BEFORE the clock) for a many-file Mastery: from the public GM each download is
        # ~1.3-2 s, so 28 warmups deliveries over 6 sockets / 8 threads took 7.2 s -- the whole 7 s window (local replay).
        # Measured: 28 parallel calls = 4.4 s on 16 sockets vs 2.0 s on 32; pre-opening 32 costs ~0.1 s before the clock.
        _POOL = _Pool(GM, size=int(os.environ.get("HCTF_GM_POOL", "32")))
    return _POOL


class GMError(RuntimeError):
    """A GM HTTP error where a verdict is not acceptable (a download). `rate_limited` = transient: back off, retry."""

    def __init__(self, status, raw):
        super().__init__(f"GM HTTP {status}: {raw[:200]!r}")
        self.rate_limited = status == 429 or b"rate_limited" in (raw or b"")


def _refusal(status, raw):
    """A 429/503 that is a deterministic GM verdict, not load: a JSON body whose error isn't rate_limited (Day 8:
    503 training_rotation_invalid). Backing off on it only burns time before the caller can react."""
    if status not in (429, 503) or b"rate_limited" in (raw or b""):
        return False
    try:
        return bool(json.loads(raw).get("error"))
    except (ValueError, AttributeError):
        return False


def _open(method, query, body=None, headers=None, verdict_ok=True, waits=(0.5, 1.0), timeout=None):
    """Pooled request with a SHORT 429/503 backoff (the clock is running): 0.5s then 1s, then give up.
    4xx with a JSON body is a GM VERDICT (409 {"error": "prerequisite_required"}, ...), not a crash: it is returned
    so the caller classifies it (raising turned a prerequisite refusal into exec_error -> a pointless generalize).
    verdict_ok=False (downloads): ANY 4xx/5xx raises GMError -- Day 7 script TT saved the 24-byte
    '{"error":"rate_limited"}' body as evidence.zip and burned a 2-min generalize on a solver that was fine."""
    for wait in (*waits, None):
        status, raw = _pool().request(method, query, body, headers, **({"timeout": timeout} if timeout else {}))
        if status in (429, 503) and wait is not None and not _refusal(status, raw):
            time.sleep(wait)
            continue
        if status >= 400:
            if not verdict_ok:
                raise GMError(status, raw)
            try:
                json.loads(raw)
            except ValueError:
                raise RuntimeError(f"GM HTTP {status}: {raw[:200]!r}") from None
        return raw


def _post(payload, timeout=None):
    """POST -> the parsed body. An empty / non-JSON reply (2xx or an HTML 5xx) comes back as {"error": "unjudged_*"}
    instead of raising: it judged nothing, and the ValueError used to crash the whole attempt mid-window."""
    try:
        raw = _open("POST", "", json.dumps(payload).encode(), _auth({"Content-Type": "application/json"}),
                    timeout=timeout)
    except RuntimeError as e:   # _open: a 4xx/5xx without a JSON body
        return {"error": "unjudged_http", "detail": str(e)[:200]}
    except http.client.HTTPException as e:
        # IncompleteRead: the reply body was cut off mid-read (D15 script Mastery: 69 KB of a 2.7 MB localize reply).
        # The GM judged the request but we never saw the verdict: unjudged -> _submit resends it (a submit is
        # idempotent: banked ids just reconfirm). It is not an OSError, so it used to escape every handler and abort
        # the whole in-window localization (5 sets, 16 fixable fields -> a 3-min generalize). OSErrors (timeouts,
        # RemoteDisconnected) still propagate: their callers own the no-double-POST rule.
        if isinstance(e, OSError):
            raise
        return {"error": "unjudged_transport", "detail": repr(e)[:200]}
    try:
        res = json.loads(raw)
    except ValueError:
        return {"error": "unjudged_nonjson", "detail": (raw or b"")[:200].decode("utf-8", "replace")}
    return res if isinstance(res, dict) else {"error": "unjudged_nonjson", "detail": str(res)[:200]}


# A submit reply is a VERDICT only when it carries one of these results. rate_limited, an empty or non-JSON body, or an
# error with no result judged NOTHING: it is resent, and never counted as incorrect (reviewer rule; ours turned a
# surviving 429 into "incorrect" -> _localize marked never-judged fields wrong -> gm_feedback "rejected" -> a generalize
# away from right values).
VERDICTS = ("correct", "accepted", "incorrect", "expired")
UNJUDGED_RESENDS = tuple(float(x) for x in os.environ.get("HCTF_UNJUDGED_RESENDS", "0.3,0.8").split(",") if x)


def _unjudged(res):
    return not isinstance(res, dict) or str(res.get("result", "")).lower() not in VERDICTS


def _transient(res):
    """An unjudged reply worth resending (load / transport), not a deterministic refusal (unknown answer id, ...)."""
    if not isinstance(res, dict) or not res:
        return True
    err = str(res.get("error") or "")
    return not err or "rate_limited" in err or err.startswith("unjudged_")


def _submit(cid, answers, body, out=None, timeout=None):
    """One submit that is JUDGED when the GM can judge it: an unjudged transient reply is resent (UNJUDGED_RESENDS
    backoffs) while the clock allows. OSError still propagates (a timeout is never resent: no double POST)."""
    res = None
    for wait in (*UNJUDGED_RESENDS, None):
        res = _post({"op": "submit", "challenge": cid, "answers": answers},
                    timeout=timeout if timeout is not None else _submit_timeout(body))
        if not _unjudged(res) or not _transient(res) or wait is None:
            break
        left = _deadline_left(body)
        if left is not None and left < wait + 1.0:
            break
        if out is not None:
            out["unjudged_resends"] = out.get("unjudged_resends", 0) + 1
        time.sleep(wait)
    if out is not None:
        if _unjudged(res):
            out.setdefault("unjudged", []).append(str((res or {}).get("error") or "empty")[:80])
        elif _progress(res, out.get("gm_remaining")) == "reconfirm":
            out["reconfirms"] = out.get("reconfirms", 0) + 1   # `remaining` didn't move: nothing new banked
        if isinstance(res.get("remaining"), int):
            out["gm_remaining"] = res["remaining"]
    return res


def _progress(res, before=None):
    """What an accepted submit banked: 'progress' when `remaining` shrank (or the GM names accepted_ids), 'reconfirm'
    when it did not move (already-banked ids judged again -- not progress, not wrong), 'unknown' without a baseline."""
    if str((res or {}).get("result", "")).lower() != "accepted":
        return None
    rem = res.get("remaining")
    if isinstance(rem, int) and isinstance(before, int):
        return "progress" if rem < before else "reconfirm"
    if isinstance(res.get("accepted_ids"), list):
        return "progress" if res["accepted_ids"] else "reconfirm"
    return "unknown"


START_TIMEOUT = float(os.environ.get("HCTF_START_TIMEOUT", "10"))   # local GM starts take ~5 s, Homebase ~1 s


def _post_once(payload, tries=3):
    """start / retry, before the clock: each call is cut at START_TIMEOUT and RESENT on a hang. Safe because both are
    idempotent while an attempt is live (start reconnects to it; a retry on a live attempt resumes it without spending
    an attempt -- verified on a rehearsal copy 2026-10-08). Was the pool's 20 s socket timeout + one resend: a hung start cost 35 s
    before script Mastery's clock even began (mainblind3)."""
    import http.client
    for i in range(tries):
        try:
            res = _post(payload, timeout=START_TIMEOUT)
        except (OSError, http.client.HTTPException):
            if i == tries - 1:
                raise
            continue
        if isinstance(res, dict) and res.get("error") == "unjudged_transport" and i < tries - 1:
            continue    # reply cut off mid-body (IncompleteRead, now an unjudged body, not a raise): idempotent -> resend
        return res


# Day 8: Time Trial / Mastery became DUAL-POOL routes. A plain start/retry = the regular (untimed, not Hall of Fame)
# pool; run_for_time:true = a fresh timed Hall of Fame attempt. The regular pool refused every lane but warmups (503
# training_rotation_invalid). Legacy routes (binary D8) and Single Solve reject the property with 409
# timed_intent_not_available -> resend without it.
# HCTF_RUN_FOR_TIME: "auto" (default since 2026-10-15) = the UNTIMED regular pool first -- flag + full CourseStack points,
# retryable without a clock, only the Hall of Fame entry is forgone (user: HoF doesn't matter) -- and the timed pool
# only when the regular one refuses (training_rotation_invalid). "1" = HoF pool first (the 2026-10-08 policy).
# "0" = never ask for it (scout / probes that must not spend ranked attempts). Timed-by-default routes (no
# run_for_time_supported: D12, D14) start timed whatever we send.
def _rft():
    return _opt("HCTF_RUN_FOR_TIME", "auto")


def _hof_wanted(cid):
    return _rft() == "1" and cid.rsplit("/", 1)[-1] in ("time_trial", "mastery")


# The GM's "no fresh variant left" verdicts: `rotation_exhausted` (lessons) and `retry_variants_unavailable` (seen live:
# r11a binary D11 TT -- it fell into the start-refused backoff, 30 retries / ~11 min, and the mode was lost).
EXHAUSTED = ("rotation_exhausted", "retry_variants_unavailable")


def _exhausted(err):
    return any(x in str(err or "") for x in EXHAUSTED)


def _post_untimed(cid):
    """An UNTIMED attempt once the fresh timed pool is spent (top-team rule: out of unique attempts -> stop going for the
    Hall of Fame, still take the flag). Plain `retry` (no run_for_time) = the regular pool on a run_for_time_supported
    route (variant_fresh may be false: the last regular artifact, still full points); a legacy timed-by-default route
    answers that retry with an exhausted verdict -> `practice` continues the last artifact with no timer and a correct
    submit still completes the mode + unlocks the next (`"practice": true`)."""
    body = _post_once({"op": "retry", "challenge": cid})
    err = body.get("error") if isinstance(body, dict) else None
    if _WT is not None and _WT.is_live_body(body):
        return body     # web: untimed by default; a `preparing` retry is awaited by the caller, never `practice`d
    if err or body.get("deadline") or not body.get("answer_ids"):
        # still timed (legacy route with fresh variants left -- callers only come here after an exhausted verdict) or
        # refused: the practice continuation is the untimed path on these routes
        prac = _post_once({"op": "practice", "challenge": cid})
        if isinstance(prac, dict) and prac.get("answer_ids") and not prac.get("error"):
            return prac
        if err:
            return body if not (isinstance(prac, dict) and prac.get("error")) else prac
    return body


def _post_start(payload, tries=3):
    """_post_once with the pool policy (_rft): the regular pool by default, HoF first only on HCTF_RUN_FOR_TIME=1; the
    route's only pool when it has no HoF pool; the HoF pool when the regular one refuses (unless HCTF_RUN_FOR_TIME=0)."""
    if _hof_wanted(payload.get("challenge", "")) and "run_for_time" not in payload:
        payload = {**payload, "run_for_time": True}
    body = _post_once(payload, tries)
    err = str(body.get("error")) if isinstance(body, dict) else ""
    if payload.get("run_for_time") and "timed_intent_not_available" in err:
        body = _post_once({k: v for k, v in payload.items() if k != "run_for_time"}, tries)
    elif not payload.get("run_for_time") and "training_rotation_invalid" in err and _rft() != "0":
        body = _post_once({**payload, "run_for_time": True}, tries)
    return body


def _age(body):
    """Seconds since this attempt's clock started (None if unknown)."""
    import datetime as dt
    try:
        a = dt.datetime.fromisoformat(body["started_at"].replace("Z", "+00:00"))
        return (dt.datetime.now(dt.timezone.utc) - a).total_seconds()
    except (KeyError, TypeError, ValueError, AttributeError):
        return None


def _submit_timeout(body):
    """Seconds a submit may take: the clock's remainder + 1.5 s grace (min 2 s). Blind D7 replay: a GM submit hung, the
    pool's 20 s socket timeout + one RESEND made it 40.7 s for an 11 s window (and could POST the answers twice)."""
    left = _deadline_left(body)
    return 20.0 if left is None else max(2.0, left + 1.5)


def _get_bytes(cap, timeout=20):
    raw = _open("GET", f"?op=download&capability={cap}", headers=_auth(), verdict_ok=False, waits=(0.5, 1.0, 2.0))
    if len(raw) < 512 and raw.lstrip().startswith(b'{"error"'):   # an error body served with a 2xx: still not bytes
        raise GMError(200, raw)
    return raw


def _window(body):
    """Length of this attempt's clock in seconds (deadline - started_at), or None."""
    import datetime as dt
    try:
        a = dt.datetime.fromisoformat(body["started_at"].replace("Z", "+00:00"))
        d = dt.datetime.fromisoformat(body["deadline"].replace("Z", "+00:00"))
        return round((d - a).total_seconds(), 2)
    except (KeyError, TypeError, ValueError, AttributeError):
        return None


def _deadline_left(body):
    d = (body or {}).get("deadline")
    if not d:
        return None
    import datetime as dt
    end = dt.datetime.fromisoformat(d.replace("Z", "+00:00"))
    return (end - dt.datetime.now(dt.timezone.utc)).total_seconds()


def _plan(body):
    """(filename, capability) per unique deliverable, named by the questions' container names (see cli._planned_downloads)."""
    caps = []
    arts = body.get("artifacts")
    src = arts if isinstance(arts, list) and arts else (body.get("downloads") or
          ([body["download"]] if body.get("download") else []))
    for x in src:
        s = x.get("download", "") if isinstance(x, dict) else str(x)
        m = CAP_RE.search(s)
        if m and m.group(1) not in caps:
            caps.append(m.group(1))
    containers = []
    for q in body.get("questions") or []:
        a = q.get("artifact")
        if a:
            n = os.path.basename(a.split("->")[0].strip())
            if n and n not in containers:
                containers.append(n)
    return [(containers[i] if i < len(containers) else f"artifact-{i}.bin", c) for i, c in enumerate(caps)]


def _normalize(v, q):
    norm = (q or {}).get("normalization")
    v = _json_coerce(v, q)
    if norm == "exact":
        return v
    v = v.strip()
    return v.lower() if norm == "case_insensitive" else v


def _answer_str(v):
    """Same rule as solvers.answer_str: a list/dict the solver returned goes out as compact JSON, never str()'s repr."""
    if isinstance(v, str):
        return v
    if isinstance(v, (list, dict)):
        return json.dumps(v, separators=(",", ":"), ensure_ascii=False)
    return str(v)


def _json_coerce(value, q):
    """Same rule as cli._json_coerce (this file runs standalone on Homebase): answer_format.kind "json" + a Python
    literal (`['a', 'b']`) -> the same data as compact JSON (D23 metadata Mastery, every set). Valid JSON untouched."""
    af = (q or {}).get("answer_format") if isinstance((q or {}).get("answer_format"), dict) else {}
    if str(af.get("kind")) != "json" or not isinstance(value, str):
        return value
    s = value.strip()
    if not s or s[0] not in "[{(":
        return value
    try:
        json.loads(s)
        return value
    except ValueError:
        pass
    import ast
    try:
        obj = ast.literal_eval(s)
    except (ValueError, SyntaxError, TypeError, MemoryError, RecursionError):
        return value
    if isinstance(obj, tuple):
        obj = list(obj)
    if not isinstance(obj, (list, dict)):
        return value
    try:
        return json.dumps(obj, separators=(",", ":"), ensure_ascii=False)
    except (TypeError, ValueError):
        return value


def _vocab():
    """Closed vocabularies by field suffix, from lib/vocab.json (grown by `hctf labels` whenever the GM confirms a
    label), so a wrong label can be corrected inside the same attempt."""
    try:
        return {k: list(v) for k, v in json.loads((HW / "lib" / "vocab.json").read_text()).items()}
    except (OSError, ValueError):
        return {}


def _suffix(aid):
    m = re.search(r"([-_][A-Za-z0-9]+)$", aid.rsplit(".", 1)[-1])
    return m.group(1) if m else None


def _lane_from_solver_dir(sd):
    """Lane for the per-lane playbook, from the challenge's meta.json next to the solver dir."""
    try:
        return json.loads(((HW / sd).parent / "meta.json").read_text()).get("lane")
    except (OSError, ValueError, AttributeError):
        return None


def _playbook_alts(aid, cur):
    """Playbook-ranked candidate labels for a wrong field (e.g. VBS On-Error control -> error_guard first), so a
    BRAND-NEW construct the GM has never confirmed can still be corrected in-window on its first encounter. Best
    effort: lib may be unavailable, and the resolver falls back to vocab.json either way."""
    if not _CTX.lane:
        return []
    try:
        if str(HW) not in sys.path:
            sys.path.insert(0, str(HW))
        from lib import playbook
        return [c for c in playbook.seed_candidates(_CTX.lane, aid, solver_value=cur) if c and c != cur]
    except Exception:  # noqa: BLE001 - never let the playbook break the clock path
        return []


def _is_label(aid, vocab):
    """A synthetic-label field (closed-vocab family in vocab.json, or a playbook family for this lane)."""
    if (_suffix(aid) or "") in vocab:
        return True
    if not _CTX.lane:
        return False
    try:
        if str(HW) not in sys.path:
            sys.path.insert(0, str(HW))
        from lib import playbook
        return playbook.entry_for(_CTX.lane, aid) is not None
    except Exception:  # noqa: BLE001
        return False


# Closed-vocab label families (mirror of hctf.labels.CACHEABLE_FAMILIES; kept here so this file stays standalone on
# Homebase). Only these can be "uncertain"/"novel": ATT&CK ids, symbols, etc. are labels-ish but never cached.
_CACHEABLE = {"control", "expansion", "format", "representation", "transform", "endianness", "machine", "class", "type"}


def _family(aid):
    return (_suffix(aid) or "").lstrip("-_").lower()


def _uncertain(aid, val, vocab):
    """A closed-vocab label whose value the GM has never confirmed for its family (a construct new to us)."""
    return _family(aid) in _CACHEABLE and _is_label(aid, vocab) and str(val) not in vocab.get(_suffix(aid) or "", [])


def _label_first(group, answers, vocab):
    """Order a failed set for the search: UNCERTAIN labels (solver value never GM-confirmed for its family) first,
    then other labels, then deterministic values. Returned as separate groups so a short window judges the likely
    culprits before it spends submits on hashes/strings that are almost always right."""
    unc, lab, rest = [], [], []
    for aid in group:
        if _uncertain(aid, answers.get(aid), vocab):
            unc.append(aid)
        elif _is_label(aid, vocab):
            lab.append(aid)
        else:
            rest.append(aid)
    return [g for g in (unc, lab, rest) if g]


PROGRESS_KEYS = ("attempt_id", "deadline", "no_clock", "untimed", "run_for_time", "window", "per_set", "full_result",
                 "partial_submit", "verified", "result", "already_passed", "resumed_banked", "phase")


def _progress_path(cid):
    return HW / ".run" / "tmp-timed" / (re.sub(r"[^A-Za-z0-9]+", "_", cid) + ".progress.json")


def _write_progress(cid, out, phase=None):
    """Persist this attempt's identity + what the GM has accepted so far (atomic). A runner killed from outside (the
    caller's subprocess timeout) used to lose everything: D16 script Mastery, six kills, each time `op=start` again
    because last_timed.json had no attempt_id. workers.run_timed reads this back on a timeout."""
    if phase:
        out["phase"] = phase
    try:
        p = _progress_path(cid)
        p.parent.mkdir(parents=True, exist_ok=True)
        tmp = p.with_name(p.name + f".{os.getpid()}.tmp")
        tmp.write_text(json.dumps({k: out[k] for k in PROGRESS_KEYS if k in out}))
        os.replace(tmp, p)
    except (OSError, TypeError, ValueError):
        pass


def _runner_left():
    """Seconds until the CALLER kills this process (HCTF_RUNNER_DEADLINE, epoch), minus a margin for the final resubmit +
    printing the result; None when unbounded."""
    try:
        margin = float(_opt("HCTF_RUNNER_MARGIN", "15"))
        d = _opt("HCTF_RUNNER_DEADLINE")
        if d:
            return float(d) - time.time() - margin
        b = _opt("HCTF_RUNNER_BUDGET")       # Homebase: relative to this attempt's start (no cross-host clock skew)
        if b and getattr(_CTX, "t0", None):
            return _CTX.t0 + float(b) - time.time() - margin
    except ValueError:
        pass
    return None


try:
    import grouptest as _GT          # hctf/ is this file's directory (synced whole to Homebase)
except ImportError:
    try:
        from hctf import grouptest as _GT     # imported as hctf.hb_timed
    except ImportError:  # pragma: no cover - an old Homebase copy: the sequential bisect below
        _GT = None


try:
    import webtarget as _WT          # hctf/ is this file's directory (synced whole to Homebase)
except ImportError:
    try:
        from hctf import webtarget as _WT     # imported as hctf.hb_timed
    except ImportError:  # pragma: no cover - an old Homebase copy: no live-target wait
        _WT = None


def _status_body(cid):
    import urllib.parse
    try:
        raw = _open("GET", "?" + urllib.parse.urlencode({"op": "status", "challenge": cid}), headers=_auth())
        b = json.loads(raw)
        return b if isinstance(b, dict) else {}
    except Exception:  # noqa: BLE001 - one failed poll
        return {}


def _arena_start(cid):
    """The browser arena's `start` (hctf/gm.py cmd_arena): revives a `cleaned` web attempt."""
    try:
        import gm as _gm
    except ImportError:
        from hctf import gm as _gm
    # run_for_time only on timed routes: a Single Solve answers 409 timed_intent_not_available to it
    env = _gm.cmd_arena("start", cid, run_for_time=False if re.search(r"/(time_trial|mastery)$", cid) else None,
                        token=_token())
    return env.get("body") if isinstance(env.get("body"), dict) else {}


def _await_live(cid, body, out):
    """Web (live target): a start/retry that answers `preparing` has no ids/targets and NO clock yet -- poll status until
    the target is up (a `cleaned` attempt is revived via the arena), instead of reading it as a failed start (D19: 5
    `no_answer_ids` tries in 30 s, chain stopped). Non-web bodies pass through untouched."""
    if _WT is None or not _WT.needs_wait(body):
        return body
    t = time.time()

    def kick(c, n):
        # a start stuck in `preparing` (D20: both Mastery first starts 5:21; every retry 11-18 s): public `retry`
        # (hands back the same unsolved attempt once live) / arena `start`, alternating -- webtarget.kick_plan
        if _WT.kick_plan(c, n) == "retry":
            return _post_once({"op": "retry", "challenge": c})   # plain retry: never the pool fallbacks of _post_start
        return _arena_start(c)
    body = _WT.await_target(cid, body, _status_body, revive=_arena_start,
                            log=lambda m: print(m, file=sys.stderr), wait=float(_opt("HCTF_WEB_PREPARE_WAIT", _WT.WAIT)),
                            kick=kick, trace=out.setdefault("web_trace", []))
    out["web_wait"] = round(out.get("web_wait", 0) + time.time() - t, 1)
    return body


def _free_text_format(af):
    """D25 C4: an answer_format no label retry can fix -- exact artifact text, an integer, or a pattern
    that is only a hex / hash / digit shape (a pattern naming labels / names / tokens stays a label field)."""
    if not isinstance(af, dict):
        return False
    kind = str(af.get("kind") or "").lower()
    if kind in ("exact_text", "integer"):
        return True
    if kind != "pattern":
        return False
    syn = str(af.get("syntax") or "").lower()
    return bool(re.search(r"hexadecimal|sha-?\d+|md5|digits?\b", syn)) and not re.search(
        r"label|name|token|constant|architecture|format|container", syn)


def _localize(cid, answers, groups, per_set, body, out):
    """Window permitting, binary-search the wrong answer_ids inside each failed set (subset submits on the SAME
    attempt), then try the field's other known labels (lib/vocab.json). Reports what the GM verified so the
    variant becomes a regression case: out["verified"] holds only answers the GM accepted on this attempt.
    Failed sets are localized in PARALLEL (HCTF_LOCALIZE_PARALLEL threads; sets are independent and the per-set submit
    already runs concurrently over the same keep-alive pool) -- a13sota7: a 5-set script Mastery spent its whole budget
    on sets 1-2 one after another and fixed nothing in-window."""
    import threading
    from concurrent.futures import ThreadPoolExecutor
    lock = threading.Lock()
    state = {"complete": True}
    unjudged, ok_fields, fixed = [], set(), {}
    t_loc = time.time()

    def ok(res):
        r = str(res.get("result", "")).lower()
        if r == "correct" or r == "already_solved" or (r == "accepted" and res.get("remaining") == 0):
            out["localize_completed_attempt"] = True   # a fix submit completed the attempt (the GM said so)
        return r in ("correct", "accepted", "already_solved")

    def budget_left():
        # no deadline (untimed regular pool / practice): a time budget instead of none -- rehearsal D13 a13sota6: an untimed
        # script Mastery localized 5 sets x 913 fields past the 60 s orchestrator call timeout, 4 times (12 min lost)
        left = _deadline_left(body)
        if left is None:
            left = float(_opt("HCTF_LOCALIZE_UNTIMED_S", "75")) - (time.time() - t_loc)
        rl = _runner_left()        # never outlive the caller's kill: stop, resubmit what is fixed, print the result
        return left if rl is None else min(left, rl)

    def incomplete():
        with lock:
            state["complete"] = False

    def sub(ans):
        # A timeout / dropped socket on ONE localization submit judged nothing: that subset stays unjudged and every
        # other subset and set carries on (D15 script Mastery: one cut-off reply ended all 5 sets' localization).
        try:
            return _submit(cid, ans, body, out)
        except Exception as e:  # noqa: BLE001
            with lock:
                out.setdefault("localize_errors", []).append(repr(e)[:160])
            return {"error": f"unjudged_exc {e!r}"[:160]}

    def narrow(group, wrong):
        if not group:
            return
        if budget_left() < 0.8:
            incomplete()
            return
        res = sub({k: answers[k] for k in group})
        if ok(res):
            with lock:
                ok_fields.update(group)
            return
        if _unjudged(res):
            # the GM judged nothing (rate_limited / non-JSON / refusal): never record these fields as wrong
            with lock:
                unjudged.extend(group)
            incomplete()
            return
        if len(group) == 1:
            wrong.append(group[0])
            return
        mid = len(group) // 2
        narrow(group[:mid], wrong)
        narrow(group[mid:], wrong)

    def alternatives(aid, vocab):
        if aid in freetext:
            return   # D25 C4: exact text / integer / hash-shaped field -- no label spelling can fix it
        cur = answers.get(aid)
        # what an EARLIER attempt of this challenge (D15: the Time Trial) learned for this family + this rejected value
        hint = hints.get(_suffix(aid) or "", {}).get(str(cur), {})
        enum = enums.get(aid) or []
        alts = []
        for alt in list(hint) + list(vocab.get(_suffix(aid) or "", [])) + _playbook_alts(aid, cur):
            if alt != cur and alt not in alts and (not enum or alt in enum):
                alts.append(alt)
        alts += [v for v in enum if v != cur and v not in alts]     # an enum: the contract's complete vocabulary
        with lock:   # the value this attempt has accepted most often so far goes first (a13sota8: 20 of 21 fixes
            seen = {}  # were one label, tried third every time)
            for v in fixed.values():
                seen[v] = seen.get(v, 0) + 1
            # + values the GM ACCEPTED for sibling fields of the same family in this attempt (same construct, rubric)
            for a2 in ok_fields:
                if a2 != aid and _suffix(a2) == _suffix(aid) and answers.get(a2) not in (None, cur):
                    seen[answers[a2]] = seen.get(answers[a2], 0) + 1
        alts.sort(key=lambda v: (-hint.get(v, 0), -seen.get(v, 0)))
        for alt in alts:
            if budget_left() < 0.5:
                incomplete()
                return
            res = sub({aid: alt})
            if ok(res):
                with lock:
                    fixed[aid] = alt
                return
            if _unjudged(res):
                return
            with lock:
                out.setdefault("localize_tried", {}).setdefault(aid, []).append(alt)

    def one_set(key, v, vocab):
        """-> this set's wrong ids, in field order; fixes land in `fixed`. Never raises: a failure stays in this set."""
        wrong = []
        try:
            if v["result"] in ("correct", "accepted"):
                with lock:
                    ok_fields.update(groups.get(key, {}))
                return wrong
            if v["result"] == "incorrect" and not v.get("assumed") and len(groups.get(key, {})) == 1:
                # a one-field set judged incorrect IS that field's verdict: re-submitting it alone only repeats it
                # (rehearsal D13 replay, warmups Mastery: 41 such submits, ~20 s of a failed attempt)
                wrong.append(next(iter(groups[key])))
            elif _GT is not None:
                # parallel waves (hctf/grouptest.py): the set's label-first groups cut into contiguous sub-groups, every
                # open group probed at once, failing ones halved -- D16 script Mastery: the sequential bisect of 5 x 1095
                # fields needed ~259 s for 4 wrong fields; the outer runner killed it at 120 s, six times.
                def gprobe(g):
                    # grouptest's pool threads: this attempt's context (daemon opts, lane, t0) is thread-local
                    _CTX.lane, _CTX.opts, _CTX.on_event, _CTX.solver_dir, _CTX.t0 = ctx
                    if budget_left() < 0.8:
                        return None
                    res = sub(g)
                    if ok(res):
                        with lock:
                            ok_fields.update(g)
                        return "solved" if out.get("localize_completed_attempt") else "ok"
                    if _unjudged(res):     # retried once by grouptest; still-unjudged ids come back in st
                        return "rate" if "rate_limited" in json.dumps(res)[:2000] else None
                    return "bad"
                gs = []
                # SUSPECTS first, one field per group: a value label_hints records as GM-rejected before (D16 Mastery:
                # call_double -> for_indirect, x6) -- the rest of the set then banks in large groups
                keys = list(groups.get(key, {}).keys())
                sus = [x for x in keys if hints.get(_suffix(x) or "", {}).get(str(answers.get(x)))][:_GT.CONC]
                gs += [{x: answers[x]} for x in sus]
                rest = [x for x in keys if x not in sus]
                for grp in _label_first(rest, answers, vocab):
                    gs += _GT.initial_groups({a: answers[a] for a in grp}, target=max(2, _GT.TARGET_GROUPS // 3),
                                             families=False)
                found, st = _GT.find_rejected(gprobe, {a: answers[a] for g in gs for a in g}, groups=gs,
                                              conc=max(2, _GT.CONC // max(1, n_failed)),
                                              # only a set the GM itself judged incorrect is KNOWN bad; an assumed
                                              # one (the bulk submit failed) gets its lone field probed
                                              whole_known_bad=v["result"] == "incorrect" and not v.get("assumed"),
                                              stop=lambda: budget_left() < 0.8)
                with lock:
                    out.setdefault("localize_waves", []).append({"set": key, **{k: st.get(k) for k in
                                                                 ("probes", "waves", "rate_limited", "seconds")}})
                if st.get("unjudged_ids"):
                    with lock:
                        unjudged.extend(st["unjudged_ids"])
                if st.get("unjudged_fields") or budget_left() < 0.8:
                    incomplete()
                order = list(groups.get(key, {}).keys())
                wrong += sorted(found, key=order.index)
            else:
                for grp in _label_first(list(groups.get(key, {}).keys()), answers, vocab):
                    narrow(grp, wrong)
            if v["result"] == "incorrect":
                # D25 C4: this set's wrong fields are known now -- before the label retries, the resubmit, the runner's
                # return and the variant pull (binary D25 Mastery: ~35 s + 26 s before the live worker started)
                _event("set_localized", out, slim=True, set=key, set_wrong=[[x, answers.get(x)] for x in wrong])
            if len(wrong) > 1:
                # every wrong field's alternatives at once (sequential, D16 alt: ~2-5 s per probe per field)
                def alt_ctx(aid):
                    _CTX.lane, _CTX.opts, _CTX.on_event, _CTX.solver_dir, _CTX.t0 = ctx
                    alternatives(aid, vocab)
                with ThreadPoolExecutor(max_workers=min(len(wrong), 6)) as ax:
                    list(ax.map(alt_ctx, wrong))
            else:
                for aid in wrong:
                    alternatives(aid, vocab)
        except Exception as e:  # noqa: BLE001
            with lock:
                out.setdefault("localize_errors", []).append(f"{key}: {e!r}"[:160])
            incomplete()
        return wrong

    vocab = _vocab()
    hints = _hints()
    enums = {}
    for q in body.get("questions") or []:
        af = q.get("answer_format") or {}
        if af.get("kind") == "enum" and af.get("accepted_values") and q.get("id"):
            enums[q["id"]] = [str(x) for x in af["accepted_values"]]
    for aid in answers:            # answer ids may carry a set prefix the question id lacks (set2.batch-x-expansion)
        if aid not in enums:
            base_q = aid.split(".", 1)[-1]
            if base_q in enums:
                enums[aid] = enums[base_q]
    freetext = set()
    if _opt("HCTF_LOCALIZE_SKIP_FREETEXT", "1") == "1":
        for q in body.get("questions") or []:
            if isinstance(q, dict) and q.get("id") and _free_text_format(q.get("answer_format")):
                freetext.add(q["id"])
        freetext |= {aid for aid in answers if aid.split(".", 1)[-1] in freetext}
    # _CTX is thread-local: the pool threads below would see lane/opts = None (no playbook alternatives, the daemon's
    # HCTF_LOCALIZE_UNTIMED_S ignored) -- hand this attempt's context to each of them
    ctx = (_CTX.lane, _CTX.opts, _CTX.on_event, _CTX.solver_dir, getattr(_CTX, "t0", None))

    def one_set_ctx(key, v, vocab):
        _CTX.lane, _CTX.opts, _CTX.on_event, _CTX.solver_dir, _CTX.t0 = ctx
        try:
            return one_set(key, v, vocab)
        finally:
            _CTX.lane = _CTX.opts = _CTX.on_event = _CTX.solver_dir = _CTX.t0 = None
    by_set = {}
    n_failed = sum(1 for v in per_set.values() if v.get("result") not in ("correct", "accepted"))
    try:
        keys = list(per_set)
        par = max(1, min(int(_opt("HCTF_LOCALIZE_PARALLEL", "5")), len(keys)))
        with ThreadPoolExecutor(max_workers=par) as ex:
            futs = {k: ex.submit(one_set_ctx, k, per_set[k], vocab) for k in keys}
            for k in keys:
                by_set[k] = futs[k].result()
    except Exception as e:  # noqa: BLE001 - diagnostics only
        out["localize_error"] = repr(e)
        state["complete"] = False
    wrong = [a for k in per_set for a in by_set.get(k, [])]
    out["wrong"] = [[a, answers.get(a)] for a in wrong]
    out["fixed"] = fixed
    out["localize_complete"] = state["complete"]
    if unjudged:
        out["localize_unjudged"] = unjudged
    out["verified"] = {**{a: answers[a] for a in ok_fields if a in answers}, **fixed}
    out["novel_labels"] = _novel(out["verified"], vocab)
    if out.get("localize_errors"):
        out["localize_error"] = out["localize_errors"][0]   # the key the orchestrator / dashboards already read
    _record_hints(answers, fixed)


def _hints_path():
    sd = _CTX.solver_dir
    return (HW / sd).parent / "label_hints.json" if sd else None


def _hints():
    """{family suffix: {rejected value: {GM-accepted value: n}}} learned by in-window fixes on earlier attempts of THIS
    challenge (any mode). A ranking hint for the next attempt's corrector, never an answer rewrite: on D15 script the
    Time Trial's 8 x expansion delayed -> percent held for 20 of Mastery's 30 `delayed` answers, not the other 10."""
    p = _hints_path()
    try:
        h = json.loads(p.read_text()) if p else {}
    except (OSError, ValueError):
        h = {}
    try:   # + every OTHER challenge's hints (workers.timed_env -> HCTF_LABEL_HINTS): D16 Mastery learnt
        # call_double -> for_indirect, which the next challenge's corrector never saw
        for suf, m in (json.loads(_opt("HCTF_LABEL_HINTS") or "{}") or {}).items():
            for wrong, rights in (m or {}).items():
                tgt = h.setdefault(suf, {}).setdefault(wrong, {})
                for v, n in (rights or {}).items():
                    tgt[v] = max(tgt.get(v, 0), int(n or 0))
    except (ValueError, TypeError, AttributeError):
        pass
    return h


def _record_hints(answers, fixed):
    p = _hints_path()
    if not p or not fixed:
        return
    h = _hints()
    for aid, val in fixed.items():
        suf, cur = _suffix(aid), answers.get(aid)
        if not suf or cur in (None, ""):
            continue
        d = h.setdefault(suf, {}).setdefault(str(cur), {})
        d[val] = d.get(val, 0) + 1
    try:
        tmp = p.with_suffix(".tmp")
        tmp.write_text(json.dumps(h, indent=1, sort_keys=True))
        tmp.replace(p)
    except OSError:
        pass


RESUBMIT_FIXED = os.environ.get("HCTF_RESUBMIT_FIXED", "1") != "0"


def _resubmit_fixed(cid, answers, body, out):
    """After _localize corrected EVERY wrong field on this attempt (GM-accepted alternatives in out["fixed"]): resubmit
    the whole corrected answer set on the SAME attempt -- the GM keeps it open after an incorrect full submit and passes
    it (verified on a rehearsal copy 2026-10-15: full submit incorrect -> single-field fix accepted (remaining 912) -> full resubmit
    CORRECT). rehearsal D13 replays: every failed script Time Trial had all wrong labels fixed in-window and still cost a
    generalize + retry (3-11 min each). Clock permitting; True when the attempt is now CORRECT."""
    if not RESUBMIT_FIXED or str(out.get("result", "")).lower() != "incorrect":
        return False
    fixed = out.get("fixed") or {}
    if out.get("localize_completed_attempt"):
        # the GM itself said a localization submit completed this attempt: it is passed, nothing to resubmit
        out.update(result="correct", resubmit_fixed="completed_by_localize", bad_sets=[],
                   verified={**{a: v for a, v in answers.items() if v not in (None, "")}, **fixed})
        return True
    if not out.get("localize_complete"):
        return False
    wrong = [w[0] for w in out.get("wrong") or []]
    ids = list(body.get("answer_ids") or [])
    final = {**{a: v for a, v in answers.items() if v not in (None, "")}, **fixed}
    if not wrong or any(a not in fixed for a in wrong) or (ids and any(a not in final for a in ids)):
        return False
    left = _deadline_left(body)
    if left is not None and left < 0.6:
        out["resubmit_fixed"] = "no clock left"
        return False
    try:
        res = _submit(cid, final, body, out)
    except OSError as e:
        out["resubmit_fixed"] = f"no answer: {e!r}"[:160]
        return False
    rk = str(res.get("result", "")).lower()
    out["resubmit_fixed"] = rk
    # already_solved = THIS attempt was completed before the resubmit (the GM answers it only after the attempt went
    # CORRECT -- alt 2026-10-15 probe): localization's last accepted fix finished it (a13sota5: 3 "incorrect" Time
    # Trials were in fact passed, and each cost a generalize)
    if rk == "already_solved" or (rk in ("correct", "accepted") and not res.get("remaining")):
        out["result"] = "correct"
        out["verified"] = dict(final)
        out["bad_sets"] = []
        return True
    return False


def _novel(verified, vocab):
    """GM-verified label values not yet in vocab.json: what this variant TAUGHT us (new construct spellings)."""
    return {a: v for a, v in (verified or {}).items() if _uncertain(a, v, vocab)}


def _solver_env():
    env = dict(os.environ, PYTHONPATH=str(HW))
    # user-level tools `hctf hb setup` installs without root (static 7-Zip as 7zz/7z on the the VM: no sudo there)
    env["PATH"] = f"{Path.home() / '.local' / 'bin'}:{Path.home() / 'hbtools' / 'bin'}:{env.get('PATH', '')}"
    if (Path.home() / "hbtools" / "jdk").is_dir():
        env.setdefault("JAVA_HOME", str(Path.home() / "hbtools" / "jdk"))   # setup/homebase_tools.sh (jadx/apktool)
    import shutil as _sh
    if not _sh.which("7z", path=env["PATH"]):  # still none: the pyzipper-backed bin/shims/7z
        env["PATH"] = f"{HW / 'bin' / 'shims'}:{env.get('PATH', '')}"
    return env


PIPELINE = os.environ.get("HCTF_PIPELINE_SETS", "1") == "1"
PIPELINE_MIN_BYTES = float(os.environ.get("HCTF_PIPELINE_MIN_MB", "20")) * 1e6
PIPELINE_DL = int(os.environ.get("HCTF_PIPELINE_DL", "3"))
# A solver that solves Mastery sets one after another (no group_by_set / process pool anywhere in its dir -- copied
# prior-day solvers on binary/script, SPEED.md: binary Mastery solve 8.3 s) gets the per-set runner from this size on.
PIPELINE_SEQ_MIN_MB = float(os.environ.get("HCTF_PIPELINE_SEQ_MIN_MB", "5"))


def _sequential_solver(solve):
    """True when nothing in the solver's dir solves sets in parallel itself."""
    try:
        src = "\n".join(p.read_text(errors="replace") for p in Path(solve).parent.glob("*.py"))
    except OSError:
        return False
    return not any(s in src for s in ("group_by_set", "ProcessPoolExecutor", "multiprocessing", "os.fork"))


def _total_bytes(body):
    """Delivery bytes: the body's artifact sizes, else the caller's HCTF_EXPECT_BYTES (from the status-time contract --
    a live start body lists no sizes)."""
    n = sum(int(x.get("size") or 0) for x in body.get("artifacts") or [] if isinstance(x, dict))
    return n or int(_opt("HCTF_EXPECT_BYTES") or 0)


def _set_plan(body, plan, ids):
    """{set key: [delivery file names]} when every set (`setN.` ids) reads only its OWN deliveries, else None (a single
    set, a shared delivery, a question naming no known delivery: the plain download-all-then-solve path)."""
    names = {n for n, _ in plan}
    keys = {_setkey(i) for i in ids}
    if len(keys) < 2 or "_" in keys:
        return None
    files = {}
    for q in body.get("questions") or []:
        aid, art = q.get("id") or "", q.get("artifact") or ""
        n = os.path.basename(art.split("->")[0].strip()) if art else ""
        if n:
            if n not in names:
                return None
            files.setdefault(_setkey(aid), set()).add(n)
    owner = {}
    for k, ns in files.items():
        for n in ns:
            if owner.setdefault(n, k) != k:
                return None
    if set(files) != keys or set(owner) != names:
        return None
    return {k: sorted(files[k]) for k in sorted(files, key=lambda s: int(re.sub(r"\D", "", s) or 0))}


def _pipelined(sets, plan, body, ids, adir, solve, env, fetch, left, out, t_started):
    """Download PIPELINE_DL deliveries at a time in set order; each set whose deliveries are all in runs solve.py on its
    own sub-contract (that set's ids/questions, a dir holding only its deliveries) while the next sets download.
    -> a CompletedProcess-like object with the merged answers, or None when any set run failed (the caller then runs
    the whole solver once on everything, as before). Download errors propagate (GMError)."""
    import shutil as _sh
    import threading
    from types import SimpleNamespace
    caps = dict(plan)
    order = [n for k in sets for n in sets[k]]
    pending = {k: set(v) for k, v in sets.items()}
    lock = threading.Lock()
    results, t_first = {}, []
    budget_end = time.time() + _solve_budget(body, left) + 1.5   # the clock's end minus the submit allowance
    solver_pool = ThreadPoolExecutor(max_workers=max(1, os.cpu_count() or 2))
    futs = {}

    def run_set(k):
        d = adir / f".set-{k}"
        d.mkdir(exist_ok=True)
        for n in sets[k]:
            os.link(adir / n, d / n)
        sub = dict(body, answer_ids=[i for i in ids if _setkey(i) == k],
                   questions=[q for q in body.get("questions") or [] if _setkey(q.get("id") or "") == k])
        (d / "contract.json").write_text(json.dumps(sub))
        t_first.append(time.time())
        r = _run_solver(solve, d / "contract.json", d, max(1.0, budget_end - time.time()), env)
        got = json.loads(r.stdout.strip().splitlines()[-1])
        return {i: got[i] for i in sub["answer_ids"] if i in got}

    def fetch_one(n):
        fetch((n, caps[n]))
        with lock:
            for k, need in pending.items():
                if n in need:
                    need.discard(n)
                    if not need:
                        futs[k] = solver_pool.submit(run_set, k)

    try:
        with ThreadPoolExecutor(max_workers=max(1, int(_opt("HCTF_PIPELINE_DL", "3")))) as ex:
            for _ in ex.map(fetch_one, order):
                pass
        out["_t_downloaded"] = time.time()
        for k, f in futs.items():
            try:
                results[k] = f.result()
            except Exception as e:  # noqa: BLE001 - any set failure -> whole-solver fallback
                out["pipeline_fallback"] = f"{k}: {str(e)[:160]}"
                return None
    finally:
        solver_pool.shutdown(wait=False)
        for k in sets:
            _sh.rmtree(adir / f".set-{k}", ignore_errors=True)   # hardlinks: never pulled back twice
    answers = {}
    for k in sets:
        answers.update(results.get(k) or {})
    if any(i not in answers for i in ids):
        out["pipeline_fallback"] = f"{sum(i not in answers for i in ids)} id(s) unanswered by the per-set runs"
        return None
    out["pipelined"] = {"sets": len(sets), "dl_parallel": int(_opt("HCTF_PIPELINE_DL", "3")),
                        "first_set_solve_at": round(min(t_first) - t_started, 2) if t_first else None}
    return SimpleNamespace(stdout=json.dumps(answers), stderr="", returncode=0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cid")
    ap.add_argument("solver_dir")           # relative to HW, e.g. challenges/day02/warmups-half-a-turn/solver
    ap.add_argument("--op", default="start", choices=["start", "retry", "untimed", "resume"])
    ap.add_argument("--min-left", type=float, default=None,
                    help="re-roll a RESUMED attempt with less clock than this (s); default max(3, window/2)")
    a = ap.parse_args()
    print(json.dumps(run_attempt(a.cid, a.solver_dir, op=a.op, min_left=a.min_left)))


def run_attempt(cid, solver_dir, op="start", min_left=None, opts=None, on_event=None):
    """One timed attempt (start -> download -> solve -> submit) -> the result dict main() prints. In-process entry
    for hb_daemon: `opts` are this attempt's knobs (HCTF_EXPECT_BYTES, HCTF_RUN_FOR_TIME, ...), the solver runs via
    SOLVER when set. Thread-safe: per-attempt state lives in _CTX. `on_event`: see _event."""
    from types import SimpleNamespace
    _CTX.lane, _CTX.opts, _CTX.on_event = _lane_from_solver_dir(solver_dir), dict(opts or {}), on_event
    _CTX.solver_dir = solver_dir
    _CTX.t0 = time.time()
    spawn = {}
    try:   # D24 #1: the local route's spawn stamp (workers.run_timed) -> interpreter start + imports
        ts = float(os.environ.get("HCTF_T_SPAWN") or 0)
        if ts and 0 <= _CTX.t0 - ts < 120:
            spawn["main"] = round(_CTX.t0 - ts, 2)
    except ValueError:
        pass
    lock = _mode_lock(cid)
    spawn["lock"] = round(time.time() - _CTX.t0, 2)
    _CTX.spawn = spawn
    try:
        if lock is None:
            return {"cid": cid, "result": "exec_error", "detail": "another runner holds this mode (mode lock)",
                    "submitted": {}, **_read_progress(cid)}
        return _attempt(SimpleNamespace(cid=cid, solver_dir=solver_dir, op=op, min_left=min_left))
    finally:
        if lock is not None:
            lock.close()
        _CTX.lane = _CTX.opts = _CTX.on_event = _CTX.solver_dir = _CTX.t0 = _CTX.spawn = None


def _mode_lock(cid):
    """One runner per mode at a time (flock on .run/tmp-timed/<slug>.lock): every runner of a mode shares (and wipes)
    .run/tmp-timed/<slug>/ -- D16, a manual resume and the orchestrator's retry deleted each other's bytes mid-attempt.
    A second runner waits for the first (it would only work the same live attempt); None = still held at our deadline."""
    import fcntl
    p = _progress_path(cid).with_suffix("").with_suffix(".lock")
    p.parent.mkdir(parents=True, exist_ok=True)
    f = open(p, "w")
    rl = _runner_left()
    until = time.time() + (rl if rl is not None else 600)
    while True:
        try:
            fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
            return f
        except BlockingIOError:
            if time.time() >= until:
                f.close()
                return None
            time.sleep(0.5)


def _read_progress(cid):
    try:
        d = json.loads(_progress_path(cid).read_text())
        d.pop("result", None)
        return d
    except (OSError, ValueError):
        return {}


def _body_attempt_id(body):
    """cli.attempt_id's rule (this module also runs on Homebase without hctf.cli)."""
    for k in ("attempt_id", "attempt", "attemptId"):
        v = (body or {}).get(k)
        if isinstance(v, dict):
            v = v.get("id")
        if v:
            return str(v)
    return None


def _prestarted_body(cid, why=None):
    """The orchestrator's pre-start of THIS mode (start body + downloaded bytes + .prefetch.json in the runner's dir),
    used ONCE instead of a second `start` call when it is fresh, untimed and complete. D22: after a 4-25 s pre-start the
    runner still re-called `start` to reconnect -- another 2-7 s per mode at the drop, on the critical path. A clocked or
    stale one (HCTF_PRESTART_TRUST_S, 300) falls back to the normal start; HCTF_PRESTART_REUSE=0 disables.
    `why` (a list): the reason a pre-start that EXISTS was not used is appended (D24 #1 instrumentation)."""
    if _opt("HCTF_PRESTART_REUSE", "1") != "1":
        return None
    adir = HW / ".run" / "tmp-timed" / re.sub(r"[^A-Za-z0-9]+", "_", cid)
    try:
        if (adir / ".prefetch.reused").exists():
            return None
        pj = json.loads((adir / ".prefetch.json").read_text())
        body = json.loads((adir / "contract.json").read_text())
    except (OSError, ValueError):
        return None
    att = _body_attempt_id(body)
    if (not isinstance(body, dict) or body.get("deadline") or body.get("error") or not body.get("answer_ids")
            or not att or str(pj.get("attempt_id")) != att or not pj.get("files")
            or time.time() - float(pj.get("t") or 0) > float(_opt("HCTF_PRESTART_TRUST_S", "300"))
            or not all((adir / n).exists() for n in pj["files"])):
        if why is not None:
            why.append("clocked" if isinstance(body, dict) and body.get("deadline") else
                       "stale" if time.time() - float(pj.get("t") or 0) > float(_opt("HCTF_PRESTART_TRUST_S", "300"))
                       else "mismatch")
        return None
    try:
        (adir / ".prefetch.reused").write_text(att)
    except OSError:
        return None
    return body


def _attempt(a):
    tw = time.time()
    pool = _pool()              # open + TLS-handshake the keep-alive connections BEFORE the clock starts
    if hasattr(pool, "fresh"):
        pool.fresh()            # (hb_daemon: the pool idled since the last attempt -> replace stale sockets)
    t0 = time.time()
    out = {"cid": a.cid, "submitted": {}, "pool_warm": round(t0 - tw, 2)}
    if _CTX.spawn is not None and _opt("HCTF_TIMING_MARKS", "1") == "1":
        out["spawn"] = dict(_CTX.spawn, pool=out["pool_warm"])   # D24 #1: where the runner's pre-start seconds went

    untimed = a.op == "untimed"
    # resume = reconnect (`start`) to the LIVE attempt the caller knows holds banked ids: never re-roll it short-clock
    # (a retry advances to a fresh variant and DISCARDS every banked id -- reviewer rule; GM guidance: "start reconnects
    # to the same attempt; only retry spends one of the unique_attempts_remaining"). Expired/finished still re-roll.
    resume = a.op == "resume"
    if resume:
        out["resumed_banked"] = True
    miss = []
    body = _prestarted_body(a.cid, miss) if a.op == "start" and not untimed and not resume else None
    if miss and _opt("HCTF_TIMING_MARKS", "1") == "1":
        out["prestart_miss"] = miss[0]   # a pre-start existed but could not be used (clocked / stale / mismatch)
    if body is not None:
        out["prestart_reused"] = True    # D22 post-mortem #13: no second `start` after the orchestrator's pre-start
    else:
        body = (_post_untimed(a.cid) if untimed else
                _post_start({"op": "start" if resume else a.op, "challenge": a.cid}))
    if (a.op == "retry" and body.get("error")
            and not any(x in str(body.get("error")) for x in ("rate_limited", "exhausted", *EXHAUSTED))):
        body = _post_start({"op": "start", "challenge": a.cid})  # retry refused (no finished attempt to re-roll): plain start
    body = _await_live(a.cid, body, out)   # web: `preparing` / `cleaned` -> wait for the live target (no clock yet)
    # fresh clock if this attempt is already expired / past its deadline
    left = _deadline_left(body)
    # ...and a fresh clock when `start` hands back a FINISHED attempt (result CORRECT/INCORRECT, no deadline, no
    # answer_ids): the GM resumes the latest attempt, so re-attempting a passed mode (Mastery prerequisite re-pass,
    # scout, replay) got 'no_answer_ids' forever -- replay d7fix2 burned ~20 generalize workers on it.
    finished = not body.get("error") and not body.get("answer_ids")
    # replay_gm stand-in: re-runs passed modes (d7fix2). HCTF_REPLAY_REROLL=0 keeps the real GM's rule against a local
    # stand-in (the fault-injection suite serves timed modes locally with the real semantics).
    replay = any(h in GM for h in ("127.0.0.1", "localhost")) and _opt("HCTF_REPLAY_REROLL", "1") == "1"
    if (finished and a.op in ("start", "resume") and str(body.get("result", "")).upper() == "CORRECT"
            and not replay and _opt("HCTF_REROLL_CORRECT", "0") != "1"):
        # The mode's latest attempt is already CORRECT: report the pass, never re-roll it. D16 script Mastery: a retry
        # after an out-of-band pass re-rolled e50cf4a5 into a fresh 5475-question attempt (the GM's latest status then
        # read not-correct). Callers that WANT a new variant (scout, hof) say op=retry.
        out.update(result="correct", already_passed=True, attempt_id=body.get("attempt_id"),
                   deadline=body.get("deadline"), no_clock=not body.get("deadline"))
        _write_progress(a.cid, out)
        return out
    if not untimed and not body.get("_web_wait") and (body.get("result") == "expired" or finished
                                                       or (left is not None and left <= 0.5)):
        body = _await_live(a.cid, _post_start({"op": "retry", "challenge": a.cid}), out)
        left = _deadline_left(body)
    # ...and never run on a RESUMED attempt that is nearly out of clock (Day 8 script Mastery: `start` resumed an
    # attempt with ~3.5 s left -> 2 s solver budget -> misread as "solver too slow" -> 143 s generalize). Wait it out
    # (still before OUR clock) and re-roll. A fresh attempt (age ~0) has left == window and never trips this.
    # D18 warmups TT: a retry can never succeed once the GM says unique_attempts_remaining == 0 -- the re-roll slept out a
    # 4 s tail (a ~1 s solve fit) and got retry_variants_unavailable. Run on whatever clock is left instead.
    for _ in range(2):
        win, age = _window(body), _age(body)
        need = a.min_left if a.min_left is not None else max(3.0, (win or 0) / 2)
        if (resume or body.get("error") or left is None or left >= need or (age is not None and age < 2.0)
                or body.get("unique_attempts_remaining") == 0):
            break
        out["rerolled_short"] = round(left, 2)
        time.sleep(max(0.0, left) + 0.6)
        body = _post_start({"op": "retry", "challenge": a.cid})
        left = _deadline_left(body)
    out["deadline"] = body.get("deadline")
    if body.get("answer_ids") and not body.get("deadline"):
        out["no_clock"] = True     # a live attempt without a clock (regular pool / resumed untimed): resumable as-is
    out["attempt_id"] = body.get("attempt_id")
    out["window"] = _window(body)
    if body.get("attempt_id") and body.get("answer_ids"):
        _write_progress(a.cid, out, "started")
    ids = body.get("answer_ids") or []
    qmap = _paired(ids, body.get("questions") or [])
    if body.get("unique_attempts_remaining") is not None:
        out["attempts_remaining"] = body.get("unique_attempts_remaining")
    for k in ("run_for_time", "hall_of_fame_eligible", "ranked_attempts_remaining", "variant_fresh", "practice"):
        if body.get(k) is not None:
            out[k] = body.get(k)          # which pool this attempt came from (Day 8 dual-pool routes)
    if untimed:
        out["untimed"] = True
    if _WT is not None and _WT.is_live_body(body) and not _WT.ready(body) and not body.get("error") and not (
            str(body.get("result", "")).upper() == "CORRECT"):
        # web target never came up (still preparing / dead after the revives): a start refusal, never the solver's
        # fault -> the orchestrator backs off and retries (error:start), no generalize
        out["result"] = f"web_target_{str(body.get('result') or 'unavailable').lower()}"
        out["detail"] = {k: v for k, v in body.items() if k not in ("questions", "prompt", "guidance")}
        out["start_refused"] = True
        return out
    if body.get("error") or not ids:
        out["result"] = body.get("error") or "no_answer_ids"
        out["detail"] = body
        if _exhausted(body.get("error")):
            out["exhausted"] = True       # no fresh variant left: the caller switches to an untimed attempt
        # The GM refused to hand out an attempt: nothing ran, the solver is not implicated (never generalize on it).
        out["start_refused"] = True
        if "rate_limited" in str(body.get("error")):
            out["gm_rate_limited"] = True
        return out
    t_started = time.time()
    out["gm_remaining"] = body["remaining"] if isinstance(body.get("remaining"), int) else len(ids)

    # download artifacts into a temp dir next to the GM
    adir = HW / ".run" / "tmp-timed" / re.sub(r"[^A-Za-z0-9]+", "_", a.cid)
    adir.mkdir(parents=True, exist_ok=True)
    prefetched = False
    try:   # the orchestrator pre-started THIS attempt at the single's CORRECT and already downloaded its bytes
        pj = json.loads((adir / ".prefetch.json").read_text())
        prefetched = (pj.get("attempt_id") == body.get("attempt_id") and bool(pj.get("files"))
                      and all((adir / n).exists() for n in pj["files"]))
    except (OSError, ValueError, AttributeError):
        pass
    if prefetched:
        out["prefetched"] = True
    else:
        for f in adir.glob("*"):
            if f.is_file():
                f.unlink()
    # Download every per-set delivery CONCURRENTLY: over the public GM each call is ~0.2s RTT, so a
    # many-file Mastery bundle must fetch in parallel or the ~6-10s window expires before the solver runs.
    plan = _plan(body)
    contract = adir / "contract.json"
    contract.write_text(json.dumps(body))
    env = _solver_env()
    solve = HW / a.solver_dir / "solve.py"

    def _fetch(item):
        name, cap = item
        (adir / name).write_bytes(_get_bytes(cap))

    # Large multi-set Mastery bundle (D9 binary: 5 x 31 MB = 6.6 s of download, then a 5.4 s solve): fetch the sets a
    # few at a time and solve each one the moment its delivery lands, so most of the solve hides behind the downloads.
    min_mb = float(_opt("HCTF_PIPELINE_MIN_MB", "20"))
    if plan and _sequential_solver(solve):
        min_mb = min(min_mb, float(_opt("HCTF_PIPELINE_SEQ_MIN_MB", str(PIPELINE_SEQ_MIN_MB))))
    sets = (_set_plan(body, plan, ids) if _opt("HCTF_PIPELINE_SETS", "1") == "1" and plan and not prefetched
            and _total_bytes(body) >= min_mb * 1e6 else None)
    piped = None
    try:
        if sets:
            piped = _pipelined(sets, plan, body, ids, adir, solve, env, _fetch, left, out, t_started)
        elif plan and not prefetched:
            dlw = int(_opt("HCTF_DL_PARALLEL", "48"))
            if ratebucket:
                dlw = ratebucket.wave_width(dlw)   # narrow the download burst only while under run-wide 429 pressure
            with ThreadPoolExecutor(max_workers=min(dlw, len(plan))) as ex:
                for _ in ex.map(_fetch, plan):  # propagate any download exception
                    pass
    except GMError as e:
        # The RUNNER failed, not the solver: never hand the solver an error body as evidence. exec_error is
        # retried by the orchestrator (no generalize); gm_rate_limited makes it back off first.
        out["result"] = "exec_error"
        out["gm_rate_limited"] = e.rate_limited
        out["detail"] = f"download failed: {e}"
        return out
    t_downloaded = out.pop("_t_downloaded", None) or time.time()

    # run the solver (already correct, offline-built); lib on PYTHONPATH
    budget = _solve_budget(body, left)
    try:
        if piped is not None:
            r = piped                       # every set answered by its own early run
        else:
            r = _run_solver(solve, contract, adir, budget, env)
    except subprocess.TimeoutExpired as e:
        # Emit a real result (attempt_id + saved contract/bytes) instead of crashing: the caller then pulls THIS
        # variant for the speed generalize (a crash left a stale download dir that was mistaken for this attempt).
        win = out.get("window")
        fair = win is None or budget >= 0.8 * (win - (t_downloaded - t_started) - 1.5)
        out["phases"] = {"start": round(t_started - t0, 2), "download": round(t_downloaded - t_started, 2),
                         "solve": round(budget, 2)}
        if fair:
            out["result"] = "exec_error"
            out["solver_too_slow"] = True
            out["detail"] = f"solve.py timed out after {e.timeout:.1f}s (in-window solver budget)"
        else:
            # The solver never had the window (the clock was mostly gone before it ran): a timing loss, not a slow
            # solver -- the orchestrator retries on a fresh clock instead of generalizing for speed.
            out["result"] = "expired"
            out["clock_short"] = True
            out["detail"] = f"solver budget only {budget:.1f}s of a {win}s window (clock spent before the solve)"
        return _emit(out, adir)
    try:
        answers = {k: _normalize(_answer_str(v), qmap.get(k, {}))
                   for k, v in json.loads(r.stdout.strip().splitlines()[-1]).items()}
    except Exception:
        out["result"] = "solver_error"
        out["detail"] = r.stderr[-800:]
        return _emit(out, adir)

    bank = _bank_load(a.cid, out.get("attempt_id"))
    if bank:
        # Reconnected to an attempt that already banked GM-accepted values (localization / fixes cut short): reuse them
        # verbatim for these exact answer ids instead of re-deriving -- the solver still answers wrong where the GM had
        # already accepted a correction (D15 script Mastery: 4108 accepted + 16 fixes, then a 3-min generalize).
        over = {k: bank[k] for k in ids if k in bank and answers.get(k) != bank[k]}
        answers.update(over)
        out["bank_overlay"] = len(over)
    missing = [i for i in ids if i not in answers]
    out["submitted"] = answers
    t_solved = time.time()
    out["phases"] = {"start": round(t_started - t0, 2), "download": round(t_downloaded - t_started, 2),
                     "solve": round(t_solved - t_downloaded, 2)}
    if missing:
        out["result"] = "solver_incomplete"
        out["missing"] = missing
        part = {k: answers[k] for k in ids if k in answers and answers[k] != ""}
        # a reconnect to the same open attempt: values the GM already REJECTED here are not judged again (D23 script TT:
        # the unchanged solver's 171 known-wrong answers made the retry re-bisect 593 fields for 99 s)
        known_bad = _bank_rejected(a.cid, out.get("attempt_id"))
        if known_bad:
            drop = [k for k, v in part.items() if v in known_bad.get(k, ())]
            for k in drop:
                part.pop(k)
            if drop:
                out["partial_skipped_rejected"] = len(drop)
        else:
            drop = []
        _event("solved", out, result="solver_incomplete")   # before the partial submit + localization
        if part and _opt("HCTF_PARTIAL_SUBMIT", "1") == "1":
            # Submit what the solver DID answer: the GM saves correct partial progress (banks whole Mastery sets) and
            # its verdict tells the generalize worker which answered fields to leave alone. An escalated variant (D7
            # metadata TT 1 -> 11 fields) used to burn the whole window with nothing submitted.
            _partial_submit(a.cid, part, body, out, setkey=_setkey)
            if ((out.get("partial_submit") or {}).get("result") in ("correct", "accepted")
                    and _opt("HCTF_INWINDOW_FILL", "1") == "1"):
                _fill_missing(a.cid, [k for k in ids if k not in part], qmap, adir, body, out)
            out["phases"]["submit"] = round(time.time() - t_solved, 2)
            out["elapsed"] = round(time.time() - t0, 2)
            out["in_window"] = round(time.time() - t_started, 2)
        if drop:
            # still WRONG for the orchestrator (generalize / live answer): judged on an earlier run of this attempt
            have = {x[0] for x in out.get("partial_wrong") or [] if isinstance(x, (list, tuple))}
            out["partial_wrong"] = list(out.get("partial_wrong") or []) + [
                [k, answers[k]] for k in drop if k not in have]
        return _emit(out, adir)

    # FAST PATH: submit EVERY answer in one request. A public-GM submit round-trip is ~0.2-several s, so N
    # sequential per-set POSTs can blow a ~6-10s Mastery window (set 1 banks, set 2 expires). One POST covering
    # all sets fits even a tight window when the solver is complete+correct.
    groups = {}
    for aid, v in answers.items():
        groups.setdefault(_setkey(aid), {})[aid] = v
    if len(groups) > 1 and _opt("HCTF_PARALLEL_SET_SUBMIT", "0") == "1":  # measured: no faster (GM serial)
        # One POST per set, CONCURRENTLY over the pre-opened pool: a 798-answer single POST took 2.3-4.7 s from WSL
        # (no Homebase), the bulk of a 7 s Mastery window; per-set POSTs in parallel cost ~one smaller round-trip.
        with ThreadPoolExecutor(max_workers=len(groups)) as ex:
            ress = dict(zip(groups, ex.map(lambda k: _submit(a.cid, groups[k], body),
                                           list(groups))))
        out["phases"]["submit"] = round(time.time() - t_solved, 2)
        per_set = {k: {"result": str(r.get("result", "")).lower(), "remaining": r.get("remaining")} for k, r in ress.items()}
        out["per_set"], out["submit_mode"] = per_set, "parallel_sets"
        _write_progress(a.cid, out, "submitted")
        if all(v["result"] in ("correct", "accepted") for v in per_set.values()):
            out["result"] = "correct"
            out["verified"] = dict(answers)
            out["novel_labels"] = _novel(answers, _vocab())
        else:
            out["result"] = ("expired" if any(v["result"] == "expired" for v in per_set.values()) else
                             "incorrect" if any(v["result"] == "incorrect" for v in per_set.values()) else "unjudged")
            out["bad_sets"] = [k for k, v in per_set.items() if v["result"] == "incorrect"]
            if out["result"] == "incorrect":
                _event("per_set", out, slim=True, per_set=per_set, bad_sets=out["bad_sets"])   # D25 C4
                _localize(a.cid, answers, groups, per_set, body, out)
                _resubmit_fixed(a.cid, answers, body, out)
        out["elapsed"] = round(time.time() - t0, 2)
        out["in_window"] = round(time.time() - t_started, 2)
        return _emit(out, adir)
    full = None
    for send in range(2):
        try:
            full = _submit(a.cid, answers, body, out)
            break
        except OSError as e:   # socket.timeout included: the GM didn't answer before the clock (+grace) ran out
            left_now = _deadline_left(body)
            # A connection the server dropped WITHOUT answering (RemoteDisconnected / reset / broken pipe -- all
            # ConnectionError) never got judged: resend ONCE on a fresh socket while the clock allows. A timeout is
            # never resent (the GM may still be processing it -- no double POST).
            transport = isinstance(e, ConnectionError)
            if send == 0 and transport and (left_now is None or left_now > 1.0):
                out["submit_resent"] = repr(e)
                continue
            out["phases"]["submit"] = round(time.time() - t_solved, 2)
            out["result"] = "expired"
            if transport:
                out["submit_transport_error"] = True
            out["detail"] = (f"submit got no GM answer within the window ({e!r}); "
                             f"{'resent once' if out.get('submit_resent') else 'not resent'}")
            out["elapsed"] = round(time.time() - t0, 2)
            out["in_window"] = round(time.time() - t_started, 2)
            return _emit(out, adir)
    out["phases"]["submit"] = round(time.time() - t_solved, 2)
    fk = str(full.get("result", "")).lower()
    out["full_result"] = fk
    if fk in ("correct", "accepted") and not full.get("remaining"):
        out["result"] = "correct"
        out["verified"] = dict(answers)
        out["novel_labels"] = _novel(answers, _vocab())
        out["elapsed"] = round(time.time() - t0, 2)
        out["in_window"] = round(time.time() - t_started, 2)  # time that actually counts against the clock
        return _emit(out, adir)

    # Not fully correct: break down per set to learn which set failed (clock permitting), so the offline
    # generalize worker gets granular feedback on the next cycle.
    if fk == "incorrect":
        _event("solved", out, result="incorrect")           # before the per-set breakdown + localization
    # An UNJUDGED full submit (still rate_limited / non-JSON after the resends) never becomes "incorrect": the per-set
    # breakdown below judges what it can; sets the GM never judged stay unjudged (no localize, no wrong fields).
    per_set, final = {}, fk if fk in VERDICTS else "unjudged"

    def _set_submit(grp):
        try:
            return _submit(a.cid, grp, body, out)
        except OSError as e:    # no answer before the clock (+grace): never judged -- not a wrong set
            return {"error": f"unjudged_timeout {e!r}"[:120]}
    pre = None
    if len(groups) > 1 and _deadline_left(body) is None and _opt("HCTF_PARALLEL_SET_BREAKDOWN", "1") == "1":
        # no clock: judge every set at once (rehearsal fair D16 script Mastery: 5 x 1095-answer resubmits one by one, ~38 s;
        # the GM judges concurrent submits -- 12 in 3.3 s vs 1.9 s for one)
        with ThreadPoolExecutor(max_workers=len(groups)) as ex:
            pre = dict(zip(groups, ex.map(_set_submit, groups.values())))
        out["breakdown"] = "parallel"
    for key, grp in groups.items():
        res = pre[key] if pre is not None else _set_submit(grp)
        rk = str(res.get("result", "")).lower() if not _unjudged(res) else "unjudged"
        per_set[key] = {"result": rk, "remaining": res.get("remaining")}
        if rk == "expired":
            final = "expired"
            break
        if rk == "incorrect":
            final = "incorrect"
        elif rk == "unjudged" and final != "incorrect":
            final = "unjudged"
    out["result"] = "correct" if all(v["result"] in ("correct", "accepted") for v in per_set.values()) and per_set else final
    out["per_set"] = per_set
    _write_progress(a.cid, out, "submitted")
    out["bad_sets"] = [k for k, v in per_set.items() if v["result"] == "incorrect"]
    if final == "incorrect":
        # D25 C4: the first per-set verdicts -> the orchestrator (the live answer can start as each set is localized)
        _event("per_set", out, slim=True, per_set=per_set, bad_sets=out["bad_sets"])
        _localize(a.cid, answers, groups, {k: v for k, v in per_set.items() if v["result"] != "unjudged"}, body, out)
        _resubmit_fixed(a.cid, answers, body, out)
    out["elapsed"] = round(time.time() - t0, 2)
    out["in_window"] = round(time.time() - t_started, 2)  # excludes the pre-clock start/retry overhead
    return _emit(out, adir)


def _pair_index(ids, qs):
    """D24 #2: lookup(answer_id) -> question via an exact-id index + the longest boundary suffix, or None when the index
    can't promise the scan's answer (mirror of hctf.solvers._pair_index -- this file runs standalone on Homebase)."""
    if not isinstance(ids, list) or not isinstance(qs, list):
        return None
    exact = {}
    for q in qs:
        if not isinstance(q, dict):
            return None
        qid = q.get("id")
        if qid is None:
            continue
        if not isinstance(qid, str) or "\n" in qid:
            return None
        exact.setdefault(qid, q)
    if any(not isinstance(a, str) or "\n" in a for a in ids):
        return None

    def lookup(aid):
        q = exact.get(aid)
        if q is None:
            for j, c in enumerate(aid):
                if c in "._-" and j + 1 < len(aid):
                    q = exact.get(aid[j + 1:])
                    if q is not None:
                        break
        return q
    return lookup


def _paired(ids, qs):
    """{answer_id: question}: exact question id, else the longest question id the answer id ends with, else by position
    (stdlib mirror of hctf.solvers.paired_questions -- this file runs standalone on Homebase). The per-id scan of every
    question took 17.8 s of a 12,480-id script Mastery's start phase: indexed now (HCTF_PAIR_INDEX=0: the scan)."""
    look = _pair_index(ids, qs) if _opt("HCTF_PAIR_INDEX", "1") != "0" else None
    out = {}
    for i, aid in enumerate(ids):
        if look is not None:
            q = look(aid)
        else:
            q = next((q for q in qs if q.get("id") == aid), None)
            if q is None:
                sufs = [q for q in qs if q.get("id") and re.search(rf"(^|[._-]){re.escape(q['id'])}$", aid)]
                q = max(sufs, key=lambda q: len(q["id"]), default=None)
        if q is None and i < len(qs):
            q = qs[i]
        out[aid] = q or {}
    return out


def _solve_budget(body, left_at_start):
    """Seconds solve.py may run: the clock's remainder NOW (after the downloads) - 1.5 s for the submit, min 2 s.
    Measured at start it let the solver run past the deadline by the whole download time."""
    left = _deadline_left(body)
    if left is None:
        if body.get("deadline") is None and (body.get("practice") or body.get("run_for_time") is False):
            # An untimed regular / practice attempt has NO clock; this cap only bounds a slow/hung solver. Scale it with
            # the contract size: a large Mastery (many sets/fields) legitimately needs longer than a flat 60 s, and the
            # solver now emits partials at the deadline (lib.solverrt.arm_deadline), so a generous cap just lets a slow-
            # but-correct solver finish fully instead of handing a partial to in-attempt localize. D16: a 5475-id script
            # Mastery was guillotined at 60 s. Flat behaviour restored by HCTF_UNTIMED_BUDGET_PER_FIELD=0.
            base = float(_opt("HCTF_UNTIMED_BUDGET", "60"))
            n = len(body.get("answer_ids") or body.get("questions") or [])
            per = float(_opt("HCTF_UNTIMED_BUDGET_PER_FIELD", "0.05"))
            cap = float(_opt("HCTF_UNTIMED_BUDGET_MAX", "300"))
            return max(base, min(cap, base + n * per))
        left = left_at_start if left_at_start is not None else 30
    return max(2, left - 1.5)


def _setkey(aid):
    m = re.match(r"(set|slot)[._-]?\d+", aid)
    return m.group(0) if m else "_"


_SLUG_TAIL = re.compile(r"(?<![A-Za-z0-9])([a-z]+-[a-z]+-[a-z]+-\d{2})\s*$")


def _fill_guesses(q, adir):
    """Ranked slug guesses for a warmups field the solver left empty: lib.decode.decode_candidates on the field's own
    numbered blob (positional reading first, then the joint free-codec assignments). [] for anything else."""
    try:
        if str(HW) not in sys.path:
            sys.path.insert(0, str(HW))
        from lib import decode, slug
        from lib.common import find_artifact
        if not slug.is_slug_question(q) or not q.get("artifact"):
            return []
        text = find_artifact(adir, str(q["artifact"])).decode("utf-8", "replace")
        out = []
        for cand in decode.decode_candidates(text, limit=3):
            m = _SLUG_TAIL.search(cand)
            if m and m.group(1) not in out:
                out.append(m.group(1))
        return out
    except Exception:  # noqa: BLE001 - best effort; never break the clock path
        return []


def _fill_missing(cid, empty, qmap, adir, body, out, tries=2):
    """In-window completion after an ACCEPTED partial submit: submit a guess for every field the solver left empty, at
    most `tries` rounds, while the clock allows. D14 warmups Mastery: 67/68 accepted with ~26 s left and set22 empty;
    lib's ranked decodings held the GM slug. Correct when the GM then reports nothing remaining; otherwise the attempt
    stays solver_incomplete (the generalize runs on this variant as before)."""
    guesses = {aid: _fill_guesses(qmap.get(aid, {}), adir) for aid in empty}
    if not empty or not all(guesses.values()):
        return
    tried = []
    for i in range(tries):
        left = _deadline_left(body)
        if (left is not None and left < 1.5) or (i and all(len(g) <= i for g in guesses.values())):
            break
        batch = {aid: g[min(i, len(g) - 1)] for aid, g in guesses.items()}
        try:
            res = _submit(cid, batch, body, out)
        except OSError as e:
            tried.append({"answers": batch, "result": "no_answer", "detail": repr(e)})
            break
        rk = str(res.get("result", "")).lower()
        tried.append({"answers": batch, "result": rk, "remaining": res.get("remaining")})
        if rk in ("correct", "accepted") and not res.get("remaining"):
            out["result"] = "correct"
            out["verified"] = dict(out.get("verified") or {}, **batch)
            out["submitted"] = dict(out.get("submitted") or {}, **batch)
            out.pop("missing", None)
            break
        if rk != "incorrect":
            break
    out["inwindow_fill"] = tried


def _partial_submit(cid, part, body, out, setkey=_setkey):
    """One bounded submit of the answered subset of an incomplete solve (never resent). Accepted -> those fields are
    GM-verified. Rejected -> localize the wrong ones (window permitting). Results go under partial_* keys so the
    orchestrator still treats the attempt as solver_incomplete and generalizes on this exact variant."""
    try:
        res = _submit(cid, part, body, out)
    except OSError as e:
        out["partial_submit"] = {"result": "no_answer", "detail": repr(e)}
        return
    rk = str(res.get("result", "")).lower() if not _unjudged(res) else "unjudged"
    out["partial_submit"] = {"result": rk, "remaining": res.get("remaining"), "n": len(part)}
    if rk in ("correct", "accepted"):
        out["verified"] = dict(part)
        out["novel_labels"] = _novel(part, _vocab())
        return
    if rk != "incorrect":
        return
    groups = {}
    for aid, v in part.items():
        groups.setdefault(setkey(aid), {})[aid] = v
    # "assumed": only the WHOLE partial submit was judged incorrect, not each set (no one-field-set shortcut)
    _localize(cid, part, groups, {k: {"result": "incorrect", "assumed": True} for k in groups}, body, out)
    out["partial_wrong"] = out.pop("wrong", [])
    out["partial_fixed"] = out.pop("fixed", {})
    out["partial_localize_complete"] = out.pop("localize_complete", False)


def _emit(out, adir):
    """Print the one-line result and keep a copy next to the attempt's bytes (contract.json + downloads), so the
    caller can turn the variant into a regression case with the GM-verified answers."""
    if out.get("cid"):
        _write_progress(out["cid"], out, "done")
    try:
        (adir / "result.json").write_text(json.dumps(out))
    except OSError:
        pass
    _bank_save(out)
    return out


def _bank_path(cid):
    return HW / ".run" / "timed-bank" / (re.sub(r"[^A-Za-z0-9]+", "_", cid) + ".json")


def _bank_load(cid, attempt_id):
    """-> {answer_id: GM-accepted value} banked on THIS attempt by an earlier run that reconnected to it, else {}."""
    if not attempt_id or _opt("HCTF_BANK_OVERLAY", "1") != "1":
        return {}
    try:
        b = json.loads(_bank_path(cid).read_text())
    except (OSError, ValueError):
        b = {}
    out = dict(b.get("verified") or {}) if b.get("attempt_id") == attempt_id else {}
    try:   # values accepted through outside submits (the live-answer worker), forwarded by the orchestrator
        ov = json.loads(_opt("HCTF_LIVE_OVERLAY", "") or "{}")
        if ov.get("attempt") == attempt_id:
            out.update(ov.get("answers") or {})
    except (ValueError, AttributeError):
        pass
    return out


def _bank_save(out):
    """Keep what the GM accepted on a still-unpassed attempt (merged across reconnects); drop it once passed."""
    cid, aid = out.get("cid"), out.get("attempt_id")
    if not cid or not aid:
        return
    p = _bank_path(cid)
    try:
        if str(out.get("result", "")).lower() == "correct":
            p.unlink(missing_ok=True)
            return
        ver = {**(out.get("partial_fixed") or {}), **(out.get("verified") or {})}
        rej = {}
        for pair in (out.get("partial_wrong") or []) + (out.get("wrong") or []):
            if isinstance(pair, (list, tuple)) and len(pair) == 2 and pair[1] not in (None, "") and pair[0] not in ver:
                rej.setdefault(pair[0], [])
                if str(pair[1]) not in rej[pair[0]]:
                    rej[pair[0]].append(str(pair[1]))
        if not ver and not rej:
            return
        p.parent.mkdir(parents=True, exist_ok=True)
        old = _bank_load(cid, aid)
        old_rej = _bank_rejected(cid, aid)
        for k, vs in rej.items():
            old_rej[k] = list(dict.fromkeys(old_rej.get(k, []) + vs))
        merged = {**old, **ver}
        tmp = p.with_suffix(".tmp")
        tmp.write_text(json.dumps({"attempt_id": aid, "verified": merged,
                                   "rejected": {k: v for k, v in old_rej.items() if k not in merged}}))
        tmp.replace(p)
    except OSError:
        pass


def _bank_rejected(cid, attempt_id):
    """{answer_id: [values the GM rejected on THIS attempt]} from earlier runs that reconnected to it, else {}."""
    if not attempt_id or _opt("HCTF_BANK_OVERLAY", "1") != "1":
        return {}
    try:
        b = json.loads(_bank_path(cid).read_text())
    except (OSError, ValueError):
        return {}
    return {k: list(v) for k, v in (b.get("rejected") or {}).items()} if b.get("attempt_id") == attempt_id else {}


if __name__ == "__main__":
    main()
