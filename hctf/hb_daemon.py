#!/usr/bin/env python3
"""Homebase timed-attempt daemon: one long-lived process per run, driven over ONE persistent ssh stdio channel.

Per attempt it saves the ssh exec + interpreter start + GM pool warm-up (~0.6-1.0 s before the clock) and, inside the
clock, the solver's interpreter start (warm zygote fork: 15-51 ms vs 150-230 ms) and ~60 ms per GM call (public GM over
HTTPS with the bearer: 170 ms vs 232 ms through the inside proxy). The attempt itself is hb_timed.run_attempt -- every GM
rule stays in hb_timed; only the solver launch (hb_timed.SOLVER -> a zygote, see hb_zygote.py) differs.

Protocol: JSON lines on stdin/stdout.
  first line  {"hello": 1, "gm": "<GM base url>", "token": "<bearer or null>"}   (token kept in memory only: never
              env/argv/disk/log -- the solvers' environment never sees it)
  requests    {"id", "op": "ping" | "warm" | "gm" | "attempt" | "race" | "shutdown", ...}
              warm    {"solver": "<dir rel to ~/hw>"}
              race    {"cid", "solvers": ["<dir rel to ~/hw>", ...], "solve_timeout": s, "attempt_id": "<the client's>"}
                      -> {"attempt_id", "answer_ids", "outs": {solver: [answers, err, secs]}, "start_s", "dl_s",
                      "bytes", "files"}: the in-network reuse race (see _race); NO-BEARER channels only
              attempt {"cid", "solver", "op": "start"|"retry", "min_left", "opts": {HCTF_* knobs},
                       "inline_max": bytes (optional: a failed attempt's files <= this come back as result._inline),
                       "events": true (optional, HCTF_EARLY_GENERALIZE: {"id", "event": "solved", "data", "_inline"}
                       lines before the final response)}
  responses   {"id", "ok": true, ...} / {"id", "ok": false, "error"}; one thread per request (5 chains at once).
Usage (Homebase, cwd ~/hw): python3 hctf/hb_daemon.py --stdio
"""
import json
import os
import subprocess
import sys
import threading
import time
import traceback
import uuid
from pathlib import Path
from types import SimpleNamespace

HW = Path(__file__).resolve().parent.parent
LOG = HW / ".run" / "hb_daemon.log"
_out_lock = threading.Lock()


def log(msg):
    try:
        LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(LOG, "a") as f:
            f.write(time.strftime("%H:%M:%S ") + msg + "\n")
    except OSError:
        pass


def send(obj):
    with _out_lock:
        sys.stdout.write(json.dumps(obj) + "\n")
        sys.stdout.flush()


def _sig(sdir):
    sdir = Path(sdir)
    return tuple(sorted((str(f.relative_to(sdir)), f.stat().st_mtime_ns, f.stat().st_size) for f in sdir.rglob("*")
                        if f.is_file() and "cases" not in f.relative_to(sdir).parts and "__pycache__" not in f.parts))


