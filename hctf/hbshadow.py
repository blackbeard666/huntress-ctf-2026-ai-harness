"""Homebase SHADOW workers: a second, independent Single Solve worker on the Homebase VM -- Claude Code on Bedrock
(Opus 4.7 through the VM's instance role), paid from the account's daily Homebase credits (hctf/hbbudget.py) -- racing
the local worker on the lanes that bound the sweep (script/binary singles: 84-235 s vs 25-40 s for the others).

  * the VM mirror is ~/hw/<same relative paths>; the shadow downloads its own artifact copy over the inside GM (a 31 MB
    binary over the ~140 KB/s player VPN would take minutes), so only small state files cross the VPN
  * it submits through the inside GM as the VM's owner = this account, on the SAME Single Solve attempt
  * every poll merges the GM confirmations it got into the local confirmed.json/submissions.jsonl, so the local worker,
    _watch_ready and the stop gate see them
  * once the single is CORRECT, its solver is pulled into .run/shadow-dayNN/<chal>/solver and verified locally exactly
    like the early-handoff snapshot; if the local worker isn't ready yet, the chain ends it and continues from the
    shadow's solver
  * it is ended (process group killed) the moment the chain leaves the Single Solve; its cost goes to the ledger

Off for replays (the VM can only reach the real GM), without Homebase, or when the day's credits can't cover it.
"""
import json
import os
import re
import shlex
import shutil
import threading
import time
from pathlib import Path

from . import cli, hbbudget, paths, remote, solvers, workers

ROOT = paths.ROOT
# OPT-IN (HCTF_HB_SHADOW=1). 2026-10-09: alt ran OUT of Homebase credits ~30 min after power-on, after only ~0.5 VM-h
# + ~$1.4 list of Bedrock test runs -- the credits-per-$ rate is unknown and may be steep. Off until calibrated.
ENABLED = os.environ.get("HCTF_HB_SHADOW", "0") == "1"
LANES = {x.strip() for x in os.environ.get("HCTF_HB_SHADOW_LANES",
                                           "script-analysis,binary-reverse-engineering,binary").split(",") if x.strip()}
MAX_CONCURRENT = int(os.environ.get("HCTF_HB_SHADOW_MAX", "2"))   # 2 vCPU / 3.8 GB VM shared with hb_timed
SHADOW_USD = float(os.environ.get("HCTF_HB_SHADOW_USD", "8"))      # per-shadow --max-budget-usd
MODEL = os.environ.get("HCTF_HB_MODEL", "global.anthropic.claude-opus-4-7")
POLL_S = float(os.environ.get("HCTF_HB_SHADOW_POLL", "5"))
HB_WAIT_S = float(os.environ.get("HCTF_HB_SHADOW_WAIT", "45"))
DEAD_S = float(os.environ.get("HCTF_HB_SHADOW_DEAD", "60"))   # unreachable this long -> give the shadow up
MAX_PUSH = os.environ.get("HCTF_HB_SHADOW_MAX_PUSH", "4m")          # per-file cap for state pushed over the VPN
ART_PUSH = int(os.environ.get("HCTF_HB_SHADOW_ART_PUSH", str(6 << 20)))  # artifacts up to this go over the VPN
HW = workers.HB_WORK
# Bedrock model ids for the aliases Claude Code may pick internally (the role is denied Sonnet 4.6).
BEDROCK_ENV = {
    "CLAUDE_CODE_USE_BEDROCK": "1", "AWS_REGION": "us-east-1", "AWS_DEFAULT_REGION": "us-east-1",
    "ANTHROPIC_DEFAULT_OPUS_MODEL": MODEL,
    "ANTHROPIC_DEFAULT_SONNET_MODEL": "global.anthropic.claude-sonnet-4-5-20250929-v1:0",
    "ANTHROPIC_DEFAULT_HAIKU_MODEL": "global.anthropic.claude-haiku-4-5-20251001-v1:0",
    "DISABLE_TELEMETRY": "1", "DISABLE_AUTOUPDATER": "1", "DISABLE_ERROR_REPORTING": "1",
}
_live = set()
_live_lock = threading.Lock()


