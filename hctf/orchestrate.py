"""`hctf run`: every released challenge as an independent chain, all chains in parallel.

chain(base) = Single Solve (LLM worker) -> solver proven on its regression case
            -> Time Trial (scripted; fix worker on failure) -> Mastery (scripted; fix worker on failure)

The GM enforces those prerequisites, so each chain is sequential while all chains run concurrently.
Worker slots: local `claude -p` (HCTF_LOCAL_SLOTS) + Homebase `codex exec` (HCTF_HB_SLOTS, credit-gated).
Fix workers racing a deadline skip the slot queue.
"""
import datetime
import json
import os
import re
import shutil
import sys
import threading
import time
import traceback
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from . import cli, paths, remote, scout, solvers, timed, workers

ROOT = Path(__file__).resolve().parent.parent
CREDIT_SOFT = float(os.environ.get("HCTF_CREDIT_SOFT", "4"))   # below: no new Homebase (codex) workers
CREDIT_HARD = float(os.environ.get("HCTF_CREDIT_HARD", "1.5"))  # below: no new timed starts; VM kept for GM
SINGLE_TIMEOUT = int(os.environ.get("HCTF_SINGLE_TIMEOUT", str(25 * 60)))
GENERALIZE_TIMEOUT = int(os.environ.get("HCTF_GENERALIZE_TIMEOUT", str(12 * 60)))
MAX_SINGLE_LAUNCHES = 3
MAX_TIMED_RETRIES = 5
CLOCK_RETRIES = int(os.environ.get("HCTF_CLOCK_RETRIES", "12"))  # extra retries for pure clock expiries
RATE_RETRIES = int(os.environ.get("HCTF_RATE_RETRIES", "6"))  # extra retries (with backoff) for GM 429s
# Retries (5/10/20 s backoff, then 20 s) when the GM refuses to start an attempt at all: ~10 min of patience, no worker.
START_RETRIES = int(os.environ.get("HCTF_START_RETRIES", "30"))


def _resume_need(prev):
    """Seconds of clock a resumed attempt must still have to be worth running: the last run's in-window phases
    (download + solve + submit) + 1.5 s, at least 3 s (half the window when no phases are known)."""
    ph = prev.get("phases") or {}
    used = sum(float(ph.get(k) or 0) for k in ("download", "solve", "submit"))
    if used:
        return max(3.0, used + 1.5)
    return max(3.0, float(prev.get("window") or 0) / 2)
CHAIN_CRASH_RETRIES = int(os.environ.get("HCTF_CHAIN_CRASH_RETRIES", "1"))  # re-run a crashed chain (done modes skip)
# Early handoff: once the Single Solve is CORRECT and a snapshot of the still-running worker's solver reproduces
# its confirmed answers, make ONE speculative Time Trial -> Mastery pass from that snapshot instead of idling until
# the worker exits (rehearsal Day 5: answers CORRECT at T+3:10, worker hardened the solver until T+6:25).
BASELINE_CASE_TIMEOUT = float(os.environ.get("HCTF_BASELINE_CASE_TIMEOUT", "8"))  # > any 6-7s window  # pre-generalize regression baseline
# Owner: earlier days are LEARNING NOTES (reference/techniques/<lane>.md), never "rerun yesterday's solver first" -- the
# day's challenge may be unrelated (an old solver confidently submitted a wrong value; old warmups/metadata solvers
# produced nothing). Opt back in with HCTF_REUSE_OLD_SOLVERS=1.
REUSE_OLD_SOLVERS = os.environ.get("HCTF_REUSE_OLD_SOLVERS", "0") == "1"
ENUM_PROBE_BUDGET = int(os.environ.get("HCTF_ENUM_PROBE_BUDGET", "0"))  # OFF: the worker identifies labels; set >0 to pre-probe question-listed enum options
REUSE_PROBE_BUDGET = int(os.environ.get("HCTF_REUSE_PROBE_BUDGET", "20"))  # merged-reuse submits before the worker
STOP_WHEN_READY = os.environ.get("HCTF_STOP_WHEN_READY", "1") != "0"  # end the single worker at CORRECT + verified solver
SPEC_STABLE = float(os.environ.get("HCTF_SPEC_STABLE", "2"))  # solver files untouched this long before a snapshot
SPEC_POLL = float(os.environ.get("HCTF_SPEC_POLL", "1"))
# The single's solver on its OWN case must beat this (local s) or a speed generalize runs BEFORE the first timed attempt:
# Homebase is ~1.5x slower and the 7-13 s window also pays GM start/download/submit (blind D7 replay: binary 5.9 s ->
# Time Trial exec_error "too slow", one attempt + ~30 s burned before the speed fix even started). 0 disables.
SINGLE_SPEED_BUDGET = float(os.environ.get("HCTF_SINGLE_SPEED_BUDGET", "2.5"))
# Time Trial scouting before Mastery (hctf/scout.py): extra TT attempts that harvest new variants and learn label
# spellings on the cheap clock. 0 = off. `hctf run --scout N` overrides.
SCOUT_ROUNDS = int(os.environ.get("HCTF_SCOUT_ROUNDS", "0"))
SCOUT_CLEAN = int(os.environ.get("HCTF_SCOUT_CLEAN", "2"))          # stop after this many clean rounds in a row
SCOUT_GENERALIZE = int(os.environ.get("HCTF_SCOUT_GENERALIZE", "2"))  # offline fix cycles between scout bursts
# Variant harvest beside a gap-fixing generalize: fresh attempts of the same mode (started, downloaded, never submitted)
# whose bytes the pre-worker solver leaves incomplete become extra variant cases the SAME worker fixes. main4 replay:
# script TT failed on 3 different unseen constructs in a row (JScript hex arrays, JScript relay, cx_Freeze carrier) +
# one more on Mastery = 4 generalize/retry cycles (~3:20) where one multi-variant cycle would do.
HARVEST_VARIANTS = int(os.environ.get("HCTF_HARVEST_VARIANTS", "3"))
HARVEST_MIN_ATTEMPTS = int(os.environ.get("HCTF_HARVEST_MIN_ATTEMPTS", "8"))   # GM unique_attempts_remaining floor for a harvest
# s after an attempt's deadline before the next retry. A retry while the previous attempt is still live just RESUMES it
# (verified on a rehearsal copy 2026-10-08: same attempt_id, unique_attempts_remaining unchanged), so an early one costs nothing and
# _harvest polls once a second until the id changes (was deadline + 5 s: ~4 s lost per harvested variant).
HARVEST_GAP = float(os.environ.get("HCTF_HARVEST_GAP", "0.5"))
HARVEST_YIELD_MAX = float(os.environ.get("HCTF_HARVEST_YIELD_MAX", "30"))
HARVEST_CALL_TIMEOUT = float(os.environ.get("HCTF_HARVEST_CALL_TIMEOUT", "20"))   # per GM call (default cli.call: 180 s)
HARVEST_JOIN_MAX = float(os.environ.get("HCTF_HARVEST_JOIN_MAX", "10"))           # wait for the harvest after the worker


def attempt_over(body):
    """A start/status body for an attempt that is no longer live (expired / finished / past its deadline / no task):
    a `retry` is needed for a fresh variant. Mirrors hb_timed's re-roll rule."""
    if body.get("error"):
        return False
    if str(body.get("result", "")).lower() in ("expired", "correct", "incorrect", "finished"):
        return True
    if not body.get("answer_ids") or not cli.attempt_id(body):
        return True
    left = timed.seconds_left(body)
    return left is not None and left <= 0.5  # max s a harvest waits out other live clocks

_print_lock = threading.Lock()


def _by_set(answers):
    """Group answers by their set/slot prefix so each unit submits separately (clearer accept/incorrect)."""
    groups = {}
    for aid, val in answers.items():
        m = re.match(r"(set|slot)[._-]?\d+", aid)
        groups.setdefault(m.group(0) if m else "_", {})[aid] = val
    return groups


def say(msg):
    with _print_lock:
        print(time.strftime("%H:%M:%S"), msg, flush=True)


# ---------------------------------------------------------------- governor

class Governor:
    """Credits only gate the OPTIONAL Homebase codex pool now. GM access and timed runs go direct over
    the pairing token, so they no longer depend on credits. When Homebase is unused, credits aren't read."""

    def __init__(self, hb_enabled=False):
        self._t, self._v, self._lock = 0, None, threading.Lock()
        self.hb_enabled = hb_enabled

    def credits(self):
        if not self.hb_enabled:
            return 99.0  # Homebase unused: credits gate nothing, and reading them spins up the browser session
        with self._lock:
            if time.time() - self._t > 300 or self._v is None:
                try:
                    self._v = remote.power("status")["credits"]
                except Exception as e:  # noqa: BLE001 - governor must never kill the run
                    say(f"[governor] credit read failed: {e}")
                    self._v = self._v if self._v is not None else 99.0
                self._t = time.time()
            return self._v

    def allow_homebase_workers(self):
        return self.hb_enabled and self.credits() > CREDIT_SOFT

    def allow_timed(self):
        return True  # timed runs locally against the public GM; no credit gate


# ---------------------------------------------------------------- pools

class Pools:
    def __init__(self, local, homebase, gov):
        self.local = threading.BoundedSemaphore(local) if local else None
        self.hb = threading.BoundedSemaphore(homebase) if homebase else None
        self.gov = gov

    def acquire(self, prefer_homebase=False):
        """Block until a slot is free. Returns 'local' or 'homebase'."""
        while True:
            order = [("homebase", self.hb), ("local", self.local)] if prefer_homebase else \
                    [("local", self.local), ("homebase", self.hb)]
            for name, sem in order:
                if sem is None or (name == "homebase" and not self.gov.allow_homebase_workers()):
                    continue
                if sem.acquire(blocking=False):
                    return name
            time.sleep(2)

    def release(self, name):
        (self.local if name == "local" else self.hb).release()


# ---------------------------------------------------------------- chain state

_state_lock = threading.Lock()


def set_state(base, **kw):
    p = paths.challenge_root(base) / "chain.json"
    with _state_lock:
        try:
            st = json.loads(p.read_text()) if p.exists() else {}
        except ValueError:
            st = {}
        st.update(kw, updated=time.strftime("%Y-%m-%dT%H:%M:%S"))
        tmp = p.with_name(f".chain.json.{threading.get_ident()}")
        tmp.write_text(json.dumps(st, indent=2))
        os.replace(tmp, p)  # atomic: `hctf dash`/`why` never read a half-written file


TRIAGE_INLINE_CAP = int(os.environ.get("HCTF_TRIAGE_INLINE_CAP", "6000"))
CUMULATIVE_LANES = ("binary-reverse-engineering", "script-analysis")


def triage_summary(cid, cap=TRIAGE_INLINE_CAP):
    """triage.md from its STATUS section on (answer formats / family table, artifacts, pre-extracted members incl. tiny
    text members), inlined into the prompt: every Day 7 worker's second turn was `head triage.md; jq contract`."""
    p = cli.cdir(cid) / "triage.md"
    try:
        t = p.read_text()
    except OSError:
        return "(no triage.md: read contract.json and artifacts/latest/ directly)"
    i = t.find("## STATUS")
    body = t[i:] if i >= 0 else t
    if len(body) > cap:
        body = body[:cap].rsplit("\n", 1)[0] + f"\n... (truncated here -- the rest is in `{p.relative_to(ROOT)}`)"
    return body.strip()


CARRY_RE = re.compile(r"(?:^|\.)d(\d{2})[-_]")


def prior_solver_dirs(lane, sdir):
    """{day number: solver dir} for every EARLIER day of this lane that has a solve.py (all lanes)."""
    day = sdir.parent.parent.name
    out = {}
    for m in sorted(ROOT.glob("challenges/day*/*/meta.json")):
        if m.parent.parent.name >= day or not (m.parent / "solver" / "solve.py").exists():
            continue
        try:
            if json.loads(m.read_text()).get("lane") != lane:
                continue
        except (OSError, ValueError):
            continue
        dm = re.match(r"day(\d+)", m.parent.parent.name)
        if dm:
            out[int(dm.group(1))] = m.parent / "solver"
    return out


def carry_over_note(lane, sdir, ids):
    """Escalated variants re-ask EARLIER days' questions (D7 metadata TT: 1 -> 11 fields incl. d04/d05/d06 carry-overs).
    For answer_ids naming an earlier day (`dNN-...`, `set1.dNN_...`), point at that day's solver of this lane as a
    REFERENCE to adapt -- the harness never runs it. Returns '' when there is none."""
    m = re.match(r"day(\d+)", sdir.parent.parent.name)
    if not m:
        return ""
    today = int(m.group(1))
    days = sorted({int(x.group(1)) for a in ids for x in [CARRY_RE.search(a)] if x and int(x.group(1)) < today})
    dirs = prior_solver_dirs(lane, sdir)
    hits = [(d, dirs[d]) for d in days if d in dirs]
    if not hits:
        return ""
    return ("CARRY-OVER questions from earlier days of this lane (escalated variant): "
            + "; ".join(f"`d{d:02d}-*` = Day {d}'s family, see `{p.relative_to(ROOT)}/NOTES.md` + `solve.py`"
                        for d, p in hits)
            + ". Adapt (import or port) that parsing into today's solver -- answers still come from today's bytes.")


SET_RE = re.compile(r"^(?:set|slot)[._-]?\d+[._-]")


def _contract_shape(contract):
    """(answer-id families with the set prefix stripped, artifact member extensions) of a contract."""
    ids = list((contract or {}).get("answer_ids") or []) + [q.get("id") or "" for q in (contract or {}).get("questions") or []]
    fams = {SET_RE.sub("", a) for a in ids if a}
    exts = set()
    for q in (contract or {}).get("questions") or []:
        art = (q.get("artifact") or "").split("->")[-1].strip()
        m = re.search(r"\.([A-Za-z0-9]{1,8})$", art)
        if m:
            exts.add(m.group(1).lower())
    return fams, exts


def mastery_delta(single_contract, timed_contracts):
    """What the Time Trial / Mastery contracts ask that today's Single does NOT (compounding Mastery: earlier days'
    concepts mixed in). -> short text for the single prompt, '' when the timed contracts add nothing."""
    sfam, sext = _contract_shape(single_contract)
    if not sfam:
        return ""
    extra_f, extra_e = set(), set()
    for tc in timed_contracts:
        fam, ext = _contract_shape(tc)
        extra_f |= fam - sfam
        extra_e |= ext - sext
    if not extra_f and not extra_e:
        return ""
    parts = []
    if extra_f:
        parts.append(f"{len(extra_f)} question id(s) the Single never asks, e.g. "
                     + ", ".join(f"`{x}`" for x in sorted(extra_f)[:12]))
    if extra_e:
        parts.append("artifact kinds the Single doesn't ship: " + ", ".join(f"`.{e}`" for e in sorted(extra_e)))
    return ("MASTERY COMPOUNDS: the Time Trial / Mastery contracts (status-time, under this challenge's time_trial/ and "
            "mastery/ dirs) ask " + "; ".join(parts) + ". solve.py must answer those too from the timed bytes -- "
            "dispatch on question text / artifact type; reuse earlier days' parsing for earlier days' concepts.")


def prior_solver_dir(lane, sdir):
    """Latest earlier day's solver dir of the same lane (binary/script only: their contracts are CUMULATIVE, so
    yesterday's solver already answers every earlier family). The worker copies it as a starting point; the harness
    never runs it as an answer source (harness-side reuse stays OFF)."""
    if lane not in CUMULATIVE_LANES:
        return None
    day = sdir.parent.parent.name
    best = None
    for m in sorted(ROOT.glob("challenges/day*/*/meta.json")):
        if m.parent.parent.name >= day:
            continue
        try:
            if json.loads(m.read_text()).get("lane") != lane:
                continue
        except (OSError, ValueError):
            continue
        if (m.parent / "solver" / "solve.py").exists():
            best = m.parent / "solver"
    return best


def technique_log(lane):
    """reference/techniques/<lane>.md -- the lane's learning log from earlier days (patterns, cues, tools, GM
    conventions, pitfalls) -- path PLUS its "how this lane has looked" summary inlined: a warmups worker never opened
    the log and built a solver the log's Mastery format would have told it was wrong (~150 s lost)."""
    f = ROOT / "reference" / "techniques" / f"{lane}.md"
    if not f.exists():
        return "(none yet for this lane)"
    text = f.read_text(errors="replace")
    head = text.split("\n## ", 1)[0].strip().splitlines()[1:]          # drop the title line
    summary = "\n".join(l for l in head if l.strip())[:2500]
    out = f"`{f.relative_to(ROOT)}` -- its summary (OBSERVATIONS from earlier days, not guarantees):\n{summary}"
    # The sections workers otherwise re-read in a second call (replays: 13 s, or only after the evidence at 56 s).
    for sec in ("Recognition cues", "Codec table"):
        body = _log_section(text, sec, 4500)
        if body:
            out += f"\n\n{body}"
    axes = variant_axes(lane)
    return out + (f"\n\n{axes}" if axes else "")