class Zygote:
    """One hb_zygote.py process for one solver dir; solve() is thread-safe."""

    def __init__(self, sdir):
        self.sdir, self.sig = str(sdir), _sig(sdir)
        self.p = subprocess.Popen([sys.executable, str(HW / "hctf" / "hb_zygote.py"), self.sdir], cwd=str(HW),
                                  stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True,
                                  env=dict(os.environ, PYTHONPATH=str(HW)))
        hello = json.loads(self.p.stdout.readline() or "{}")
        if not hello.get("ready"):
            raise RuntimeError(f"zygote for {sdir} did not start")
        self.warm_ms, self.warm_error = hello.get("warm_ms"), hello.get("error")
        self.lock, self.pending = threading.Lock(), {}
        threading.Thread(target=self._read, daemon=True).start()

    def _read(self):
        for line in self.p.stdout:
            try:
                r = json.loads(line)
            except ValueError:
                continue
            slot = self.pending.pop(r.get("id"), None)
            if slot:
                slot[1].update(r)
                slot[0].set()
        for ev, res in list(self.pending.values()):     # zygote died: wake everyone
            res.update(dead=True)
            ev.set()

    def alive(self):
        return self.p.poll() is None

    def solve(self, args, env, timeout):
        rid, ev, res = uuid.uuid4().hex, threading.Event(), {}
        self.pending[rid] = (ev, res)
        with self.lock:
            self.p.stdin.write(json.dumps({"id": rid, "args": args, "env": env, "timeout": timeout}) + "\n")
            self.p.stdin.flush()
        ev.wait(timeout + 10)
        if res.get("dead") or not res:
            raise RuntimeError("zygote died mid-solve")
        if res.get("timed_out"):
            raise subprocess.TimeoutExpired(["solve.py", *args], timeout, output=res.get("stdout"), stderr=res.get("stderr"))
        return SimpleNamespace(stdout=res.get("stdout", ""), stderr=res.get("stderr", ""), returncode=res.get("rc"))

    def close(self):
        try:
            self.p.stdin.write('{"op": "exit"}\n')
            self.p.stdin.flush()
        except (OSError, ValueError):
            pass


class Zygotes:
    def __init__(self):
        self.lock, self.by_dir = threading.Lock(), {}

    def get(self, sdir):
        sdir = str(Path(sdir).resolve())
        with self.lock:
            z = self.by_dir.get(sdir)
            if z is not None and z.alive() and z.sig == _sig(sdir):
                return z
            if z is not None:
                z.close()                                  # solver changed (generalize) or died: re-warm
            z = self.by_dir[sdir] = Zygote(sdir)
            log(f"zygote {Path(sdir).parent.name}: warm {z.warm_ms} ms{' (' + z.warm_error + ')' if z.warm_error else ''}")
            return z

    def solve(self, solve_path, args, env, timeout):
        """hb_timed.SOLVER: a zygote fork; a cold interpreter if the zygote can't be had."""
        try:
            return self.get(Path(solve_path).parent).solve(args, env, timeout)
        except subprocess.TimeoutExpired:
            raise
        except Exception as e:  # noqa: BLE001 - never lose an attempt to the warm path
            log(f"zygote fallback ({e}); cold solve")
            return sys.modules["hb_timed"].run_group([sys.executable, solve_path, *args], timeout=timeout, env=env)

    def close(self):
        for z in self.by_dir.values():
            z.close()


def _inline_bytes(cid, out, cap, z=False):
    """{file name: base64} of a FAILED attempt's download dir (contract.json + deliveries + result.json) when the
    whole dir is <= cap bytes and holds THIS attempt: the client then skips its post-failure pull (an ssh listing +
    byte-range fetches, or a full rsync: D13 warmups Mastery's 31 KB zip went the rsync way). None otherwise.
    z (client sent inline_z): each value is "z:" + base64(zlib(bytes)) and the cap applies to the COMPRESSED size --
    rehearsal D13 replay: a 607 KB contract.json (+97 KB zip) missed the 256 KB cap and every failed script attempt paid a
    12-13 s scoped pull over the VPN; the contract JSON compresses ~10x."""
    import base64
    import re
    if z:
        import zlib
        r = str(out.get("result", "")).lower()
        failed = r in ("solver_incomplete", "solver_error", "incorrect", "accepted") or (
            r == "exec_error" and out.get("solver_too_slow") and not out.get("clock_short"))
        if not cap or not failed or not out.get("attempt_id"):
            return None
        adir = HW / ".run" / "tmp-timed" / re.sub(r"[^A-Za-z0-9]+", "_", cid)
        try:
            files = [f for f in adir.iterdir() if f.is_file()]
            if json.loads((adir / "contract.json").read_text()).get("attempt_id") != out.get("attempt_id"):
                return None
            packed = {f.name: zlib.compress(f.read_bytes(), 6) for f in files}
            if sum(len(v) for v in packed.values()) > cap:
                return None
            return {k: "z:" + base64.b64encode(v).decode() for k, v in packed.items()}
        except (OSError, ValueError):
            return None
    r = str(out.get("result", "")).lower()
    failed = r in ("solver_incomplete", "solver_error", "incorrect", "accepted") or (
        r == "exec_error" and out.get("solver_too_slow") and not out.get("clock_short"))
    if not cap or not failed or not out.get("attempt_id"):
        return None
    adir = HW / ".run" / "tmp-timed" / re.sub(r"[^A-Za-z0-9]+", "_", cid)
    try:
        files = [f for f in adir.iterdir() if f.is_file()]
        if sum(f.stat().st_size for f in files) > cap:
            return None
        if json.loads((adir / "contract.json").read_text()).get("attempt_id") != out.get("attempt_id"):
            return None
        return {f.name: base64.b64encode(f.read_bytes()).decode() for f in files}
    except (OSError, ValueError):
        return None