def eligible(lane, base=None, log=print):
    """(ok, why). Cheap, local checks only (no SSH). On success the slot is reserved under `base` (released by
    Shadow.stop / a failed launch), so MAX_CONCURRENT holds even while launches are in flight."""
    if not ENABLED:
        return False, "HCTF_HB_SHADOW=0"
    if lane not in LANES:
        return False, f"lane {lane} not in HCTF_HB_SHADOW_LANES"
    if not remote._public_gm():
        return False, "replay GM (the VM only reaches the real GM)"
    if remote.gm_transport() != "local" or not workers.AUTO_HOMEBASE:
        return False, "Homebase not in auto mode"
    with _live_lock:
        if len(_live) >= MAX_CONCURRENT:
            return False, f"{len(_live)} shadows already running"
    ok, s = hbbudget.allow_ai(SHADOW_USD * hbbudget.CREDITS_PER_USD * 0.5)
    if not ok:
        return False, f"credit budget: {hbbudget.summary_line()}"
    with _live_lock:
        if len(_live) >= MAX_CONCURRENT:
            return False, f"{len(_live)} shadows already running"
        _live.add(base or lane)
    return True, ""


def _q(p):
    return shlex.quote(str(p))


class Shadow:
    def __init__(self, chain, cid, prompt, log=print):
        self.chain, self.cid, self.prompt, self.say = chain, cid, prompt, log
        self.mdir = cli.cdir(cid).relative_to(ROOT)                    # challenges/dayNN/<chal>/single_solve
        self.croot = chain.root.relative_to(ROOT)                       # challenges/dayNN/<chal>
        self.sdir = chain.sdir.relative_to(ROOT)                        # .../solver
        self.tag = re.sub(r"[^A-Za-z0-9]+", "_", cid) + time.strftime("_%H%M%S")
        self.rdir = f"~/{HW}/.run/shadow"
        self.pid = None
        self.started = None
        self.finished = threading.Event()
        self.alive = False
        self.correct = False
        self._merged = {}
        self._snap_sig = None
        self.snap = None
        self.cost = None

    # ---- launch
    def launch(self):
        """Push state, fetch the artifact on the VM, start claude detached. Returns True when it is running."""
        workers.sync_homebase_base()
        prior = None
        try:
            from .orchestrate import prior_solver_dir
            prior = prior_solver_dir(self.chain.lane, self.chain.sdir)
        except Exception:  # noqa: BLE001 - optional context
            pass
        dirs = [self.croot] + ([prior.relative_to(ROOT)] if prior else [])
        remote.ssh("mkdir -p " + " ".join(_q(f"{HW}/{d}") for d in dirs) + f" {self.rdir}", timeout=30)
        excl = ["--exclude=artifacts/", "--exclude=*.log", "--exclude=__pycache__/", "--exclude=time_trial/",
                "--exclude=mastery/", f"--max-size={MAX_PUSH}"]
        remote._rsync(["rsync", "-a", *excl, "-e", "SSH", str(ROOT / self.croot) + "/",
                       f"{remote.HB_USER}@{remote.HB_HOST}:{HW}/{self.croot}/"])
        if prior:
            remote._rsync(["rsync", "-a", "--exclude=__pycache__/", f"--max-size={MAX_PUSH}", "-e", "SSH",
                           str(prior) + "/", f"{remote.HB_USER}@{remote.HB_HOST}:{HW}/{prior.relative_to(ROOT)}/"])
        remote.rsync_to(ROOT / "challenges" / "index.json", f"~/{HW}/challenges/index.json")
        # Artifact: small ones (nearly every lane: KBs) go over the VPN as-is -- exactly the bytes the local worker has.
        # Big ones (binary: 31 MB = minutes over the VPN) are fetched on the VM next to the GM.
        latest = cli.cdir(self.cid) / "artifacts" / "latest"
        art = latest.resolve() if latest.exists() else None
        size = sum(f.stat().st_size for f in art.rglob("*") if f.is_file()) if art else 0
        adir = f"{HW}/{self.mdir}/artifacts"
        if art and size <= ART_PUSH:
            remote._rsync(["rsync", "-aL", "-e", "SSH", f"--rsync-path=mkdir -p {adir}/{art.name} && rsync",
                           str(art) + "/", f"{remote.HB_USER}@{remote.HB_HOST}:{adir}/{art.name}/"])
            fetch = f"ln -sfn {_q(art.name)} {_q(adir)}/latest"
        else:   # `hctf artifact` (contract capabilities), else the plain artifact op; then the same triage as local
            fetch = (f"(timeout 120 python3 -m hctf.cli artifact {_q(self.cid)} >/dev/null 2>&1 || "
                     f"(d={_q(adir)}/vm && mkdir -p $d && timeout 120 python3 ~/hctf/gm.py artifact {_q(self.cid)} $d "
                     f">/dev/null && ln -sfn vm {_q(adir)}/latest); timeout 60 python3 -m hctf.cli triage {_q(self.cid)} "
                     f">/dev/null 2>&1; true)")
        pf = ROOT / ".run" / "tmp" / f"shadow-{self.tag}.prompt"
        pf.parent.mkdir(parents=True, exist_ok=True)
        pf.write_text(self.prompt + SHADOW_NOTE)
        remote.rsync_to(pf, f"{self.rdir}/{self.tag}.prompt")
        lane = self.chain.lane
        env = {**BEDROCK_ENV, **{k: (str(Path(v).relative_to(ROOT)) if isinstance(v, Path) else str(v))
                                 for k, v in self.chain._worker_env(self.cid, "single").items()},
               "HCTF_ON_HOMEBASE": "1", "HCTF_SHADOW": "1", "HCTF_WORKER_START": str(time.time()),
               "HUNTRESS_GAME_MASTER_URL": remote.INSIDE_GM,
               "BASH_DEFAULT_TIMEOUT_MS": os.environ.get("HCTF_WORKER_BASH_TIMEOUT_MS", "25000"),
               "JAVA_HOME": "$HOME/hbtools/jdk", "TMPDIR": f"$HOME/{HW}/.run/tmp"}
        envs = " ".join(f"{k}={v if v.startswith('$HOME') else _q(v)}" for k, v in env.items())
        flags = ["--dangerously-skip-permissions", "--max-turns", str(workers._max_turns("single")),
                 "--model", MODEL, "--effort", workers.worker_effort(lane), "--output-format", "stream-json",
                 "--verbose", "--strict-mcp-config", "--settings", json.dumps(workers.worker_settings(lane)),
                 "--max-budget-usd", str(hbbudget.ai_cap_usd(SHADOW_USD))]
        if workers.WORKER_TOOLS:
            flags += ["--tools", workers.WORKER_TOOLS]
        # `;` (not &&) before setsid: `&` must background ONLY the worker, or the ssh channel stays open until it ends
        cmd = (f"cd ~/{HW} && mkdir -p .run/tmp && export {envs} PYTHONPATH=$HOME/{HW} "
               f"PATH=$HOME/{HW}/bin:$HOME/hbtools/bin:$HOME/.local/bin:$PATH && {fetch}; "
               f"setsid nice -n 10 timeout {int(workers_single_timeout())} claude -p {' '.join(_q(f) for f in flags)} "
               f"< {self.rdir}/{self.tag}.prompt > {self.rdir}/{self.tag}.log 2>&1 & echo PID=$!")
        r = remote.ssh(cmd, timeout=120, check=False)
        m = re.search(r"PID=(\d+)", r.stdout)
        if not m:
            raise RuntimeError(f"shadow launch failed: {(r.stdout + r.stderr)[-300:]}")
        self.pid, self.started, self.alive = int(m.group(1)), time.time(), True
        self._merged = dict(cli.confirmed_answers(self.cid))   # the VM started from these (pushed above)
        return True

    # ---- poll + merge
    def poll(self):
        """One SSH round-trip: alive?, VM confirmations, solver signature. Merges confirmations locally."""
        sd = f"~/{HW}/{self.sdir}"
        cmd = (f"kill -0 {self.pid} 2>/dev/null && echo ALIVE=1 || echo ALIVE=0; "
               f"echo CONF=$(cat ~/{HW}/{self.mdir}/confirmed.json 2>/dev/null | tr -d '\\n'); "
               f"grep -c '\"kind\": \"correct\"' ~/{HW}/{self.mdir}/submissions.jsonl 2>/dev/null | sed 's/^/NCORR=/'; "
               f"echo SIG=$(find {sd} -maxdepth 2 -name '*.py' -not -path '*/cases/*' -printf '%T@ ' 2>/dev/null "
               f"| tr ' ' '\\n' | sort -n | tail -1)")
        r = remote.ssh(cmd, timeout=30, check=False)
        out = dict(re.findall(r"^(ALIVE|CONF|NCORR|SIG)=(.*)$", r.stdout, re.M))
        self.alive = out.get("ALIVE") == "1"
        try:
            conf = json.loads(out.get("CONF") or "{}")
        except ValueError:
            conf = {}
        self._merge(conf, int(out.get("NCORR") or 0) > 0)
        return out.get("SIG", "")

    def _merge(self, conf, vm_correct):
        start = cli.load(self.cid, "start.json") or {}
        att = cli.attempt_id(start)
        got = conf.get(att) or {}
        new = {k: v for k, v in got.items() if self._merged.get(k) != v}
        ids = set(start.get("answer_ids") or [])
        full = vm_correct or (ids and ids <= set(got))
        if not new and not (full and not self.correct):
            return
        with cli.chal_lock(self.cid):
            local = cli.confirmed_answers(self.cid, att)
            add = {k: v for k, v in got.items() if local.get(k) != v}
            if full and not cli.is_complete(self.cid):
                cli.record_remote_result(self.cid, att, got, "correct", {"via": "homebase-shadow"})
            elif add:
                cli.record_remote_result(self.cid, att, add, "accepted", {"via": "homebase-shadow"})
        self._merged.update(got)
        if new:
            self.say(f"[{self.cid}] shadow: merged {len(new)} GM-confirmed answer(s) from Homebase")
        if full and not self.correct:
            self.correct = True
            self.say(f"[{self.cid}] shadow: Single Solve CORRECT on Homebase")

    # ---- solver handoff
    def verified_snapshot(self, sig):
        """Pull the shadow's solver (when it changed) and return it if it reproduces every confirmed answer here."""
        if not sig or sig == self._snap_sig:
            return self.snap
        rel = self.sdir.parts  # (challenges, dayNN, <chal>, solver)
        snap = ROOT / ".run" / f"shadow-{rel[1]}" / rel[2] / "solver"
        tmp = snap.parent / "solver.pull"
        shutil.rmtree(tmp, ignore_errors=True)
        tmp.mkdir(parents=True)
        remote._rsync(["rsync", "-a", "--exclude=cases/", "--exclude=__pycache__/", "-e", "SSH",
                       f"{remote.HB_USER}@{remote.HB_HOST}:{HW}/{self.sdir}/", str(tmp) + "/"])
        self._snap_sig = sig
        if not (tmp / "solve.py").exists():
            return None
        shutil.rmtree(snap, ignore_errors=True)
        tmp.rename(snap)
        if (self.chain.root / "meta.json").exists():
            shutil.copy2(self.chain.root / "meta.json", snap.parent / "meta.json")
        contract, art, conf = cli.load(self.cid, "start.json"), solvers_latest_artifacts(self.cid), \
            cli.confirmed_answers(self.cid)
        if not (contract and art and conf):
            return None
        got, err, dt = solvers.run_solver(snap, contract, art)
        bad = sorted(k for k, v in conf.items() if got.get(k) != v)
        if err or bad:
            self.say(f"[{self.cid}] shadow solver not verified here ({err or f'{len(bad)} field(s) differ, e.g. {bad[:3]}'})")
            return None
        self.snap = snap
        self.say(f"[{self.cid}] shadow solver verified locally ({dt:.1f}s)")
        return snap

    # ---- stop + account
    def stop(self, why="chain left the Single Solve"):
        if self.finished.is_set():
            return
        self.finished.set()
        with _live_lock:
            _live.discard(self.chain.base)
        if self.pid is None:
            return
        cmd = (f"kill -TERM -- -{self.pid} 2>/dev/null; sleep 1; kill -KILL -- -{self.pid} 2>/dev/null; "
               f"python3 ~/{HW}/hctf/hbcost.py {self.rdir}/{self.tag}.log")
        try:
            r = remote.ssh(cmd, timeout=60, check=False)
            d = json.loads(r.stdout.strip().splitlines()[-1])
            self.cost = d.get("usd")
            hbbudget.record_ai(self.cost, f"shadow {self.cid}", {"turns": d.get("turns"), "why": why,
                                                                 "wall": round(time.time() - self.started, 1),
                                                                 "correct": self.correct})
            self.say(f"[{self.cid}] shadow ended ({why}): ${self.cost:.2f} list, {d.get('turns')} turns, "
                     f"{time.time() - self.started:.0f}s; {hbbudget.summary_line()}")
        except Exception as e:  # noqa: BLE001 - accounting must never hurt the chain
            # unknown spend: book the per-shadow cap (conservative), so the budget never under-counts
            hbbudget.record_ai(hbbudget.ai_cap_usd(SHADOW_USD), f"shadow {self.cid} (cost unread, booked the cap)",
                               {"error": str(e)[:200]})
            self.say(f"[{self.cid}] shadow ended ({why}); cost unread ({e})")
        try:  # keep the transcript locally for post-mortems (background: it can be a few MB over the VPN)
            dst = ROOT / self.mdir / f"worker-single-hbshadow-{self.tag}.log"
            threading.Thread(target=remote._rsync, args=(["rsync", "-a", "-e", "SSH_OWN",
                             f"{remote.HB_USER}@{remote.HB_HOST}:{HW}/.run/shadow/{self.tag}.log", str(dst)],),
                             daemon=True).start()
        except Exception:  # noqa: BLE001
            pass