def _log_section(text, title, cap):
    m = re.search(r"^## " + re.escape(title) + r".*?(?=^## |\Z)", text, re.M | re.S)
    return m.group(0).strip()[:cap] if m else ""


# Parallel per-language subagents for the script lane (fair from-scratch D6 replays, same knowledge): serial worker
# (main6) single 225 s / lane 247 s; subagents main7 158 s / 181 s but main8 302 s / 407 s -- the lane waits on the
# SLOWEST subagent (JScript/Batch took ~200 s in main8 while the main thread polled), and its per-language code failed
# the first Time Trial (15 empty fields). High variance, not a reliable win: OFF by default; HCTF_SCRIPT_SUBAGENTS=1 on.
SCRIPT_SUBAGENTS = os.environ.get("HCTF_SCRIPT_SUBAGENTS", "0") == "1"


def subagent_policy(lane):
    if SCRIPT_SUBAGENTS and lane == "script-analysis":
        return ("Subagents (script lane): the contract covers several host languages and writing every "
                "per-language analyser serially is the slowest part of this lane (~300 chars/s of code). Once triage's "
                "decoded plans and the Variant axes are read: write ONE brief file (contract answer-id grammar, the "
                "per-language function signature `analyse(paths, contract) -> {answer_id: value}` in "
                "`solver/lang_<language>.py`, `lib.codec` for every declared codec, the playbook rules), then launch one "
                "subagent per host language in ONE message (each owns only its `lang_<x>.py`) and, meanwhile, write the "
                "`solve.py` dispatcher yourself; then ONE blocking wait -- never poll. Submit from solve.py as usual.")
    return ("Subagents: none by default -- one worker writing one solver is fastest when triage already decoded the "
            "payloads. Only if several genuinely independent NEW formats each need real reverse engineering: at most 2 "
            "subagents, launched in ONE message with ONE shared brief file, then ONE blocking wait for both -- never "
            "poll (a replay lost 61 s writing briefs one by one and 79 s busy-waiting on a subagent).")


def variant_axes(lane):
    """The log's "## Variant axes" section (what differed between single / Time Trial / Mastery variants of one day):
    inlined so the solver is written for those axes up front -- the D6 from-scratch replay lost 4 generalize cycles
    (~3:20) to one unseen axis value each (hex vs decimal literals, urlsafe base64, a cx_Freeze carrier)."""
    f = ROOT / "reference" / "techniques" / f"{lane}.md"
    if not f.exists():
        return ""
    m = re.search(r"^## Variant axes.*?(?=^## |\Z)", f.read_text(errors="replace"), re.M | re.S)
    return m.group(0).strip()[:2500] if m else ""


def _rel(p):
    """Path for a worker prompt: project-relative when possible."""
    try:
        return Path(p).relative_to(ROOT)
    except (ValueError, TypeError):
        return p


def ensure_case_and_test(cid, sdir, full=True):
    """Turn the Single Solve's confirmed answers into regression case 'single_solve' and run all cases
    (full=False: only record the case -- the caller already verified the solver on it)."""
    contract = cli.load(cid, "start.json")
    art = timed.latest_artifacts(cid)
    conf = cli.confirmed_answers(cid)
    if contract and art and conf and (sdir / "solve.py").exists():
        solvers.add_case(sdir, "single_solve", contract, art, conf)
    if not (sdir / "solve.py").exists():
        return False, "no solve.py"
    if not full:
        return True, None
    res = solvers.test_solver(sdir)
    return bool(res) and all(r["ok"] for r in res), res


def record_timed_case(cid, sdir):
    contract = cli.load(cid, "start.json")
    art = timed.latest_artifacts(cid)
    conf = cli.confirmed_answers(cid)
    if contract and art and conf:
        name = f"{solvers.mode_of(cid)}-{(cli.attempt_id(contract) or 'x')[:8]}"
        solvers.add_case(sdir, name, contract, art, conf)


def capture_variant(cid, sdir):
    """Save the current (unsolved) variant as a regression case so the offline fix worker can work on
    the real bytes. expected.json holds only answers the GM already confirmed (often empty here)."""
    contract = cli.load(cid, "start.json")
    art = timed.artifacts_for(cid, contract)
    if contract and art:
        name = f"variant-{solvers.mode_of(cid)}-{(cli.attempt_id(contract) or 'x')[:8]}"
        solvers.add_case(sdir, name, timed.trim_to_present(contract, art),
                         art, timed.present_only(contract, art, cli.confirmed_answers(cid)))


def _text_head(data, lines=40, chars=1500):
    """First lines of an artifact if it reads as text, else None (binaries go to the worker's own tools)."""
    if not data:
        return None
    sample = data[:4096]
    if sum(32 <= b < 127 or b in (9, 10, 13) for b in sample) < 0.9 * len(sample):
        return None
    text = sample.decode("utf-8", "replace")
    return "\n".join(text.splitlines()[:lines])[:chars]


def _case_texts(case, want):
    """(member name, text) for every text member of a case's artifacts (zips walked recursively) passing want(text)."""
    from lib.common import iter_entries
    for name, load, _parent in iter_entries(case / "artifacts"):
        if name.lower().endswith((".zip", ".apk", ".jar", ".exe", ".dll", ".bin", ".so", ".dex")):
            continue
        try:
            data = load()
        except Exception:  # noqa: BLE001
            continue
        if data[:2] == b"PK" or b"\x00" in data[:2048]:
            continue
        text = data.decode("utf-8", "replace")
        if want(text):
            yield name, text


def construct_census(sdir, lane, failing_members=(), max_cases=24):
    """Every construct of the lane's codec family across ALL the solver's cases, so a generalize worker sees the family
    instead of one sample (rehearsal Day 7 replay: 4 variants drew reversed_base64 x3 + decimal_csv, the worker fixed exactly
    those, the next variant drew xor_hex -> another cycle). Script lane: declared codecs (lib.codec.find_codecs),
    marking those on the failing files and whether lib.codec decodes them. Mobile: huntress_puzzle.json codecs and
    whether lib.android.decode_payload reaches an ANS code. '' for lanes without a codec family."""
    cases = sorted((c for c in (Path(sdir) / "cases").glob("*/") if not c.name.startswith("family-")),
                   key=lambda p: p.stat().st_mtime, reverse=True)[:max_cases]
    failing_members = {m.split("->")[-1].strip() for m in failing_members}
    if lane == "script-analysis":
        from lib import codec
        seen, bad, on_fail = {}, set(), {}
        for c in cases:
            for name, text in _case_texts(c, lambda t: "odec_" in t or "ODEC_" in t or "HUNTRESS-CODEC" in t):
                for d in codec.find_codecs(text):
                    spec = "|".join(x for x in (d["rep"], d["transform"], d["key"]) if x) or "?"
                    tr, _key = codec._spec(d["rep"], d["transform"], d["key"])   # 'xor_hex|21' -> repeating_key_xor
                    shape = f"{d['rep']}|{tr}"
                    seen[shape] = seen.get(shape, 0) + 1
                    if not d.get("plain"):
                        bad.add(spec)
                    if name in failing_members:
                        on_fail[shape] = on_fail.get(shape, True) and bool(d.get("plain"))
        if not seen:
            return ""
        reps = sorted({k.split("|")[0] for k in seen})
        trs = sorted({k.split("|")[1] for k in seen})
        lines = [f"Codec census over the newest {len(cases)} case(s): {len(seen)} distinct rep|transform shapes; "
                 f"reps {reps}; transforms {trs}."]
        if on_fail:
            lines.append("Shapes the FAILING file(s) have used across those cases (the family to cover, not just this "
                         "sample): " + ", ".join(f"{k}{'' if v else ' (lib.codec: NO decode)'}" for k, v in sorted(on_fail.items())))
        if bad:
            lines.append(f"lib.codec can NOT decode {len(bad)} declared spec(s): {sorted(bad)[:12]}")
        lines.append("Treat these as ONE family: route EVERY declared codec through `lib.codec.decode` / "
                     "`find_codecs` (it already composes any known rep x transform and has a name-agnostic fallback) "
                     "instead of a per-name table in the solver.")
        return "\n".join(lines)
    if lane == "mobile-android":
        import zipfile as _zf
        from lib.android import ANS_RE_T, decode_payload
        seen = {}
        for c in cases:
            for apk in (c / "artifacts").rglob("*"):
                try:
                    with _zf.ZipFile(apk) as z:
                        for n in z.namelist():
                            if n.endswith("huntress_puzzle.json"):
                                pz = json.loads(z.read(n))
                                name = str(pz.get("codec"))
                                ok = bool(ANS_RE_T.search(decode_payload(pz.get("codec"), pz.get("data", ""), pz.get("key")) or ""))
                                seen[name] = seen.get(name, True) and ok
                except Exception:  # noqa: BLE001 - not an apk / not readable
                    continue
        if not seen:
            return ""
        return (f"Puzzle-codec census over {len(cases)} case(s): " +
                ", ".join(f"{k} ({'decodes' if v else 'NO ANS'})" for k, v in sorted(seen.items())) +
                ". `lib.android.decode_payload` falls back to a name-agnostic search with the ANS shape as oracle.")
    return ""


_LANG_OF_EXT = {"sh": "bash", "bash": "bash", "js": "js", "mjs": "node", "cjs": "node", "vbs": "vbs", "bat": "batch",
                "cmd": "batch", "ps1": "power", "py": "py", "pyc": "py"}


def handler_pointer(sdir, tokens, top=6, strong=(), lang=None):
    """Solver functions most likely to handle the failing construct: `def` blocks of the solver's .py files ranked by
    how many of `tokens` (failing file-name parts, codec names) they mention. Saves the generalize worker's
    `cat solve.py; cat bashplan.py` (thousands of lines) -- rehearsal Day 7 replay: both workers started that way."""
    toks = {t.lower() for t in tokens if t and len(t) >= 3}
    strong = {t.lower() for t in strong if t and len(t) >= 3}
    if not toks and not strong:
        return ""
    hits = []
    for f in sorted(Path(sdir).glob("*.py")):
        if f.name.startswith(("make_", "test_", "gen_")):
            continue   # case generators / tests, not what runs in the window
        try:
            lines = f.read_text(errors="replace").splitlines()
        except OSError:
            continue
        starts = [i for i, ln in enumerate(lines) if re.match(r"\s*def \w+", ln)] + [len(lines)]
        for a, b in zip(starts, starts[1:]):
            body = "\n".join(lines[a:b]).lower()
            score = sum(body.count(t) for t in toks) + 3 * sum(body.count(t) for t in strong)
            if score and lang and lang in f.name.lower():
                score += 3   # bashplan.py for a .sh fixture, not batchplan.py
            if score:
                hits.append((score / max(1, b - a) ** 0.5, score, f.name, a + 1, lines[a].strip()[:90]))
    if not hits:
        return ""
    hits.sort(key=lambda h: -h[0])   # hit DENSITY: a focused codec_decode beats a 300-line analyse()
    hits = [h[1:] for h in hits]
    return "Solver functions mentioning the failing construct (file:line, hits):\n" + "\n".join(
        f"  {fn}:{ln}  {sig}  ({sc})" for sc, fn, ln, sig in hits[:top])


FAMILY_PROBE = os.environ.get("HCTF_FAMILY_PROBE", "1") != "0"
# Answer-invariant mutation probe (hctf/mutate.py, every lane): renamed delivery, reordered/subset questions, an unknown
# extra question, Mastery-shaped sets. A HARD miss is adopted as a mutation-* case and generalized BEFORE the first
# timed attempt (organizer, Day 8: TT/Mastery hand out "new, dynamic variations/mutations ... new unseen effects").
MUTATION_PROBE = os.environ.get("HCTF_MUTATION_PROBE", "1") != "0"
# Compounding probe (hctf/compound.py): replay the single's solver on EARLIER days' GM-verified cases of the lane. The
# organizers (Day 8): Mastery should compound -- today's concept plus concepts from days past -- so a solver that lost an
# earlier concept fails Mastery. Hard misses -> compound-dKK-* cases + one generalize before Mastery.
COMPOUND_PROBE = os.environ.get("HCTF_COMPOUND_PROBE", "1") != "0"
# Warm Single workers: launched at chain start beside GM start/download/triage (workers.WarmWorker). 0 = cold launch.
WARM_WORKERS = os.environ.get("HCTF_WARM_WORKERS", "1") != "0"
# Prior-solver dry run (cumulative lanes): diagnostics of yesterday's solver on today's bytes, never its values.
PRIOR_DRY_RUN = os.environ.get("HCTF_PRIOR_DRY_RUN", "1") != "0"
PRIOR_DRY_RUN_SECONDS = float(os.environ.get("HCTF_PRIOR_DRY_RUN_SECONDS", "15"))
COMPOUND_PROBE_SECONDS = float(os.environ.get("HCTF_COMPOUND_PROBE_SECONDS", "45"))
# Mastery speed gate: estimated Mastery solve (mutation probe's 2-set mastery-shape run) vs the known TT window. Mastery
# windows were 1-2.7x the TT window on D3-D8, so only an estimate over MASTERY_GATE_RATIO x TT window acts.
MASTERY_GATE_RATIO = float(os.environ.get("HCTF_MASTERY_GATE_RATIO", "2.0"))


def mutation_probe(sdir, mastery_contract=None, timeout=90):
    """Run hctf/mutate.py under the venv -> (text, [failing HARD mutation case dirs], summary)."""
    import subprocess
    out = ROOT / ".run" / "mutation" / Path(sdir).resolve().parent.name
    argv = [str(paths.VENV_PY), "-m", "hctf.mutate", "probe", str(sdir), "--out", str(out)]
    if mastery_contract and Path(mastery_contract).exists():
        argv += ["--mastery-contract", str(mastery_contract)]
    try:
        r = subprocess.run(argv, cwd=ROOT, capture_output=True, text=True, timeout=timeout)
        d = json.loads(r.stdout.strip().splitlines()[-1])
    except Exception as e:  # noqa: BLE001 - advisory
        return f"(mutation probe skipped: {str(e)[:120]})", [], {}
    return d.get("text") or "", d.get("hard_failed") or [], d


def compound_probe(sdir, seconds=None):
    """-> (text, [hard-miss result dicts], [all results]) for the single's solver on earlier days' verified cases."""
    from . import compound
    try:
        res = compound.check(sdir, deadline=time.time() + (seconds or COMPOUND_PROBE_SECONDS))
    except Exception as e:  # noqa: BLE001 - advisory
        return f"(compound probe skipped: {str(e)[:120]})", [], []
    return compound.summary(res), compound.hard_misses(res), res


def mastery_estimate(mut_summary, mastery_contract):
    """Estimated Mastery solve seconds = (2-set mastery-shape run / 2) x Mastery set count x 1.5, or None."""
    shape = next((r for r in (mut_summary or {}).get("results") or [] if r.get("mutation") == "mastery-shape"
                  and r.get("ok")), None)
    try:
        mc = json.loads(Path(mastery_contract).read_text())
        # The real GM's status-time contract carries ids only on questions[] (no answer_ids): rehearsal D8 printed no estimate.
        ids = mc.get("answer_ids") or [q.get("id") for q in mc.get("questions") or [] if q.get("id")]
    except (OSError, ValueError, TypeError):
        ids = []
    sets = {a.split(".", 1)[0] for a in ids if re.match(r"(set|slot)\d+\.", a)}
    if not shape or not sets:
        return None
    # Marginal cost per set = 2-set run - 1-set base run; the rest is process startup, paid once. (Plain shape/2 x sets
    # counted python startup per set: replay d8warm1 estimated warmups 38 sets at 5.7 s, real solve ~0.2 s.)
    base = (mut_summary or {}).get("base_seconds")
    two = float(shape["seconds"])
    per = max(0.005, two - float(base)) if base is not None else two / 2
    startup = max(0.0, two - 2 * per)
    return round(startup + per * len(sets) * 1.5, 2)