GM_OPS = ("start", "submit", "status")


def _gm_call(hb_timed, req):
    """A gm.py-shaped envelope ({http, body, text, elapsed, ...}) for op start|submit|status on hb_timed's pool.
    429/503 load gets the same short backoff as an attempt; a JSON 4xx is a verdict and is returned as such."""
    kind, cid = req.get("kind"), req.get("cid")
    if kind not in GM_OPS or not cid:
        raise ValueError(f"gm op {kind!r} / cid {cid!r} not allowed")
    t0 = time.time()
    if kind == "status":
        from urllib.parse import urlencode
        method, query, body, headers = "GET", "?" + urlencode({"op": "status", "challenge": cid}), None, hb_timed._auth()
    else:
        payload = {"op": kind, "challenge": cid, **({"answers": req.get("answers") or {}} if kind == "submit" else {})}
        method, query, body = "POST", "", json.dumps(payload).encode()
        headers = hb_timed._auth({"Content-Type": "application/json"})
    slept = 0.0
    for wait in (0.5, 1.0, None):
        # submit: fresh socket + hard timeout, NEVER resent (a second POST is a second submission); start/status are
        # idempotent: a kept-alive pooled socket, one resend on a dropped connection
        status, raw = hb_timed._pool().request(method, query, body, headers,
                                               timeout=(req.get("timeout") or 30) if kind == "submit" else None)
        if status in (429, 503) and wait is not None and not hb_timed._refusal(status, raw):
            time.sleep(wait)
            slept += wait
            continue
        break
    try:
        parsed, text = json.loads(raw), None
    except ValueError:
        parsed, text = None, (raw or b"")[:2000].decode("utf-8", "replace")
    if kind == "submit" and isinstance(parsed, dict) and isinstance(parsed.get("accepted_ids"), list):
        # the GM sends the attempt's CUMULATIVE accepted ids (~38 KB on a 1095-field single); the client only intersects
        # them with this request's answers -- 12 parallel probes x 38 KB clogged the one ssh stdio channel
        mine = set(req.get("answers") or {})
        parsed["accepted_ids"] = [a for a in parsed["accepted_ids"] if a in mine]
    return {"http": status, "body": parsed, "text": text, "saved": [], "content_type": "application/json",
            "elapsed": round(time.time() - t0, 3), "retries": int(slept > 0), "slept": slept}


RACE_DIR = HW / ".run" / "tmp-race"
RACE_PARALLEL = 2      # the VM has 2 vCPUs (t3.small): more solver processes only queue