def solvers_latest_artifacts(cid):
    from . import timed
    return timed.latest_artifacts(cid)


def workers_single_timeout():
    from .orchestrate import SINGLE_TIMEOUT
    return SINGLE_TIMEOUT


SHADOW_NOTE = """

## You are the HOMEBASE SHADOW worker
You run on the Homebase VM, in parallel with another worker on a different machine solving the same challenge.
Work independently in this tree (it mirrors the same relative paths). The artifact was downloaded here over the
inside Game Master; if `artifacts/latest` is missing, run `hctf artifact <id>` yourself. Submit with `hctf submit`
exactly as instructed above -- confirmations are shared with the other worker automatically. The harness ends you as
soon as either worker finishes, so keep the solver (`solve.py`) committed to disk as soon as it reproduces answers.
Heavy tools live in ~/hbtools/bin (jadx, apktool, Ghidra analyzeHeadless with a 1.5 GB heap, rizin, ilspycmd, upx,
GoReSym, exiftool); this VM has 2 vCPUs and 3.8 GB RAM, so prefer targeted commands over whole-program analysis.
"""


def run_beside(chain, cid, prompt, ready_get, done, log=print):
    """Thread body: launch, poll until `done`, hand a verified solver to the chain through ready_get() -> (event, lock).
    Returns the Shadow (or None if not launched)."""
    sh = Shadow(chain, cid, prompt, log)
    try:
        # at the drop the VM is still being probed/provisioned by the prewarm thread: give it a moment (off the chain)
        if not workers.wait_homebase(HB_WAIT_S, log):
            raise RuntimeError(f"Homebase not ready within {HB_WAIT_S:g}s")
        sh.launch()
        log(f"[{cid}] shadow worker -> Homebase (Bedrock {MODEL}, cap ${hbbudget.ai_cap_usd(SHADOW_USD):g}; "
            f"{hbbudget.summary_line()})")
    except Exception as e:  # noqa: BLE001 - the shadow is optional
        log(f"[{cid}] shadow launch skipped: {e}")
        sh.finished.set()
        with _live_lock:
            _live.discard(chain.base)
        return None
    chain._shadow = sh
    fails = 0
    try:
        while not done.wait(POLL_S):
            try:
                sig = sh.poll()
                fails = 0
            except Exception as e:  # noqa: BLE001 - a VPN blip; next poll
                fails += 1
                if fails * POLL_S >= DEAD_S:   # VM stopped (alt 10-09: powered off ~30 min after power-on)
                    log(f"[{cid}] shadow abandoned: Homebase unreachable for {fails * POLL_S:.0f}s ({e})")
                    sh.alive = False
                    break
                if fails == 1:
                    log(f"[{cid}] shadow poll note: {e}")
                continue
            if cli.is_complete(cid):
                ready, lock = ready_get()
                if ready is not None and not ready.is_set():
                    snap = sh.verified_snapshot(sig)
                    if snap:
                        with lock:
                            if not ready.is_set():
                                chain._ready_snap = snap
                                log(f"[{cid}] shadow reached a verified solver first -> ending the local worker")
                                ready.set()
            if not sh.alive:
                if not cli.is_complete(cid):
                    log(f"[{cid}] shadow exited without a CORRECT single")
                elif sh.snap is None:
                    sh.verified_snapshot(sig)
                break
    finally:
        sh.stop("done" if not sh.alive else "chain left the Single Solve")
    return sh