def _family_cli(action, sdir, out, extra=(), timeout=60):
    """Run hctf/family.py under the venv (AES zips need pyzipper) -> parsed JSON, or {"error": ...}."""
    import subprocess
    argv = [str(paths.VENV_PY), "-m", "hctf.family", action, str(sdir), "--out", str(out), *extra]
    try:
        r = subprocess.run(argv, cwd=ROOT, capture_output=True, text=True, timeout=timeout)
        return json.loads(r.stdout.strip().splitlines()[-1])
    except Exception as e:  # noqa: BLE001 - advisory
        return {"error": str(e)[:120]}


def family_probe(sdir, exts, timeout=60, noise=(), exclude=()):
    """Script lane: re-encode the failing language's fixtures of the newest verified case under OTHER known codecs
    (hctf/family.py, one language per case) and report which ones the solver can't reproduce -- the rest of the codec
    family the next variant may draw (rehearsal Day 7 replay: xor_hex arrived one cycle after reversed_base64 was fixed).
    Returns (text, [missed family case dirs])."""
    out = ROOT / ".run" / "family" / Path(sdir).resolve().parent.name
    extra = (["--n", "2"] + [a for e in sorted(exts or ()) for a in ("--ext", e)]
             + [a for e in sorted(exclude) for a in ("--exclude-ext", e)])
    d = _family_cli("probe-each", sdir, out, extra, timeout)
    if d.get("error"):
        return f"(codec-family probe skipped: {d['error']})", []
    res = d.get("results") or []
    if not res:
        return "", []
    miss = [x for x in res if not x["ok"]]
    langs = sorted(exts) if exts else sorted({x["ext"] for x in res})
    head = (f"Codec-family probe (SYNTHETIC -- {len(res)} {'/'.join(langs)} fixture(s) of cases/{d.get('base')} "
            f"re-encoded under other rep x transform names lib.codec knows, one language per case; cases in "
            f"{out.relative_to(ROOT)}/<ext>/family-*): the solver reproduces {len(res) - len(miss)}/{len(res)}.")
    if not miss:
        return head + " The declared-codec path already composes the whole family.", []
    lines = [head, "Misses (re-encoded file: new codec, wrong/total answers):"]
    lines += [f"  {x['ext']}/{x['case']}/{x['member']}: {x['spec']}  ({x['wrong']}/{x['of']}, {x['empty']} empty)"
              for x in miss[:10]]
    noisy = sorted({x["ext"] for x in miss} & set(noise))
    lines.append("Fix these in the same pass: route the declared Codec_ through lib.codec.decode instead of a per-name "
                 "table." + (f" Language(s) {noisy} are calibrated as NOISE for this lane (the solver emulates their "
                             "decode routine, which the recoding leaves unchanged) -- don't chase those." if noisy else ""))
    return "\n".join(lines), sorted({x["case_dir"] for x in miss if x["ext"] not in set(noise)})


def speed_watch_sets(res, sdir, mode):
    """For a speed-only generalize: (verified cases that are slow >= 2 s or error, {newest variant-<mode> case})."""
    targets = {r["case"] for r in (res or []) if not r.get("unverified") and (r.get("seconds", 0) >= 2.0 or r.get("error"))}
    var = sorted((Path(sdir) / "cases").glob(f"variant-{mode}-*/"), key=lambda p: p.stat().st_mtime)
    return targets, ({var[-1].name} if var else set())


def failing_artifacts(sdir, mode, ids):
    """(newest variant-<mode> case dir, [artifact names the failing ids ask about]) or (None, [])."""
    var = sorted((Path(sdir) / "cases").glob(f"variant-{mode}-*/"), key=lambda p: p.stat().st_mtime)
    if not var or not ids:
        return None, []
    try:
        qs = {q.get("id"): q for q in json.loads((var[-1] / "contract.json").read_text()).get("questions") or []}
    except (OSError, ValueError):
        return var[-1], []
    arts = []
    for a in ids:
        art = (qs.get(a) or {}).get("artifact")
        if art and art not in arts:
            arts.append(art)
    return var[-1], arts


def _exts(arts):
    return {Path(a.split("->")[-1].strip()).suffix.lstrip(".").lower() for a in arts} - {""}


def failing_evidence(sdir, mode, ids, max_files=3, lane=None, family_text=None):
    """Inline evidence for a generalize prompt: for the fields the solver got wrong/left empty on the newest
    `variant-<mode>-*` case, the artifact(s) they ask about, the head of each failing file and the same-named file from
    a PASSING case. Rehearsal Day 7: both script generalize workers spent their first 4-6 calls (ls cases, read contract,
    7z x, find the file) just reaching what this block shows."""
    from lib.common import find_artifact
    cases = Path(sdir) / "cases"
    case, arts = failing_artifacts(sdir, mode, ids)
    if not arts:
        return ""
    passing = [c for c in sorted(cases.glob("*/")) if c.name in ("single_solve",) or c.name.startswith(("auto-", "time_trial-"))]
    out = [f"Failing case `cases/{case.name}` -- {len(ids)} field(s) about {len(arts)} artifact(s): {', '.join(arts[:6])}"]
    for art in arts[:max_files]:
        member = art.split("->")[-1].strip()
        try:
            head = _text_head(find_artifact(case / "artifacts", art))
        except Exception:  # noqa: BLE001 - evidence is best-effort; the worker can always open the case itself
            head = None
        out.append(f"--- FAILING `{art}` ({case.name}):\n{head}" if head else f"--- FAILING `{art}`: binary/unreadable here")
        for c in passing:
            try:
                cq = json.loads((c / "contract.json").read_text()).get("questions") or []
                cart = next((q["artifact"] for q in cq if str(q.get("artifact", "")).split("->")[-1].strip() == member), None)
                ph = _text_head(find_artifact(c / "artifacts", cart)) if cart else None
            except Exception:  # noqa: BLE001
                ph = None
            if ph:
                out.append(f"--- PASSING counterpart `{cart}` ({c.name}) -- the solver handles this one:\n{ph}")
                break
    head = "\n".join(out)[:6000]
    extra = []
    try:
        cen = construct_census(sdir, lane, arts) if lane else ""
        if cen:
            extra.append(cen)
        toks, langs = set(), set()
        for art in arts:
            stem = Path(art.split("->")[-1].strip())
            toks.update(re.split(r"[-_.]", stem.stem))
            langs.add(_LANG_OF_EXT.get(stem.suffix.lstrip(".").lower()))
        strong = {"codec", "material", "decode"}
        m = re.search(r"have used across those cases[^:]*: (.*)", cen or "")
        if m:
            strong.update(re.findall(r"([a-z0-9_]+)\|", m.group(1)))
        langs.discard(None)
        hp = handler_pointer(sdir, toks, strong=strong, lang=next(iter(langs)) if len(langs) == 1 else None)
        if hp:
            extra.append(hp)
        if family_text is None and lane == "script-analysis" and FAMILY_PROBE and _exts(arts):
            family_text = family_probe(sdir, _exts(arts))[0]
        if family_text:
            extra.append(family_text)
    except Exception as e:  # noqa: BLE001 - advisory
        extra.append(f"(census/handler note: {e})")
    return head + ("\n\n" + "\n\n".join(extra) if extra else "")


def wait_until_expired(cid, extra=3):
    """Block until the live attempt's deadline has passed, so a retry will be accepted."""
    contract = cli.load(cid, "start.json")
    left = timed.seconds_left(contract)
    if left and left > 0:
        time.sleep(left + extra)


# ---------------------------------------------------------------- chain