def _race(hb_timed, req):
    """In-network reuse race for a big Single Solve (orchestrate._hb_race, D25: the binary single's 35.7 MB took 68.6 s
    at 0.52 MB/s over the public path at the drop, 1.67 s inside the network). `start` here only RECONNECTS: the client
    sends this after its own start landed (attempt_id) and the GM resumes the open attempt, so two first starts never
    race. Then the deliveries over the VM's own network and the given prior solvers on them (warm zygotes). Answers
    only come back -- no GM submit happens here; the client gates, merges and submits. Refused on a channel that holds
    the bearer: the relay daemons talk to the in-network proxy with no credentials (event guidance: none on Homebase)."""
    import re
    import shutil
    from concurrent.futures import ThreadPoolExecutor
    if hb_timed._token():
        raise ValueError("race runs only on a no-bearer channel (relay daemon)")
    cid, sols = req.get("cid"), [str(x) for x in req.get("solvers") or []]
    if not cid or not sols:
        raise ValueError("race needs cid + solvers")
    timeout = float(req.get("solve_timeout") or 20)
    t0 = time.time()
    body = hb_timed._post_once({"op": "start", "challenge": cid})
    att = hb_timed._body_attempt_id(body) if isinstance(body, dict) else None
    out = {"attempt_id": att, "answer_ids": list((body or {}).get("answer_ids") or []), "outs": {},
           "start_s": round(time.time() - t0, 2)}
    if not att or (body or {}).get("error"):
        out["error"] = f"start: {str((body or {}).get('error') or 'no attempt id')[:200]}"
        return out
    if req.get("attempt_id") and req["attempt_id"] != att:
        out["error"] = f"attempt mismatch: GM resumed {att}, client has {req['attempt_id']}"
        return out
    plan = hb_timed._plan(body)
    safe = re.sub(r"[^A-Za-z0-9]+", "_", cid)
    if RACE_DIR.exists():
        for old in RACE_DIR.iterdir():          # one race dir per challenge, only the latest attempt (VM disk is small)
            if old.name.startswith(safe + "__") and old.name != f"{safe}__{att}":
                shutil.rmtree(old, ignore_errors=True)
    adir = RACE_DIR / f"{safe}__{att}"
    adir.mkdir(parents=True, exist_ok=True)
    (adir / "contract.json").write_text(json.dumps(body))
    t1 = time.time()

    def fetch(item):
        name, cap = item
        dst = adir / name
        if not dst.exists():
            tmp = dst.with_name(dst.name + ".part")
            tmp.write_bytes(hb_timed._get_bytes(cap))
            tmp.replace(dst)
        return dst.stat().st_size
    with ThreadPoolExecutor(max_workers=max(1, min(4, len(plan)))) as ex:
        sizes = list(ex.map(fetch, plan))
    out.update(dl_s=round(time.time() - t1, 2), bytes=sum(sizes), files=len(sizes))
    env = hb_timed._solver_env()
    env.setdefault("HCTF_SOLVER_MAX_PROCS", "2")

    def one(rel):
        solve = HW / rel / "solve.py"
        if not solve.exists():
            return rel, [{}, f"no solver on Homebase at {rel}", 0.0]
        ts = time.time()
        try:
            r = hb_timed._run_solver(solve, adir / "contract.json", adir, timeout, env)
        except Exception as e:  # noqa: BLE001 - one solver's failure is that solver's verdict
            return rel, [{}, f"{type(e).__name__}: {str(e)[:300]}", round(time.time() - ts, 2)]
        dt = round(time.time() - ts, 2)
        if getattr(r, "returncode", 1):
            return rel, [{}, f"exit {r.returncode}: {(r.stderr or '').strip()[-600:]}", dt]
        try:
            got = json.loads((r.stdout or "").strip().splitlines()[-1])
            return rel, [got if isinstance(got, dict) else {}, None if isinstance(got, dict) else "not a JSON object", dt]
        except (IndexError, ValueError):
            return rel, [{}, f"stdout is not JSON: {(r.stdout or '')[-200:]!r}", dt]
    with ThreadPoolExecutor(max_workers=RACE_PARALLEL) as ex:
        out["outs"] = dict(ex.map(one, sols))
    out["race_s"] = round(time.time() - t0, 2)
    return out