class Chain:
    def __init__(self, base, entries, pools, gov, only_modes=None):
        self.base, self.pools, self.gov = base, pools, gov
        self.entries = {e["mode"]: e for e in entries}
        ss = self.entries.get("single_solve") or next(iter(self.entries.values()))
        self.lane, self.name = ss.get("lane", "misc"), ss.get("name", base)
        self.sdir = paths.solver_dir(base)
        self.root = paths.challenge_root(base)
        self.only_modes = only_modes
        (self.root / "meta.json").write_text(json.dumps({"base": base, "lane": self.lane, "name": self.name,
                                     "ids": {m: e["id"] for m, e in self.entries.items()}}, indent=2, ensure_ascii=False))

    # -- workers
    def _worker_env(self, cid, stage):
        return {"HCTF_CHAL": cid, "HCTF_BASE": self.base, "HCTF_STAGE": stage, "HCTF_SOLVER_DIR": self.sdir,
                "HCTF_CHAL_DIR": cli.cdir(cid), "HCTF_LANE": self.lane}

    def _launch_warm(self, cid):
        """Start the Single worker NOW (chain start) with the static prompt; the triage follows (WarmWorker)."""
        prior = prior_solver_dir(self.lane, self.sdir)
        if prior:
            prior_note = (f"This lane's contract is CUMULATIVE: `{prior.relative_to(ROOT)}` is the latest earlier "
                          f"solver of this lane and already answers every earlier family. FIRST copy it (all its "
                          f"files) over `{self.sdir.relative_to(ROOT)}`, then add only today's new families. "
                          "Never use an old solver's output as your answer without today's bytes behind it.")
        else:
            prior_note = "(final prior-solver note arrives in your next message)"
        pending = "(arrives in your next message, with the go signal)"
        text = workers.render("single", skill=workers.lane_skill(self.lane), triage=pending,
                              lane_helpers=workers.lane_helpers(self.lane), prior_solver=prior_note,
                              name=self.name, cid=cid, lane=self.lane, techniques=technique_log(self.lane),
                              persona=workers.lane_persona(self.lane), playbook=workers.lane_playbook(self.lane),
                              chal_dir=cli.cdir(cid).relative_to(ROOT), solver_dir=self.sdir.relative_to(ROOT),
                              timed_contracts=pending, subagent_policy=subagent_policy(self.lane), extra="")
        text += ("\n\n---\nWARM START: the harness is still starting this challenge and downloading/triaging its "
                 "artifacts. Do NOT run any tool and do not start yet: read the above, then reply with exactly READY. "
                 "Your next message carries the triage and the go signal.")
        cli.cdir(cid).mkdir(parents=True, exist_ok=True)
        say(f"[{cid}] single worker warming up beside start/download/triage")
        return workers.WarmWorker(cli.cdir(cid), "single", text, self._worker_env(cid, "single"))

    def _start_prior_dry_run(self, cid):
        """Cumulative lanes: run yesterday's solver once on today's bytes in the background (diagnostics only: speed,
        where it hangs, which ids it leaves empty -- never its values). Joined before the worker's task is sent."""
        self._dry_fut = None
        prior = prior_solver_dir(self.lane, self.sdir)
        contract = cli.load(cid, "start.json") or cli.load(cid, "contract.json")
        art = timed.latest_artifacts(cid)
        if not (PRIOR_DRY_RUN and prior and contract and art):
            return
        self._dry_fut = ThreadPoolExecutor(max_workers=1).submit(solvers.dry_run_diagnostics, prior, contract, art,
                                                                  PRIOR_DRY_RUN_SECONDS)

    def _prior_dry_run_text(self):
        fut = getattr(self, "_dry_fut", None)
        if fut is None:
            return ""
        try:
            d = fut.result(timeout=PRIOR_DRY_RUN_SECONDS + 10)
        except Exception as e:  # noqa: BLE001 - diagnostics are best-effort
            say(f"[{self.base}] prior dry run note: {e}")
            return ""
        say(f"[{self.base}] prior solver dry run: {d['seconds']}s, timed_out={d['timed_out']}, "
            f"answered {d['answered']}/{d['total']}")
        return solvers.render_dry_run(d)

    def _tool_prefetch(self, cid, source):
        """Install the preferred tools of toolchains the challenge's own text names (hctf/toolchain.py): from the name at
        chain start, then from the prompt/questions right after `start` -- before the download and the byte scan."""
        if self.lane == "welcome":
            return
        try:
            from . import toolchain
            text = source if isinstance(source, str) else toolchain.challenge_text(source, self.name)
            toolchain.prefetch(text, cid, log=say)
        except Exception as e:  # noqa: BLE001 - best-effort
            say(f"[{cid}] tool prefetch note: {e}")

    def _cancel_warm(self):
        w, self._warm = getattr(self, "_warm", None), None
        if w is not None:
            w.cancel()

    def run_worker(self, cid, stage, prompt, timeout, urgent=False, prefer_homebase=False, stop=None, warm=None,
                   warm_task=None):
        env = self._worker_env(cid, stage)
        # A warm worker is already running locally: it takes no pool slot (and so must not release one).
        acquired = not urgent and not (warm is not None and warm.alive())
        pool = self.pools.acquire(prefer_homebase) if acquired else "local"
        set_state(self.base, worker=f"{stage}@{pool}")
        say(f"[{cid}] {stage} worker -> {pool}{' (warm)' if warm is not None else ''} (timeout {timeout:.0f}s)")
        try:
            if pool == "local":
                rc, log = workers.run_local(cli.cdir(cid), stage, prompt, env, timeout, stop=stop, warm=warm,
                                            warm_task=warm_task)
            else:
                if warm is not None:
                    warm.cancel()
                rc, log = workers.run_homebase(self.root, cli.cdir(cid), stage, prompt, env, timeout)
        finally:
            if acquired:
                self.pools.release(pool)
            set_state(self.base, worker=None)
        say(f"[{cid}] {stage} worker exit {rc} ({Path(log).name})")
        return rc

    def fix(self, cid, contract, art, problems, left):
        prompt = workers.render("fix", cid=cid, base=self.base, seconds_left=int(left or 0),
                                deadline=contract.get("deadline"), chal_dir=cli.cdir(cid).relative_to(ROOT),
                                solver_dir=self.sdir.relative_to(ROOT), persona=workers.lane_persona(self.lane),
                                problems="\n".join(f"  - {p}" for p in problems) or "  - (none reported)")
        set_state(self.base, stage=f"{solvers.mode_of(cid)}:fixing")
        self.run_worker(cid, "fix", prompt, max(20, (left or 600) - 15), urgent=True)

    def generalize(self, cid, wrong=None, fixed=None, diag=None):
        """Offline (no clock): improve the solver so it handles the captured variant and still passes old cases.
        `wrong`: (answer_id, solver_value) pairs the GM rejected; `fixed`: {answer_id: value} the GM accepted as the
        right label on that attempt; `diag`: facts about the attempt (window, elapsed, how much was judged), so the
        worker is told the truth — "timing" only when every field was actually judged correct."""
        mode = solvers.mode_of(cid)
        probs = []
        fam = None
        if self.lane == "script-analysis" and FAMILY_PROBE and wrong:
            exts = _exts(failing_artifacts(self.sdir, mode, [a for a, _ in wrong])[1])
            if exts:   # runs beside the baseline replay below (~1.7 s of venv + 2 solver runs off the critical path)
                fam = ThreadPoolExecutor(max_workers=1).submit(
                    lambda: family_probe(self.sdir, exts, noise=self._family_noise())[0])
        # ONE fast parallel replay (8s/case) serves both the problem list and the transactional baseline (was a full
        # 120s/case run here plus a second baseline run: 141s before the worker spawned, replay run 2).
        ensure_case_and_test(paths.base_id(cid), self.sdir, full=False)
        res = (solvers.test_solver(self.sdir, timeout=BASELINE_CASE_TIMEOUT)
               if (self.sdir / "solve.py").exists() else [])
        self._pre_res = res
        for r in (res or []):
            if not r.get("ok"):
                probs.append(f"case {r['case']}: error={r.get('error')} diff={r.get('diff')} unverified={r.get('unverified')}")
        lines = []
        for a, v in (wrong or []):
            if fixed and a in fixed:
                lines.append(f"  - `{a}`: solver produced {v!r}; the GM REJECTED it and ACCEPTED {fixed[a]!r} on the same "
                             "attempt. Find the byte-level feature that selects this label (compare with cases where the "
                             "solver's label was right) and make solve.py emit it — never hard-code the variant.")
            else:
                lines.append(f"  - `{a}`: solver produced {v!r}, the GM judged this INCORRECT — re-derive this exact field "
                             "from the bytes and make the solver reproduce the GM's value")
        d = diag or {}
        if lines:
            gm_wrong = "\n".join(lines)
        elif wrong == [] and d.get("complete") and d.get("probed") == d.get("total"):
            gm_wrong = (f"  - every one of the {d.get('total')} fields was judged CORRECT individually, so this is a TIMING "
                        f"failure: window {d.get('window')}s, attempt took {d.get('elapsed')}s, phases {d.get('phases')}. "
                        "Do NOT change answers; reduce the solver's own time only if `solve` dominates the phases.")
        elif wrong == []:
            gm_wrong = (f"  - the probe was CUT SHORT: only {d.get('probed')}/{d.get('total')} fields were judged (all of those "
                        f"correct). The wrong field(s) are among the unjudged ones: {d.get('unjudged', [])[:40]}. "
                        "Re-derive those from the bytes. Do NOT treat this as a timing problem.")
        else:
            gm_wrong = "  - (no per-field GM verdict was available this cycle)"
        if d.get("crash"):
            gm_wrong += ("\n  - solve.py CRASHED on this variant inside the window (no JSON line -> nothing submitted). "
                         "Make every field fail independently; its stderr tail:\n"
                         + "\n".join("    " + ln for ln in d["crash"].splitlines()[-12:]))
        carry = carry_over_note(self.lane, self.sdir, [a for a, _ in (wrong or [])])
        if carry:
            gm_wrong += "\n  - " + carry
        if d.get("accepted"):
            acc = d["accepted"]
            gm_wrong += (f"\n  - the GM ACCEPTED these {len(acc)} answered field(s) on this attempt -- keep producing them: "
                         + ", ".join(f"`{a}`" for a in acc[:30]) + (" ..." if len(acc) > 30 else ""))
        if d.get("window") or d.get("elapsed"):
            gm_wrong += f"\n  - attempt facts: window {d.get('window')}s, elapsed {d.get('elapsed')}s, routed {d.get('routed') or 'local'}"
        if d.get("hb_env_mismatch"):
            gm_wrong += ("\n  - THE SOLVER PRODUCED NO ANSWERS ON HOMEBASE although it works locally: it depends on something the "
                         "Homebase VM lacks. Homebase has python3 + the pip deps (pyzipper, pyelftools, pefile, capstone, "
                         "pycryptodome, androguard, ...) but NOT 7z/p7zip or other apt tools. Open zips with "
                         "`lib.common.read_member` / pyzipper; no subprocess to 7z, jadx, or anything outside the import list.")
        if d.get("family_pre"):
            gm_wrong += ("\n  - NO TIMED ATTEMPT HAS RUN YET: the single is CORRECT, but the solver can't decode other members "
                         "of this day's codec family. The `family-*` cases are the single's own fixtures re-encoded under "
                         "other rep x transform names lib.codec knows (answers unchanged except representation/transform). "
                         "Time Trial / Mastery variants draw these: make every family-* case pass by routing declared "
                         "codecs through lib.codec.decode (generic), not by adding names to a table.\n"
                         + "\n".join("    " + ln for ln in d["family_pre"].splitlines()))
        if d.get("compound_pre"):
            gm_wrong += ("\n  - COMPOUNDING: the solver no longer answers EARLIER days' verified cases of this lane (the "
                         "`compound-dKK-*` cases: an earlier day's own bytes, contract and GM-verified answers). Mastery is "
                         "meant to compound today's concept with concepts from days past, so today's solver must still "
                         "handle every earlier day's artifact kinds and questions. Make every compound-* case pass by "
                         "dispatching on artifact type / question text (port or import the earlier day's parsing -- see "
                         "that day's solver/NOTES.md), without breaking today's cases.\n"
                         + "\n".join("    " + ln for ln in d["compound_pre"].splitlines()))
        if d.get("mutation_pre"):
            gm_wrong += ("\n  - NO TIMED ATTEMPT HAS RUN YET: the single is CORRECT, but the solver breaks on ANSWER-INVARIANT "
                         "mutations of its own case (the `mutation-*` cases: same member bytes and names, same expected "
                         "answers). Time Trial / Mastery hand out new variants with exactly these kinds of changes. Make "
                         "every mutation-* case pass by deriving the structure (resolve each question's artifact by its "
                         "container/member name or sha, route by question text / answer_id suffix, answer each field "
                         "independently, None only for a question you can't handle) -- never by special-casing the "
                         "mutation.\n" + "\n".join("    " + ln for ln in d["mutation_pre"].splitlines()))
        elif getattr(self, "_mutation_soft", None):
            gm_wrong += ("\n  - (FYI, not the target) the mutation probe also saw these softer misses -- cover them only "
                         "if it is the same small change:\n" + "\n".join("    " + ln for ln in self._mutation_soft.splitlines()))
        if d.get("single_seconds"):
            gm_wrong += (f"\n  - NO TIMED ATTEMPT HAS RUN YET: solve.py takes {d['single_seconds']}s on the Single Solve case "
                         f"itself (budget {SINGLE_SPEED_BUDGET:g}s locally; Homebase is ~1.5x slower and the 7-13 s window also "
                         "pays GM start/download/submit). Its answers are right -- make it FAST, change no answer, and "
                         "skip third-party libraries/runtime classes bundled into the artifact.")
        if d.get("solver_too_slow"):
            gm_wrong += ("\n  - THE SOLVER IS TOO SLOW: solve.py hit the in-window timeout on this variant (answers may well be right). "
                         "Make it fast -- no per-set brute force over every decoder, no subprocess per set, decode once, "
                         "early-exit on the first candidate that matches the answer_format; time it with `time hctf solver-run`.")
        if d.get("solver_too_slow") or d.get("single_seconds"):
            # The harness profiles the slow case itself (newest variant-* for an in-window timeout, else the single).
            cases = self.sdir / "cases"
            var = sorted(cases.glob("variant-*/"), key=lambda p: p.stat().st_mtime)
            prof = solvers.profile_solver(self.sdir, var[-1] if var and not d.get("single_seconds") else cases / "single_solve")
            if prof:
                gm_wrong += ("\n  - HOT PATH (harness-run profile, sorted by cumulative time -- start here, no need to re-profile):\n"
                             + "\n".join("    " + ln for ln in prof.splitlines()))
        left_att = (timed.last_result(cid) or {}).get("attempts_remaining")
        low_budget = left_att is not None and left_att < HARVEST_MIN_ATTEMPTS
        if low_budget and HARVEST_VARIANTS:
            say(f"[{cid}] only {left_att} unique attempt(s) left for this mode today: no variant harvest")
        harvest = bool(HARVEST_VARIANTS and wrong and all(v is None for _, v in wrong) and remote.gm_transport() == "local"
                       and not low_budget)
        if harvest:
            # (built BEFORE render -- until the rehearsal Day 7 review this note was appended after the prompt was rendered,
            # so no worker ever saw it)
            gm_wrong += ("\n  - MORE VARIANTS ARRIVE WHILE YOU WORK: the harness is fetching up to "
                         f"{HARVEST_VARIANTS} fresh variants of this mode in the background and saves each one the "
                         "current solver can't fully answer as another `variant-*` case. Re-run `hctf solver-test` "
                         "before you finish -- every variant-* case must come out with every field filled.")
        try:
            ftxt = ""
            if fam is not None:
                try:
                    ftxt = fam.result(timeout=60)
                except Exception as e:  # noqa: BLE001
                    ftxt = f"(codec-family probe note: {e})"
            evidence = failing_evidence(self.sdir, mode, [a for a, _ in (wrong or [])], lane=self.lane,
                                        family_text=ftxt if fam is not None else "")
        except Exception as e:  # noqa: BLE001 - advisory
            evidence = ""
            say(f"[{cid}] evidence block note: {e}")
        prompt = workers.render("generalize", cid=cid, base=self.base, mode=mode,
                                chal_dir=cli.cdir(cid).relative_to(ROOT), solver_dir=self.sdir.relative_to(ROOT),
                                persona=workers.lane_persona(self.lane), playbook=workers.lane_playbook(self.lane),
                                variant_axes=variant_axes(self.lane) or "(none recorded yet for this lane)",
                                problems="\n".join(f"  - {p}" for p in probs) or (
                                    "  - every case passes -- the problem is SPEED" if d.get("solver_too_slow")
                                    else "  - solver did not produce all answers"),
                                gm_wrong=gm_wrong,
                                evidence=evidence or "(not extracted -- open the newest variant-* case yourself)")
        set_state(self.base, stage=f"{mode}:generalizing")
        targets = {r["case"] for r in (res or []) if not r.get("ok") and not r.get("unverified")}
        # A failed variant has no GM-verified answers (unverified), so "passes" can't be judged -- but fields the solver
        # left EMPTY can: green once it answers every field of such a case (full replay: the watcher never fired, all
        # three generalize workers ran to their own end). Correctness is still checked by the accept step + GM retry.
        fill = {r["case"] for r in (res or []) if r.get("unverified") and r.get("answered", 0) < r.get("total", 0)}
        if d.get("solver_too_slow"):
            # Speed-only generalize: every case may already PASS, just slowly -> targets/fill empty, the watcher never
            # started and the worker ran to its own end (blind D7 replay: binary sped up 6 s -> 0.3 s by call 7, ~60 s
            # in, then re-derived every answer by hand until 284 s). Watch the slow case(s) for SPEED instead: green
            # once they come in under 2 s with nothing broken (_watch_green's need_fast check).
            slow_t, slow_f = speed_watch_sets(res, self.sdir, mode)
            targets |= slow_t
            fill |= slow_f
        self._snapshot_solver()
        green, done, harvesting = threading.Event(), threading.Event(), threading.Event()
        if harvest:
            harvesting.set()
        watch = threading.Thread(target=self._watch_green, daemon=True,
                                 args=(targets, set(self._baseline), bool(d.get("solver_too_slow")), green, done, fill,
                                       harvesting))
        if (targets or fill) and STOP_WHEN_READY:
            watch.start()
        reaper = None
        if harvest:   # starts after the snapshot: the harvest judges new variants with the PRE-worker solver
            reaper = threading.Thread(target=self._harvest_variants, daemon=True,
                                      args=(cid, HARVEST_VARIANTS, fill, done, harvesting))
            reaper.start()
        try:
            self.run_worker(cid, "generalize", prompt, GENERALIZE_TIMEOUT, stop=green)
        finally:
            done.set()
            if watch.is_alive():
                watch.join()
            if reaper:
                # Bounded: a GM call stuck inside the harvest must not hold the accept + retry (blind3: ~15 s after the
                # worker had already exited). A late variant just lands as one more case for the next cycle.
                reaper.join(timeout=HARVEST_JOIN_MAX)
                if reaper.is_alive():
                    say(f"[{cid}] harvest still busy {HARVEST_JOIN_MAX:g}s after the worker ended: not waiting for it")
            self._accept_or_restore(cid)
            if reaper:
                # The last harvested attempt may still be live: a retry now would RESUME it (start is idempotent
                # while the clock runs) with its clock half spent.
                scout._wait_expired(getattr(self, "_harvest_deadline", None), say, cid)

    def _harvest_variants(self, cid, n, fill, done, harvesting):
        try:
            self._harvest(cid, n, fill, done)
        finally:
            harvesting.clear()

    def _harvest(self, cid, n, fill, done):
        """Beside a generalize worker fixing EMPTY fields: start up to `n` fresh attempts of this mode (never submitted;
        a failed/expired timed attempt costs nothing on the scoreboard), download each variant into .run/harvest/, run
        the pre-worker solver snapshot on it and save every variant it leaves incomplete as a `variant-<mode>-<att8>`
        case + add it to the watcher's fill set. Never touches start.json / contract.json (the worker may read them)."""
        mode, snap = solvers.mode_of(cid), self._snap_dir()
        last = timed.last_result(cid) or {}
        prev = last.get("deadline") or (cli.load(cid, "start.json") or {}).get("deadline")
        prev_att = last.get("attempt_id")
        got = 0
        for _ in range(n):
            if not self._harvest_sleep(prev, done):
                break
            try:
                for _poll in range(8):
                    with cli.chal_lock(cid), cli.quiet():
                        env = cli.call(cid, "start", cid, timeout=HARVEST_CALL_TIMEOUT)
                        body = env.get("body") or {}
                        if env.get("http") == 200 and not body.get("error") and attempt_over(body):
                            # `start` RESUMES the latest attempt: after the failed one's deadline that is an expired or
                            # finished attempt -- with OR without its attempt_id (main's GM keeps the id: the harvest
                            # polled 8x and gave up, mainblind1 metadata) -- so re-roll a fresh variant like hb_timed.
                            env = cli.call(cid, "retry", cid, timeout=HARVEST_CALL_TIMEOUT)
                    body = env.get("body") or {}
                    if not (prev_att and cli.attempt_id(body) == prev_att) or done.wait(1.0):
                        break   # a NEW attempt (or an error / the generalize ended); same id = previous still live
                att = cli.attempt_id(body)
                if prev_att and att == prev_att:
                    break       # the generalize ended while the previous attempt was still live
                prev_att = att
                if env.get("http") != 200 or body.get("error") or not att:
                    say(f"[{cid}] harvest: start refused ({str(body)[:120]}); stopping the harvest")
                    break
                prev = self._harvest_deadline = body.get("deadline")
                dst = ROOT / ".run" / "harvest" / paths.slugify(cid) / att[:8]
                dst.mkdir(parents=True, exist_ok=True)
                plan = cli._planned_downloads(body)
                from concurrent.futures import ThreadPoolExecutor
                with ThreadPoolExecutor(max_workers=8) as ex, cli.quiet():
                    envs = list(ex.map(lambda it: cli.call(cid, "download", it[1], str(dst), "--name", it[0],
                                                           timeout=HARVEST_CALL_TIMEOUT * 2), plan))
                if not plan or not all(e.get("saved") for e in envs):
                    say(f"[{cid}] harvest: download incomplete for {att[:8]}; skipping it")
                    continue
                if not (snap / "solve.py").exists():
                    break
                ans, err, secs = solvers.run_solver(snap, body, dst, timeout=BASELINE_CASE_TIMEOUT)
                ids = body.get("answer_ids") or [q.get("id") for q in body.get("questions") or [] if q.get("id")]
                empty = [i for i in ids if ans.get(i) in (None, "")]
                if err or empty:
                    name = f"variant-{mode}-{att[:8]}"
                    solvers.add_case(self.sdir, name, body, dst, {})
                    fill.add(name)
                    got += 1
                    say(f"[{cid}] harvest: {name} -- pre-worker solver left {len(empty)}/{len(ids)} empty"
                        f"{' (' + str(err)[:60] + ')' if err else ''}; added for this generalize")
                else:
                    say(f"[{cid}] harvest: variant {att[:8]} fully answered by the pre-worker solver ({secs:.1f}s)")
            except Exception as e:  # noqa: BLE001 - advisory: the generalize proceeds on the original variant
                say(f"[{cid}] harvest note: {e}")
                break
        if got:
            say(f"[{cid}] harvest: {got} extra failing variant(s) handed to the generalize worker")

    @staticmethod
    def _harvest_sleep(deadline, done):
        """Wait out the previous attempt's clock + the GM rate gap; False if the generalize ended meanwhile."""
        left = 0.0
        if deadline:
            try:
                end = datetime.datetime.fromisoformat(str(deadline).replace("Z", "+00:00"))
                left = max(0.0, (end - datetime.datetime.now(datetime.timezone.utc)).total_seconds())
            except ValueError:
                pass
        if done.wait(left + HARVEST_GAP) or done.is_set():
            return False
        # ...and never start + download beside ANOTHER chain's live clock (GM 429s land on that attempt's download).
        end = time.time() + HARVEST_YIELD_MAX
        while timed.inflight() and time.time() < end:
            if done.wait(0.5):
                return False
        return not done.is_set()

    def _watch_green(self, targets, baseline, need_fast, green, done, fill=frozenset(), harvesting=None):
        """Beside a generalize worker: once solver code has been quiet 3s and the failing target case(s) pass with no
        previously-passing case broken (and fast, for a speed fix), end the worker -- the replays' generalize workers
        spent 22-46s after the fix on solver-test reruns, robustness checks and notes. While a variant harvest is
        still running (`harvesting` set) the worker is never ended: more failing variants may be on the way."""
        start, checked = self._solver_mtimes(), None
        while not done.wait(2.0):
            m = self._solver_mtimes()
            if not m or m == start or time.time() - max(m.values()) < 3:
                continue
            busy = bool(harvesting and harvesting.is_set())
            key = (tuple(sorted(m.items())), len(fill), busy)
            if key == checked or busy:
                continue
            checked = key
            try:
                res = solvers.test_solver(self.sdir, timeout=BASELINE_CASE_TIMEOUT)
            except Exception:  # noqa: BLE001
                continue
            if self._solver_mtimes() != m:
                continue  # edited while testing
            ok = {r["case"] for r in res if r.get("ok")}
            filled = {r["case"] for r in res if r.get("total") and r.get("answered") == r.get("total") and not r.get("error")}
            fast = all(r.get("seconds", 99) < 2.0 for r in res if r["case"] in (targets | set(fill)))
            if targets <= ok and set(fill) <= filled and baseline <= ok and (fast or not need_fast):
                self._green_res = (m, self._case_names(), res)  # _accept_or_restore reuses it (same code + cases)
                say(f"[{self.base}] generalize green ({sorted(targets | set(fill))[:3]} pass/complete, no regressions) "
                    "-> ending the worker")
                green.set()
                return

    # -- transactional generalize: a worker that is killed / times out / breaks old cases must never leave a
    #    half-edited solver behind (happened twice on the rehearsal copy: warmups solve.py, Dim and Dimmer vbsplan.py).
    def _snap_dir(self):
        return self.root / ".generalize-snapshot"

    def _snapshot_solver(self):
        snap = self._snap_dir()
        if snap.exists():
            shutil.rmtree(snap)
        if self.sdir.exists():
            shutil.copytree(self.sdir, snap, ignore=shutil.ignore_patterns("__pycache__"))
        # Baseline: which cases pass BEFORE the worker. Unverified variant cases are legitimately red; the bar is
        # "nothing that passed may break", not "everything green".
        try:
            # Short per-case timeout: a too-slow solver otherwise burns 120s PER CASE here before the generalize worker
            # can even start (rehearsal rehearsal: 4 min). A case that slow can't pass a 7s window anyway.
            res = getattr(self, "_pre_res", None)
            if res is None:
                res = (solvers.test_solver(self.sdir, timeout=BASELINE_CASE_TIMEOUT)
                       if (self.sdir / "solve.py").exists() else [])
            self._pre_res = None
            self._baseline = {r.get("case") for r in (res or []) if r.get("ok")}
        except Exception:  # noqa: BLE001
            self._baseline = set()

    def _restore_snapshot(self, why):
        snap = self._snap_dir()
        if not snap.exists():
            return
        rejected = self.root / ".generalize-rejected"
        if rejected.exists():
            shutil.rmtree(rejected)
        if self.sdir.exists():
            shutil.move(str(self.sdir), str(rejected))   # kept for inspection; never imported by the dispatcher
        shutil.move(str(snap), str(self.sdir))
        say(f"[{self.base}] generalize REJECTED ({why}); solver restored to its pre-worker state "
            f"(worker's version kept in {rejected.relative_to(ROOT)})")

    def _accept_or_restore(self, cid):
        """After the generalize worker exits for ANY reason: keep its edits only if every case that passed before
        still passes (and the solver still runs at all)."""
        snap = self._snap_dir()
        if not snap.exists():
            return
        cached, self._green_res = getattr(self, "_green_res", None), None
        try:
            if cached and cached[0] == self._solver_mtimes() and cached[1] == self._case_names():
                # The watcher just ran the full suite on this exact code + case set and found no regression: a second
                # run only adds 5-10 s between "green" and the retry (rehearsal Day 7: 14 s / 20 s gaps on the script lane).
                res = cached[2]
            else:
                res = solvers.test_solver(self.sdir) if (self.sdir / "solve.py").exists() else []
        except Exception as e:  # noqa: BLE001
            res = None
            err = repr(e)
        passed = {r.get("case") for r in (res or []) if r.get("ok")}
        broken = sorted(getattr(self, "_baseline", set()) - passed)
        if res and not broken:
            shutil.rmtree(snap)
            gained = sorted(passed - getattr(self, "_baseline", set()))
            if gained:
                say(f"[{self.base}] generalize accepted: now also passes {gained[:6]}")
            return
        self._restore_snapshot(f"broke previously-passing cases {broken[:6]}" if res else
                               f"solver no longer runs ({err if res is None else 'no solve.py / no cases'})")

    def recover_interrupted_generalize(self):
        """A snapshot left on disk means the orchestrator died mid-generalize (killed run): restore it."""
        if self._snap_dir().exists():
            self._restore_snapshot("previous run was interrupted mid-generalize")

    def try_existing_solvers(self, cid):
        """Merged reuse (no model time): run EVERY same-lane solver (+ question-text matches) on the full contract,
        merge per field, and submit what they agree on -- partial is fine, the untimed GM accepts it and pins each
        field. Seeds this challenge's solver from the best one. Returns True if the single is complete; otherwise
        self._reuse_note tells the worker exactly which fields are left (it starts from the seeded solver)."""
        self._reuse_note = ""
        contract = cli.load(cid, "start.json") or cli.load(cid, "contract.json")
        art = timed.latest_artifacts(cid)
        if not contract or not art:
            return False
        ids = list(contract.get("answer_ids") or [])
        t0 = time.time()
        plan = solvers.reuse_plan(contract, art, self.lane, exclude=[self.sdir])
        high, spec, alts = plan["high"], plan["spec"], plan["alts"]
        if not high and not spec:
            say(f"[{cid}] reuse: no prior solver answers any of {len(ids)} field(s) ({len(plan['runs'])} tried)")
            return False
        set_state(self.base, stage="single:reuse")
        say(f"[{cid}] reuse: {len(high)} confident + {len(spec)} speculative of {len(ids)} field(s) from "
            f"{len(plan['runs'])} solver(s) in {time.time() - t0:.1f}s; seed {plan['best'] and plan['best'].parent.name}")
        budget = [REUSE_PROBE_BUDGET]
        wrong = set()

        def narrow(group):
            """Submit a group; on incorrect, bisect (probe-tagged) until the wrong fields are isolated."""
            group = {a: v for a, v in group.items() if a not in cli.confirmed_answers(cid)}
            if not group or budget[0] <= 0 or cli.is_complete(cid):
                return
            budget[0] -= 1
            kind, _body, refused = cli.submit(cid, group, force=True, probe=True)
            if kind in ("correct", "accepted") or refused:
                return
            if len(group) == 1:
                wrong.update(group)
                return
            keys = list(group)
            narrow({k: group[k] for k in keys[:len(keys) // 2]})
            narrow({k: group[k] for k in keys[len(keys) // 2:]})

        narrow(high)
        rest = {a: v for a, v in spec.items() if a not in cli.confirmed_answers(cid)}
        left = [a for a in ids if a not in cli.confirmed_answers(cid)]
        if rest and set(left) <= set(rest):
            narrow(rest)  # speculative values only when they could finish it (Day 6 binary: 8/8 were wrong)
        for a in sorted(wrong):  # a field judged wrong: try the other solvers' distinct values (Day 4 mobile)
            for v in [x for x in alts.get(a, []) if x != high.get(a, spec.get(a))][:3]:
                if budget[0] <= 0 or a in cli.confirmed_answers(cid):
                    break
                budget[0] -= 1
                if cli.submit(cid, {a: v}, force=True, probe=True)[0] in ("correct", "accepted"):
                    break
        self._probe_enums(cid, contract)
        # Seed this challenge's own solver from the best prior one (the worker extends it; timed modes run it).
        best = plan["best"]
        if best and not (self.sdir / "solve.py").exists():
            shutil.copytree(best, self.sdir, dirs_exist_ok=True, ignore=shutil.ignore_patterns("cases", "__pycache__"))
        conf = cli.confirmed_answers(cid)
        if cli.is_complete(cid):
            got, err, _ = solvers.run_solver(self.sdir, contract, art)
            missing = sorted(a for a, v in conf.items() if got.get(a) != v)
            if not err and not missing:
                ensure_case_and_test(cid, self.sdir, full=False)
                say(f"[{cid}] solved by merged reuse in {time.time() - t0:.1f}s (seed reproduces every answer)")
                return True
            # Complete, but the answers came from several solvers: the worker only has to make the seed emit them.
            self._reuse_note = (f"\nREUSE PRE-PASS: the Single Solve is already CORRECT (merged from several prior solvers). "
                                f"Your only job: make `{_rel(self.sdir)}/solve.py` (seeded from "
                                f"{best and _rel(best)}) also emit these confirmed answers, then STOP: "
                                f"{json.dumps({a: conf[a] for a in missing[:40]})}")
            return False
        remaining = [a for a in ids if a not in conf]
        hints = {a: spec[a] for a in remaining if a in spec}
        self._reuse_note = (
            f"\nREUSE PRE-PASS (already done by the harness, {time.time() - t0:.0f}s): {len(conf)}/{len(ids)} answers are "
            f"ALREADY ACCEPTED by the GM (see confirmed.json) -- do not re-derive or re-submit them. "
            f"`{_rel(self.sdir)}/solve.py` is seeded from `{best and _rel(best)}` and already emits "
            f"most of them: run `hctf solver-run {cid}` first. Only these {len(remaining)} answer_id(s) are left: "
            f"{', '.join(remaining[:80])}{' ...' if len(remaining) > 80 else ''}."
            + (f" Unverified values older solvers produced for some of them (hints, may be wrong): "
               f"{json.dumps(dict(list(hints.items())[:20]))}." if hints else "")
            + (f" Judged WRONG by the GM: {', '.join(sorted(wrong)[:20])}." if wrong else ""))
        say(f"[{cid}] reuse: {len(conf)}/{len(ids)} accepted; worker gets the {len(remaining)} remaining field(s)")
        return False

    def _probe_enums(self, cid, contract, budget=None):
        """Enum fields still open after reuse: try the options the QUESTION names (subset of answer_format.accepted_values,
        in question order), one per submit. The untimed single judges each; on a new script language this resolves the
        role of an unseen behavior graph without an LLM (the lane solver leaves exactly those for want of evidence)."""
        budget = [ENUM_PROBE_BUDGET if budget is None else budget]
        done = 0
        for aid, q in solvers.paired_questions(contract):
            if aid in cli.confirmed_answers(cid) or budget[0] <= 0:
                continue
            fmt = q.get("answer_format") or {}
            allowed = fmt.get("accepted_values") or []
            if fmt.get("kind") != "enum" or not allowed:
                continue
            text = q.get("question") or ""
            named = sorted((v for v in allowed if re.search(rf"(?<![\w-]){re.escape(v)}(?![\w-])", text)), key=text.find)
            for v in named or allowed:
                if budget[0] <= 0:
                    break
                budget[0] -= 1
                if cli.submit(cid, {aid: v}, force=True, probe=True)[0] in ("correct", "accepted"):
                    done += 1
                    break
        if done:
            say(f"[{cid}] enum probe: resolved {done} field(s) from the options their questions list")

    def auto_labels(self, cid, budget=12):
        """No-model fallback after a Single Solve worker stops short: for each still-unconfirmed field whose ending
        has a known label vocabulary (lib/vocab.json / sibling confirmed labels), run the label resolver with the
        solver's own value as the term source. Returns cli.is_complete(cid)."""
        from . import labels
        contract = cli.load(cid, "start.json")
        art = timed.latest_artifacts(cid)
        if not contract or not art or not (self.sdir / "solve.py").exists():
            return False
        try:
            answers, _ = solvers.solve_contract(contract, art, default_solver=self.sdir)
        except Exception:  # noqa: BLE001
            return False
        conf = cli.confirmed_answers(cid)
        vocab = labels.load_vocab()
        for aid in contract.get("answer_ids") or []:
            has_playbook = bool(labels.playbook and labels.playbook.entry_for(self.lane, aid))
            if aid in conf or (labels.ending(aid) not in vocab and not labels.sibling_labels(aid) and not has_playbook):
                continue
            cands = labels.candidates(cid, aid, solver_value=answers.get(aid), lane=self.lane)
            if answers.get(aid) and answers[aid] not in labels.judged_wrong(cid, aid):
                cands = [answers[aid]] + cands
            r = labels.probe(cid, aid, cands, budget=budget, log=say)
            say(f"[{cid}] auto-labels {aid}: {r.get('accepted') or 'not resolved'} ({len(r.get('tried', []))} tried)")
        return cli.is_complete(cid)

    def _record_labels(self, cid):
        # Cache the Single Solve's confirmed closed-vocab labels into vocab.json NOW (untimed), so the timed
        # modes enter with those spellings already confirmed and never carry an unconfirmed label onto a clock.
        try:
            from . import labels
            labels.record_from_confirmed(cid, lane=self.lane, log=say)
        except Exception as e:  # noqa: BLE001 - label caching is best-effort
            say(f"[{cid}] label cache note: {e}")

    # -- stages
    def single(self):
        e = self.entries.get("single_solve")
        if not e:
            return True
        cid = e["id"]
        self._start_family_calibration()   # background; consumed after the single (pre-attempt family probe)
        welcome = self.lane == "welcome"
        # A mode with no local trace at all (fresh drop: no start.json / submissions yet) can't be solved by us yet:
        # skip gm_solved's status round trip (~2s on every lane at the drop) -- `start` below answers it anyway.
        fresh = not any((cli.cdir(cid) / f).exists() for f in ("start.json", "submissions.jsonl", "solved_once"))
        if cli.is_complete(cid) or (not fresh and cli.gm_solved(cid)):
            # Solved: a solver that exists is good enough to proceed. Failing auto-* variant cases are the timed
            # stages' business (they feed the generalize worker); they must not relaunch the Single Solve worker.
            if welcome or (self.sdir / "solve.py").exists() or all(
                    cli.gm_solved(self.entries[m]["id"]) for m in ("time_trial", "mastery") if m in self.entries):
                if not welcome:
                    ok, _ = ensure_case_and_test(cid, self.sdir)
                    say(f"[{cid}] already solved (solver regression {'ok' if ok else 'has failing cases'})")
                return True
        set_state(self.base, stage="single:fetch")
        self._warm = None
        if WARM_WORKERS and not welcome:
            try:
                self._warm = self._launch_warm(cid)
            except Exception as e:  # noqa: BLE001 - warm start is an optimization; cold launch below
                say(f"[{cid}] warm worker note: {e}")
        # Tools for a toolchain the challenge NAME already names (e.g. "Swift Justice") start installing now.
        self._tool_prefetch(cid, self.name)
        # Timed contracts (status only: no clock starts) are prefetched BESIDE start/download/triage, not after them.
        self._tstatus = {}
        tmodes = [m for m in ("time_trial", "mastery") if m in self.entries]

        def fetch(m):  # both timed contracts at once (no clock starts on a status call)
            tcid = self.entries[m]["id"]
            st = cli.call(tcid, "status", tcid)["body"] or {}
            self._tstatus[m] = st.get("error") or st.get("result")
            if st.get("questions"):
                cli.save(tcid, "contract.json", st)
            return f"  - {m}: `{tcid}` -> `{cli.cdir(tcid).relative_to(ROOT)}/contract.json`"
        tpool = ThreadPoolExecutor(max_workers=2)
        tfuts = [tpool.submit(fetch, m) for m in tmodes]
        tpool.shutdown(wait=False)
        body, err = timed.ensure_started(cid)
        self._tool_prefetch(cid, (body or {}))   # the prompt + questions arrive with `start`: before any download
        self._start_prior_dry_run(cid)
        # The GM sometimes hands the flag back directly (issued_flag, e.g. orientation challenges). Use it instead of
        # solving when there's a single answer_id to put it in — a free first-blood the harness used to discard.
        fb = body or {}
        if fb.get("issued_flag") and len(fb.get("answer_ids") or []) == 1 and not cli.is_complete(cid):
            cli.submit(cid, {fb["answer_ids"][0]: fb["issued_flag"]})
            if cli.is_complete(cid):
                say(f"[{cid}] solved via GM issued_flag (no solver needed)")
                self._cancel_warm()
                return True
        # Reuse-first (no model time): a prior solver matched by question text may already solve this. Try it
        # BEFORE triage so a hit skips triage and the LLM worker entirely — the fastest path to first blood.
        if not welcome and REUSE_OLD_SOLVERS and self.try_existing_solvers(cid):
            say(f"[{cid}] solved by existing solver library (no worker needed)")
            self._cancel_warm()
            return True
        if not welcome and not (self.sdir / "solve.py").exists():
            # Nothing reusable: start the worker from the harness skeleton (contract I/O, per-set loop, sha256-paired
            # artifact lookup incl. Mastery's 'delivery N: x.apk' names) instead of hunting for a template (10-15s per
            # lane in the replays; mobile's single never handled Mastery naming -> a 2.5-min generalize).
            self.sdir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / "hctf" / "templates" / "solve_skeleton.py", self.sdir / "solve.py")
        try:
            from . import triage as triage_mod
            triage_mod.triage(cid)  # deterministic grounding before the LLM worker starts
        except Exception as e:  # noqa: BLE001 - triage is best-effort
            say(f"[{cid}] triage note: {e}")
        if body is None:
            # e.g. read-the-rules: no artifact, but the contract still names the answer ids
            st = cli.call(cid, "status", cid)["body"] or {}
            if st.get("answer_ids") or st.get("questions"):
                cli.save(cid, "contract.json", st)
                if not cli.load(cid, "start.json"):
                    cli.save(cid, "start.json", st)
        timed_info = []
        for f in tfuts:
            try:
                timed_info.append(f.result())
            except Exception as e:  # noqa: BLE001 - the prompt just lists fewer contracts
                say(f"[{cid}] timed contract prefetch note: {e}")
        for n in range(MAX_SINGLE_LAUNCHES):
            extra = ""
            notes = cli.cdir(cid) / "notes.md"
            if n and notes.exists():
                extra = (f"\nThis is relaunch #{n}: a previous worker stopped before finishing. Read `{notes.relative_to(ROOT)}` "
                         "first, do not repeat its dead ends, and pick the most promising unexplored lead.")
            if welcome:
                extra += "\nThis is an orientation challenge: no solver is needed, only a correct submission."
            extra += getattr(self, "_reuse_note", "")
            prior = prior_solver_dir(self.lane, self.sdir)
            if prior:
                prior_note = (f"This lane's contract is CUMULATIVE: `{prior.relative_to(ROOT)}` is the latest earlier "
                              f"solver of this lane and already answers every earlier family. FIRST copy it (all its "
                              f"files) over `{self.sdir.relative_to(ROOT)}`, then add only today's new families. "
                              "Never use an old solver's output as your answer without today's bytes behind it.")
                dry = self._prior_dry_run_text() if n == 0 else ""
                if dry:
                    prior_note += "\n" + dry
            else:
                prior_note = ("Write the solver from the skeleton + the lane helpers below; don't go looking for earlier "
                              "days' solvers (replays lost 13-24 s per run doing that).")
                tids = []
                for m in ("time_trial", "mastery"):
                    tc = cli.load(f"{self.base}/{m}", "contract.json") or {}
                    tids += list(tc.get("answer_ids") or []) + [q.get("id") or "" for q in tc.get("questions") or []]
                carry = carry_over_note(self.lane, self.sdir, tids)
                if carry:
                    prior_note += " EXCEPT: the timed contracts already carry earlier days' questions. " + carry
            delta = mastery_delta(cli.load(cid, "start.json") or cli.load(cid, "contract.json"),
                                  [cli.load(f"{self.base}/{m}", "contract.json") or {} for m in ("time_trial", "mastery")])
            if delta:
                prior_note += " " + delta
                say(f"[{cid}] {delta[:200]}")
            prompt = workers.render("single", skill=workers.lane_skill(self.lane), triage=triage_summary(cid),
                                    lane_helpers=workers.lane_helpers(self.lane), prior_solver=prior_note,
                                    name=self.name, cid=cid, lane=self.lane, techniques=technique_log(self.lane),
                                    persona=workers.lane_persona(self.lane), playbook=workers.lane_playbook(self.lane),
                                    chal_dir=cli.cdir(cid).relative_to(ROOT), solver_dir=self.sdir.relative_to(ROOT),
                                    timed_contracts="\n".join(timed_info) or "  - (none: Single Solve only)",
                                    subagent_policy=subagent_policy(self.lane), extra=extra)
            set_state(self.base, stage="single:solving", launches=n + 1)
            heavy = self.lane in ("binary-reverse-engineering", "binary")
            ready, done_evt, watch = threading.Event(), threading.Event(), None
            self._ready_snap = None
            if STOP_WHEN_READY and not welcome:
                watch = threading.Thread(target=self._watch_ready, args=(cid, ready, done_evt), daemon=True)
                watch.start()
            warm, self._warm = (self._warm, None) if n == 0 else (None, None)
            warm_task = None
            if warm is not None:
                warm_task = ("GO. The artifacts are downloaded and triaged; everything in your first message stands. "
                             "Here are the parts that were pending -- start now.\n\n## Triage (deterministic, already "
                             f"computed)\n{triage_summary(cid)}\n\n## Time Trial / Mastery contracts (status-time)\n"
                             + ("\n".join(timed_info) or "  - (none: Single Solve only)")
                             + f"\n\n## Prior-solver note (final version)\n{prior_note}\n{extra}")
            try:
                rc = self.run_worker(cid, "single", prompt, SINGLE_TIMEOUT, prefer_homebase=heavy, stop=ready,
                                     warm=warm, warm_task=warm_task)
            finally:
                done_evt.set()
                if watch:
                    watch.join()
            if rc == workers.STOPPED_RC and self._ready_snap:
                # Ended on purpose: CORRECT + verified solver. Restore the verified files, record the single as a
                # regression case and go straight to the timed modes (the full-suite replay is not needed: the
                # snapshot was just verified on this exact case).
                self._restore_ready_snapshot(self._ready_snap)
                ensure_case_and_test(cid, self.sdir, full=False)
                say(f"[{cid}] after worker: stopped at CORRECT with a verified solver")
                self._record_labels(cid)
                self._start_family_pre(cid)
                self._start_mutation_pre(cid)
                self._start_compound_pre(cid)
                return True
            done = cli.is_complete(cid)
            if not done and not welcome:
                done = self.auto_labels(cid)
            ok, res = (True, None) if welcome else ensure_case_and_test(cid, self.sdir)
            say(f"[{cid}] after worker: complete={done} solver_ok={ok}")
            if ok and isinstance(res, list):
                self._note_single_speed(cid, next((r.get("seconds") for r in res if r.get("case") == "single_solve"), None))
            if done and ok:
                self._record_labels(cid)
                self._start_family_pre(cid)
                self._start_mutation_pre(cid)
                self._start_compound_pre(cid)
                return True
            if (cli.cdir(cid) / "HELP.md").exists():
                set_state(self.base, stage="single:help", help=(cli.cdir(cid) / "HELP.md").read_text()[:1500])
                return False
        set_state(self.base, stage="single:blocked")
        return False

    # -- early handoff (speculative timed attempts while the Single Solve worker is still running)
    def _case_names(self):
        return sorted(p.name for p in (self.sdir / "cases").glob("*/"))

    def _solver_mtimes(self):
        if not self.sdir.exists():
            return {}
        # Solver CODE only: a late NOTES.md / scratch write must not reset the stability clock (Day 6).
        return {p.name: p.stat().st_mtime for p in self.sdir.iterdir() if p.is_file() and p.suffix == ".py"}

    def _submit_stamp(self, cid, mtimes):
        """The stamp `hctf submit --from-solver` wrote, if it was made by exactly this solver code (else None)."""
        try:
            st = json.loads((cli.cdir(cid) / ".solver_stamp.json").read_text())
        except (OSError, ValueError):
            return None
        return st if st.get("mtimes") == mtimes and isinstance(st.get("answers"), dict) else None

    def _spec_snapshot(self, cid):
        """Copy the worker's in-progress solver (minus cases) to `.run/spec-dayNN/<chal>/solver` -- the same depth as
        challenges/dayNN/<chal>/solver, since solvers locate the project root via parents[N] -- if its files have been
        stable for SPEC_STABLE s and it reproduces the GM-confirmed Single Solve answers. Returns the dir or None."""
        m0 = self._solver_mtimes()
        stamp = self._submit_stamp(cid, m0)
        if "solve.py" not in m0 or (not stamp and time.time() - max(m0.values()) < SPEC_STABLE):
            return None
        if m0 == getattr(self, "_spec_rejected", None):
            return None  # this exact solver already failed verification; wait for the worker to change it
        contract, art, conf = cli.load(cid, "start.json"), timed.latest_artifacts(cid), cli.confirmed_answers(cid)
        if not (contract and art and conf):
            return None
        rel = self.sdir.relative_to(paths.CHALLENGES).parts  # (dayNN, <chal>, solver)
        if len(rel) != 3:
            return None
        snap = ROOT / ".run" / f"spec-{rel[0]}" / rel[1] / "solver"
        if snap.exists():
            shutil.rmtree(snap)
        shutil.copytree(self.sdir, snap, ignore=shutil.ignore_patterns("cases", "__pycache__"))
        if (self.root / "meta.json").exists():
            shutil.copy2(self.root / "meta.json", snap.parent / "meta.json")  # hb_timed reads the lane from it
        if self._solver_mtimes() != m0:
            return None  # the worker edited mid-copy; next poll
        if stamp and all(stamp["answers"].get(k) == v for k, v in conf.items()):
            # `hctf submit --from-solver` just ran this exact code and it produced every confirmed answer: no re-run.
            self._note_single_speed(cid, stamp.get("seconds"))
            return snap
        got, err, dt = solvers.run_solver(snap, contract, art)
        bad = sorted(k for k, v in conf.items() if got.get(k) != v)
        if err or bad:
            self._spec_rejected = m0
            say(f"[{cid}] early handoff: snapshot not ready ({err or f'{len(bad)} field(s) differ, e.g. {bad[:3]}'})")
            return None
        self._note_single_speed(cid, dt)
        return snap

    # -- codec-family probe BEFORE the first timed attempt (script lane). blind2/blind3: the Time Trial passed clean, then
    #    Mastery met the next member of the bash codec family (bash-advanced-tokens) -- a failed attempt, an escalated
    #    next variant and a generalize every run. The probe only ran inside a generalize, i.e. too late.
    def _start_family_calibration(self):
        """Background, at single start: which fixture languages the probe can judge for this lane (calibrated on the
        previous day's final solver; VBScript is noise -- its solver emulates the decode routine)."""
        self._fam_noise_fut = None
        if self.lane != "script-analysis" or not FAMILY_PROBE:
            return
        prior = prior_solver_dir(self.lane, self.sdir)
        if prior:
            out = ROOT / ".run" / "family" / f"calib-{prior.parent.name}"
            self._fam_noise_fut = ThreadPoolExecutor(max_workers=1).submit(_family_cli, "calibrate", prior, out, (), 120)

    def _family_noise(self):
        """Calibrated noise languages, or None if no calibration is available (then never act pre-emptively)."""
        fut = getattr(self, "_fam_noise_fut", None)
        if fut is None:
            return None
        try:
            d = fut.result(timeout=60)
        except Exception:  # noqa: BLE001
            return None
        return None if d.get("error") else set(d.get("noise") or [])

    def _start_mutation_pre(self, cid):
        """Background, once the single's solver is final: the answer-invariant mutation probe (every lane)."""
        self._mut_pre_fut = None
        if not MUTATION_PROBE or not (self.sdir / "solve.py").exists():
            return
        mc = cli.cdir(f"{self.base}/mastery") / "contract.json"
        self._mut_pre_fut = ThreadPoolExecutor(max_workers=1).submit(mutation_probe, self.sdir, mc)

    def _mutation_pre_result(self, wait=True):
        """wait=False (the single is too slow, a speed generalize is coming anyway): take the result only if the probe
        already finished -- mainblind4: waiting on a 6.5 s solver's probe held binary's critical path ~13 s."""
        if getattr(self, "_mut_pre_fut", None) is None:
            if not wait:
                return "", []
            self._start_mutation_pre(self.base)   # single solved by an earlier run: probe now (a few seconds)
        fut = getattr(self, "_mut_pre_fut", None)
        if fut is None or (not wait and not fut.done()):
            return "", []
        try:
            txt, cases, summ = fut.result(timeout=100)
            self._mut_summary = summ   # its mastery-shape timing feeds the Mastery speed gate
            return txt, cases
        except Exception as e:  # noqa: BLE001
            say(f"[{self.base}] mutation pre-probe note: {e}")
            return "", []

    def _start_compound_pre(self, cid):
        """Background, once the single's solver is final: the compounding probe (earlier days' verified cases)."""
        self._cmp_pre_fut = None
        if not COMPOUND_PROBE or not (self.sdir / "solve.py").exists():
            return
        self._cmp_pre_fut = ThreadPoolExecutor(max_workers=1).submit(compound_probe, self.sdir)

    def _compound_pre_result(self, wait=True):
        if getattr(self, "_cmp_pre_fut", None) is None:
            if not wait:
                return "", []
            self._start_compound_pre(self.base)
        fut = getattr(self, "_cmp_pre_fut", None)
        if fut is None or (not wait and not fut.done()):
            return "", []
        try:
            txt, hard, _ = fut.result(timeout=COMPOUND_PROBE_SECONDS + 60)
            return txt, hard
        except Exception as e:  # noqa: BLE001
            say(f"[{self.base}] compound pre-probe note: {e}")
            return "", []

    def _late_probes(self, cid, wait=True):
        """Probes that run beside the first Time Trial (mutation + compounding): adopt hard misses as regression cases.
        Returns the diag dict for a generalize ({} when clean). Each result is consumed once."""
        pre = {}
        if not getattr(self, "_mut_late_done", False):
            mtxt, mcases = self._mutation_pre_result(wait=wait)
            if mcases or mtxt or wait:
                self._mut_late_done = True
            if mcases:
                n = self._adopt_mutation_cases(mcases)
                say(f"[{cid}] mutation probe: the single's solver breaks on {len(mcases)} answer-invariant mutation(s) "
                    f"({n} adopted as mutation-* regression cases)")
                pre["mutation_pre"] = mtxt
            elif mtxt:
                say(f"[{cid}] mutation probe (soft only, no action): {mtxt.splitlines()[0]}")
                self._mutation_soft = mtxt
        if not getattr(self, "_cmp_late_done", False):
            ctxt, hard = self._compound_pre_result(wait=wait)
            if hard or ctxt or wait:
                self._cmp_late_done = True
            if hard:
                from . import compound
                n = compound.adopt(self.sdir, hard)
                say(f"[{cid}] compounding probe: the solver lost {len(hard)} earlier-day case(s) of this lane "
                    f"({n} adopted as compound-dKK-* regression cases)")
                pre["compound_pre"] = ctxt
        return pre

    def _adopt_mutation_cases(self, case_dirs):
        """Copy failing HARD mutation cases into cases/ as verified regression cases (answers = the single's
        GM-verified answers: every mutation is answer-invariant)."""
        n = 0
        for cd in case_dirs:
            src = Path(cd)
            if not (src / "expected.json").exists():
                continue
            dst = self.sdir / "cases" / src.name
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst, ignore=shutil.ignore_patterns("mutation.json"))
            n += 1
        return n

    def _start_family_pre(self, cid):
        """Background, once the single's solver is final: probe it on every judgeable language."""
        self._fam_pre_fut = None
        if self.lane != "script-analysis" or not FAMILY_PROBE or getattr(self, "_fam_noise_fut", None) is None:
            return

        def run():
            noise = self._family_noise()
            if noise is None:
                return "", []
            return family_probe(self.sdir, None, noise=noise, exclude=noise)
        self._fam_pre_fut = ThreadPoolExecutor(max_workers=1).submit(run)

    def _family_pre_result(self):
        fut = getattr(self, "_fam_pre_fut", None)
        if fut is None:
            return "", []
        try:
            return fut.result(timeout=90)
        except Exception as e:  # noqa: BLE001
            say(f"[{self.base}] family pre-probe note: {e}")
            return "", []

    def _adopt_family_cases(self, case_dirs):
        """Copy missed family cases into cases/ as verified regression cases (judgeable languages only: their expected
        answers are the GM-verified base answers with representation/transform rewritten)."""
        n = 0
        for cd in case_dirs:
            src = Path(cd)
            if not (src / "expected.json").exists():
                continue
            dst = self.sdir / "cases" / f"family-{src.parent.name}-{src.name.split('-')[-1]}"
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst, ignore=shutil.ignore_patterns("recoded.json"))
            n += 1
        return n

    def _mastery_speed_gate(self, cid):
        """Before the first Mastery attempt: estimate the Mastery solve from the mutation probe's 2-set mastery-shape
        run and compare it with the Time Trial's known window (Mastery windows were 1-2.7x TT on D3-D8). Way over ->
        one speed generalize first (no attempt spent). Advisory: no estimate or no TT window -> nothing."""
        if getattr(self, "_mastery_gate_done", False):
            return
        self._mastery_gate_done = True
        tt = self.entries.get("time_trial")
        try:
            tt_win = float(json.loads((cli.cdir(tt["id"]) / "window.json").read_text()).get("seconds")) if tt else None
        except (OSError, ValueError, TypeError):
            tt_win = None
        est = mastery_estimate(getattr(self, "_mut_summary", None), cli.cdir(cid) / "contract.json")
        if not est or not tt_win:
            return
        limit = MASTERY_GATE_RATIO * tt_win
        say(f"[{cid}] Mastery speed estimate {est:g}s (TT window {tt_win:g}s, gate {limit:g}s)")
        if est > limit:
            say(f"[{cid}] estimated Mastery solve {est:g}s > {limit:g}s: generalizing for speed BEFORE Mastery")
            self.generalize(cid, wrong=None, fixed=None, diag={"solver_too_slow": True, "mastery_estimate": est,
                                                                 "single_seconds": est})

    def _note_single_speed(self, cid, seconds):
        self._single_slow = None
        if SINGLE_SPEED_BUDGET and seconds and seconds > SINGLE_SPEED_BUDGET:
            self._single_slow = round(seconds, 2)
            say(f"[{cid}] single solver takes {seconds:.1f}s on its own case (budget {SINGLE_SPEED_BUDGET:g}s): "
                "speed generalize before the first timed attempt")

    def _watch_ready(self, cid, ready, done):
        """Runs beside the Single Solve worker. The moment the single is CORRECT and the worker's solver (stable 2s)
        reproduces every GM-confirmed answer, keep that verified snapshot and set `ready`: run_local then ends the
        worker and the timed modes start from the snapshot at once. Day 6: 60% of worker time (1101/1850s) came after
        the first CORRECT, and every first-correct snapshot already passed its real TT+Mastery variants offline."""
        try:
            while not done.wait(SPEC_POLL):
                if cli.is_complete(cid):
                    snap = self._spec_snapshot(cid)
                    if snap:
                        self._ready_snap = snap
                        say(f"[{cid}] single CORRECT + solver verified -> ending the worker, timed modes start now")
                        ready.set()
                        return
        except Exception as e:  # noqa: BLE001 - the watcher must never hurt the chain
            say(f"[{cid}] ready-watch note: {e}")

    def _restore_ready_snapshot(self, snap):
        """After a stopped worker: put the verified snapshot's files back over the live solver (the worker may have been
        mid-edit when it was ended). cases/ in the live dir is kept."""
        for src in snap.rglob("*"):
            if src.is_file() and "__pycache__" not in src.parts:
                dst = self.sdir / src.relative_to(snap)
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)

    @staticmethod
    def _clock_expiry(cid):
        """The last attempt expired although the solver answered everything: the clock, not the solver. A GM-judged
        WRONG answer is the solver even when the clock then ran out (Day 7 warmups Mastery: full submit 'incorrect' on
        set1, the in-window per-set localize ate the rest of the 9s clock -> 'expired', and the lane was blocked as
        "timing")."""
        last = timed.last_result(cid) or {}
        judged_wrong = last.get("full_result") == "incorrect" or any(
            (v or {}).get("result") == "incorrect" for v in (last.get("per_set") or {}).values())
        return ((last.get("phases") or {}).get("solve") is not None and not last.get("missing")
                and not judged_wrong)

    def timed_stage(self, mode):
        e = self.entries.get(mode)
        if not e:
            return True
        cid = e["id"]
        # This run saw the mode `start_required` minutes ago and nothing else attempts it: skip the GM status call
        # (2-7s per mode on the critical path, replay run 3).
        seen_fresh = getattr(self, "_tstatus", {}).get(mode) == "start_required"
        if cli.is_complete(cid) or (not seen_fresh and cli.gm_solved(cid)):
            return True
        if not getattr(self, "_pre_attempt_done", False):
            self._pre_attempt_done = True
            pre = {}
            if getattr(self, "_single_slow", None):
                say(f"[{cid}] solver too slow on the single ({self._single_slow}s): generalizing for speed BEFORE the "
                    "first timed attempt (no attempt spent)")
                pre.update(solver_too_slow=True, single_seconds=self._single_slow)
            ftxt, fcases = self._family_pre_result()
            if fcases:
                n = self._adopt_family_cases(fcases)
                say(f"[{cid}] codec-family probe: the single's solver misses {len(fcases)} re-encoded case(s) "
                    f"({n} adopted as family-* regression cases): generalizing BEFORE the first timed attempt")
                pre["family_pre"] = ftxt
            # Mutation + compounding probes run BESIDE the first Time Trial (mutation probe: 0 hits in mainblind3-7 + D8;
            # it held binary ~5 s): take them now only if already done; Mastery (or a TT-failure generalize) awaits them.
            # A later mode with no TT before it (TT already passed) waits for them here.
            # A speed-only generalize doesn't wait for them either (rehearsal D8 binary: ~10 s idle before the worker launched);
            # Mastery still awaits them below.
            speed_only = mode == "time_trial" and bool(pre) and set(pre) <= {"solver_too_slow", "single_seconds"}
            pre.update(self._late_probes(cid, wait=(mode != "time_trial" or bool(pre)) and not speed_only))
            if pre:
                self.generalize(cid, wrong=None, fixed=None, diag=pre)
        elif mode != "time_trial":
            late = self._late_probes(cid, wait=True)
            if late:
                say(f"[{cid}] probes that ran beside the Time Trial found misses: generalizing BEFORE Mastery")
                self.generalize(cid, wrong=None, fixed=None, diag=late)
        if mode == "mastery":
            self._mastery_speed_gate(cid)
        clock_retries = 0
        rate_retries = 0
        start_retries = 0
        attempt = -1
        while attempt < MAX_TIMED_RETRIES:
            attempt += 1
            while not self.gov.allow_timed():
                set_state(self.base, stage=f"{mode}:waiting-credits")
                time.sleep(300)
            set_state(self.base, stage=f"{mode}:running", attempt=attempt + 1)
            # Clock-critical path runs locally against the public GM (pairing token; ~6s windows).
            # The mode's previous attempt (failed / harvested) is over: ask for a fresh clock directly. `start` would
            # resume it ({"result": "expired"}) and hb_timed then POSTs retry anyway -- 2.5-5 s of GM round trips
            # (rehearsal Day 7 script Mastery re-attempt: start phase 5.1 s).
            prev = timed.last_result(cid) or {}
            left = timed.seconds_left(prev) if prev.get("attempt_id") else None
            need = _resume_need(prev)
            if left is not None and 0 < left < need:
                # Day 8 script Mastery: the previous attempt still had ~4 s, so `start` RESUMED it -> 2 s solver budget
                # -> "solver too slow" -> a 143 s generalize. Let it run out (pre-clock for us), then re-roll.
                say(f"[{cid}] previous attempt has only {left:.1f}s left (< {need:.1f}s needed): waiting it out, then retry")
                time.sleep(left + 0.6)
                left = 0
            res = timed.run(cid, self.sdir, log=say, **({"op": "retry"} if left is not None and left <= 0 else {}))
            say(f"[{cid}] result: {res}")
            set_state(self.base, **{f"{mode}_result": res})
            if res == "correct":
                record_timed_case(cid, self.sdir)
                return True
            if res.startswith("error:prerequisite"):
                # The GM's status shows only the LATEST attempt: if a scout/probe attempt after the Time Trial pass
                # left it expired, re-pass the Time Trial so Mastery's prerequisite is satisfied again.
                tt = self.entries.get("time_trial")
                if mode == "mastery" and tt and not cli.gm_latest_correct(tt["id"]):
                    say(f"[{cid}] prerequisite: latest Time Trial attempt is not CORRECT; re-passing it")
                    self.ensure_latest_pass(tt["id"])
                else:
                    time.sleep(3)  # CourseStack scoring may still be pending for the previous mode
                continue
            if res == "error:exhausted":
                # GM 'rotation_exhausted' (replay d7fix3: metadata TT after the real run + 3 replays): no new variant
                # will be issued today. Terminal -- a generalize worker has nothing to fix (it burned 5 of them).
                say(f"[{cid}] GM rotation exhausted for this mode: no new attempts today; stopping (no generalize)")
                set_state(self.base, stage=f"{mode}:exhausted")
                break
            if res == "error:rate" and rate_retries < RATE_RETRIES:
                # GM 429 on start/download (Day 7 script TT: harvest + another lane's timed runs hammered the GM and a
                # rate-limit body became evidence.zip). Nothing to fix: back off and retry on its own budget.
                rate_retries += 1
                attempt -= 1
                wait = min(5 * rate_retries, 20)
                say(f"[{cid}] GM rate-limited the attempt; backing off {wait}s (rate retry {rate_retries}/{RATE_RETRIES})")
                set_state(self.base, stage=f"{mode}:rate-limited")
                time.sleep(wait)
                continue
            if res == "error:start":
                # The GM refused to hand out an attempt (Day 8 dual-pool routes: 503 training_rotation_invalid). The
                # solver never ran -- a generalize worker has nothing to fix (6 useless ones on Day 8). Back off, retry.
                if start_retries < START_RETRIES:
                    start_retries += 1
                    attempt -= 1
                    wait = (5, 10, 20)[min(start_retries - 1, 2)]
                    err = str((timed.last_result(cid) or {}).get("result") or "")
                    say(f"[{cid}] GM refused the start ({err}); backing off {wait}s "
                        f"(start retry {start_retries}/{START_RETRIES}, no generalize)")
                    set_state(self.base, stage=f"{mode}:start-refused")
                    time.sleep(wait)
                    continue
                say(f"[{cid}] GM kept refusing the start ({START_RETRIES} retries); stopping this mode (no generalize)")
                set_state(self.base, stage=f"{mode}:start-refused")
                break
            if res in ("error:exec", "error:rate"):
                # Transport failure (Day 6 binary TT: exec_error -> 12-min generalize path). Wait briefly for Homebase
                # health (local is the fallback anyway) and retry; it costs a TT attempt, never a worker.
                if attempt < MAX_TIMED_RETRIES:
                    say(f"[{cid}] timed runner failed ({(timed.last_result(cid) or {}).get('detail', '')!s:.120}); retrying")
                    set_state(self.base, stage=f"{mode}:retrying")
                    workers.wait_homebase(10)
                    continue
                break
            if res not in ("expired", "blocked"):
                break
            last = timed.last_result(cid) or {}
            if res == "expired" and self._clock_expiry(cid) and clock_retries >= CLOCK_RETRIES:
                # Clock-only failures exhausted their own retry budget: a generalize worker can't speed up the network
                # (main replay: one was launched anyway after "timing, not the solver"). Stop here.
                say(f"[{cid}] clock expiries exhausted ({clock_retries}); the solver is fine -- not generalizing")
                break
            if res == "expired" and self._clock_expiry(cid) and clock_retries < CLOCK_RETRIES:
                # The solver answered everything and the CLOCK ran out: a transport/timing failure. Probing can't judge
                # anything on an expired clock and a generalize worker can't speed up the network (rehearsal copy,
                # Dim and Dimmer mastery: 0/462 judged, worker concluded "solver correct, timing"). Just retry.
                say(f"[{cid}] expired on the CLOCK (in-window {last.get('in_window')}s / window {last.get('window')}s, "
                    f"phases {last.get('phases')}): timing, not the solver -- retrying without probe/generalize")
                set_state(self.base, stage=f"{mode}:timing")
                # Clock expiries are FREE on the scoreboard and don't consume the solver-failure budget: from WSL
                # (no Homebase) a 798-answer Mastery passed 6/6 one hour and expired 6/6 in a slow GM spell the
                # hour before -- keep trying through the spell with a gentle backoff.
                clock_retries += 1
                attempt -= 1
                time.sleep(min(2 * clock_retries, 10))
                continue
            # A failed timed attempt means the solver is wrong or incomplete for this variant (with Homebase
            # execution the window is no longer the bottleneck). Always improve the solver offline, then retry.
            # The generalize worker re-derives the variant's correct answers itself (ground truth), so it can
            # fix WRONG answers too, not just missing ones. Fetch the variant locally for it to work on.
            wrong, fixed, diag = None, None, {}
            last = timed.last_result(cid) or {}
            diag = {k: last.get(k) for k in ("window", "elapsed", "phases", "routed", "solver_too_slow", "hb_env_mismatch")}
            if last.get("result") == "solver_error":
                diag["crash"] = str(last.get("detail") or "")[-800:]
            if last.get("wrong") is not None:
                # The timed runner already localized this attempt in-window (same variant, saved as an auto-* case
                # with the GM-verified answers): use that instead of burning a fresh attempt on a different variant.
                wrong = [tuple(x) for x in last["wrong"]]
                fixed = last.get("fixed") or {}
                diag.update(complete=bool(last.get("localize_complete")), probed=None, total=None)
                try:
                    # Also keep the failed variant itself as a `variant-*` case (its bytes were pulled back, scoped to
                    # the failing sets): the worker gets the failing evidence and the green watcher a target -- the
                    # auto-* case alone holds only verified answers, so it already passes (D8 check: worker would run
                    # to the 12-min timeout).
                    tdir = timed.timed_dir(cid)
                    tc = json.loads((tdir / "contract.json").read_text()) if (tdir / "contract.json").exists() else None
                    if tc and last.get("attempt_id") and cli.attempt_id(tc) == last["attempt_id"]:
                        cli.save(cid, "start.json", tc)
                        cli.save(cid, "contract.json", tc)
                        capture_variant(cid, self.sdir)
                except Exception as e:  # noqa: BLE001 - evidence is best-effort
                    say(f"[{cid}] variant capture note: {e}")
                if not wrong and not last.get("localize_complete"):
                    wrong = None  # cut short with nothing found: fall back to the probe below
            if wrong is None:
                try:
                    tdir = timed.timed_dir(cid)
                    tc = json.loads((tdir / "contract.json").read_text()) if (tdir / "contract.json").exists() else None
                    same = bool(tc and last.get("attempt_id") and cli.attempt_id(tc) == last["attempt_id"])
                    if same and (last.get("solver_too_slow") or last.get("missing")):
                        # Work on THE FAILED VARIANT itself (its contract + bytes were pulled after the failure). Probing
                        # a fresh attempt judges a DIFFERENT variant: replay runs 2-3 read "all fields ok" off one and
                        # blamed the environment for two real solver gaps (bash comma keys, PE 0x8664).
                        cli.save(cid, "start.json", tc)
                        cli.save(cid, "contract.json", tc)
                        if last.get("missing") and not last.get("solver_too_slow"):
                            wrong = [(a, None) for a in last["missing"]]
                            # the in-window partial submit judged the answered subset (hb_timed._partial_submit)
                            bad = [tuple(x) for x in last.get("partial_wrong") or []]
                            wrong += bad
                            fixed = last.get("partial_fixed") or {}
                            diag["accepted"] = sorted((last.get("verified") or {}).keys())
                            say(f"[{cid}] solver left {len(last['missing'])} field(s) empty on this variant "
                                f"({len(bad)} answered wrong, GM accepted {len(diag['accepted'])}): generalizing on it")
                    else:
                        timed.ensure_started(cid)  # fresh attempt + download of the current variant for offline work
                    if last.get("solver_too_slow") or wrong is not None:
                        # Probing runs the same too-slow solver: it learns nothing (rehearsal rehearsal: 3 min for "28/28
                        # wrong" from an empty output). The fix is speed -- straight to generalize with that diagnosis.
                        if last.get("solver_too_slow"):
                            say(f"[{cid}] solver too slow for the window: skipping the field probe, generalizing for speed")
                    else:
                        wrong = timed.probe_fields(cid, self.sdir, log=say)  # binary search, per-field verdicts
                        dj = cli.cdir(cid) / "diagnosis.json"
                        if dj.exists():  # probe_fields returns early (no file) when there is nothing to probe
                            pd = json.loads(dj.read_text())
                            diag.update({k: pd.get(k) for k in ("complete", "probed", "total", "unjudged")})
                except Exception as e:  # noqa: BLE001
                    say(f"[{cid}] local fetch/probe for generalize failed: {e}")
                if cli.is_complete(cid):
                    # The probe's own submits passed this mode (replay run 3 binary TT: it went CORRECT, then the harness
                    # retried anyway and failed again -- 33s wasted after the pass).
                    say(f"[{cid}] the probe attempt itself passed the mode")
                    set_state(self.base, **{f"{mode}_result": "correct"})
                    record_timed_case(cid, self.sdir)
                    return True
                capture_variant(cid, self.sdir)  # expected.json now enriched by the probe-confirmed fields
            # Online label resolution FIRST: for closed-vocab label fields, probe the GM (the only authority on the
            # spelling) rather than letting the offline generalize worker GUESS and burn another attempt (the Q6 pain).
            if wrong and any(v is not None for _, v in wrong):
                try:
                    # only fields the solver DID answer (wrongly): an empty field is a solver gap, not a label spelling
                    got = timed.resolve_labels_online(cid, self.sdir, [a for a, v in wrong if v is not None], self.lane,
                                                      log=say)
                except Exception as e:  # noqa: BLE001
                    got = set()
                    say(f"[{cid}] online label resolve note: {e}")
                if got:
                    if cli.is_complete(cid):
                        set_state(self.base, **{f"{mode}_result": "correct"})
                        record_timed_case(cid, self.sdir)
                        return True
                    wrong = [(a, v) for a, v in wrong if a not in got]
                    if not wrong:
                        say(f"[{cid}] resolved {len(got)} label(s) online (cached); retrying without generalize")
                        continue
            if wrong == [] and diag.get("complete") and attempt < MAX_TIMED_RETRIES:
                # The probe judged EVERY field and found none wrong: the solver is right, the failure was the
                # environment or the clock (rehearsal rehearsal: 399/399 ok after a Homebase-only failure, yet a 12-min
                # generalize started). Retry instead; the Homebase 7z shim / local fallback handle the environment.
                say(f"[{cid}] probe: every field correct -> environment/timing, retrying without generalize")
                set_state(self.base, stage=f"{mode}:retrying")
                continue
            say(f"[{cid}] {res}: improving the solver offline for this variant, then retrying")
            diag.update(self._late_probes(cid, wait=True))   # one worker fixes the variant AND any probe misses
            self.generalize(cid, wrong=wrong, fixed=fixed, diag=diag)
        set_state(self.base, stage=f"{mode}:blocked")
        return False

    def ensure_latest_pass(self, cid, tries=3):
        """Make the GM's LATEST attempt for this timed mode CORRECT (after scouting), so a prerequisite check that
        reads the latest status sees a pass. The solve itself is already banked on the scoreboard."""
        from . import scout
        for _ in range(tries):
            if cli.gm_latest_correct(cid):
                return True
            scout._wait_expired((timed.last_result(cid) or {}).get("deadline"), say, cid)
            time.sleep(scout.RATE_GAP)
            timed.run(cid, self.sdir, log=say)
        return cli.gm_latest_correct(cid)

    def scout_stage(self):
        """Between a passed Time Trial and Mastery: run Time Trial scout rounds (new variant each) so unseen
        constructs get their GM label on the cheap clock; generalize offline on fields the in-window corrector
        couldn't fix; finally leave the latest Time Trial attempt CORRECT. Advisory: Mastery runs regardless."""
        tt, ms = self.entries.get("time_trial"), self.entries.get("mastery")
        if not SCOUT_ROUNDS or not tt or not ms or cli.gm_solved(ms["id"]):
            return
        from . import scout
        cid = tt["id"]
        s = {}
        for cycle in range(SCOUT_GENERALIZE + 1):
            set_state(self.base, stage="time_trial:scouting", scout_cycle=cycle + 1)
            s = scout.scout(cid, self.sdir, rounds=SCOUT_ROUNDS, clean=SCOUT_CLEAN, log=say)
            set_state(self.base, scout={"cycle": cycle + 1, "clean_streak": s["clean_streak"],
                                        "new_labels": s["new_labels"], "fixed": s["fixed"],
                                        "unresolved": s["unresolved"][:20], "solver_failed": s.get("solver_failed")})
            if (not s["unresolved"] and not s.get("solver_failed")) or cycle == SCOUT_GENERALIZE:
                break
            last = timed.last_result(cid) or {}
            say(f"[{cid}] scout found {len(s['unresolved'])} unresolved field(s); generalizing before Mastery")
            self.generalize(cid, wrong=s["unresolved"] or None, fixed=s["fixed"],
                            diag={k: last.get(k) for k in ("window", "elapsed", "phases", "routed")})
        ok = self.ensure_latest_pass(cid)
        say(f"[{cid}] scouting done: clean_streak={s.get('clean_streak')} new_labels={len(s.get('new_labels') or {})} "
            f"unresolved={len(s.get('unresolved') or [])}; latest Time Trial {'CORRECT' if ok else 'NOT correct'}")

    def run(self):
        for n in range(CHAIN_CRASH_RETRIES + 1):
            try:
                return self._run()
            except Exception:  # noqa: BLE001 - one chain must never take down the others
                tb = traceback.format_exc()
                if n < CHAIN_CRASH_RETRIES:
                    say(f"[{self.base}] CRASHED; retrying the chain in 10s (solved modes are skipped):\n{tb}")
                    set_state(self.base, stage="crash-retry", error=tb[-2000:])
                    time.sleep(10)
                    continue
                set_state(self.base, stage="crashed", error=tb[-2000:])
                say(f"[{self.base}] CRASHED:\n{tb}")

    def _run(self):
        set_state(self.base, stage="queued", name=self.name, lane=self.lane, worker=None)
        self.recover_interrupted_generalize()
        modes = self.only_modes or ["single_solve", "time_trial", "mastery"]
        if "single_solve" in modes and not self.single():
            return
        for mode in ("time_trial", "mastery"):
            if mode == "mastery" and mode in modes:
                self.scout_stage()   # no-op unless SCOUT_ROUNDS > 0
            if mode in modes and mode in self.entries and not self.timed_stage(mode):
                return
        set_state(self.base, stage="done")
        say(f"[{self.base}] chain complete")


# ---------------------------------------------------------------- entry points

_provisioned = False


def ensure_homebase_provisioned():
    """Provision Homebase's solver deps once per process (idempotent; cheap if already installed).
    A factory reset wipes them, so this guarantees hb_timed can run any solver next to the GM."""
    global _provisioned
    if _provisioned:
        return
    try:
        remote.rsync_to(ROOT / "setup" / "homebase_setup.sh", "~/homebase_setup.sh")
        r = remote.ssh("bash ~/homebase_setup.sh 2>&1 | tail -2", timeout=600, check=False)
        say(f"[homebase] provisioned: {r.stdout.strip()[-160:]}")
        _provisioned = True
    except Exception as e:  # noqa: BLE001 - provisioning best-effort; hb_timed will surface real gaps
        say(f"[homebase] provisioning note: {e}")


def released_challenges(day=None):
    args = ["list", "--all"] if day is None else ["list", "--day", str(day)]
    body = cli.call(None, *args)["body"] or {}
    return body.get("challenges", [])


def run(day=None, only=None, local_slots=5, hb_slots=0, modes=None, prewarm_homebase=None, keep_homebase=None,
        scout_rounds=None):
    global SCOUT_ROUNDS
    if scout_rounds is not None:
        SCOUT_ROUNDS = scout_rounds
    if keep_homebase is None:
        keep_homebase = os.environ.get("HCTF_KEEP_HOMEBASE", "0") != "0"
    timed_in_scope = (not modes) or any(m in ("time_trial", "mastery") for m in modes)
    if prewarm_homebase is None:
        # Default ON for timed runs: boot + provision Homebase in the BACKGROUND at run start, so a tight-window
        # failover never waits on a cold VM (start it immediately, don't wait for an expiry — user request). Singles
        # run locally while it boots, so the warm VM costs ~nothing extra. Disable with HCTF_PREWARM_HOMEBASE=0.
        prewarm_homebase = (workers.AUTO_HOMEBASE and timed_in_scope and not hb_slots
                            and os.environ.get("HCTF_PREWARM_HOMEBASE", "1") != "0")
    if hb_slots:  # Homebase is opt-in now (extra codex pool); GM + timed run locally via the pairing token
        remote.ensure_up()
        remote.deploy()
        ensure_homebase_provisioned()  # codex workers run on Homebase; make sure their deps are present
    elif prewarm_homebase:
        # Boot + provision Homebase in the background NOW, so it's already up when a tight timed window needs it
        # (the on-demand path blocks on the same lock, so no cold-start stall mid-clock). Powered off at run end.
        threading.Thread(target=workers._homebase_ready, args=(say,), daemon=True).start()
        say("[homebase] pre-warming in the background for timed windows (powers off only if this run powered it on; "
            "otherwise `hctf hb off` when done)")
    gov = Governor(hb_enabled=bool(hb_slots))
    pools = Pools(local_slots, hb_slots, gov)
    groups = {}
    for c in released_challenges(day):
        groups.setdefault(solvers.base_id(c["id"]), []).append(c)
    if only:
        groups = {b: v for b, v in groups.items() if any(o in b for o in only)}
    skip = {x.strip() for x in os.environ.get("HCTF_SKIP_IDS", "").split(",") if x.strip()}
    if skip:   # e.g. a replay sparing a mode whose variant pool is nearly used up
        groups = {b: [c for c in v if c["id"] not in skip] for b, v in groups.items()}
        say(f"skipping (HCTF_SKIP_IDS): {sorted(skip)}")
    say(f"{len(groups)} chains ({sum(map(len, groups.values()))} challenge modes), "
        f"slots local={local_slots} homebase={hb_slots}, credits={gov.credits()}")
    try:
        with ThreadPoolExecutor(max_workers=max(1, len(groups))) as ex:
            for base, entries in sorted(groups.items()):
                ex.submit(Chain(base, entries, pools, gov, modes).run)
    finally:
        if not hb_slots and not keep_homebase:  # Homebase switched on only for tight timed windows: switch it off again
            workers.power_off_homebase_if_ours(say)
        elif keep_homebase:
            say("[homebase] left running (--keep-homebase); power it off with `hctf hb off` when done")
    say("all chains finished")
    if RATCHET and day is not None:
        ratchet(day)


RATCHET = os.environ.get("HCTF_RATCHET", "1") != "0"
RATCHET_TIMEOUT = float(os.environ.get("HCTF_RATCHET_TIMEOUT", str(15 * 60)))


def ratchet(day):
    """Post-run, single-writer knowledge merge: collect every `## Proposed lib additions` section the day's workers
    wrote in solver/NOTES.md and let ONE worker fold the GM-confirmed ones into lib/ (workers no longer edit lib/
    mid-run: Day 6's script worker rewrote lib/knowledge.py + lib/scripts.py while four other lanes imported them)."""
    tag = f"day{int(day):02d}"
    props = []
    for notes in sorted((paths.CHALLENGES / tag).glob("*/solver/NOTES.md")):
        text = notes.read_text(errors="replace")
        m = re.search(r"^##\s*Proposed lib additions\s*$(.*?)(?=^##\s|\Z)", text, re.M | re.S)
        if m and m.group(1).strip():
            props.append(f"### {notes.relative_to(ROOT)}\n{m.group(1).strip()}")
    chals = sorted(str(p.relative_to(ROOT)) for p in (paths.CHALLENGES / tag).glob("*/meta.json"))
    if not chals:
        say(f"[ratchet] {tag}: nothing to learn from")
        return
    prompt = workers.render("ratchet", day=tag, day_num=int(day), challenges="\n".join(f"- {c}" for c in chals),
                            proposals="\n\n".join(props) or "(no `## Proposed lib additions` this day)")
    say(f"[ratchet] {tag}: technique logs + {len(props)} lib proposal section(s)")
    # Transactional: a killed/timed-out ratchet left lib/ half-edited on the rehearsal replay (an unvalidated helper that
    # extracted 0 files). Snapshot lib/, and restore it unless the worker exits 0 AND the test suites still pass.
    backup = ROOT / ".run" / f"ratchet-lib-{tag}"
    shutil.rmtree(backup, ignore_errors=True)
    shutil.copytree(ROOT / "lib", backup, ignore=shutil.ignore_patterns("__pycache__"))
    rc, log = workers.run_local(paths.CHALLENGES / tag, "ratchet", prompt, {"HCTF_STAGE": "ratchet"}, RATCHET_TIMEOUT)
    ok = rc == 0
    if ok:
        import subprocess as _sp
        for t in ("tests/test_orchestrate.py", "tests/test_day6_fixes.py"):
            if (ROOT / t).exists() and _sp.run([sys.executable, t], cwd=ROOT, capture_output=True, timeout=600).returncode:
                ok = False
                say(f"[ratchet] {tag}: {t} fails after the merge")
    if ok:
        shutil.rmtree(backup, ignore_errors=True)
        say(f"[ratchet] {tag}: merged ({Path(log).name})")
    else:
        shutil.rmtree(ROOT / "lib")
        shutil.copytree(backup, ROOT / "lib")
        say(f"[ratchet] {tag}: REVERTED lib/ (worker exit {rc}); proposals stay in solver/NOTES.md ({Path(log).name})")
    if SPEED_HARDEN:
        try:
            speed_harden(day=day)
        except Exception as e:  # noqa: BLE001 - post-run best-effort
            say(f"[speed-harden] {tag}: skipped ({e})")


SPEED_HARDEN = os.environ.get("HCTF_SPEED_HARDEN", "1") != "0"


def speed_harden(day=None, cid=None, log=None):
    """Off the clock, after the run: every lane solver whose slowest GM-verified regression case exceeds
    SINGLE_SPEED_BUDGET gets ONE speed generalize (transactional: kept only if every case still passes). Tomorrow's
    worker copies this solver -- rehearsal D8: Day 7's slow Kotlin-jar path cost an 84 s pre-attempt speed generalize on
    the critical path. Returns {base: (slowest_before, slowest_after or None)}."""
    log = log or say
    if cid:
        bases = [paths.base_id(cid)]
    else:
        bases = []
        for m in sorted((paths.CHALLENGES / f"day{int(day):02d}").glob("*/meta.json")):
            try:
                bases.append(json.loads(m.read_text())["base"])
            except (OSError, ValueError, KeyError):
                pass
    gov = Governor()
    pools = Pools(1, 0, gov)
    out = {}
    for base in bases:
        sdir = paths.solver_dir(base)
        if not (sdir / "solve.py").exists():
            continue
        res = solvers.test_solver(sdir)
        timed_ok = [r for r in res if not r.get("unverified") and not r.get("error")]
        slow = max((r["seconds"] for r in timed_ok), default=0.0)
        worst = max(timed_ok, key=lambda r: r["seconds"], default=None)
        if slow <= SINGLE_SPEED_BUDGET:
            log(f"[speed-harden] {base}: slowest case {slow:.1f}s <= {SINGLE_SPEED_BUDGET:g}s, nothing to do")
            out[base] = (slow, None)
            continue
        log(f"[speed-harden] {base}: slowest case {worst['case']} {slow:.1f}s > {SINGLE_SPEED_BUDGET:g}s -> speed generalize")
        chain = chain_for(base, pools, gov)
        chain.generalize(base, wrong=None, fixed=None, diag={"solver_too_slow": True, "single_seconds": round(slow, 2)})
        after = max((r["seconds"] for r in solvers.test_solver(sdir) if not r.get("unverified") and not r.get("error")),
                    default=0.0)
        log(f"[speed-harden] {base}: slowest case {slow:.1f}s -> {after:.1f}s")
        out[base] = (slow, after)
    return out


def chain_for(cid, pools, gov):
    """Build a Chain for one challenge from the local index (no extra list call needed)."""
    base = paths.base_id(cid)
    info = paths.lookup(base) or {}
    entries = [{"id": base if m == "single_solve" else f"{base}/{m}", "mode": m,
                "lane": info.get("lane", "misc"), "name": info.get("name", base)} for m in paths.MODES]
    if info.get("lane") == "welcome":
        entries = entries[:1]
    return Chain(base, entries, pools, gov)


def run_one_timed(cid, local_slots=2):
    gov = Governor()
    chain = chain_for(cid, Pools(local_slots, 0, gov), gov)
    try:
        ok = chain.timed_stage(paths.mode_of(cid))
    finally:
        if os.environ.get("HCTF_KEEP_HOMEBASE", "0") == "0":
            workers.power_off_homebase_if_ours(say)
    return 0 if ok else 1


def _mode_solved_local(cid):
    """Local, network-free truth for whether a mode is solved: the gm_solved sticky marker or any recorded
    CORRECT submission. The live chain.json `stage` lags (it tracks worker activity, not per-mode completion),
    so a passed single_solve with timed stages still running used to display as `single:solving`."""
    try:
        return (cli.cdir(cid) / "solved_once").exists() or cli.ever_correct(cid)
    except Exception:  # noqa: BLE001 - unknown means "not known solved"
        return False


def dashboard():
    hdr = ("chain", "lane", "stage", "worker", "single", "tt", "mastery", "updated")
    rows = []
    for p in sorted(paths.CHALLENGES.glob("day*/*/chain.json")):
        s = json.loads(p.read_text())
        try:
            ids = (json.loads((p.parent / "meta.json").read_text()) or {}).get("ids", {})
        except (OSError, ValueError):
            ids = {}
        # Per-mode solved from local truth, falling back to the chain's recorded result (never the stale stage).
        single = "correct" if ids.get("single_solve") and _mode_solved_local(ids["single_solve"]) else ""
        tt = "correct" if (ids.get("time_trial") and _mode_solved_local(ids["time_trial"])) else s.get("time_trial_result", "")
        mastery = "correct" if (ids.get("mastery") and _mode_solved_local(ids["mastery"])) else s.get("mastery_result", "")
        rows.append((str(p.parent.relative_to(paths.CHALLENGES)), s.get("lane", ""), s.get("stage", ""),
                     s.get("worker") or "", single, tt, mastery, s.get("updated", "")))
    w = [max(len(str(r[i])) for r in rows + [hdr]) for i in range(len(hdr))]
    for r in [hdr] + rows:
        print("  ".join(str(x).ljust(w[i]) for i, x in enumerate(r)))