def main():
    hello = json.loads(sys.stdin.readline() or "{}")
    if hello.get("gm"):
        os.environ["HUNTRESS_GAME_MASTER_URL"] = hello["gm"]     # hb_timed reads it at import
    sys.path.insert(0, str(HW / "hctf"))
    import hb_timed
    hb_timed._TOKEN = hello.get("token") or None
    if not hb_timed._TOKEN:
        # a no-bearer channel (the relay daemons -> in-network proxy): never hb_timed's env / secrets-file fallback
        hb_timed._token = lambda: None
    zyg = Zygotes()
    hb_timed.SOLVER = zyg.solve
    try:
        hb_timed._pool()                                          # TLS handshakes now, not inside the first clock
    except Exception as e:  # noqa: BLE001
        log(f"pool warm note: {e}")
    log(f"up: gm={hb_timed.GM} bearer={'yes' if hb_timed._TOKEN else 'no'} pid={os.getpid()}")
    send({"id": "hello", "ok": True, "pid": os.getpid(), "gm": hb_timed.GM})

    def handle(req):
        rid, op = req.get("id"), req.get("op")
        try:
            if op == "ping":
                send({"id": rid, "ok": True, "zygotes": len(zyg.by_dir)})
            elif op == "warm":
                z = zyg.get(HW / req["solver"])
                send({"id": rid, "ok": True, "warm_ms": z.warm_ms, "error": z.warm_error})
            elif op == "gm":
                # One GM call on the warm pool (no ssh exec, no interpreter start): the run's Single Solve start /
                # submit. D12: per-call ssh + `python3 gm.py` on the busy VM put a single start out 2-6 s late.
                send({"id": rid, "ok": True, **_gm_call(hb_timed, req)})
            elif op == "race":
                res = _race(hb_timed, req)
                log(f"race {req.get('cid')}: {res.get('error') or 'ok'} {res.get('bytes')} B dl {res.get('dl_s')}s "
                    f"total {res.get('race_s')}s")
                send({"id": rid, "ok": True, "result": res})
            elif op == "attempt":
                t = time.time()
                on_event = None
                if req.get("events"):
                    # HCTF_EARLY_GENERALIZE: mid-attempt events on the same id ({"id", "event", ...}, no "ok") with the
                    # attempt's bytes inline, so the client can hand the variant to a generalize worker before the
                    # in-window localization ends (old clients never ask; old daemons never send)
                    cap = int(req.get("inline_max") or 0)

                    def on_event(ev, rid=rid, cid=req["cid"], cap=cap):
                        msg = {"id": rid, "event": ev.get("event"), "data": ev}
                        inline = _inline_bytes(cid, dict(ev, result="solver_incomplete"), cap, z=bool(req.get("inline_z")))
                        if inline:
                            msg["_inline"] = inline
                        send(msg)
                out = hb_timed.run_attempt(req["cid"], req["solver"], op=req.get("op_mode") or "start",
                                           min_left=req.get("min_left"), opts=req.get("opts"), on_event=on_event)
                out["daemon_s"] = round(time.time() - t, 2)
                log(f"attempt {req['cid']}: {out.get('result')} elapsed={out.get('elapsed')}")
                inline = _inline_bytes(req["cid"], out, int(req.get("inline_max") or 0), z=bool(req.get("inline_z")))   # absent (old client) -> none
                if inline:
                    out["_inline"] = inline
                send({"id": rid, "ok": True, "result": out})
            else:
                send({"id": rid, "ok": False, "error": f"unknown op {op!r}"})
        except Exception as e:  # noqa: BLE001
            log(f"{op} failed: {traceback.format_exc()[-800:]}")
            send({"id": rid, "ok": False, "error": f"{type(e).__name__}: {str(e)[:300]}"})

    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            req = json.loads(line)
        except ValueError:
            continue
        if req.get("op") == "shutdown":
            send({"id": req.get("id"), "ok": True})
            break
        threading.Thread(target=handle, args=(req,), daemon=True).start()
    zyg.close()
    log("down")


if __name__ == "__main__":
    if "--stdio" not in sys.argv:
        sys.exit(__doc__)
    main()
