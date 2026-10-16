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
from collections import Counter
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
# Fresh timed pool spent (rotation_exhausted / retry_variants_unavailable): solver rounds on an UNTIMED attempt (regular
# pool or practice continuation) -- the flag + points without a clock. 0 = old behaviour (stop the mode).
UNTIMED_ROUNDS = int(os.environ.get("HCTF_UNTIMED_ROUNDS", "3"))
# previous start reported 0 fresh attempts -> skip the refused timed retry, go untimed at once (D14)
SKIP_DOOMED_RETRY = os.environ.get("HCTF_SKIP_DOOMED_RETRY", "1") != "0"


# Never re-roll (retry / wait-it-out) an attempt that still holds banked ids: reconnect with op=resume (start) instead.
KEEP_BANKED = os.environ.get("HCTF_KEEP_BANKED", "1") == "1"


def _prev_banked(prev):
    """The previous attempt (last_timed.json) banked ids a retry would DISCARD: anything the GM accepted on it (partial
    submit, a per-set / localized subset, an in-window fill) while the mode is not yet CORRECT."""
    if not prev.get("attempt_id") or str(prev.get("result", "")).lower() == "correct":
        return False
    if prev.get("verified") or str(prev.get("full_result", "")).lower() == "accepted":
        return True
    if str((prev.get("partial_submit") or {}).get("result", "")).lower() in ("correct", "accepted"):
        return True
    if any(str((v or {}).get("result", "")).lower() in ("correct", "accepted") for v in (prev.get("per_set") or {}).values()):
        return True
    return any(str(t.get("result", "")).lower() in ("correct", "accepted") for t in prev.get("inwindow_fill") or [])


def label_only_failure(wrong):
    """True when every GM-rejected field is a closed-vocab LABEL family (control / expansion / format / ...): the case
    where a generalize worker tends to hunt for why the grader changed instead of fitting a rule (rehearsal D13 replay: 8.5 min,
    then an overfit date-gated rule). Gets the LABEL-ONLY prompt cue and a duel from the first generalize."""
    ids = [a for a, _ in (wrong or [])]
    if not ids:
        return False
    try:
        from lib.playbook import field_family
        from .labels import CACHEABLE_FAMILIES
    except Exception:  # noqa: BLE001
        return False
    return all(field_family(a) in CACHEABLE_FAMILIES for a in ids)


def _rel(p):
    try:
        return Path(p).relative_to(ROOT)
    except ValueError:
        return Path(p)


def generation_split(bad_dates, good_dates):
    """The cases the solver gets a label family WRONG on and the ones it gets RIGHT come from disjoint attempt-start
    date ranges -> the GM re-labelled from one day on (alt armA D15 script: 35 earlier-day cases say batch expansion
    `delayed` where D15's GM says `percent` for byte-identical joins; the worker spent 372 s looking for a byte rule).
    -> one-line description, or ""."""
    bad, good = sorted(d for d in bad_dates if d), sorted(d for d in good_dates if d)
    if not bad or not good or len(bad_dates - {""}) < 1:
        return ""
    if bad[-1] < good[0]:
        return (f"the solver is WRONG only on attempts started {bad[0]}..{bad[-1]} and RIGHT on those started "
                f"{good[0]}..{good[-1]}: the GM's label for this family changed between {bad[-1]} and {good[0]}")
    if good[-1] < bad[0]:
        return (f"the solver is RIGHT only on attempts started {good[0]}..{good[-1]} and WRONG on those started "
                f"{bad[0]}..{bad[-1]}: the GM's label for this family changed between {good[-1]} and {bad[0]}")
    return ""


def label_table(sdir, res, wrong, cap=60):
    """The table a label-only generalize worker otherwise spends 2-3 minutes scripting (rehearsal D13 replays: 140-190 s of
    tabulation before the first edit). From the baseline test_solver results (`res`) + every case's expected.json:
    per failing label family, the GM-verified label distribution over ALL cases, then every disagreement grouped by
    (GM label, solver output) with the cases/fields it covers. "" when nothing applies."""
    try:
        from lib.playbook import field_family
    except Exception:  # noqa: BLE001
        return ""
    fams = {field_family(a) for a, _ in (wrong or [])}
    if not fams:
        return ""
    dist, has_fam, date = {}, {}, {}
    for exp in sorted(Path(sdir).glob("cases/*/expected.json")):
        try:
            e = json.loads(exp.read_text())
        except (OSError, ValueError):
            continue
        try:   # the GM grades with the rubric of the day it STARTED the attempt: every case carries that date
            date[exp.parent.name] = str(json.loads((exp.parent / "contract.json").read_text()).get("started_at")
                                        or "")[:10]
        except (OSError, ValueError, AttributeError):
            date[exp.parent.name] = ""
        for a, v in e.items():
            f = field_family(a)
            if f in fams:
                dist.setdefault(f, {}).setdefault(str(v), 0)
                dist[f][str(v)] += 1
                has_fam.setdefault(f, set()).add(exp.parent.name)
    groups, bad_fam = {}, {}
    for r in res or []:
        for a, d in (r.get("diff") or {}).items():
            f = field_family(a)
            if f in fams:
                groups.setdefault((f, str(d.get("expected")), str(d.get("got"))), []).append(f"{r['case']}:{a}")
                bad_fam.setdefault(f, set()).add(r["case"])
    if not dist and not groups:
        return ""
    out = ["LABEL TABLE (harness-computed from every case's GM-verified expected.json and the CURRENT solver's output; "
           "do not re-tabulate):"]
    for f, d in sorted(dist.items()):
        out.append(f"    `{f}` GM labels over all cases: " + ", ".join(f"{k} x{n}" for k, n in sorted(d.items(),
                                                                                                    key=lambda x: -x[1])))
    if groups:
        out.append("    disagreements (GM-verified label <- solver output: case:answer_id ...):")
        for (f, want, got), items in sorted(groups.items(), key=lambda x: -len(x[1])):
            out.append(f"      [{f}] GM {want!s} <- solver {got!s}  ({len(items)}): " + ", ".join(items[:6])
                       + (" ..." if len(items) > 6 else ""))
            split = generation_split({date.get(i.split(":", 1)[0], "") for i in items},
                                     {date.get(c, "") for c in has_fam.get(f, set()) - bad_fam.get(f, set())})
            if split:
                out.append(f"        GENERATION SPLIT: {split}")
            if len(out) >= cap:
                out.append("      ... (truncated)")
                break
    else:
        out.append("    (the current solver already matches every verified label in the corpus: the miss is only in "
                   "the new variant's bytes)")
    return "\n".join(out)


LIVE_ANSWER = os.environ.get("HCTF_LIVE_ANSWER", "1") == "1"
LIVE_MAX_FIELDS = int(os.environ.get("HCTF_LIVE_MAX_FIELDS", "40"))
LIVE_TIMEOUT = float(os.environ.get("HCTF_LIVE_TIMEOUT", "900"))
RESUME_CONTINUES = int(os.environ.get("HCTF_RESUME_CONTINUES", "2"))
TT_FIX_GATE = os.environ.get("HCTF_TT_FIX_GATE", "1") == "1"
SINGLE_DUEL_CASES = os.environ.get("HCTF_SINGLE_DUEL_CASES", "1") == "1"
BASELINE_PRE = os.environ.get("HCTF_BASELINE_PRE", "1") == "1"
BASELINE_PRE_PAR = int(os.environ.get("HCTF_BASELINE_PRE_PAR", "4"))
BASELINE_PRE_JOIN = float(os.environ.get("HCTF_BASELINE_PRE_JOIN", "60"))
# generalize green watcher: poll / code-quiet seconds (was 2 s / 3 s: up to ~5 s between the fix and the worker's end)
GREEN_POLL = float(os.environ.get("HCTF_GREEN_POLL", "0.5"))
GREEN_QUIET = float(os.environ.get("HCTF_GREEN_QUIET", "1.5"))
LIVE_BG_GEN = os.environ.get("HCTF_LIVE_BG_GEN", "1") == "1"   # TT live pass + solver misses: generalize goes on aside
BG_GEN_NOTE = """
- BACKGROUND JOB: the Time Trial already PASSED (a live worker answered on the open attempt). Nothing waits on you. Your
  only job: the solver must PRODUCE the {n} field(s) it left empty there ({ids}) -- Mastery asks them again. Their
  GM-verified answers are in `cases/{target}/expected.json`. Pass that case + every case that passes now, then stop.
"""
NEWID_HOLD = float(os.environ.get("HCTF_NEWID_HOLD", "45"))     # 0 = off
NEWID_STABLE = float(os.environ.get("HCTF_NEWID_STABLE", "1.0"))
NEWID_MAX = int(os.environ.get("HCTF_NEWID_MAX", "6"))           # background dry runs per single
NEWID_WAIT = float(os.environ.get("HCTF_NEWID_WAIT", "2.0"))     # at CORRECT: wait this long for a running dry run
UNTIMED_SKIP_PREGEN = os.environ.get("HCTF_UNTIMED_SKIP_PREGEN", "1") == "1"   # no pre-Mastery generalize on an untimed pool


def _cut_short(last):
    """A failed UNTIMED attempt whose in-attempt localization did not finish its job -- stopped early (a transport
    error, its time budget) or fixed every wrong field without completing the attempt -- while holding GM-accepted
    ids: reconnecting finishes it (hb_timed overlays the banked values and localizes the rest). D15 script Mastery:
    one cut-off reply ended localization with 16 `delayed` -> `percent` fixes found; a 3-min generalize followed."""
    if str(last.get("result", "")).lower() != "incorrect" or not _prev_banked(last):
        return False
    if last.get("deadline") is not None or not (last.get("untimed") or last.get("no_clock")
                                                or last.get("run_for_time") is False):
        return False   # a clocked attempt is gone by now
    if not last.get("localize_complete"):
        return True
    wrong = [w[0] for w in last.get("wrong") or []]
    return bool(wrong) and all(a in (last.get("fixed") or {}) for a in wrong)


def _live_fields(last, wrong, fixed):
    """Answer ids still unresolved on a failed UNTIMED attempt (wrong and not fixed in-window, or missing), else []."""
    if last.get("deadline") is not None or not (last.get("untimed") or last.get("no_clock")
                                                or last.get("run_for_time") is False):
        return []
    if not last.get("attempt_id"):
        return []
    ids = [a for a, _ in (wrong or []) if a not in (fixed or {})] + list(last.get("missing") or [])
    return list(dict.fromkeys(ids))


class LiveAnswer:
    """Dynamic fallback beside a generalize (C1, 2026-10-15): a single-style worker answers ONLY the unresolved fields of
    the still-open untimed attempt from its bytes and submits them to that attempt. The generalize keeps the solver
    general for tomorrow; this one just passes today's mode. `passed` = the GM said CORRECT; `all_accepted` = every
    listed field accepted (a resume then completes the attempt with workers.live_overlay)."""

    def __init__(self, chain, cid, last, fields, wrong, fixed):
        self.chain, self.cid, self.fields = chain, cid, fields
        self.attempt = last.get("attempt_id")
        self.stop_evt, self.done = threading.Event(), threading.Event()
        self.passed = self.all_accepted = False
        self._links = []
        tdir = timed.timed_dir(cid)
        try:
            contract = json.loads((tdir / "contract.json").read_text())
        except (OSError, ValueError):
            contract = cli.load(cid, "start.json") or {}
        qmap = {q.get("id"): q for q in contract.get("questions") or [] if isinstance(q, dict)}
        sub = dict(wrong or [])
        rejected = {}
        for a, v in (last.get("wrong") or []) + (last.get("partial_wrong") or []):
            if v not in (None, ""):
                rejected.setdefault(a, set()).add(str(v))
        for a, vs in (last.get("localize_tried") or {}).items():
            rejected.setdefault(a, set()).update(str(v) for v in vs)
        lines = []
        for a in fields:
            q = qmap.get(a) or {}
            fmt = q.get("answer_format") or {}
            lines.append(f"  - `{a}`: {str(q.get('question') or '?')[:220]} | artifact `{q.get('artifact') or '?'}` | "
                         f"format {json.dumps(fmt)[:160]} | solver gave {sub.get(a)!r}"
                         + (f" | REJECTED: {sorted(rejected[a])[:6]}" if rejected.get(a) else ""))
        self._need = {os.path.basename(str((qmap.get(a) or {}).get("artifact") or "").split("->")[0].strip())
                      for a in fields} - {""}
        self._render = dict(
            persona=workers.lane_persona(chain.lane), cid=cid, attempt=str(self.attempt)[:8],
            accepted=len(last.get("verified") or {}), n=len(fields), fields="\n".join(lines),
            contract=(tdir / "contract.json").relative_to(ROOT) if (tdir / "contract.json").exists() else
            cli.cdir(cid).relative_to(ROOT) / "start.json",
            solver_dir=chain.sdir.relative_to(ROOT), lane=chain.lane, chal_dir=cli.cdir(cid).relative_to(ROOT))
        try:   # the Stop gate (.claude/hooks/stop_gate.py, stage live) reads what this worker owes
            (cli.cdir(cid) / ".live_fields.json").write_text(json.dumps({"attempt": self.attempt, "fields": fields}))
        except OSError:
            pass
        self.thread = threading.Thread(target=self._run, daemon=True, name=f"live-{cid}")
        self.watch = threading.Thread(target=self._watch, daemon=True, name=f"live-watch-{cid}")

    def start(self):
        say(f"[{self.cid}] live-answer worker on attempt {str(self.attempt)[:8]} for {len(self.fields)} field(s), "
            "racing the generalize")
        self.thread.start()
        self.watch.start()
        return self

    def link(self, evt):
        """Also set `evt` (the generalize's stop event) when the live worker passes the mode."""
        self._links.append(evt)
        if self.passed or self.all_accepted:
            evt.set()

    def _art_dir(self):
        """Where every listed field's delivery is: the failure pull fetched ONE representative set per failing family
        (enough for the generalize); a live answer needs each listed set -> public download of the attempt otherwise."""
        tdir = timed.timed_dir(self.cid)
        have = {p.name for p in tdir.iterdir()} if tdir.is_dir() else set()
        if (tdir / "contract.json").exists() and self._need <= have:
            return tdir
        try:
            class A:  # argparse-like namespace for cli.c_artifact (downloads start.json's deliveries, public GM)
                id, delivery = self.cid, None
            with cli.quiet():
                cli.c_artifact(A)
        except Exception as e:  # noqa: BLE001 - the worker can still fetch with `hctf artifact`
            say(f"[{self.cid}] live-answer: artifact download note: {str(e)[:160]}")
        return timed.latest_artifacts(self.cid) or tdir

    def _run(self):
        try:
            art = self._art_dir()
            self.prompt = workers.render("live", art_dir=Path(art).relative_to(ROOT), **self._render)
            self.chain.run_worker(self.cid, "live", self.prompt, LIVE_TIMEOUT, urgent=True, stop=self.stop_evt)
        except Exception as e:  # noqa: BLE001 - the generalize carries on regardless
            say(f"[{self.cid}] live-answer worker failed: {str(e)[:200]}")
        finally:
            self.done.set()

    def _state(self):
        ov = workers.live_overlay(self.cid, self.attempt) or {}
        acc = set((ov.get("answers") or {}))
        correct = False
        try:
            for ln in open(cli.cdir(self.cid) / "submissions.jsonl"):
                r = json.loads(ln)
                if r.get("attempt") == self.attempt and r.get("kind") == "correct":
                    correct = True
        except (OSError, ValueError):
            pass
        return correct, set(self.fields) <= acc

    def _watch(self):
        while not self.done.is_set() and not self.stop_evt.is_set():
            self.passed, self.all_accepted = self._state()
            if self.passed or self.all_accepted:
                say(f"[{self.cid}] live-answer: {'mode CORRECT' if self.passed else 'every listed field accepted'} "
                    "-> ending the generalize")
                for e in self._links:
                    e.set()
                self.stop_evt.set()
                break
            self.done.wait(2.0)
        self.passed, self.all_accepted = self._state()

    def finish(self, wait=5.0):
        self.stop_evt.set()
        self.thread.join(timeout=wait)
        self.watch.join(timeout=wait)
        self.passed, self.all_accepted = self._state()
        return self


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
# Reuse RACE (user, 2026-10-12; supersedes "harness auto-reuse OFF" for the lanes below): the moment the single's bytes
# land, run the newest same-lane solvers on them and submit their answers BESIDE the LLM worker. A CORRECT single is then
# picked up by the STOP_WHEN_READY watcher (staged prior solver verified -> worker ended -> timed modes start). Lanes
# come from the backtest (.run/backtest_reuse.sh: confident-value precision per lane); at most RACE_PROBES submits.
REUSE_RACE = os.environ.get("HCTF_REUSE_RACE", "1") != "0"
REUSE_RACE_LANES = {x.strip() for x in os.environ.get(
    "HCTF_REUSE_RACE_LANES", "script-analysis,binary-reverse-engineering,mobile-android,metadata-forensics,warmups"
).split(",") if x.strip()}
REUSE_RACE_PROBES = int(os.environ.get("HCTF_REUSE_RACE_PROBES", "3"))
REUSE_RACE_SOLVERS = int(os.environ.get("HCTF_REUSE_RACE_SOLVERS", "3"))   # newest N same-lane solvers
REUSE_RACE_TIMEOUT = float(os.environ.get("HCTF_REUSE_RACE_TIMEOUT", "20"))
# Partial banking (D12 binary: merged 120 rejected over ONE speculative field, 60 banked, budget out -> worker +58 s):
# after a rejected/incomplete merged set, bank the CONFIDENT subset as one batch, then the speculative remainder, then
# other solvers' values / spelling alternates for each isolated wrong field -- stopping the moment the worker submits.
RACE_PARTIAL = os.environ.get("HCTF_RACE_PARTIAL", "1") != "0"
RACE_TOTAL_PROBES = int(os.environ.get("HCTF_RACE_TOTAL_PROBES", "7"))
RACE_SPEC_PROBES = int(os.environ.get("HCTF_RACE_SPEC_PROBES", "4"))
# Drop race values that fail the local format checks or the slug plausibility gate (lib/slug.py) BEFORE submitting:
# the race submits with force=True, which skips them (D13 warmups: a rot-N gibberish slug cost a GM submission).
RACE_FORMAT_GATE = os.environ.get("HCTF_RACE_FORMAT_GATE", "1") != "0"
# What the race learned (banked count, remaining ids, hint + judged-wrong values) reaches the worker: in the go text if
# the race finished first, else via the inbox (hctf/inbox.py -> .claude/hooks/nudge.py on its next tool call).
INBOX = os.environ.get("HCTF_INBOX", "1") != "0"
# Past-solve retrieval by challenge fingerprint (hctf/retrieval.py): a "Similar past solves" block in the single and
# generalize prompts + similarity-ranked reuse-race solver selection. Index rebuilt in the background at run start.
RETRIEVAL = os.environ.get("HCTF_RETRIEVAL", "1") != "0"
RETRIEVAL_K = int(os.environ.get("HCTF_RETRIEVAL_K", "3"))
# Label scouting (Chain._label_scout): extra Time Trial variants before the generalize of a label-only failure. 0 = off.
LABEL_SCOUT_ROUNDS = int(os.environ.get("HCTF_LABEL_SCOUT_ROUNDS", "0"))   # OFF: a13sota3 -- contradictory labels across variants -> rejected generalizes
FAMILY_EVIDENCE_WAIT = float(os.environ.get("HCTF_FAMILY_EVIDENCE_WAIT", "10"))   # generalize prompt: family-probe wait
# LLM coordinator (hctf/coordinator.py): reads stuck workers' traces and posts one targeted hint to their inbox.
COORDINATOR = os.environ.get("HCTF_COORDINATOR", "1") != "0"
# The go no longer waits for the prior-solver dry run (binary go came at T+16-22 behind it); the dry-run note follows
# through the inbox when it finishes. The staged-solver copy is still awaited (the prompt promises it is in place).
GO_EARLY = os.environ.get("HCTF_GO_EARLY", "1") != "0"
STOP_WHEN_READY = os.environ.get("HCTF_STOP_WHEN_READY", "1") != "0"  # end the single worker at CORRECT + verified solver
SPEC_STABLE = float(os.environ.get("HCTF_SPEC_STABLE", "0.75"))  # solver files untouched this long before a snapshot
# (was 2 s: _spec_snapshot re-checks the mtimes after its copy, so a mid-edit copy is caught anyway; D13 metadata
# spent 8 s between CORRECT and the handoff)
SPEC_POLL = float(os.environ.get("HCTF_SPEC_POLL", "0.25"))  # D9: single CORRECT -> ready took up to 1 s of poll
# The single's solver on its OWN case must beat this (local s) or a speed generalize runs BEFORE the first timed attempt:
# Homebase is ~1.5x slower and the 7-13 s window also pays GM start/download/submit (blind D7 replay: binary 5.9 s ->
# Time Trial exec_error "too slow", one attempt + ~30 s burned before the speed fix even started). 0 disables.
SINGLE_SPEED_BUDGET = float(os.environ.get("HCTF_SINGLE_SPEED_BUDGET", "2.5"))
SINGLE_SPEED_RETIME = os.environ.get("HCTF_SINGLE_SPEED_RETIME", "1") != "0"   # re-time once alone before flagging
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
# Lanes whose day N+1 single starts from day N's solver (+ its cases). Mobile + warmups joined 2026-10-15 (user OK):
# warmups Mastery = every earlier day's encoding; D15 mobile Mastery mixed earlier days' APKs.
CUMULATIVE_LANES = tuple(x.strip() for x in os.environ.get(
    "HCTF_CUMULATIVE_LANES", "binary-reverse-engineering,script-analysis,mobile-android,warmups").split(",") if x.strip())


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
VARIANT_RE = re.compile(r"^(d\d{2}[-_][a-z0-9]+[-_])\d{3}(?=[-_])")


def field_shape(aid):
    """An answer id minus its set prefix and per-variant counter: `set1.d09-pe-003-pe-x-hex` -> `d09-pe-N-pe-x-hex`.
    D10 metadata: TT/Mastery asked `d09-pe-00{2,3,4}-...` = the Single's own `d09-pe-001-...` field re-rolled."""
    return VARIANT_RE.sub(r"\1N", SET_RE.sub("", aid or ""))


def prior_case_shapes(prior):
    """Field shapes every regression case of an earlier solver asks (read from ITS cases/, not today's staged copy).
    Lets the dry run name today's NEW ids even when the prior solver fills all of them (D11 script: 811/811 answered,
    the worker spent ~4 turns finding the 58 new TypeScript ids). None when there is no corpus to compare against."""
    shapes = set()
    for f in (Path(prior) / "cases").glob("*/contract.json"):
        try:
            shapes |= {field_shape(a) for a in _contract_ids(json.loads(f.read_text()))}
        except (OSError, ValueError):
            continue
    return shapes or None


def _contract_ids(contract):
    return [a for a in list((contract or {}).get("answer_ids") or [])
            + [q.get("id") or "" for q in (contract or {}).get("questions") or []] if a]


def _contract_shape(contract):
    """(answer-id families with the set prefix + variant counter stripped, artifact member extensions) of a contract."""
    fams = {field_shape(a) for a in _contract_ids(contract)}
    exts = set()
    for q in (contract or {}).get("questions") or []:
        art = (q.get("artifact") or "").split("->")[-1].strip()
        m = re.search(r"\.([A-Za-z0-9]{1,8})$", art)
        if m:
            exts.add(m.group(1).lower())
    return fams, exts


_SHAPE_LOCK = threading.Lock()


def lane_known_shapes(lane, day):
    """Field shapes this lane asked on any EARLIER day (single / time_trial / mastery contracts as saved). Cached per
    file (size + mtime) in .run/shape-cache.json: script's Mastery contracts are ~3 MB each."""
    with _SHAPE_LOCK:   # five lanes build their single prompts at once at the drop
        return _lane_known_shapes(lane, day)


def _lane_known_shapes(lane, day):
    cache_p = ROOT / ".run" / "shape-cache.json"
    try:
        cache = json.loads(cache_p.read_text())
    except (OSError, ValueError):
        cache = {}
    known, dirty = set(), False
    for m in sorted(ROOT.glob("challenges/day*/*/meta.json")):
        dm = re.match(r"day(\d+)$", m.parent.parent.name)
        if not dm or int(dm.group(1)) >= day:
            continue
        try:
            if json.loads(m.read_text()).get("lane") != lane:
                continue
        except (OSError, ValueError):
            continue
        for f in m.parent.glob("*/contract.json"):
            try:
                st = f.stat()
                key, sig = str(f.relative_to(ROOT)), f"{st.st_size}:{int(st.st_mtime)}"
                if (cache.get(key) or {}).get("sig") != sig:
                    cache[key] = {"sig": sig, "shapes": sorted({field_shape(a) for a in
                                                                _contract_ids(json.loads(f.read_text()))})}
                    dirty = True
                known |= set(cache[key]["shapes"])
            except (OSError, ValueError):
                continue
    if dirty:
        try:
            tmp = cache_p.with_suffix(".tmp")
            tmp.write_text(json.dumps(cache))
            tmp.replace(cache_p)
        except OSError:
            pass
    return known


DELTA_NOVEL_CHARS = int(os.environ.get("HCTF_DELTA_NOVEL_CHARS", "1500"))


def mastery_delta(single_contract, timed_contracts, known=None):
    """What the Time Trial / Mastery contracts ask that today's Single does NOT (compounding Mastery: earlier days'
    concepts mixed in). -> short text for the single prompt, '' when the timed contracts add nothing.
    `known`: callable -> field shapes this lane asked on earlier days (lane_known_shapes), called only when there IS a
    delta. Ids NEW to the lane come first and are all listed (D15 metadata: the one new id,
    `metadata-day-15-synthesis-sha256-order`, sat at #20 of 23 alphabetically, past a 12-id cut -> TT missed it)."""
    sfam, sext = _contract_shape(single_contract)
    if not sfam:
        return ""
    extra_f, extra_e = set(), set()
    for tc in timed_contracts:
        fam, ext = _contract_shape(tc)
        # compared on field_shape, SHOWN as a real id (set prefix stripped) the worker can grep in the timed contracts
        extra_f |= {SET_RE.sub("", a) for a in _contract_ids(tc) if field_shape(a) in fam - sfam}
        extra_e |= ext - sext
    if not extra_f and not extra_e:
        return ""
    parts = []
    if extra_f:
        ex = sorted({field_shape(x): x for x in sorted(extra_f, reverse=True)}.values())   # one example per field
        try:
            seen = known() if callable(known) else (known or set())
        except Exception:  # noqa: BLE001 - the hint must never cost the single
            seen = set()
        novel = [x for x in ex if field_shape(x) not in seen] if seen else []
        carried = [x for x in ex if x not in novel]
        if not seen:
            # no lane history to compare against (first day / lookup failed): every extra id, character-capped
            shown = []
            for x in ex:
                if sum(len(y) + 4 for y in shown) + len(x) > DELTA_NOVEL_CHARS:
                    break
                shown.append(x)
            parts.append(f"{len(ex)} question id(s) the Single never asks, e.g. " + ", ".join(f"`{x}`" for x in shown))
            carried = []
        if novel:
            shown, size = [], 0
            for x in novel:
                if size + len(x) > DELTA_NOVEL_CHARS:
                    break
                shown.append(x)
                size += len(x) + 4
            more = f" (+{len(novel) - len(shown)} more in the timed contracts)" if len(shown) < len(novel) else ""
            parts.append(f"{len(novel)} question id(s) NEW to this lane (no earlier day asked them, no earlier solver "
                         "answers them -- read their question text in the timed contracts): "
                         + ", ".join(f"`{x}`" for x in shown) + more)
        if carried:
            parts.append(f"{len(carried)} id(s) carried over from earlier days, e.g. "
                         + ", ".join(f"`{x}`" for x in carried[:8]))
    if extra_e:
        parts.append("artifact kinds the Single doesn't ship: " + ", ".join(f"`.{e}`" for e in sorted(extra_e)))
    return ("MASTERY COMPOUNDS: the Time Trial / Mastery contracts (status-time, under this challenge's time_trial/ and "
            "mastery/ dirs) ask " + "; ".join(parts) + ". solve.py must answer those too from the timed bytes -- "
            "dispatch on question text / artifact type; reuse earlier days' parsing for earlier days' concepts.")


def _is_skeleton(sdir):
    """solve.py is still the untouched harness skeleton (rehearsal D10: 3 lanes speculatively pushed it at chain start, 5 s
    each under contention, for code no attempt would ever run)."""
    try:
        return (Path(sdir) / "solve.py").read_bytes() == (ROOT / "hctf" / "templates" / "solve_skeleton.py").read_bytes()
    except OSError:
        return False


def _link_or_copy(src, dst):
    """copytree copy_function: a case's artifacts/ bytes (write-once GM downloads, ~99% of a corpus) are HARDLINKED,
    everything else (contract/expected JSON, code) copied so an in-place edit never reaches the earlier day. D9-D11:
    copying binary's 411-654 MB cases/ stalled EVERY worker's tool calls 6-17 s (probe: trivial jq 0.05 -> 2.2 s
    during the copy, 0.05 s during a 0.04 s hardlink pass). add_case rmtree()s before re-saving: links stay safe."""
    if "artifacts" in Path(src).parts:
        try:
            os.link(src, dst)
            return dst
        except OSError:  # cross-device / existing dst / no link support: plain copy
            pass
    return shutil.copy2(src, dst)


def stage_prior_solver(prior, sdir, cases=True):
    """Copy an earlier day's solver dir (__pycache__ and generalize scratch excluded; cases/ only when `cases`) into
    `sdir`, keeping anything already there. Returns `sdir`."""
    sdir = Path(sdir)
    sdir.mkdir(parents=True, exist_ok=True)
    skip = ("__pycache__", ".generalize-*", "*.pyc") + (() if cases else ("cases",))
    shutil.copytree(prior, sdir, dirs_exist_ok=True, ignore=shutil.ignore_patterns(*skip), copy_function=_link_or_copy)
    return sdir


# Lanes whose single starts from the LANE solver (challenges/_lane/<lane>/solver, a cumulative registry front-end)
# instead of the bare skeleton. Off ("") = the skeleton, as before.
LANE_SEED_LANES = {x.strip() for x in os.environ.get("HCTF_LANE_SEED_LANES", "metadata-forensics").split(",") if x.strip()}


def lane_seed_dir(lane):
    """The lane solver dir to seed a new day's solver from, or None (lane not seeded / no lane solver)."""
    if lane not in LANE_SEED_LANES:
        return None
    dirs = paths.lane_solver_dirs(lane)
    return dirs[0] if dirs else None


def lane_seed_note(seed, sdir):
    return (f"The harness SEEDED `{Path(sdir).relative_to(ROOT)}/solve.py` from this lane's cumulative solver "
            f"(`{Path(seed).relative_to(ROOT)}`): through `lib.meta` it already answers every GM-verified field family "
            "of earlier days (identity/hashes/magic, text BOM, JPEG/PNG dims, PDF header, ZIP EOCD/CD names, PE "
            "machine/entry/version strings, .NET MVID, MSI ProductCode; `python3 -c 'import lib.meta as m; "
            "print(m.known_fields())'` lists them with their tier). Do NOT rewrite it and don't look for earlier days' "
            "solvers: add ONLY today's new field(s) in its `local_answer()` (derive from the bytes; return None for "
            "anything else), and check the speculative values lib.meta gives for today's ids against the bytes -- "
            "a speculative extractor is a guess, not a verified answer. If today's field is a near-name of a "
            "registered one (lib.meta.resolve already maps `<field>_windows`/`_utc`/... and `<field>_<more>` onto "
            "it), DELEGATE in `local_answer()` to that extractor (e.g. lib.meta.prebuilt.<fmt> `parse()`/`*_value`) "
            "instead of writing a new parser -- D14's LNK parser was already in lib/meta/prebuilt/lnk.py. Run Python "
            "with `.venv/bin/python` (LnkParse3, regipy, python-evtx, pefile, oletools live there, not in the system "
            "python3). Note any new field in `## Proposed lib additions` of solver/NOTES.md; the post-run ratchet "
            "folds it into lib/meta.")


def stage_prior_cases(prior, sdir):
    """The prior solver's cases/ (regression + variant corpus), copied AFTER the worker's go: D10 binary's go waited
    11.6 s on Day 9's 411 MB cases/ while the code it needs was 1 file. Joined before anything reads cases/.
    Artifacts are hardlinked (_link_or_copy): the copy itself stalled every other worker."""
    src = Path(prior) / "cases"
    if src.is_dir():
        shutil.copytree(src, Path(sdir) / "cases", dirs_exist_ok=True, ignore=shutil.ignore_patterns("__pycache__"),
                        copy_function=_link_or_copy)


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


COVERAGE_CUES = os.environ.get("HCTF_COVERAGE_CUES", "1") == "1"
COVERAGE_CUES_CHARS = int(os.environ.get("HCTF_COVERAGE_CUES_CHARS", "4500"))


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
    cov = ROOT / "reference" / "coverage" / f"{lane}.md"
    if COVERAGE_CUES and cov.exists():
        # Concepts this lane has NOT met yet (coverage atlas, 2026-10-15): fingerprints -> standard tool, so an unseen
        # format/codec/language is identified in a turn or two instead of explored from scratch.
        body = _log_section(cov.read_text(errors="replace"), "Recognition cues", COVERAGE_CUES_CHARS)
        if body:
            out += (f"\n\nNOT-YET-SEEN concepts of this lane (`{cov.relative_to(ROOT)}`, full table there):\n" + body)
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
    the real bytes. expected.json holds only answers the GM already confirmed (often empty here). VERIFIED_GREEN: also
    the answers the GM accepted on THIS attempt in-window (last_timed `verified` / `fixed` / `partial_fixed`) and a
    gm_feedback.json {attempt, rejected: {aid: [values the GM judged wrong]}, require_complete} that test_solver
    enforces -- so "green" on this case means GM-verified fields right, no rejected value repeated, every field filled."""
    contract = cli.load(cid, "start.json")
    art = timed.artifacts_for(cid, contract)
    if contract and art:
        name = f"variant-{solvers.mode_of(cid)}-{(cli.attempt_id(contract) or 'x')[:8]}"
        expected = timed.present_only(contract, art, cli.confirmed_answers(cid))
        feedback = None
        last = (timed.last_result(cid) or {}) if VERIFIED_GREEN else {}
        att = cli.attempt_id(contract)
        if last and att and last.get("attempt_id") == att:
            ver = {**(last.get("verified") or {}), **(last.get("partial_fixed") or {}), **(last.get("fixed") or {})}
            expected = {**timed.present_only(contract, art, ver), **expected}
            rejected = {}
            for pair in (last.get("partial_wrong") or []) + (last.get("wrong") or []):
                if isinstance(pair, (list, tuple)) and len(pair) == 2 and pair[1] not in (None, ""):
                    a, v = pair
                    if expected.get(a) != v and v not in rejected.setdefault(a, []):
                        rejected[a].append(v)
            feedback = {"attempt": att, "rejected": {a: v for a, v in rejected.items() if v},
                        "require_complete": True, "verified": len(expected)}
        case = solvers.add_case(sdir, name, timed.trim_to_present(contract, art), art, expected)
        if feedback is not None:
            (case / "gm_feedback.json").write_text(json.dumps(feedback, indent=1, ensure_ascii=False))
        return case


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
# Today-probe (hctf/today_probe.py, warmups): yesterday's verified Mastery sets re-split with TODAY's codec (inferred from
# the Single) on a new last line -- D12/D13's first Mastery attempts failed on exactly that mix (reversal / Atbash vs
# rot-N on 11/58 and 24/63 sets, then ~45-400 s of evidence pull + generalize). Starts beside the compound probe at the
# Single's CORRECT, consumed only before Mastery (bounded wait) or by a Mastery-failure generalize; misses ->
# compound-today-* cases + one generalize BEFORE the Mastery attempt.
TODAY_PROBE = os.environ.get("HCTF_TODAY_PROBE", "1") != "0"
TODAY_PROBE_LANES = {x.strip() for x in os.environ.get("HCTF_TODAY_PROBE_LANES", "warmups").split(",") if x.strip()}
# Up to this long before the (one-shot) Mastery attempt: rehearsal fair D14 -- the probe flagged the miss 22 s after a 5 s wait
# had given up; the attempt failed and cost a generalize + the untimed fallback. Pre-clock time, bounded by the probe.
TODAY_PROBE_WAIT = float(os.environ.get("HCTF_TODAY_PROBE_WAIT", "30"))
# re-probes on fresh random draws after a today-probe-triggered generalize, before the (one) Mastery attempt
TODAY_RECHECKS = int(os.environ.get("HCTF_TODAY_RECHECKS", "2"))
TODAY_MERGE_WAIT = float(os.environ.get("HCTF_TODAY_MERGE_WAIT", "5"))   # the lane-agnostic merge probe (advisory)
# Lane-agnostic variant (today_probe.merge_probe): today's Single appended as set N+1 of yesterday's verified Mastery
# contract; a miss counts only when the solver passes both halves alone. Same slot / consumption as the today-probe.
TODAY_MERGE_PROBE = os.environ.get("HCTF_TODAY_MERGE_PROBE", "1") != "0"
TODAY_MERGE_LANES = {x.strip() for x in os.environ.get(
    "HCTF_TODAY_MERGE_LANES", "metadata-forensics,binary-reverse-engineering,script-analysis").split(",") if x.strip()}
# Verified-green (D12: generalize #1 went "green" on a variant case whose answers nobody had verified -- every field
# filled -- and the untimed retry came back 11/58 wrong): capture_variant folds the GM's in-window verdicts into the
# variant case (accepted answers -> expected.json, rejected values -> gm_feedback.json, which solvers.test_solver
# enforces), and the green watcher never ends a worker on fill-only evidence unless a GM-verified target passes too.
VERIFIED_GREEN = os.environ.get("HCTF_VERIFIED_GREEN", "1") != "0"
# Run the hot-path profile for a speed generalize in a thread beside the baseline replay (SIGINT at
# HCTF_PROFILE_SECONDS -> <mode dir>/profile.txt the worker reads) instead of up to 45 s before the worker launch.
PROFILE_ASYNC = os.environ.get("HCTF_PROFILE_ASYNC", "1") != "0"
PROFILE_SECONDS = float(os.environ.get("HCTF_PROFILE_SECONDS", "10"))
# Warm Single workers: launched at chain start beside GM start/download/triage (workers.WarmWorker). 0 = cold launch.
WARM_WORKERS = os.environ.get("HCTF_WARM_WORKERS", "1") != "0"
# Prior-solver dry run (cumulative lanes): diagnostics of yesterday's solver on today's bytes, never its values.
PRIOR_DRY_RUN = os.environ.get("HCTF_PRIOR_DRY_RUN", "1") != "0"
# Hand the Single worker its go signal before triage's recon section (filled in afterwards) when the prior solver's dry
# run answers this share of today's ids.
DEFER_RECON = os.environ.get("HCTF_DEFER_RECON", "1") != "0"
DEFER_RECON_RATIO = float(os.environ.get("HCTF_DEFER_RECON_RATIO", "0.8"))
# Copy the latest earlier solver of a cumulative lane into today's solver dir beside triage (else the worker does it).
PRESTAGE_PRIOR = os.environ.get("HCTF_PRESTAGE_PRIOR", "1") != "0"
# Pre-push + warm the verified Single solver on Homebase at "ready" (workers.prepush_solver). 0 = push at kickoff.
PREPUSH = os.environ.get("HCTF_PREPUSH", "1") != "0"
PREPUSH_AT_STAMP = os.environ.get("HCTF_PREPUSH_AT_STAMP", "1") != "0"   # start the pre-push at the solver stamp
# ... and speculatively (files only, no zygote warm) once solve.py code has been unchanged PREPUSH_STABLE s, at most
# PREPUSH_SPEC_MAX times per Single (LLM turns pause >1 s after most edits, so each settled edit ships). r10a: stamps
# land 0.2-0.6 s before the verdict (mobile/warmups/metadata), so the stamp alone saved ~0; a staged prior solver
# (script) is final ~T+8 and binary's last edit came 2.6 s before its stamp.
PREPUSH_STABLE = float(os.environ.get("HCTF_PREPUSH_STABLE", "1.0"))
PREPUSH_SPEC_MAX = int(os.environ.get("HCTF_PREPUSH_SPEC_MAX", "12"))   # 12-140 KB tars, no warm: a bound, not a budget
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


def today_probe(sdir, seconds=30, kind="codec", salt=0):
    """-> hctf.today_probe.probe() (kind codec: warmups) / merge_probe() (kind merge) result dict for the single's solver
    (status clean|miss|unidentified|...). salt > 0 (codec): a fresh random draw for a re-probe."""
    from . import today_probe as tp
    try:
        res = (tp.merge_probe(sdir, deadline=time.time() + seconds) if kind == "merge"
               else tp.probe(sdir, deadline=time.time() + seconds, salt=salt))
    except Exception as e:  # noqa: BLE001 - advisory
        res = {"status": "error", "error": str(e)[:200], "results": [], "hard": []}
    res["kind"] = kind
    return res


def remeasure_estimate(sdir, mut_summary, mastery_contract, reps=2):
    """mastery_estimate from the base + mastery-shape mutation cases re-timed SEQUENTIALLY (best of `reps`), or None."""
    shape = next((r for r in (mut_summary or {}).get("results") or [] if r.get("mutation") == "mastery-shape"
                  and r.get("ok") and r.get("case")), None)
    if not shape or not (mut_summary or {}).get("base"):
        return None

    def best(case):
        case = Path(case)
        try:
            contract = json.loads((case / "contract.json").read_text())
        except (OSError, ValueError):
            return None
        ts = []
        for _ in range(reps):
            _got, err, dt = solvers.run_solver(Path(sdir), contract, case / "artifacts", 30)
            if err:
                return None
            ts.append(dt)
        return min(ts)
    b, two = best(Path(sdir) / "cases" / mut_summary["base"]), best(shape["case"])
    if b is None or two is None:
        return None
    return mastery_estimate(dict(mut_summary, base_seconds=b, results=[dict(shape, seconds=two)]), mastery_contract)


LATE_PROBE_WAIT = float(os.environ.get("HCTF_LATE_PROBE_WAIT", "2"))
ESTIMATE_MIN_MARGINAL = float(os.environ.get("HCTF_ESTIMATE_MIN_MARGINAL", "0.15"))


def tt_solve_cap(tt_last, mastery_contract):
    """Upper bound on the Mastery solve from the passing Time Trial's measured in-window `solve` phase (one set, same
    executor): solve x Mastery sets x 1.5 (floor 0.05 s/set). None without a correct TT with phases or a set count."""
    try:
        last = json.loads(Path(tt_last).read_text())
        solve = float((last.get("phases") or {})["solve"])
        mc = json.loads(Path(mastery_contract).read_text())
    except (OSError, ValueError, TypeError, KeyError):
        return None
    if last.get("result") != "correct":
        return None
    ids = mc.get("answer_ids") or [q.get("id") for q in mc.get("questions") or [] if q.get("id")]
    sets = {a.split(".", 1)[0] for a in ids if re.match(r"(set|slot)\d+\.", a or "")}
    if not sets:
        return None
    return round(max(solve, 0.05) * len(sets) * 1.5, 2)


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
    if base is not None and two - float(base) < ESTIMATE_MIN_MARGINAL:
        # A 1-vs-2-set difference this small is process-start jitter, not per-set work: D9 warmups extrapolated ~0.1 s
        # of jitter x 43 sets to a 7.44 s estimate (gate 14 s) for a 0.3 s real solve.
        per = 0.005
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
        self._genx()
        (self.root / "meta.json").write_text(json.dumps({"base": base, "lane": self.lane, "name": self.name,
                                     "ids": {m: e["id"] for m, e in self.entries.items()}}, indent=2, ensure_ascii=False))

    def _genx(self):
        """(lock, {cid: generalize count}), created lazily (tests build Chain without __init__). The lock picks ONE
        generalize winner: the chain's own worker or the duel (hctf/duel.py, which reads the same `_gen_lock`)."""
        d = self.__dict__
        return d.setdefault("_gen_lock", threading.Lock()), d.setdefault("_gen_count", {})

    # -- workers
    def _worker_env(self, cid, stage):
        return {"HCTF_CHAL": cid, "HCTF_BASE": self.base, "HCTF_STAGE": stage, "HCTF_SOLVER_DIR": self.sdir,
                "HCTF_CHAL_DIR": cli.cdir(cid), "HCTF_LANE": self.lane}

    def _launch_warm(self, cid):
        """Start the Single worker NOW (chain start) with the static prompt; the triage follows (WarmWorker)."""
        prior = prior_solver_dir(self.lane, self.sdir)
        if prior and PRESTAGE_PRIOR and not (self.sdir / "solve.py").exists():
            prior_note = (f"This lane's contract is CUMULATIVE: `{prior.relative_to(ROOT)}` is the latest earlier "
                          f"solver of this lane and already answers every earlier family. The harness is copying it "
                          f"(all files) into `{self.sdir.relative_to(ROOT)}` right now -- it is in place before your go "
                          "signal; do NOT copy it yourself. Add only today's new families. "
                          "Never use an old solver's output as your answer without today's bytes behind it.")
        elif prior:
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
        self._dry_fut = ThreadPoolExecutor(max_workers=1).submit(
            lambda: solvers.dry_run_diagnostics(prior, contract, art, PRIOR_DRY_RUN_SECONDS,
                                                known=prior_case_shapes(prior), shape=field_shape))

    def _recon_deferrable(self):
        """Triage may hand off before its recon section when yesterday's solver (dry run, already finished) answers
        >= DEFER_RECON_RATIO of today's ids: the worker's job is the delta, found from the dry run's empty fields."""
        fut = getattr(self, "_dry_fut", None)
        if not (DEFER_RECON and fut is not None and fut.done()):
            return False
        try:
            d = fut.result()
        except Exception:  # noqa: BLE001
            return False
        return bool(d.get("total")) and not d.get("timed_out") and d["answered"] / d["total"] >= DEFER_RECON_RATIO

    def _prior_dry_run_text(self, cid=None):
        fut = getattr(self, "_dry_fut", None)
        if fut is None:
            return ""
        if GO_EARLY and cid is not None and not fut.done():
            # don't hold the go for it (binary go came at T+16-22 behind the dry run): its note follows via the inbox
            def late(f, cid=cid):
                try:
                    d = f.result()
                except Exception:  # noqa: BLE001
                    return
                say(f"[{self.base}] prior solver dry run (late): {d['seconds']}s, timed_out={d['timed_out']}, "
                    f"answered {d['answered']}/{d['total']}")
                self._deliver_note(cid, "PRIOR-SOLVER DRY RUN (finished after your start): " + solvers.render_dry_run(d),
                                   key="dry-run")
            fut.add_done_callback(late)
            say(f"[{self.base}] go sent without the prior-solver dry run (still running; note follows via inbox)")
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
        if rc == workers.AUTH_RC:
            say(f"!!! [{cid}] Claude auth failed: run `claude auth login` on the host, then re-run this chain")
            set_state(self.base, help="Claude auth failed (OAuth expired?): `claude auth login`, then re-run the chain")
        return rc

    def fix(self, cid, contract, art, problems, left):
        prompt = workers.render("fix", cid=cid, base=self.base, seconds_left=int(left or 0),
                                deadline=contract.get("deadline"), chal_dir=cli.cdir(cid).relative_to(ROOT),
                                solver_dir=self.sdir.relative_to(ROOT), persona=workers.lane_persona(self.lane),
                                problems="\n".join(f"  - {p}" for p in problems) or "  - (none reported)")
        set_state(self.base, stage=f"{solvers.mode_of(cid)}:fixing")
        self.run_worker(cid, "fix", prompt, max(20, (left or 600) - 15), urgent=True)

    def generalize(self, cid, wrong=None, fixed=None, diag=None, live=None):
        """Offline (no clock): improve the solver so it handles the captured variant and still passes old cases.
        `wrong`: (answer_id, solver_value) pairs the GM rejected; `fixed`: {answer_id: value} the GM accepted as the
        right label on that attempt; `diag`: facts about the attempt (window, elapsed, how much was judged), so the
        worker is told the truth — "timing" only when every field was actually judged correct."""
        self._bg_gen_take(cid, "a new generalize starts")
        mode = solvers.mode_of(cid)
        probs = []
        fam = None
        if self.lane == "script-analysis" and FAMILY_PROBE and wrong:
            exts = _exts(failing_artifacts(self.sdir, mode, [a for a, _ in wrong])[1])
            if exts:   # runs beside the baseline replay below (~1.7 s of venv + 2 solver runs off the critical path)
                fam = ThreadPoolExecutor(max_workers=1).submit(
                    lambda: family_probe(self.sdir, exts, noise=self._family_noise())[0])
        d0 = diag or {}
        prof_async = None
        if PROFILE_ASYNC and (d0.get("solver_too_slow") or d0.get("single_seconds")):
            # beside the baseline replay, SIGINT-bounded; the worker reads <mode dir>/profile.txt (8-30 s saved per speed
            # generalize: the synchronous profile ran to its 45 s cap on a solver that couldn't finish)
            prof_async = self._start_profile(cid, bool(d0.get("single_seconds")))
        # ONE fast parallel replay (8s/case) serves both the problem list and the transactional baseline (was a full
        # 120s/case run here plus a second baseline run: 141s before the worker spawned, replay run 2).
        ensure_case_and_test(paths.base_id(cid), self.sdir, full=False)
        res = self._baseline_results()
        self._pre_res = res
        for r in (res or []):
            if not r.get("ok"):
                probs.append(f"case {r['case']}: error={r.get('error')} diff={r.get('diff')} unverified={r.get('unverified')}"
                             + (f" answered={r.get('answered')}/{r.get('total')} GM-REJECTED values produced again="
                                f"{r.get('rejected_got')}" if r.get("rejected_hits") else ""))
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
        # A probe-driven generalize (compounding / mutation misses: no attempt verdict) gets the table too when the
        # suite's own misses are all labels (alt armA D15 script: 35 compound cases, `delayed` vs today's `percent`).
        tab_wrong = wrong or [(a, dd.get("got")) for r in (res or []) if not r.get("ok")
                              for a, dd in (r.get("diff") or {}).items()]
        if label_only_failure(tab_wrong):
            gm_wrong += ("\n  - LABEL-ONLY: every wrong field is a closed-vocab label -- follow LABEL-ONLY REJECTIONS below "
                         "(fit one byte-observable rule to every case's verified labels; no root-cause hunt, no date "
                         "gates unless the table prints GENERATION SPLIT)")
            try:
                lt = label_table(self.sdir, res, tab_wrong)
                if lt:
                    gm_wrong += "\n  - " + lt
            except Exception as e:  # noqa: BLE001 - advisory
                say(f"[{cid}] label table note: {e}")
        if d.get("accepted"):
            acc = d["accepted"]
            gm_wrong += (f"\n  - the GM ACCEPTED these {len(acc)} answered field(s) on this attempt -- keep producing them: "
                         + ", ".join(f"`{a}`" for a in acc[:30]) + (" ..." if len(acc) > 30 else ""))
        if d.get("window") or d.get("elapsed"):
            gm_wrong += f"\n  - attempt facts: window {d.get('window')}s, elapsed {d.get('elapsed')}s, routed {d.get('routed') or 'local'}"
        if d.get("early"):
            gm_wrong += ("\n  - EARLY START: the attempt is still being judged in-window while you work. The GM's verdicts on the "
                         f"answered fields land in `cases/{d.get('variant_case')}/` (expected.json = accepted, "
                         "gm_feedback.json = rejected values) within ~20 s: re-run `hctf solver-test` before you finish.")
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
        if d.get("compound_today"):
            gm_wrong += ("\n  - NO MASTERY ATTEMPT HAS RUN YET -- TODAY'S CODEC IN A MASTERY MIX: the harness rebuilt yesterday's "
                         "GM-verified Mastery sets with one more line, today's codec (identified from the Single's bytes), "
                         "cuts mid-word like the GM's (the `compound-today-*` cases: same contract + verified slugs, "
                         "`truth.json` = every line's codec, plain piece and encoded bytes). D12/D13's first Mastery "
                         "attempts failed on exactly this. Make every compound-today-* case pass WITHOUT breaking any "
                         "other case, generically, in LIB: add today's codec to `lib.warmups_codecs.DAYS` as "
                         "(day, name, exact encoder, decoder, free) -- `lib.decode.decode_chunked` decodes line k with "
                         "day k's codec and checks the exact re-encode (right on every verified set D1-D14); a "
                         "free-text codec also goes in `lib.decode.FREE_CODECS` / `register_free` for the joint "
                         "fallback. Make solve.py decode numbered blobs with `lib.decode.decode_chunked` ONLY -- no "
                         "private per-line or joint decoder (D14: a solver-local `_joint` left set22 empty).\n"
                         + "\n".join("    " + ln for ln in d["compound_today"].splitlines()))
        if d.get("compound_merge"):
            gm_wrong += ("\n  - NO MASTERY ATTEMPT HAS RUN YET -- MERGED-SHAPE REHEARSAL: Mastery compounds today's concept with "
                         "earlier days'. The `compound-merge-*` case is yesterday's GM-verified Mastery contract with "
                         "today's Single appended as the last set (its delivery renamed in yesterday's convention; "
                         "every expected answer GM-verified). The solver answers both halves alone but not merged: "
                         "make it route each set by its own artifact / question text (no one-family-per-contract "
                         "assumption, no hard-coded set count or delivery name), without breaking any case.\n"
                         + "\n".join("    " + ln for ln in d["compound_merge"].splitlines()))
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
        if d.get("parallel_sets"):
            ps = d["parallel_sets"]
            gm_wrong += (f"\n  - SOLVE MASTERY SETS IN PARALLEL: `cases/{ps['case']}` has {ps['sets']} sets and takes {ps['seconds']}s "
                         f"({ps['per_set']}s per set) solved one after another; a Mastery attempt runs every set inside ONE clock "
                         "on a 2-vCPU VM. Restructure main(): group the (answer_id, question) pairs with "
                         "`lib.common.group_by_set(pairs)` and solve each group in a fork `ProcessPoolExecutor` "
                         "(max_workers=min(len(groups), os.cpu_count())), merging the dicts; single-set contracts stay "
                         "sequential; any pool error falls back to the sequential loop. Copy the pattern from "
                         "`hctf/templates/solve_skeleton.py` main(). Change NO answer: every case must still pass.")
        if prof_async is not None:
            gm_wrong += (f"\n  - HOT PATH: the harness is profiling `cases/{prof_async[0]}` right now (cProfile, sorted by "
                         f"cumulative time, interrupted at {PROFILE_SECONDS:g}s if it runs that long) -> "
                         f"`{_rel(prof_async[1])}` appears within ~{PROFILE_SECONDS + 3:g}s of your start: read it "
                         "first instead of re-profiling (profile yourself only if it never shows up).")
        elif d.get("solver_too_slow") or d.get("single_seconds"):
            # The harness profiles the slow case itself (newest variant-* for an in-window timeout, else the single).
            cases = self.sdir / "cases"
            var = sorted(cases.glob("variant-*/"), key=lambda p: p.stat().st_mtime)
            prof = solvers.profile_solver(self.sdir, var[-1] if var and not d.get("single_seconds") else cases / "single_solve")
            if prof:
                gm_wrong += ("\n  - HOT PATH (harness-run profile, sorted by cumulative time -- start here, no need to re-profile):\n"
                             + "\n".join("    " + ln for ln in prof.splitlines()))
        if RETRIEVAL:
            try:
                from . import retrieval
                rnote = retrieval.note_for(cli.cdir(paths.base_id(cid)), self.lane, self.root.name, k=2)
                if rnote:
                    gm_wrong += "\n  - (FYI) " + rnote.strip().replace("\n", "\n    ")
            except Exception as e:  # noqa: BLE001 - advisory
                say(f"[{cid}] retrieval note: {e}")
        left_att = (timed.last_result(cid) or {}).get("attempts_remaining")
        low_budget = left_att is not None and left_att < HARVEST_MIN_ATTEMPTS
        if low_budget and HARVEST_VARIANTS:
            say(f"[{cid}] only {left_att} unique attempt(s) left for this mode today: no variant harvest")
        harvest = bool(HARVEST_VARIANTS and wrong and all(v is None for _, v in wrong) and remote.gm_transport() == "local"
                       and not low_budget and not d.get("early"))   # early: this attempt's clock is still live
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
                    ftxt = fam.result(timeout=FAMILY_EVIDENCE_WAIT)   # ~2 s typical; never hold the launch for long
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
        if live is not None:
            live.link(green)   # a live-answer pass ends this worker (its edits are still judged by _accept_or_restore)
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
        expected_before = self._exp_before = self._expected_snapshot()   # (_early_join folds late GM verdicts in)
        gcount = self._genx()[1]
        gcount[cid] = gcount.get(cid, 0) + 1
        gen_duel = None
        if not harvest and (targets or fill) and STOP_WHEN_READY:
            lab = label_only_failure(wrong)
            gen_duel = self._maybe_start_gen_duel(cid, prompt, targets, fill, bool(d.get("solver_too_slow")), green,
                                                  first=lab or bool(d.get("solver_too_slow")), quick=lab)
        try:
            self._gen_prompt = prompt   # a background generalize after a live pass reuses it (_start_bg_gen)
            self.run_worker(cid, "generalize", prompt, GENERALIZE_TIMEOUT, stop=green)
        finally:
            self._restore_expected(cid, expected_before)
            done.set()
            if gen_duel is not None:
                gen_duel.stop()
            if watch.is_alive():
                watch.join()
            if gen_duel is not None and gen_duel.won:
                try:
                    gen_duel.adopt_into(self.sdir, log=say)
                    # the duel's watcher ran the full suite on exactly this code (copy2 keeps mtimes): the accept step
                    # reuses it when the case set matches too, else re-runs (rehearsal D13 replay: 3-6 s per duel win)
                    self._green_res = getattr(gen_duel, "green_res", None)
                except Exception as e:  # noqa: BLE001 - the accept step below still judges whatever is there
                    say(f"[{cid}] duel adopt note: {e}")
            if reaper and live is not None and live.passed:
                say(f"[{cid}] passed by the live answer: not waiting for the harvest")
            elif reaper:
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

    # -- early generalize (workers.EARLY_GENERALIZE, default OFF): the daemon's mid-attempt "solved" event starts the
    #    generalize worker on the failed variant while hb_timed still localizes in-window (~15 s on D13 warmups Mastery).
    def _early_kw(self, cid, untimed=False):
        self._early = None
        if not workers.EARLY_GENERALIZE or untimed:
            return {}
        return {"on_event": lambda data: self._early_event(cid, data)}

    def _early_event(self, cid, data):
        if data.get("event") != "solved" or not data.get("local") or getattr(self, "_early", None) is not None:
            return
        tc = json.loads((Path(data["local"]) / "contract.json").read_text())
        if not data.get("attempt_id") or cli.attempt_id(tc) != data["attempt_id"]:
            return
        cli.save(cid, "start.json", tc)
        cli.save(cid, "contract.json", tc)
        case = capture_variant(cid, self.sdir)
        if case is None:
            return
        missing = list(data.get("missing") or [])
        diag = {"early": True, "variant_case": case.name, "window": data.get("window"), "phases": data.get("phases")}
        say(f"[{cid}] early generalize: solver {data.get('result')} ({len(missing)} empty) -- starting the worker on "
            f"{case.name} while the attempt is still judged")
        t = threading.Thread(target=self.generalize, daemon=True,
                             args=(cid, [(a, None) for a in missing] or None, {}, diag))
        self._early = {"thread": t, "case": case, "attempt": data["attempt_id"]}
        t.start()

    def _early_join(self, cid):
        """After the attempt's final result: fold its GM verdicts into the early variant case (and into the running
        generalize's expected snapshot, so its restore keeps them), then wait for that worker. True if one ran."""
        e, self._early = getattr(self, "_early", None), None
        if not e:
            return False
        try:
            last = timed.last_result(cid) or {}
            if last.get("attempt_id") == e["attempt"]:
                case = e["case"]
                exp = json.loads((case / "expected.json").read_text()) if (case / "expected.json").exists() else {}
                c = json.loads((case / "contract.json").read_text())
                ids = set(c.get("answer_ids") or [])
                ver = {**(last.get("verified") or {}), **(last.get("partial_fixed") or {}), **(last.get("fixed") or {})}
                exp.update({a: v for a, v in ver.items() if a in ids})
                rej = {}
                for pair in (last.get("partial_wrong") or []) + (last.get("wrong") or []):
                    if isinstance(pair, (list, tuple)) and len(pair) == 2 and pair[0] in ids and pair[1] not in (None, ""):
                        if exp.get(pair[0]) != pair[1] and pair[1] not in rej.setdefault(pair[0], []):
                            rej[pair[0]].append(pair[1])
                fb = {"attempt": e["attempt"], "rejected": {a: v for a, v in rej.items() if v}, "require_complete": True,
                      "verified": len(exp)}
                eb, fbb = json.dumps(exp, indent=2, ensure_ascii=False).encode(), json.dumps(fb, indent=1).encode()
                (case / "expected.json").write_bytes(eb)
                (case / "gm_feedback.json").write_bytes(fbb)
                snap = getattr(self, "_exp_before", None)
                if isinstance(snap, dict):
                    snap[case.name], snap[(case.name, "gm_feedback.json")] = eb, fbb
                say(f"[{cid}] early generalize: GM verdicts folded into {case.name} ({len(exp)} accepted, "
                    f"{len(fb['rejected'])} field(s) with rejected values)")
        except Exception as ex:  # noqa: BLE001 - the worker still has the bytes
            say(f"[{cid}] early verdict merge note: {ex}")
        e["thread"].join()
        return True

    def _start_profile(self, cid, single):
        """Background cProfile of the slow case (newest variant-* for an in-window timeout, else the single), SIGINT at
        PROFILE_SECONDS, written atomically to <mode dir>/profile.txt -> (case name, path) or None."""
        cases = self.sdir / "cases"
        var = sorted(cases.glob("variant-*/"), key=lambda p: p.stat().st_mtime)
        case = var[-1] if var and not single else cases / "single_solve"
        if not (case / "contract.json").exists():
            return None
        out = cli.cdir(cid) / "profile.txt"
        try:
            out.unlink(missing_ok=True)
        except OSError:
            pass

        def go():
            try:
                prof = solvers.profile_solver(self.sdir, case, timeout=PROFILE_SECONDS, interrupt=True)
                tmp = out.with_suffix(".tmp")
                tmp.write_text(prof or f"(no profile output for cases/{case.name})")
                tmp.replace(out)
            except Exception as e:  # noqa: BLE001 - advisory
                say(f"[{cid}] async profile note: {e}")
        threading.Thread(target=go, daemon=True).start()
        return case.name, out

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
        self._fill_only_said = False
        while not done.wait(GREEN_POLL):
            m = self._solver_mtimes()
            if not m or m == start or time.time() - max(m.values()) < GREEN_QUIET:
                continue
            busy = bool(harvesting and harvesting.is_set())
            key = (tuple(sorted(m.items())), len(fill), busy)
            if key == checked or busy:
                continue
            checked = key
            try:
                # targets / fill first: the whole corpus only once they pass (most edits still fail their target)
                if not solvers.targets_pass(self.sdir, targets, fill, timeout=BASELINE_CASE_TIMEOUT):
                    continue
                res = solvers.test_solver(self.sdir, timeout=BASELINE_CASE_TIMEOUT)
            except Exception:  # noqa: BLE001
                continue
            if self._solver_mtimes() != m:
                continue  # edited while testing
            ok = {r["case"] for r in res if r.get("ok")}
            filled = {r["case"] for r in res if r.get("total") and r.get("answered") == r.get("total") and not r.get("error")}
            tg, fl = targets, set(fill)
            if workers.EARLY_GENERALIZE:
                # early generalize: the variant's GM verdicts arrive mid-worker -> a fill case that became verified is a
                # target from then on (gm_feedback.json re-read by every test_solver run)
                now = {r["case"] for r in res if not r.get("unverified")}
                tg, fl = targets | (fl & now), fl - now
            fast = all(r.get("seconds", 99) < 2.0 for r in res if r["case"] in (tg | fl))
            if tg <= ok and fl <= filled and baseline <= ok and (fast or not need_fast):
                if VERIFIED_GREEN and fl and not (tg & ok):
                    # Fill-only evidence (every field answered, nothing GM-verified among the targets -- D12: "green"
                    # on an unverified variant, then 11/58 wrong): never end the worker early on that alone.
                    if not getattr(self, "_fill_only_said", False):
                        self._fill_only_said = True
                        say(f"[{self.base}] generalize: unverified variant(s) {sorted(fill)[:3]} complete, but no "
                            "GM-verified target to confirm them -> letting the worker finish")
                    continue
                with self._genx()[0]:
                    if green.is_set():
                        return   # the duel went green first
                    self._green_res = (m, self._case_names(), res)  # _accept_or_restore reuses it (same code + cases)
                    say(f"[{self.base}] generalize green ({sorted(targets | set(fill))[:3]} pass/complete, no "
                        "regressions) -> ending the worker")
                    green.set()
                return

    # -- transactional generalize: a worker that is killed / times out / breaks old cases must never leave a
    #    half-edited solver behind (happened twice on the rehearsal copy: warmups solve.py, Dim and Dimmer vbsplan.py).
    def _snap_dir(self):
        return self.root / ".generalize-snapshot"

    def _start_baseline_pre(self, cid):
        """Background, right after the single's handoff: the full-suite baseline of the handed-over solver, so a later
        generalize (TT failure / pre-Mastery probes) replays only the cases added since (main D15 script: the race-won
        solver had never run the suite -> 16 s of baseline before the generalize worker launched)."""
        if not BASELINE_PRE or not (self.sdir / "solve.py").exists():
            return
        m0, names0 = self._solver_mtimes(), self._case_names()

        def body():
            try:
                res = solvers.test_solver(self.sdir, timeout=BASELINE_CASE_TIMEOUT, parallel=BASELINE_PRE_PAR,
                                          cases=names0 or None)
                if self._solver_mtimes() == m0 and getattr(self, "_accepted_res", None) is None:
                    self._accepted_res = (m0, names0, res)
            except Exception as e:  # noqa: BLE001 - optimization only
                say(f"[{cid}] background baseline note: {e}")
        self._baseline_thr = threading.Thread(target=body, daemon=True, name=f"baseline-{self.base}")
        self._baseline_thr.start()

    def _baseline_results(self):
        """Pre-generalize baseline (every case, BASELINE_CASE_TIMEOUT). When the last accepted generalize ran the suite
        on THIS exact solver code, reuse those results and run only the cases added since (the failed attempt's
        auto-* / variant-*): rehearsal D13 replay, the full baseline sat 3-6 s on the path to every worker launch."""
        if not (self.sdir / "solve.py").exists():
            return []
        thr = getattr(self, "_baseline_thr", None)
        if thr is not None and thr.is_alive():
            thr.join(timeout=BASELINE_PRE_JOIN)   # the background baseline of this same code is nearly done
        acc = getattr(self, "_accepted_res", None)
        if acc and acc[0] == self._solver_mtimes():
            old = {r.get("case"): r for r in acc[2]}
            names = self._case_names()
            new = [n for n in names if n not in old]
            fresh = {r["case"]: r for r in (solvers.test_solver(self.sdir, timeout=BASELINE_CASE_TIMEOUT, cases=new)
                                            if new else [])}
            return [fresh.get(n) or old[n] for n in names if n in fresh or n in old]
        return solvers.test_solver(self.sdir, timeout=BASELINE_CASE_TIMEOUT)

    def _snapshot_solver(self):
        snap = self._snap_dir()
        if snap.exists():
            shutil.rmtree(snap)
        if self.sdir.exists():
            # case artifacts hard-linked (write-once GM bytes; the script corpus is ~30 MB): the snapshot sits on the
            # critical path between "blocked" and the generalize worker's launch
            shutil.copytree(self.sdir, snap, ignore=shutil.ignore_patterns("__pycache__"), copy_function=_link_or_copy)
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

    def _expected_snapshot(self):
        """{case: expected.json bytes} -- expected answers are GM-verified only; workers must not author them.
        VERIFIED_GREEN: also {(case, "gm_feedback.json"): bytes or None} -- the GM's rejected values are GM truth too."""
        snap = {p.parent.name: p.read_bytes() for p in (self.sdir / "cases").glob("*/expected.json")}
        if VERIFIED_GREEN:
            for name in list(snap):
                fb = self.sdir / "cases" / name / "gm_feedback.json"
                snap[(name, "gm_feedback.json")] = fb.read_bytes() if fb.exists() else None
        return snap

    def _restore_expected(self, cid, before):
        """Undo any worker edit to a pre-existing case's expected.json (speed-harden d08 script: the worker wrote its own
        solver output into an unverified variant's empty expected.json, freezing 3075 unjudged values as 'GM truth')
        and gm_feedback.json (restored, or removed when the worker created one)."""
        for name, data in before.items():
            case, fname = name if isinstance(name, tuple) else (name, "expected.json")
            p = self.sdir / "cases" / case / fname
            try:
                if data is None:
                    if p.exists() and p.parent.exists():
                        p.unlink()
                        say(f"[{cid}] removed worker-made cases/{case}/{fname} (GM feedback comes from the GM only)")
                elif not p.exists() or p.read_bytes() != data:
                    p.parent.mkdir(parents=True, exist_ok=True)
                    p.write_bytes(data)
                    say(f"[{cid}] restored cases/{case}/{fname} (expected answers come from the GM only)")
            except OSError as e:
                say(f"[{cid}] {fname} restore note: {e}")

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
            self._accepted_res = (self._solver_mtimes(), self._case_names(), res)   # next baseline reuses it
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

    def _reuse_race(self, cid):
        """Background, beside triage + the LLM worker: today's single bytes through the newest same-lane solvers.
        A merged set covering EVERY field (confident = the field is GM-verified in that solver's own cases; speculative
        completes it) goes first, as one submit. With RACE_PARTIAL, a rejected or incomplete set is then BANKED in parts
        (confident subset, speculative remainder, alternates for isolated wrong fields) within RACE_TOTAL_PROBES submits,
        yielding as soon as the worker submits; what was learned goes to the worker (go text or inbox). Never a brute
        force. Touches no solver files: a win is adopted by _watch_ready (staged prior verified -> worker ended)."""
        t0 = time.time()
        try:
            contract = cli.load(cid, "start.json") or cli.load(cid, "contract.json")
            art = timed.latest_artifacts(cid)
            ids = list((contract or {}).get("answer_ids") or [])
            if not ids or not art or cli.is_complete(cid):
                return
            # same-lane newest N only (no question-text index: r11b spent 18-24 s building it under drop load)
            rank = None
            if RETRIEVAL:
                from . import retrieval
                rank = retrieval.solver_rank(cli.cdir(cid), self.lane, contract) or None
            plan = solvers.reuse_plan(contract, art, self.lane, exclude=[self.sdir], timeout=REUSE_RACE_TIMEOUT,
                                      limit=REUSE_RACE_SOLVERS, by_question=False, rank=rank)
            high, spec = dict(plan["high"]), dict(plan["spec"])
            dropped = self._race_gate(contract, high, spec) if RACE_FORMAT_GATE else []
            merged = {a: high.get(a, spec.get(a)) for a in ids if a in high or a in spec}
            say(f"[{cid}] reuse race: {len(high)} confident + {len(spec)} speculative of {len(ids)} field(s) from "
                f"{len(plan['runs'])} solver(s) in {time.time() - t0:.1f}s"
                + (f"; dropped {len(dropped)} implausible value(s) {dropped[:4]}" if dropped else ""))
            if not RACE_PARTIAL:
                if len(merged) < len(ids):
                    return  # can't finish the single: leave it to the worker (its dry-run note covers the gaps)
                used = self._race_narrow(cid, merged, REUSE_RACE_PROBES)
            else:
                used = self._race_bank(cid, ids, high, spec, merged, plan)
            if cli.is_complete(cid):
                set_state(self.base, stage="single:reuse-won")
                snap = self._race_snapshot(cid, plan["best"], contract, art)
                say(f"[{cid}] reuse race WON: single CORRECT at +{time.time() - t0:.1f}s from prior solver output "
                    f"(seed {plan['best'] and Path(plan['best']).parent.name}; "
                    + ("seed verified -> the ready-watcher hands it to the timed modes)" if snap else
                       "seed does not reproduce every answer -> waiting for the worker's solver)"))
            else:
                say(f"[{cid}] reuse race: not complete after {used} submit(s) "
                    f"({len(cli.confirmed_answers(cid))}/{len(ids)} confirmed); the worker continues")
                if RACE_PARTIAL:
                    self._deliver_note(cid, self._race_note(cid, ids, merged, plan), key="race")
        except Exception as e:  # noqa: BLE001 - the race is an optimization; the worker path is unaffected
            say(f"[{cid}] reuse race note: {e}")

    def _race_gate(self, contract, high, spec):
        """Drop (in place) race values the local format checks or the slug gate refuse -> [dropped ids]."""
        qmap = cli._questions(contract)
        out = []
        for d in (high, spec):
            for a in list(d):
                v = str(d[a])
                q = qmap.get(a, {})
                if cli._format_problem(v, q) or cli._slug_problem(v, q):
                    del d[a]
                    out.append(a)
        return out

    def _race_narrow(self, cid, group, budget):
        """The original race bisect (kill-switch path): submit, halve on rejection, <= budget submits -> used."""
        left = [budget]

        def narrow(g):
            # ONE confirmed lookup per call: inside the comprehension it re-parsed start.json per field (D12 script
            # 855 x 572 KB: 4.2 s idle, ~18 s under drop load before the race's first submit)
            done = cli.confirmed_answers(cid)
            g = {a: v for a, v in g.items() if a not in done}
            if not g or left[0] <= 0 or cli.is_complete(cid):
                return
            left[0] -= 1
            kind, _b, refused = cli.submit(cid, g, force=True, probe=True, harness="race")
            if kind != "incorrect" or refused or len(g) == 1:   # only a GM rejection is bisected (429 = unjudged)
                return
            keys = list(g)
            narrow({k: g[k] for k in keys[:len(keys) // 2]})
            narrow({k: g[k] for k in keys[len(keys) // 2:]})

        narrow(group)
        return budget - left[0]

    def _race_used(self, cid):
        """(race submits so far this attempt, has the worker submitted anything) from submissions.jsonl."""
        att = cli.attempt_id(cli.load(cid, "start.json"))
        p = cli.cdir(cid) / "submissions.jsonl"
        used, worker = 0, False
        for line in (p.read_text().splitlines() if p.exists() else []):
            try:
                h = json.loads(line)
            except ValueError:
                continue
            if h.get("attempt") != att:
                continue
            if h.get("harness") == "race":
                used += 1
            elif not h.get("harness"):
                worker = True
        return used, worker

    def _race_bank(self, cid, ids, high, spec, merged, plan):
        """RACE_PARTIAL: merged (when complete) -> confident subset -> speculative remainder -> alternates for isolated
        wrong fields, all harness="race" probes within RACE_TOTAL_PROBES; stop when the worker submits -> used."""
        def left():
            used, worker = self._race_used(cid)
            return 0 if worker or cli.is_complete(cid) else RACE_TOTAL_PROBES - used

        def todo(d):
            done = cli.confirmed_answers(cid)
            return {a: v for a, v in d.items() if a not in done}

        def batch(d, bisect_budget):
            d = todo(d)
            if not d or left() <= 0:
                return set()
            kind, _b, refused = cli.submit(cid, d, force=True, probe=True, harness="race")
            if kind != "incorrect" or refused:   # accepted, or UNJUDGED (rate_limited / error): nothing to bisect
                return set()
            if len(d) == 1:
                return set(d)
            return cli._bisect_rejected(cid, d, budget=min(bisect_budget, max(left(), 0)), harness="race",
                                        families=False)

        wrong = set()
        if len(merged) == len(ids):
            wrong |= batch(merged, 0)              # complete set: one submit (a script/binary/mobile win needs no more)
        if not cli.is_complete(cid):
            wrong |= batch({a: v for a, v in high.items() if a in merged}, 2)
            wrong |= batch({a: v for a, v in spec.items() if a in merged and a not in high}, RACE_SPEC_PROBES)
        self._race_wrong = {a: merged[a] for a in wrong if a in merged}
        try:
            from . import fmtalt
        except Exception:  # noqa: BLE001
            fmtalt = None
        qmap = cli._questions(cli.load(cid, "start.json") or {})
        for a in sorted(self._race_wrong):
            if a in cli.confirmed_answers(cid):
                continue
            tried = {self._race_wrong[a]}
            alts = [v for v in plan.get("alts", {}).get(a, []) if v not in tried]
            if fmtalt is not None:
                alts += [v for v, _t in fmtalt.alternates(a, self._race_wrong[a], qmap.get(a, {}), max_n=2)]
            for v in alts:
                if left() <= 0 or v in tried:
                    break
                tried.add(v)
                kind, _b, refused = cli.submit(cid, {a: v}, harness="race")
                if kind in ("correct", "accepted"):
                    break
        used, _w = self._race_used(cid)
        return used

    def _race_note(self, cid, ids, merged, plan):
        """What the race proved, for the worker: banked count, the ids still open (+ prior solvers' values as hints, never
        as answers) and every value the GM rejected on its own."""
        conf = cli.confirmed_answers(cid)
        rest = [a for a in ids if a not in conf]
        if not conf or not rest:
            return ""
        judged = {}
        p = cli.cdir(cid) / "submissions.jsonl"
        att = cli.attempt_id(cli.load(cid, "start.json"))
        for line in (p.read_text().splitlines() if p.exists() else []):
            try:
                h = json.loads(line)
            except ValueError:
                continue
            if h.get("attempt") == att and h.get("kind") == "incorrect" and len(h.get("answers") or {}) == 1:
                for a, v in h["answers"].items():
                    judged.setdefault(a, []).append(v)
        # Compact (alt armA D15: a 3361-char note listing 80 ids + 20 hints; both workers then sent ~60 one-to-eight
        # field submits re-confirming values the prior solver already had right): families + counts, a few hints.
        fams = Counter(re.split(r"[-_]", a.split(".")[-1], 1)[0] + "-*" for a in rest)
        hints = {a: merged[a] for a in rest if a in merged and merged[a] not in judged.get(a, [])}
        note = (f"REUSE RACE (prior solvers on today's bytes): the GM already CONFIRMED {len(conf)}/{len(ids)} field(s) -- "
                f"never recompute or resubmit them. {len(rest)} remain, by family: "
                + ", ".join(f"{f} {n}" for f, n in fams.most_common(12)) + (" ..." if len(fams) > 12 else "")
                + (f" (ids: {rest})" if len(rest) <= 12 else "")
                + f". Fix the solver for those, then ONE `hctf submit {cid} --from-solver` (it sends only unconfirmed "
                "fields and bisects a rejection itself) -- no hand-made small batches.")
        if hints:
            note += (" Prior solvers' values for a few (UNVERIFIED): " + json.dumps(
                {a: str(v)[:60] for a, v in list(hints.items())[:6]}, ensure_ascii=False))
        if judged:
            note += " GM-REJECTED values (never resubmit): " + json.dumps(
                {a: [str(x)[:60] for x in v] for a, v in list(judged.items())[:10]}, ensure_ascii=False)
        return note

    def _deliver_note(self, cid, note, key):
        """A late fact for the single worker: into the go text if it hasn't been sent yet, else the inbox."""
        if not note:
            return
        with self._go_lock:
            if not self._go_sent:
                self._go_pending.append(note)
                return
        if INBOX:
            from . import inbox
            inbox.post(cli.cdir(cid), note, key=key)
            say(f"[{cid}] {key} note -> worker inbox ({len(note)} chars)")

    def _race_snapshot(self, cid, seed, contract, art):
        """The race's seed solver as a ready snapshot (`.run/spec-dayNN/<chal>-race/solver`: same depth as the real solver
        dir) if it alone reproduces every GM-confirmed answer; _watch_ready adopts it when the worker's own solver isn't
        verified yet (r11b: the staged newest solver differed from the winning seed -> 7-12 s until the worker caught up)."""
        if not seed:
            return None
        rel = self.sdir.relative_to(paths.CHALLENGES).parts
        if len(rel) != 3:
            return None
        snap = ROOT / ".run" / f"spec-{rel[0]}" / f"{rel[1]}-race" / "solver"
        if snap.exists():
            shutil.rmtree(snap)
        shutil.copytree(seed, snap, ignore=shutil.ignore_patterns("cases", "__pycache__"))
        if (self.root / "meta.json").exists():
            shutil.copy2(self.root / "meta.json", snap.parent / "meta.json")
        conf = cli.confirmed_answers(cid)
        got, err, _dt = solvers.run_solver(snap, contract, art)
        if err or not conf or any(got.get(k) != v for k, v in conf.items()):
            return None
        self._race_snap = snap
        return snap

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
            done = cli.confirmed_answers(cid)   # once per call, not per field (each re-parses start.json)
            group = {a: v for a, v in group.items() if a not in done}
            if not group or budget[0] <= 0 or cli.is_complete(cid):
                return
            budget[0] -= 1
            kind, _body, refused = cli.submit(cid, group, force=True, probe=True)
            if kind != "incorrect" or refused:   # accepted, or UNJUDGED (rate_limited / error): never "wrong"
                return
            if len(group) == 1:
                wrong.update(group)
                return
            keys = list(group)
            narrow({k: group[k] for k in keys[:len(keys) // 2]})
            narrow({k: group[k] for k in keys[len(keys) // 2:]})

        narrow(high)
        conf = cli.confirmed_answers(cid)
        rest = {a: v for a, v in spec.items() if a not in conf}
        left = [a for a in ids if a not in conf]
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
        conf = cli.confirmed_answers(cid)   # a probe below only ever confirms its own aid, checked once
        for aid, q in solvers.paired_questions(contract):
            if aid in conf or budget[0] <= 0:
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
        try:
            return self._single()
        finally:
            ev = getattr(self, "_shadow_done", None)
            if ev is not None:
                ev.set()   # ends the Homebase shadow (its thread kills the remote worker and books the cost)
            d = getattr(self, "_duel", None)
            if d is not None:
                d.stop()   # ends the local duel worker (hctf/duel.py)

    def _maybe_start_duel(self, cid, prompt):
        """Second, differently-configured local Single Solve worker on a copy of the solver (hctf/duel.py). Launched
        after duel.DELAY s -- skipped if the reuse race (or anything else) completed the single by then."""
        from . import duel
        ok, why = duel.eligible(self.lane)
        if not ok:
            say(f"[{cid}] no duel: {why}")
            return
        if not hasattr(self, "_ready_lock"):
            self._ready_lock = threading.Lock()
        # cases=True: the duel's solver-test must see the earlier days' regression cases too (alt armA D15: a duel won
        # the single with no cases/ and lost 35 earlier-day cases -> a 372 s generalize before Mastery). Artifacts are
        # hard-linked (duel._copy_solver), so the copy is cheap.
        d = duel.Duel(self, cid, "single", prompt, SINGLE_TIMEOUT, cases=SINGLE_DUEL_CASES)
        self._duel = d
        d.start(delay=duel.DELAY, skip=lambda: cli.is_complete(cid), log=say, wake=getattr(self, "_race_done", None))
        threading.Thread(target=d.watch_single, name=f"duel-watch-{self.base}", daemon=True,
                         args=(lambda: (getattr(self, "_cur_ready", None), self._ready_lock), say)).start()

    def _maybe_start_gen_duel(self, cid, prompt, targets, fill, need_fast, green, first=False, quick=False):
        """From the (duel.GEN_AFTER+1)-th generalize of this mode on -- or the FIRST one when `first` (label-only or
        speed-only failures: the high-variance cases, rehearsal D13 replay) -- a second generalize worker on a copy of the
        solver + cases; the first to go green wins (D12-D14 warmups Mastery: 2 serial generalizes per day)."""
        from . import duel
        if duel.GEN_AFTER < 0 or (self._genx()[1].get(cid, 0) <= duel.GEN_AFTER and not (first and duel.GEN_FIRST)):
            return None
        ok, why = duel.eligible(self.lane)
        if not ok:
            say(f"[{cid}] no generalize duel: {why}")
            return None
        try:
            d = duel.Duel(self, cid, "generalize", prompt, GENERALIZE_TIMEOUT, cases=True,
                          note_extra=duel.QUICK_FIX_NOTE if quick else "")
            d.start(log=say)
            threading.Thread(target=d.watch_green, name=f"duel-green-{self.base}", daemon=True,
                             args=(set(targets), set(self._baseline), need_fast, fill, green, say)).start()
            return d
        except Exception as e:  # noqa: BLE001 - the duel is optional
            say(f"[{cid}] generalize duel note: {e}")
            return None

    def _maybe_start_shadow(self, cid, prompt):
        """Second, independent Single Solve worker on Homebase (Bedrock, daily-credit budgeted) for the slow lanes."""
        from . import hbshadow
        ok, why = hbshadow.eligible(self.lane, self.base, log=say)
        if not ok:
            if self.lane in hbshadow.LANES:
                say(f"[{cid}] no Homebase shadow: {why}")
            return
        self._shadow_done = threading.Event()
        self._ready_lock = threading.Lock()
        threading.Thread(target=hbshadow.run_beside, name=f"shadow-{self.base}", daemon=True,
                         args=(self, cid, prompt, lambda: (getattr(self, "_cur_ready", None), self._ready_lock),
                               self._shadow_done, say)).start()

    def _single(self):
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
        self._chain_t0 = time.time()
        # The GM start (+ download) goes out FIRST, before the warm worker's node start and the status prefetches
        # compete for the box (D9: chains began at T+1, GM starts were stamped T+3.1..4.8).
        start_pool = ThreadPoolExecutor(max_workers=1)
        start_fut = start_pool.submit(timed.ensure_started, cid)
        start_pool.shutdown(wait=False)
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
        self._go_lock, self._go_sent, self._go_pending = threading.Lock(), False, []
        body, err = start_fut.result()
        self._tool_prefetch(cid, (body or {}))   # the prompt + questions arrive with `start`: before any download
        self._start_prior_dry_run(cid)
        self._race_done = threading.Event()   # wakes the duel (hctf/duel.py) the moment the race has its answer
        if not welcome and REUSE_RACE and not REUSE_OLD_SOLVERS and self.lane in REUSE_RACE_LANES:
            def race():
                try:
                    self._reuse_race(cid)
                finally:
                    self._race_done.set()
            threading.Thread(target=race, daemon=True, name=f"reuse-race-{self.base}").start()
        else:
            self._race_done.set()
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
        staged = None
        if not welcome and not (self.sdir / "solve.py").exists():
            prior = prior_solver_dir(self.lane, self.sdir) if PRESTAGE_PRIOR else None
            seed = lane_seed_dir(self.lane) if not prior else None
            if prior:
                # Cumulative lane: copy yesterday's solver (all files, cases/ too) into place NOW, beside triage. Every
                # D9 worker's first command was that copy: 6.5 s (script) / 15.6 s (binary, 230 MB under 5-lane load).
                staged = ThreadPoolExecutor(max_workers=1).submit(stage_prior_solver, prior, self.sdir, False)
            elif seed:
                # Lane solver seed (metadata): every verified family is already in lib/meta -> the worker adds only today's
                # field in local_answer(), and the ratchet folds it in tonight.
                stage_prior_solver(seed, self.sdir, cases=False)
                self._lane_seed_note = lane_seed_note(seed, self.sdir)
            else:
                # Nothing reusable: start the worker from the harness skeleton (contract I/O, per-set loop, sha256-paired
                # artifact lookup incl. Mastery's 'delivery N: x.apk' names) instead of hunting for a template (10-15s
                # per lane in the replays; mobile's single never handled Mastery naming -> a 2.5-min generalize).
                self.sdir.mkdir(parents=True, exist_ok=True)
                shutil.copy2(ROOT / "hctf" / "templates" / "solve_skeleton.py", self.sdir / "solve.py")
        try:
            from . import triage as triage_mod
            triage_mod.triage(cid, defer_recon=self._recon_deferrable, log=say)  # grounding before the LLM worker
        except Exception as e:  # noqa: BLE001 - triage is best-effort
            say(f"[{cid}] triage note: {e}")
        if body is None:
            # e.g. read-the-rules: no artifact, but the contract still names the answer ids
            st = cli.call(cid, "status", cid)["body"] or {}
            if st.get("answer_ids") or st.get("questions"):
                cli.save(cid, "contract.json", st)
                if not cli.load(cid, "start.json"):
                    cli.save(cid, "start.json", st)
        retrieved = ""
        if RETRIEVAL and not welcome:
            from . import retrieval
            retrieved = retrieval.note_for(cli.cdir(cid), self.lane, self.root.name, k=RETRIEVAL_K)
            if retrieved:
                say(f"[{cid}] retrieval: {retrieved.count(chr(10) + '- **')} similar past solve(s) in the prompt")
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
            extra += retrieved
            prior = prior_solver_dir(self.lane, self.sdir)
            if staged is not None:
                try:
                    staged.result(timeout=120)
                    if prior and getattr(self, "_cases_fut", None) is None:
                        self._cases_fut = ThreadPoolExecutor(max_workers=1).submit(stage_prior_cases, prior, self.sdir)
                except Exception as e:  # noqa: BLE001 - the worker copies it itself (prompt below)
                    say(f"[{cid}] prior-solver staging note: {e}")
                    staged = False
            if prior and staged:
                prior_note = (f"This lane's contract is CUMULATIVE: `{prior.relative_to(ROOT)}` is the latest earlier "
                              f"solver of this lane and already answers every earlier family. The harness ALREADY "
                              f"copied its code into `{self.sdir.relative_to(ROOT)}` (its cases/ corpus follows in the background) "
                              "-- do NOT copy anything again; add only today's new families there. "
                              "Never use an old solver's output as your answer without today's bytes behind it.")
                dry = self._prior_dry_run_text(cid) if n == 0 else ""
                if dry:
                    prior_note += "\n" + dry
            elif prior:
                prior_note = (f"This lane's contract is CUMULATIVE: `{prior.relative_to(ROOT)}` is the latest earlier "
                              f"solver of this lane and already answers every earlier family. FIRST copy it (all its "
                              f"files) over `{self.sdir.relative_to(ROOT)}`, then add only today's new families. "
                              "Never use an old solver's output as your answer without today's bytes behind it.")
                dry = self._prior_dry_run_text(cid) if n == 0 else ""
                if dry:
                    prior_note += "\n" + dry
            elif getattr(self, "_lane_seed_note", ""):
                prior_note = self._lane_seed_note
            else:
                prior_note = ("Write the solver from the skeleton + the lane helpers below; don't go looking for earlier "
                              "days' solvers (replays lost 13-24 s per run doing that).")
                tids = []
                for m in ("time_trial", "mastery"):
                    tc = cli.load(f"{self.base}/{m}", "contract.json") or {}
                    tids += list(tc.get("answer_ids") or []) + [q.get("id") or "" for q in tc.get("questions") or []]
                # only ids today's Single does NOT ask: a re-rolled variant of today's own field is not a carry-over
                # (D10 metadata: `d09-pe-00N-...` pointed the worker at Day 9's solver, which had no handler: ~20 s)
                own = {field_shape(a) for a in _contract_ids(cli.load(cid, "start.json") or cli.load(cid, "contract.json"))}
                carry = carry_over_note(self.lane, self.sdir, [a for a in tids if field_shape(a) not in own])
                if carry:
                    prior_note += " EXCEPT: the timed contracts already carry earlier days' questions. " + carry
            _dm = re.match(r"day(\d+)", self.sdir.parent.parent.name)
            delta = mastery_delta(cli.load(cid, "start.json") or cli.load(cid, "contract.json"),
                                  [cli.load(f"{self.base}/{m}", "contract.json") or {} for m in ("time_trial", "mastery")],
                                  known=(lambda: lane_known_shapes(self.lane, int(_dm.group(1)))) if _dm else None)
            if delta:
                prior_note += " " + delta
                say(f"[{cid}] {delta[:200]}")
            if INBOX:
                from . import inbox
                carried = inbox.texts(cli.cdir(cid))   # a relaunch inherits what the previous worker was told late
                inbox.reset(cli.cdir(cid))
                if n and carried:
                    extra += "\n" + "\n".join(carried)
            with self._go_lock:
                if self._go_pending:
                    extra += "\n" + "\n".join(self._go_pending)
                self._go_pending, self._go_sent = [], True
            say(f"[{cid}] go text ready at +{time.time() - self._chain_t0:.1f}s (launch {n + 1})"
                if getattr(self, "_chain_t0", None) else f"[{cid}] go text ready (launch {n + 1})")
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
            self._cur_ready = ready
            if n == 0 and not welcome and getattr(self, "_shadow_done", None) is None:
                self._maybe_start_shadow(cid, prompt)
            if n == 0 and not welcome and getattr(self, "_duel", None) is None:
                try:
                    self._maybe_start_duel(cid, prompt)
                except Exception as e:  # noqa: BLE001 - the duel is optional
                    say(f"[{cid}] duel launch note: {e}")
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
                self._join_prior_cases(cid)
            duel_w = getattr(self, "_duel", None)
            if (rc != workers.STOPPED_RC and duel_w is not None and duel_w.alive() and not cli.is_complete(cid)
                    and not (cli.cdir(cid) / "HELP.md").exists()):
                # The chain's worker gave up / timed out while the duel is still going: let the duel finish (bounded)
                # instead of relaunching a fresh worker beside it.
                from . import duel as duel_mod
                say(f"[{cid}] single worker ended without a CORRECT single; the duel is still running -> waiting "
                    f"up to {duel_mod.WAIT:.0f}s for it")
                end = time.time() + duel_mod.WAIT
                while duel_w.alive() and not ready.is_set() and time.time() < end:
                    ready.wait(1.0)
                if ready.is_set() and self._ready_snap:
                    rc = workers.STOPPED_RC
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
                self._start_today_pre(cid)
                self._start_baseline_pre(cid)
                return True
            done = cli.is_complete(cid)
            if not done and not welcome:
                done = self.auto_labels(cid)
            ok, res = (True, None) if welcome else ensure_case_and_test(cid, self.sdir)
            shadow = getattr(self, "_shadow", None)
            if done and not ok and shadow is not None and shadow.snap is not None:
                # The local worker ended without a passing solver, but the Homebase shadow verified one: take it.
                say(f"[{cid}] local solver fails its case -> adopting the Homebase shadow's verified solver")
                self._restore_ready_snapshot(shadow.snap)
                ok, res = ensure_case_and_test(cid, self.sdir)
            duel_w = getattr(self, "_duel", None)
            if done and not ok and duel_w is not None and (duel_w.snap is not None or duel_w.alive()):
                from . import duel as duel_mod
                snap = duel_w.wait_snap(duel_mod.WAIT, log=say)
                if snap is not None:
                    say(f"[{cid}] local solver fails its case -> adopting the duel's verified solver")
                    self._restore_ready_snapshot(snap)
                    ok, res = ensure_case_and_test(cid, self.sdir)
            say(f"[{cid}] after worker: complete={done} solver_ok={ok}")
            if ok and isinstance(res, list):
                self._note_single_speed(cid, next((r.get("seconds") for r in res if r.get("case") == "single_solve"), None))
            if done and ok:
                self._record_labels(cid)
                self._start_family_pre(cid)
                self._start_mutation_pre(cid)
                self._start_compound_pre(cid)
                self._start_today_pre(cid)
                self._start_baseline_pre(cid)
                return True
            if (cli.cdir(cid) / "HELP.md").exists():
                set_state(self.base, stage="single:help", help=(cli.cdir(cid) / "HELP.md").read_text()[:1500])
                return False
        set_state(self.base, stage="single:blocked")
        return False

    def _join_prior_cases(self, cid):
        """Wait for the background prior cases/ copy (stage_prior_cases) before anything reads cases/."""
        fut = getattr(self, "_cases_fut", None)
        if fut is not None:
            try:
                fut.result(timeout=300)
            except Exception as e:  # noqa: BLE001 - the regression corpus is just smaller
                say(f"[{cid}] prior cases/ copy note: {e}")

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
        self._note_single_speed(cid, dt, rerun=(snap, contract, art))
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

    def _start_today_pre(self, cid):
        """Background, once the single's solver is final: the today-probe (warmups: yesterday's Mastery + today's codec)."""
        self._today_fut = None
        kind = self._today_kind()
        if kind is None or not (self.sdir / "solve.py").exists():
            return
        self._today_fut = ThreadPoolExecutor(max_workers=1).submit(today_probe, self.sdir, 60 if kind == "merge" else 30,
                                                                   kind)

    def _today_kind(self):
        lane = getattr(self, "lane", None)
        if TODAY_PROBE and lane in TODAY_PROBE_LANES:
            return "codec"
        if TODAY_MERGE_PROBE and lane in TODAY_MERGE_LANES:
            return "merge"
        return None

    def _today_pre_result(self, cid):
        """-> diag {"compound_today": text} when the solver misses the rehearsal (cases adopted), else {}. Waits at most
        TODAY_PROBE_WAIT s; a probe still running stays pending for the next consumer (a Mastery-failure generalize).
        Consumed once; never held back by _compound_relevant (the rehearsal IS this Mastery's shape)."""
        if self._today_kind() is None or getattr(self, "_today_done", False):
            return {}
        if getattr(self, "_today_fut", None) is None:
            self._start_today_pre(self.base)      # single solved by an earlier run: probe now (~1 s)
        fut = getattr(self, "_today_fut", None)
        if fut is None:
            self._today_done = True
            return {}
        wait = TODAY_PROBE_WAIT if self._today_kind() == "codec" else TODAY_MERGE_WAIT
        try:
            res = fut.result(timeout=wait)
        except TimeoutError:   # concurrent.futures.TimeoutError is the builtin since 3.11
            say(f"[{cid}] today-probe still running after {wait:g}s: not waiting for it")
            return {}
        except Exception as e:  # noqa: BLE001
            self._today_done = True
            say(f"!!! [{cid}] today-probe FAILED ({e}) -- the Mastery attempt runs WITHOUT its rehearsal")
            return {}
        self._today_done = True
        from . import today_probe as tp
        st = res.get("status")
        if st == "miss" and res.get("kind") == "merge":
            n = tp.adopt(self.sdir, res)
            say(f"[{cid}] today-merge probe: the solver misses yesterday's Mastery + today's Single merged into one "
                f"contract ({n} compound-merge case adopted): generalizing BEFORE the Mastery attempt")
            return {"compound_merge": tp.merge_summary(res)}
        if st == "miss":
            n = tp.adopt(self.sdir, res)
            say(f"[{cid}] today-probe: the solver misses a Mastery rehearsal with today's codec `{res.get('codec')}` on "
                f"the last line ({n} compound-today-* case(s) adopted): generalizing BEFORE the Mastery attempt")
            return {"compound_today": tp.summary(res)}
        if st == "unidentified":
            say(f"[{cid}] today-probe: today's codec unidentified from the Single -- no rehearsal")
        elif st == "error" or res.get("error"):
            # rehearsal D13 replay: `cannot import name 'warmups_codecs'` was logged as a plain status line and the Mastery
            # attempt went out unprotected (41/63 sets wrong, then a 117 s generalize)
            say(f"!!! [{cid}] today-probe FAILED ({str(res.get('error'))[:200]}) -- the Mastery attempt runs WITHOUT "
                "its rehearsal")
        else:
            say(f"[{cid}] today-probe: {st} (codec {res.get('codec')}, {res.get('seconds')}s)")
            self._note_lib_misses(cid, res)
        return {}

    def _note_lib_misses(self, cid, res):
        lm = res.get("lib_misses") or {}
        if lm:
            say(f"[{cid}] today-probe: the solver passes but plain lib.decode.decode_chunked misses "
                f"{sum(len(v) for v in lm.values())} rehearsal set(s) ({', '.join(lm)}): lib gap for the ratchet "
                "(tomorrow's seed)")

    def _today_recheck(self, cid):
        """After a today-probe-triggered generalize, re-probe on FRESH random draws before the Mastery attempt: D14's
        fixed solver passed the 2 adopted cases, then left set22 empty on the real variant, and the GM had no second
        timed attempt (attempts_remaining 0 on every D14 mode). Still missing -> generalize again (bounded)."""
        from . import today_probe as tp
        for salt in range(1, TODAY_RECHECKS + 1):
            res = today_probe(self.sdir, 30, "codec", salt=salt)
            if res.get("status") != "miss":
                say(f"[{cid}] today-probe recheck (fresh draw {salt}): {res.get('status')} ({res.get('seconds')}s)")
                self._note_lib_misses(cid, res)
                return
            n = tp.adopt(self.sdir, res)
            say(f"[{cid}] today-probe recheck (fresh draw {salt}): the generalized solver still misses "
                f"{sum(len(r['wrong']) for r in res.get('results') or [])} set(s) ({n} case(s) adopted): generalizing "
                "again BEFORE the Mastery attempt")
            self.generalize(cid, wrong=None, fixed=None, diag={"compound_today": tp.summary(res)})
        say(f"[{cid}] today-probe recheck: still missing after {TODAY_RECHECKS} fresh draw(s); Mastery starts now")

    def _await_probes(self, timeout):
        """Wait up to `timeout` s for the beside-the-TT probes -> True when every started one has finished."""
        futs = [f for f in (getattr(self, a, None) for a in ("_fam_pre_fut", "_mut_pre_fut", "_cmp_pre_fut"))
                if f is not None]
        end = time.time() + timeout
        while not all(f.done() for f in futs):
            if time.time() >= end:
                return False
            time.sleep(0.05)
        return True

    def _compound_relevant(self, cid, hard):
        """Do these compounding-probe misses matter for THIS Mastery attempt? False only when the status-time Mastery
        contract is trustworthy -- this account never attempted the mode (no attempt_id: every first real-day Mastery
        D1-D10 asked exactly its status-time fields; only D7 metadata RE-attempts escalated, 3/149) -- and no missed
        earlier-day case shares a field with it. Unknown -> True (block, as before)."""
        mc = cli.load(cid, "contract.json") or {}
        if mc.get("attempt_id") or mc.get("started_at"):
            return True
        asked = {field_shape(a) for a in _contract_ids(mc)}
        if not asked:
            return True
        for r in hard:
            try:
                c = json.loads((ROOT / r["path"] / "contract.json").read_text())
            except (OSError, ValueError, KeyError, TypeError):
                return True
            if asked & {field_shape(a) for a in _contract_ids(c)}:
                return True
        return False

    def _tt_pool_untimed(self):
        """This day's timed pool has no clock: the Time Trial's last attempt came from the regular pool (no deadline,
        run_for_time false / untimed / no_clock). D15: every lane's TT AND Mastery started that way (HoF ineligible), so
        a failed Mastery attempt stays open and is fixed in-attempt (localize + bank, live answer) -- a generalize
        BEFORE it is pure wall time (alt armA D15 script: 372 s on 35 compound misses ahead of an untimed Mastery)."""
        tt = self.entries.get("time_trial")
        if not tt or not UNTIMED_SKIP_PREGEN:
            return False
        last = timed.last_result(tt["id"]) or {}
        if not last.get("attempt_id") or last.get("deadline") is not None or last.get("run_for_time") is True:
            return False
        return bool(last.get("untimed") or last.get("no_clock") or last.get("run_for_time") is False)

    def _late_probes(self, cid, wait=True, defer_compound=False):
        """Probes that run beside the first Time Trial (codec family + mutation + compounding): adopt hard misses as
        regression cases. Returns the diag dict for a generalize ({} when clean). Each result is consumed once.
        `defer_compound` (pre-Mastery): compounding misses the Mastery contract can't ask are held back instead of
        blocking Mastery on a generalize (r10a metadata: 21 s for d01-d08 families a d09-pe-only Mastery never asked);
        a Mastery-failure generalize (defer_compound=False) still gets them."""
        pre = {}
        held = getattr(self, "_compound_held", None)
        if held and not defer_compound:
            from . import compound
            self._compound_held = None
            n = compound.adopt(self.sdir, held[1])
            say(f"[{cid}] compounding probe (held back before Mastery): {n} earlier-day case(s) adopted now")
            pre["compound_pre"] = held[0]
        ftxt, fcases = self._family_pre_result(wait=wait)
        if fcases:
            n = self._adopt_family_cases(fcases)
            say(f"[{cid}] codec-family probe: the single's solver misses {len(fcases)} re-encoded case(s) "
                f"({n} adopted as family-* regression cases)")
            pre["family_pre"] = ftxt
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
        if solvers.mode_of(cid) == "mastery":
            # today-probe: before Mastery (bounded wait of its own, whatever `wait` says) or a Mastery-failure generalize
            pre.update(self._today_pre_result(cid))
        if not getattr(self, "_cmp_late_done", False):
            ctxt, hard = self._compound_pre_result(wait=wait)
            if hard or ctxt or wait:
                self._cmp_late_done = True
            if hard and defer_compound and not self._compound_relevant(cid, hard):
                self._compound_held = (ctxt, hard)
                say(f"[{cid}] compounding probe: the solver lost {len(hard)} earlier-day case(s), none of whose fields "
                    "this first-attempt Mastery contract asks -> Mastery now (a failure generalize gets them)")
            elif hard:
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

    def _family_pre_result(self, wait=True):
        """(text, missed family case dirs). Each result is consumed ONCE (pre-attempt block or _late_probes).
        wait=False: only if the probe already finished (it runs beside the first Time Trial)."""
        fut = getattr(self, "_fam_pre_fut", None)
        if fut is None or getattr(self, "_fam_late_done", False) or (not wait and not fut.done()):
            return "", []
        self._fam_late_done = True
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
        cap = tt_solve_cap(cli.cdir(tt["id"]) / "last_timed.json", cli.cdir(cid) / "contract.json") if tt else None
        if cap is not None and cap < est:
            # The Time Trial's in-window solve = ONE set on the executor Mastery will use, under real load: per-set cost
            # can't exceed it. D10 warmups: probe-contention estimate 17.51 s (gate 24) vs TT solve 0.02 s x 48 sets.
            say(f"[{cid}] Mastery speed estimate {est:g}s capped by the Time Trial's solve phase -> {cap:g}s")
            est = cap
        say(f"[{cid}] Mastery speed estimate {est:g}s (TT window {tt_win:g}s, gate {limit:g}s)")
        if est > limit:
            # The probe timed its 1- and 2-set runs side by side with every other mutation (and 5 lanes' load), and the
            # difference x N sets is the estimate: r9b warmups 14.24 s vs a real 0.32 s Mastery solve -> an 82 s
            # useless speed generalize (the only time this gate ever fired). Re-time the two runs alone first.
            est2 = remeasure_estimate(self.sdir, getattr(self, "_mut_summary", None), cli.cdir(cid) / "contract.json")
            if est2 is not None:
                say(f"[{cid}] Mastery speed estimate re-measured alone: {est2:g}s")
                est = est2
        if est > limit:
            say(f"[{cid}] estimated Mastery solve {est:g}s > {limit:g}s: generalizing for speed BEFORE Mastery")
            self.generalize(cid, wrong=None, fixed=None, diag={"solver_too_slow": True, "mastery_estimate": est,
                                                                 "single_seconds": est})

    def _note_single_speed(self, cid, seconds, rerun=None):
        """Flag a single solver over SINGLE_SPEED_BUDGET for a speed generalize before the first timed attempt -- after
        re-timing it ONCE alone: the first timing is taken at the drop beside 5 lanes' races/probes (rehearsal fair D14:
        binary 6.7 s and script 3.2 s vs 0.18 s / 1.4 s idle -> two 3-4 min speed generalizes for nothing).
        rerun = (solver dir, contract, artifacts dir); default the solver dir on its single_solve case."""
        self._single_slow = None
        if SINGLE_SPEED_BUDGET and seconds and seconds > SINGLE_SPEED_BUDGET and SINGLE_SPEED_RETIME:
            try:
                if rerun is None:
                    case = self.sdir / "cases" / "single_solve"
                    rerun = (self.sdir, json.loads((case / "contract.json").read_text()), case / "artifacts")
                _got, err, dt2 = solvers.run_solver(rerun[0], rerun[1], rerun[2], max(10.0, 3 * seconds))
                if not err and dt2 < seconds:
                    say(f"[{cid}] single solver timed {seconds:.1f}s under drop load; re-timed alone {dt2:.1f}s")
                    seconds = dt2
            except Exception as e:  # noqa: BLE001 - keep the first timing
                say(f"[{cid}] single solver re-time note: {e}")
        if SINGLE_SPEED_BUDGET and seconds and seconds > SINGLE_SPEED_BUDGET:
            self._single_slow = round(seconds, 2)
            say(f"[{cid}] single solver takes {seconds:.1f}s on its own case (budget {SINGLE_SPEED_BUDGET:g}s): "
                "speed generalize before the first timed attempt")

    def _watch_ready(self, cid, ready, done):
        """Runs beside the Single Solve worker. The moment the single is CORRECT and the worker's solver (stable 2s)
        reproduces every GM-confirmed answer, keep that verified snapshot and set `ready`: run_local then ends the
        worker and the timed modes start from the snapshot at once. Day 6: 60% of worker time (1101/1850s) came after
        the first CORRECT, and every first-correct snapshot already passed its real TT+Mastery variants offline."""
        early, spec_n, errs = None, 0, 0
        self._newid = {}          # solver mtimes key -> Future of the new-id dry run (computed while the code is stable)
        held = False
        while not done.wait(SPEC_POLL):
            try:
                self._newid_kick()
                if PREPUSH_AT_STAMP:
                    # Push this code to Homebase BEFORE the verdict (D10: TT kickoffs waited 1.1-1.4 s on a push started
                    # at the verdict): at the `hctf submit --from-solver` stamp, or speculatively once the code has been
                    # stable PREPUSH_STABLE s. The verified push below re-pushes only if the code changed since, and
                    # warms the zygote (signature checks).
                    m = self._solver_mtimes()
                    if m and "solve.py" in m and m != early:
                        stamped = bool(self._submit_stamp(cid, m))
                        if stamped or (spec_n < PREPUSH_SPEC_MAX and time.time() - max(m.values()) >= PREPUSH_STABLE
                                       and not _is_skeleton(self.sdir)):
                            early, spec_n = m, spec_n + (not stamped)
                            self._prepush_verified(cid, self.sdir, warm=stamped)
                if cli.is_complete(cid):
                    if ready.is_set():
                        return   # the Homebase shadow handed over first
                    snap = self._spec_snapshot(cid) or getattr(self, "_race_snap", None)
                    if snap and not held and snap is not getattr(self, "_race_snap", None):
                        held = True
                        snap = self._newid_hold(cid, snap, ready, done)
                        if snap is None:
                            return   # the worker ended by itself during the hold: the normal post-worker path runs
                    if snap:
                        with getattr(self, "_ready_lock", None) or threading.Lock():
                            if ready.is_set():
                                return
                            self._ready_snap = snap
                            say(f"[{cid}] single CORRECT + solver verified -> ending the worker, timed modes start now")
                            ready.set()
                        self._prepush_verified(cid, snap)
                        return
            except Exception as e:  # noqa: BLE001 - the watcher must never hurt the chain
                # one bad iteration (a torn submissions.jsonl line, a racing rmtree) must not end the watch: the
                # chain worker could no longer be handed over (alt armA D15 13:39:52)
                errs += 1
                if errs <= 3:
                    say(f"[{cid}] ready-watch note: {e}")
                if errs >= 50:
                    return

    # -- new-id check at the single's handoff: the CORRECT submit's own dry-run warning reached a worker that was
    #    ended ~1 s later (main armB D15: the TT then missed a field only the timed contracts ask, 60 s block)
    def _newid_key(self, m):
        return tuple(sorted(m.items()))

    def _newid_kick(self):
        """Start the new-id dry run in the background once the solver code has been quiet NEWID_STABLE s (one per code
        version, at most NEWID_MAX per single) -- so the handoff never waits for it."""
        if NEWID_HOLD <= 0:
            return
        m = self._solver_mtimes()
        if not m or "solve.py" not in m or time.time() - max(m.values()) < NEWID_STABLE or _is_skeleton(self.sdir):
            return
        key = self._newid_key(m)
        if key in self._newid or len(self._newid) >= NEWID_MAX:
            return
        self._newid[key] = ThreadPoolExecutor(max_workers=1).submit(self._newid_gaps, self.base, self.sdir)

    def _newid_gaps(self, cid, sdir):
        """Answer ids NEW to this lane (no earlier day asked their shape, nor today's single) that the solver leaves EMPTY
        on a dry run of the TT / Mastery status-time contracts with the single's bytes under their artifact names.
        [] when none or inconclusive (multi-file single, solver error, under half the carried-over ids answered)."""
        import tempfile
        dm = re.match(r"day(\d+)", self.sdir.parent.parent.name)
        single = cli.load(cid, "start.json") or cli.load(cid, "contract.json") or {}
        art = timed.latest_artifacts(cid)
        files = [p for p in (art.iterdir() if art else []) if p.is_file() and p.name != "manifest.json"]
        if not dm or len(files) != 1:
            return []
        known = lane_known_shapes(self.lane, int(dm.group(1))) | {field_shape(a) for a in _contract_ids(single)}
        gaps = []
        for m in ("time_trial", "mastery"):
            tc = cli.load(f"{self.base}/{m}", "contract.json") or {}
            ids = list(dict.fromkeys(_contract_ids(tc)))
            new = [a for a in ids if field_shape(a) not in known]
            if not new or not tc.get("questions"):
                continue
            tmp = Path(tempfile.mkdtemp(prefix="newid-", dir=str(paths.TMP)))
            try:
                for q in tc["questions"]:
                    name = os.path.basename((q.get("artifact") or "").partition("->")[0].strip())
                    if name and not (tmp / name).exists():
                        shutil.copy2(files[0], tmp / name)
                c = {**{k: v for k, v in tc.items() if k not in ("artifacts", "error")}, "answer_ids": ids}
                got, err, _ = solvers.run_solver(Path(sdir), c, tmp, timeout=20)
            finally:
                shutil.rmtree(tmp, ignore_errors=True)
            old = [a for a in ids if a not in new]
            if err or (old and sum(1 for a in old if got.get(a) not in (None, "")) < 0.5 * len(old)):
                continue   # the copies don't fit this solver at all: no signal
            gaps += [a for a in new if got.get(a) in (None, "")]
        return list(dict.fromkeys(gaps))

    def _newid_result(self, snap):
        """The dry-run gaps for the snapshot's code (computed in the background; waits <= NEWID_WAIT s), or None."""
        key = self._newid_key({p.name: p.stat().st_mtime for p in Path(snap).iterdir()
                               if p.is_file() and p.suffix == ".py"})
        fut = getattr(self, "_newid", {}).get(key)
        if fut is None:
            return None
        try:
            return fut.result(timeout=NEWID_WAIT)
        except Exception:  # noqa: BLE001 - still running / failed: no hold
            return None

    def _newid_hold(self, cid, snap, ready, done):
        """Single CORRECT + verified snapshot. When the timed contracts ask ids NEW to the lane the solver leaves empty,
        tell the still-running worker and give it up to NEWID_HOLD s to fill them (handoff the moment a verified
        snapshot fills them); else hand over the verified snapshot as before. None = the worker ended on its own."""
        gaps = self._newid_result(snap)
        if not gaps:
            return snap
        shapes = sorted({field_shape(a) for a in gaps})
        hold = Path(str(snap.parent.parent) + "-hold") / snap.parent.name / "solver"
        shutil.rmtree(hold.parent, ignore_errors=True)
        hold.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(snap, hold, ignore=shutil.ignore_patterns("__pycache__"))
        if (snap.parent / "meta.json").exists():
            shutil.copy2(snap.parent / "meta.json", hold.parent / "meta.json")
        note = (f"SINGLE IS CORRECT -- keep going for {NEWID_HOLD:g}s more: the Time Trial / Mastery contracts ask "
                f"{len(gaps)} id(s) NEW to this lane that your solver leaves EMPTY ({', '.join(shapes[:8])}; e.g. "
                f"{gaps[:4]}). Read their questions in {_rel(cli.cdir(self.base).parent)}/time_trial/"
                "contract.json and mastery/contract.json, make solve.py answer them from the bytes, run "
                "`hctf solver-test` once, then stop. No submit needed; the harness hands over the moment they are filled.")
        if INBOX:
            from . import inbox
            inbox.post(cli.cdir(cid), note, key="newid")
        say(f"[{cid}] single CORRECT, but the solver leaves {len(gaps)} timed id(s) NEW to the lane empty "
            f"({', '.join(shapes[:4])}): worker told, handoff held up to {NEWID_HOLD:g}s")
        end, seen = time.time() + NEWID_HOLD, None
        while time.time() < end:
            if done.wait(SPEC_POLL):
                return None
            if ready.is_set():
                return hold
            m = self._solver_mtimes()
            if not m or self._newid_key(m) == seen or time.time() - max(m.values()) < NEWID_STABLE:
                continue
            seen = self._newid_key(m)
            s2 = self._spec_snapshot(cid)
            if s2 is None:
                continue
            g2 = self._newid_gaps(self.base, s2)
            if len(g2) < len(gaps):
                say(f"[{cid}] new-id hold: the solver now fills {len(gaps) - len(g2)}/{len(gaps)} -> handing over")
                return s2
        say(f"[{cid}] new-id hold: {NEWID_HOLD:g}s passed without a fix -> handing over the verified solver")
        return hold

    def _prepush_verified(self, cid, snap, warm=True):
        """Push the verified snapshot to Homebase while the worker is ended and the single recorded (D9: single
        CORRECT -> TT start 3.9-6.6 s per lane; the kickoff's VPN rsync sat inside it)."""
        if not PREPUSH or "time_trial" not in self.entries and "mastery" not in self.entries:
            return
        try:
            if remote.gm_transport() == "local" and not (workers.AUTO_HOMEBASE and workers._hb.get("ok")):
                return     # timed attempts will run locally: nothing to push
            workers.prepush_solver(snap, self.sdir, log=say, warm=warm)
        except Exception as e:  # noqa: BLE001 - optimization only
            say(f"[{cid}] pre-push note: {e}")

    def _restore_ready_snapshot(self, snap):
        """After a stopped worker: put the verified snapshot's files back over the live solver (the worker may have been
        mid-edit when it was ended). cases/ in the live dir is kept."""
        if snap.parent.name.endswith("-race"):
            # a different day's solver: drop the staged/worker code first so no newer helper module shadows the seed's
            for f in self.sdir.glob("*.py"):
                f.unlink()
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
            # Codec-family probe (script): beside the first Time Trial too (rehearsal D8: it held the TT kickoff ~12 s); taken
            # here only if already done, otherwise _late_probes collects it before Mastery / a TT-failure generalize.
            ftxt, fcases = self._family_pre_result(wait=mode != "time_trial")
            if fcases:
                n = self._adopt_family_cases(fcases)
                say(f"[{cid}] codec-family probe: the single's solver misses {len(fcases)} re-encoded case(s) "
                    f"({n} adopted as family-* regression cases): generalizing BEFORE the timed attempt")
                pre["family_pre"] = ftxt
            # Mutation + compounding probes run BESIDE the first Time Trial (mutation probe: 0 hits in mainblind3-7 + D8;
            # it held binary ~5 s): take them now only if already done; Mastery (or a TT-failure generalize) awaits them.
            # A later mode with no TT before it (TT already passed) waits for them here.
            # A speed-only generalize doesn't wait for them either (rehearsal D8 binary: ~10 s idle before the worker launched);
            # Mastery still awaits them below.
            speed_only = mode == "time_trial" and bool(pre) and set(pre) <= {"solver_too_slow", "single_seconds"}
            pre.update(self._late_probes(cid, wait=(mode != "time_trial" or bool(pre)) and not speed_only,
                                         defer_compound=mode == "mastery"))
            if pre:
                self.generalize(cid, wrong=None, fixed=None, diag=pre)
                if "compound_today" in pre:
                    self._today_recheck(cid)
        elif mode != "time_trial":
            # Bounded: what finished within LATE_PROBE_WAIT s is acted on now; a probe still running is consumed by a
            # Mastery-failure generalize instead (timed_stage awaits all probes there). D9 + rehearsal: script's Mastery
            # sat 5.2-5.4 s on the codec-family probe (~10 s under 5-lane load); its only hits ever were D7 replays.
            done = self._await_probes(LATE_PROBE_WAIT)
            late = self._late_probes(cid, wait=done, defer_compound=mode == "mastery")
            if not done:
                say(f"[{cid}] probes still running after {LATE_PROBE_WAIT:g}s: Mastery starts now (a failure "
                    "generalize takes their results)")
            if late and mode == "mastery" and self._tt_pool_untimed():
                # misses are adopted as cases already; the failure generalize (if Mastery fails at all) gets the diag
                self._late_held = late
                say(f"[{cid}] probes found misses ({', '.join(sorted(late))}), but the pool is UNTIMED: Mastery now "
                    "(in-attempt localization / live answer fix them; a failure generalize gets the probe results)")
            elif late:
                say(f"[{cid}] probes that ran beside the Time Trial found misses: generalizing BEFORE Mastery")
                self.generalize(cid, wrong=None, fixed=None, diag=late)
                if "compound_today" in late:
                    self._today_recheck(cid)
        if mode == "mastery":
            if TT_FIX_GATE:
                self._tt_fix_gate(cid)
            if self._tt_pool_untimed():
                say(f"[{cid}] untimed pool: no Mastery speed gate (no clock to beat)")
            else:
                self._mastery_speed_gate(cid)
        clock_retries = 0
        resume_continues = 0
        rate_retries = 0
        start_retries = 0
        untimed = False     # True once the fresh timed pool is spent: every further attempt is untimed (no clock)
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
            live_banked = KEEP_BANKED and _prev_banked(prev) and (
                (left is not None and left > 0) or (left is None and prev.get("deadline") is None
                                                    and (prev.get("untimed") or prev.get("no_clock")
                                                         or prev.get("run_for_time") is False)))
            if live_banked:
                say(f"[{cid}] retry_skipped_banked: attempt {str(prev.get('attempt_id'))[:8]} holds GM-accepted ids "
                    f"({'untimed' if left is None else f'{left:.1f}s left'}) -- reconnecting with start, never retry")
            if left is not None and 0 < left < need and not live_banked:
                # Day 8 script Mastery: the previous attempt still had ~4 s, so `start` RESUMED it -> 2 s solver budget
                # -> "solver too slow" -> a 143 s generalize. Let it run out (pre-clock for us), then re-roll.
                say(f"[{cid}] previous attempt has only {left:.1f}s left (< {need:.1f}s needed): waiting it out, then retry")
                time.sleep(left + 0.6)
                left = 0
            if (not untimed and UNTIMED_ROUNDS > 0 and SKIP_DOOMED_RETRY and left is not None and left <= 0
                    and _race_left(prev) == 0):
                # The previous attempt's start already said 0 fresh attempts remain: a retry is refused
                # (retry_variants_unavailable) -- D14 warmups Mastery spent ~5 s + a push learning that. Go untimed now.
                say(f"[{cid}] GM reported 0 fresh attempts left at the previous start: UNTIMED attempt now "
                    f"(regular pool / practice; up to {UNTIMED_ROUNDS} round(s))")
                set_state(self.base, stage=f"{mode}:untimed")
                untimed = True
                attempt = max(attempt, MAX_TIMED_RETRIES - UNTIMED_ROUNDS + 1)
            if live_banked:
                op = {"op": "resume"}
            elif untimed:
                op = {"op": "untimed"}
            else:
                op = {"op": "retry"} if left is not None and left <= 0 else {}
            res = timed.run(cid, self.sdir, log=say, **op, **self._early_kw(cid, untimed))
            say(f"[{cid}] result: {res}{' (untimed)' if untimed else ''}")
            set_state(self.base, **{f"{mode}_result": res})
            if self._early_join(cid) and res in ("expired", "blocked"):
                continue   # an early generalize already worked on this variant (verdicts merged): retry
            if res == "correct":
                if untimed:
                    say(f"[{cid}] passed on an UNTIMED attempt (fresh timed pool spent): flag + points, no Hall of Fame")
                    set_state(self.base, stage=f"{mode}:untimed-pass")
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
                # GM 'rotation_exhausted' / 'retry_variants_unavailable': no fresh timed variant left today (replay
                # d7fix3 metadata TT; r11a binary D11 TT -- 30 start retries, ~11 min, mode lost; D11's real pools were
                # binary 0 / metadata 1). Top-team rule: out of unique attempts -> stop going for the Hall of Fame and
                # take the flag on an UNTIMED attempt (regular pool / practice continuation: completes the mode and
                # unlocks the next). A generalize can't conjure a variant, so none runs on the verdict itself.
                if not untimed and UNTIMED_ROUNDS > 0:
                    say(f"[{cid}] GM: fresh timed pool exhausted for this mode; switching to an UNTIMED attempt "
                        f"(regular pool / practice; up to {UNTIMED_ROUNDS} round(s))")
                    set_state(self.base, stage=f"{mode}:untimed")
                    untimed = True
                    attempt = MAX_TIMED_RETRIES - UNTIMED_ROUNDS   # the untimed rounds get their own budget
                    continue
                say(f"[{cid}] GM rotation exhausted for this mode{' (untimed attempt refused too)' if untimed else ''}: "
                    "no new attempts today; stopping (no generalize)")
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
                    if "attempt_context_invalid" in err and start_retries == 1:
                        # r9b (2026-10-12): script Mastery answered 503 attempt_context_invalid to start, retry, plain-pool
                        # start AND status -- GM-side state for this one mode; only the organizers can clear it.
                        say(f"!!! [{cid}] GM: attempt_context_invalid (GM-side state for this mode; start/retry/status "
                            "all refuse) -- report to the organizers; backing off and retrying")
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
            if res == "blocked" and resume_continues < RESUME_CONTINUES and _cut_short(last):
                # Nothing says the solver can't pass this attempt: its localization just didn't finish. Reconnect (the
                # loop picks op=resume for a live banked attempt) instead of a generalize; speed_harden teaches the
                # solver the in-attempt fixes after the run (its failing GM-verified cases).
                resume_continues += 1
                attempt -= 1
                say(f"[{cid}] in-attempt localization cut short ({str(last.get('localize_error') or 'budget/resubmit')[:80]}; "
                    f"{len(last.get('fixed') or {})} fix(es), {len(last.get('wrong') or [])} wrong found): reconnecting "
                    f"to attempt {str(last.get('attempt_id'))[:8]} to finish it, no generalize "
                    f"(continue {resume_continues}/{RESUME_CONTINUES})")
                set_state(self.base, stage=f"{mode}:continuing")
                continue
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
            # only fields the solver DID answer (wrongly) and the GM has NOT already corrected in-window: an empty field
            # is a solver gap, and a `fixed` label is confirmed + cached already (rehearsal D13 replay: a GM start of 4-6 s
            # per blocked cycle for nothing)
            unresolved = [a for a, v in (wrong or []) if v is not None and a not in (fixed or {})]
            if unresolved:
                try:
                    got = timed.resolve_labels_online(cid, self.sdir, unresolved, self.lane, log=say)
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
            if self._bg_gen_take(cid, "the attempt failed", only_won=True):
                say(f"[{cid}] {res}: retrying with the background generalize's solver (no new generalize)")
                continue
            if label_only_failure(wrong):
                fixed = dict(fixed or {})
                if self._label_scout(cid, mode, wrong, fixed):
                    return True
            say(f"[{cid}] {res}: improving the solver offline for this variant, then retrying")
            # one worker fixes the variant AND any probe misses that are ready NOW; a probe still running stays
            # pending for the next consumer (rehearsal D13 replay: waiting cost ~7 s per blocked attempt)
            diag.update(self._late_probes(cid, wait=False))
            held = getattr(self, "_late_held", None)
            if held:
                self._late_held = None
                diag.update({k: v for k, v in held.items() if k not in diag})
            live = None
            fields = _live_fields(last, wrong, fixed) if LIVE_ANSWER else []
            if fields and len(fields) <= LIVE_MAX_FIELDS:
                try:
                    live = LiveAnswer(self, cid, last, fields, wrong, fixed).start()
                except Exception as e:  # noqa: BLE001 - the generalize path stands on its own
                    say(f"[{cid}] live-answer not started: {e}")
            self.generalize(cid, wrong=wrong, fixed=fixed, diag=diag, live=live)
            if live is not None:
                live.finish()
                if live.passed or cli.is_complete(cid):
                    say(f"[{cid}] passed by the live-answer worker (attempt {str(live.attempt)[:8]})")
                    set_state(self.base, **{f"{mode}_result": "correct"})
                    record_timed_case(cid, self.sdir)
                    self._start_bg_gen(cid, last)
                    return True
                if live.all_accepted:
                    say(f"[{cid}] live-answer: every listed field accepted -> reconnecting to complete the attempt")
                    attempt -= 1
        set_state(self.base, stage=f"{mode}:blocked")
        return False

    def _start_bg_gen(self, cid, last):
        """The Time Trial passed through the LIVE answer while its solver still MISSES fields (`missing`) Mastery asks
        again (alt armB D15 metadata: Mastery then came back solver_incomplete on the same synthesis-sha256-order field,
        ~50 s + a second generalize). The ended generalize goes on OFF the critical path: a duel-style worker on a COPY of
        the solver, target = the TT variant case (GM-verified answers incl. the live worker's). Mastery starts now with
        the current solver; its failure (or the chain's end) adopts the copy when it went green (_bg_gen_take)."""
        from . import duel
        mst = self.entries.get("mastery")
        missing = list(last.get("missing") or [])
        if not (LIVE_BG_GEN and missing and mst and not cli.is_complete(mst["id"])
                and solvers.mode_of(cid) == "time_trial"):
            return
        prompt = getattr(self, "_gen_prompt", None)
        target = f"time_trial-{(cli.attempt_id(cli.load(cid, 'start.json')) or 'x')[:8]}"
        if not prompt or not (self.sdir / "cases" / target / "expected.json").exists():
            return
        ok, why = duel.eligible(self.lane)
        if not ok:
            say(f"[{cid}] no background generalize: {why}")
            return
        green = threading.Event()
        d = duel.Duel(self, cid, "generalize", prompt, GENERALIZE_TIMEOUT, cases=True,
                      note_extra=BG_GEN_NOTE.format(target=target, n=len(missing), ids=missing[:12]))
        d.start(log=say)
        threading.Thread(target=d.watch_green, name=f"bg-gen-{self.base}", daemon=True,
                         args=({target}, set(getattr(self, "_baseline", set()) or ()), False, frozenset(), green,
                               say)).start()
        self._bg_gen = (d, green)
        say(f"[{cid}] background generalize on a solver copy for {len(missing)} field(s) the solver missed "
            f"(target case {target}); Mastery does not wait for it")

    def _bg_gen_take(self, cid, why, only_won=False):
        """Consume the background generalize: adopt its code when it went green and nothing that passes now breaks,
        else end it (unless `only_won`: then a still-running one is left alone). -> True when adopted."""
        bg = getattr(self, "_bg_gen", None)
        if not bg:
            return False
        d, green = bg
        won = green.is_set() and d.won
        if only_won and not won:
            return False
        self._bg_gen = None
        d.stop()
        if not won:
            say(f"[{cid}] background generalize ended ({why}) before it went green")
            return False
        keep = {p.name: p.read_bytes() for p in self.sdir.iterdir() if p.is_file() and p.suffix == ".py"}
        before = {r["case"] for r in self._baseline_results() if r.get("ok")}
        try:
            d.adopt_into(self.sdir, log=say)
            after = {r["case"] for r in solvers.test_solver(self.sdir, timeout=BASELINE_CASE_TIMEOUT) if r.get("ok")}
        except Exception as e:  # noqa: BLE001
            after, before = set(), before or {"?"}
            say(f"[{cid}] background generalize adopt note: {e}")
        if before - after:
            for p in self.sdir.iterdir():
                if p.is_file() and p.suffix == ".py" and p.name not in keep:
                    p.unlink()
            for n, b in keep.items():
                (self.sdir / n).write_bytes(b)
            say(f"[{cid}] background generalize NOT adopted ({why}): it breaks {sorted(before - after)[:4]}")
            return False
        self._accepted_res = None
        say(f"[{cid}] background generalize adopted ({why}): {len(after)} case(s) pass")
        return True

    def _tt_fix_gate(self, cid):
        """The Time Trial passed only through in-window fixes (wrong -> GM-accepted values): the solver still produces
        those wrong values, and Mastery asks the same families again (D15 script: TT 8 x expansion delayed -> percent
        fixed in-window, then Mastery 20 x the same). An UNTIMED Mastery corrects them in-attempt (label_hints.json
        ranks TT's accepted value first): start it now. A CLOCKED Mastery may be the day's one shot: teach the solver
        on the Time Trial's variant first (its auto-time_trial-* case holds the GM-verified answers)."""
        tt = self.entries.get("time_trial")
        if not tt or getattr(self, "_tt_gate_done", False):
            return
        self._tt_gate_done = True
        last = timed.last_result(tt["id"]) or {}
        wrong = [tuple(x) for x in last.get("wrong") or []]
        if str(last.get("result", "")).lower() != "correct" or not wrong:
            return
        fixed = last.get("fixed") or {}
        clocked = last.get("deadline") is not None or last.get("run_for_time") is True
        if not clocked:
            say(f"[{cid}] Time Trial needed {len(wrong)} in-window fix(es) ({len(fixed)} GM-accepted); its pool was "
                "untimed, so Mastery starts now and corrects them in-attempt (TT's values ranked first)")
            return
        if timed.join_capture(tt["id"], 120):
            # no auto-time_trial-* case on disk yet = no failing target for the green watcher: the generalize would run
            # to its own timeout in front of Mastery. Mastery now; a failure generalize has the case by then.
            say(f"[{cid}] Time Trial needed {len(wrong)} in-window fix(es) on a CLOCKED pool, but its regression case is "
                "still being captured: Mastery now (no blind pre-generalize)")
            return
        say(f"[{cid}] Time Trial needed {len(wrong)} in-window fix(es) on a CLOCKED pool: teaching the solver on that "
            "variant BEFORE Mastery")
        self.generalize(cid, wrong=wrong, fixed=fixed, diag={"tt_inwindow_fixes": len(wrong)})

    def _label_scout(self, cid, mode, wrong, fixed):
        """LABEL SCOUTING, before the generalize of a label-only Time Trial failure: up to LABEL_SCOUT_ROUNDS more
        attempts with the CURRENT solver (each a fresh variant; on Homebase ~13 s incl. in-window localization), so the
        worker fits its label rule on several GM-verified variants at once (each round -> an auto-time_trial-* case via
        timed.process_result) instead of one (rehearsal D13 replay: 3 generalize cycles, ~9 min, each fixing the expansion
        rule on ONE variant and missing the next). Once per mode per run; Time Trial only (Mastery attempts are
        team-shared); never below SCOUT_MIN_ATTEMPTS fresh attempts. Merges what the rounds learned into `wrong` /
        `fixed` in place. Returns True if a scout round itself passed the mode."""
        done = self.__dict__.setdefault("_label_scouted", set())
        if (not LABEL_SCOUT_ROUNDS or mode != "time_trial" or cid in done or not label_only_failure(wrong)):
            return False
        done.add(cid)
        from . import scout
        left = (timed.last_result(cid) or {}).get("attempts_remaining")
        if left is not None and left < scout.SCOUT_MIN_ATTEMPTS:
            say(f"[{cid}] label scouting skipped: only {left} attempt(s) left today")
            return False
        set_state(self.base, stage=f"{mode}:label-scouting")
        say(f"[{cid}] label-only failure: scouting up to {LABEL_SCOUT_ROUNDS} more variant(s) for GM-verified labels "
            "before ONE generalize")
        t0 = time.time()
        try:
            s = scout.scout(cid, self.sdir, rounds=LABEL_SCOUT_ROUNDS, clean=1, log=say)
        except Exception as e:  # noqa: BLE001 - scouting is advisory: the generalize below still runs
            say(f"[{cid}] label scouting note: {e}")
            return False
        n = len(s.get("rounds") or [])
        if s.get("last_correct") or cli.is_complete(cid):
            say(f"[{cid}] label scouting: a scout round passed the mode ({n} round(s), {time.time() - t0:.0f}s)")
            set_state(self.base, **{f"{mode}_result": "correct"})
            record_timed_case(cid, self.sdir)
            return True
        fixed.update(s.get("fixed") or {})
        have = {a for a, _ in wrong}
        wrong.extend(w for w in (s.get("unresolved") or []) if w[0] not in have)
        say(f"[{cid}] label scouting: {n} round(s) in {time.time() - t0:.0f}s, {len(s.get('fixed') or {})} label(s) "
            f"GM-corrected, {len(wrong)} field(s) for the generalize")
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
        self._bg_gen_take(self.base, "chain complete")
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


def _drop_instant(now=None):
    """Today's drop (HCTF_DROP_LOCAL, host local time) as an epoch -- or tomorrow's once today's is > 30 min past."""
    from .prebuild import DROP_LOCAL
    now = now or datetime.datetime.now()
    hh, mm = (int(x) for x in DROP_LOCAL.split(":"))
    d = now.replace(hour=hh, minute=mm, second=0, microsecond=0)
    if now - d > datetime.timedelta(minutes=30):
        d += datetime.timedelta(days=1)
    return d.timestamp()


def release_interval(now, drop, poll=None):
    """Seconds until the next `list` while waiting for the drop at epoch `drop`. The GM rate limit is SHARED by every
    call on our token (reviewer: a contended bucket banked 128/1506 ids vs 1506/1506 alone), and D14's flat 0.3 s poll
    sent ~3,600 lists in the 18 min before the drop: a RELEASE_HEARTBEAT list until T-RELEASE_LEAD (also catches an
    early drop; the lead covers host clock skew, which preflight checks against the GM's Date header), the normal poll
    from there, RELEASE_POLL_HOT across T-1 s..T+30 s, then the normal poll again (a late drop)."""
    poll = RELEASE_POLL if poll is None else poll
    dt = drop - now
    if dt > RELEASE_LEAD:
        return min(RELEASE_HEARTBEAT, dt - RELEASE_LEAD)
    if -30 <= dt <= 1:
        return min(poll, RELEASE_POLL_HOT)
    return poll


def wait_for_release(day, poll=None, log=None, drop=None):
    """Block until the GM lists `day`, polling IN this process (warm GM connections, no interpreter start) -> the
    listed challenges. Replaces bin/day.sh's shell loop of `hctf list` + a second list inside `hctf run`: D9 the first
    GM start landed 3-5 s after the drop was seen. Clock-aware (release_interval) against the real GM only: a replay's
    stand-in releases whenever it is started, so it keeps the flat poll (as does HCTF_RELEASE_CLOCK=0)."""
    poll = RELEASE_POLL if poll is None else poll
    clock = RELEASE_CLOCK and (drop is not None or remote._public_gm())
    if clock and drop is None:
        drop = _drop_instant()
    try:
        remote.gm_client().warm_pool(4)
    except Exception:  # noqa: BLE001 - connections open on first use instead
        pass
    n = 0
    while True:
        try:
            got = released_challenges(day)
        except Exception as e:  # noqa: BLE001 - a GM hiccup while waiting: keep polling
            got = []
            if n % 60 == 0:
                say(f"[wait] list note: {str(e)[:160]}")
        if got:
            say(f"[wait] day {day} released ({len(got)} challenge modes) -- launching")
            return got
        n += 1
        wait = release_interval(time.time(), drop, poll) if clock else poll
        if n == 1 or n % 300 == 0:
            say(f"[wait] polling the GM for day {day} (every {poll:g}s + call time"
                + (f"; heartbeat {RELEASE_HEARTBEAT:g}s until {RELEASE_LEAD:g}s before the "
                   f"{datetime.datetime.fromtimestamp(drop):%H:%M} drop)" if clock else ")"))
        time.sleep(wait)


RELEASE_POLL = float(os.environ.get("HCTF_RELEASE_POLL", "0.3"))
RELEASE_POLL_HOT = float(os.environ.get("HCTF_RELEASE_POLL_HOT", "0.2"))     # T-1 s .. T+30 s
RELEASE_HEARTBEAT = float(os.environ.get("HCTF_RELEASE_HEARTBEAT", "5"))     # one list per this long before T-lead
RELEASE_LEAD = float(os.environ.get("HCTF_RELEASE_LEAD", "20"))       # > any host clock skew preflight allows (3 s)
RELEASE_CLOCK = os.environ.get("HCTF_RELEASE_CLOCK", "1") != "0"


def run(day=None, only=None, local_slots=5, hb_slots=0, modes=None, prewarm_homebase=None, keep_homebase=None,
        scout_rounds=None, wait_release=False):
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
    if RETRIEVAL:   # before the release wait: ready long before the drop (a missing index = no retrieval block)
        from . import retrieval
        retrieval.build_async(log=say)
    gov = Governor(hb_enabled=bool(hb_slots))
    pools = Pools(local_slots, hb_slots, gov)
    groups = {}
    for c in (wait_for_release(day) if wait_release and day is not None else released_challenges(day)):
        groups.setdefault(solvers.base_id(c["id"]), []).append(c)
    if only:
        groups = {b: v for b, v in groups.items() if any(o in b for o in only)}
    skip = {x.strip() for x in os.environ.get("HCTF_SKIP_IDS", "").split(",") if x.strip()}
    if skip:   # e.g. a replay sparing a mode whose variant pool is nearly used up
        groups = {b: [c for c in v if c["id"] not in skip] for b, v in groups.items()}
        say(f"skipping (HCTF_SKIP_IDS): {sorted(skip)}")
    say(f"{len(groups)} chains ({sum(map(len, groups.values()))} challenge modes), "
        f"slots local={local_slots} homebase={hb_slots}, credits={gov.credits()}")
    coord_stop = threading.Event()
    if COORDINATOR:
        try:
            from . import coordinator
            coordinator.start(coord_stop, log=say)
        except Exception as e:  # noqa: BLE001 - advisory component
            say(f"[coord] not started ({e})")
    try:
        with ThreadPoolExecutor(max_workers=max(1, len(groups))) as ex:
            for base, entries in sorted(groups.items()):
                ex.submit(Chain(base, entries, pools, gov, modes).run)
        if HOF_RACE and timed_in_scope:
            try:
                hof_race(groups)   # off the critical path: every chain is done; Homebase still warm
            except Exception as e:  # noqa: BLE001 - best-effort
                say(f"[hof] race skipped ({e})")
    finally:
        coord_stop.set()
        if not hb_slots and not keep_homebase:  # Homebase switched on only for tight timed windows: switch it off again
            workers.power_off_homebase_if_ours(say)
        elif keep_homebase:
            say("[homebase] left running (--keep-homebase); power it off with `hctf hb off` when done")
    say("all chains finished")
    if RATCHET and day is not None:
        ratchet(day)
        if PREBUILD_AFTER_RATCHET:
            try:   # off-peak breadth (hctf/prebuild.py): detached, budget-capped, ends 30 min before the next drop
                from . import prebuild as _prebuild
                _prebuild.launch_background(day, log=say)
            except Exception as e:  # noqa: BLE001 - post-run best-effort
                say(f"[prebuild] not launched ({e})")
    _join_captures(f"day{int(day):02d}" if day is not None else "run")   # never exit mid-pull (daemon threads)


CAPTURE_JOIN_TIMEOUT = float(os.environ.get("HCTF_CAPTURE_JOIN_TIMEOUT", "900"))


def _join_captures(tag):
    t0 = time.time()
    if not any(t.is_alive() for t in timed._captures):
        return
    say(f"[capture] {tag}: waiting for {sum(t.is_alive() for t in timed._captures)} background pass capture(s)")
    left = timed.join_captures(CAPTURE_JOIN_TIMEOUT)
    say(f"[capture] {tag}: " + (f"{left} still running after {CAPTURE_JOIN_TIMEOUT:g}s (cases may be missing)" if left
                                else f"all captured ({time.time() - t0:.0f}s)"))


RATCHET = os.environ.get("HCTF_RATCHET", "1") != "0"
# After ratchet + speed_harden: LLM-authored lane breadth in the background (`hctf prebuild`; bin/day.sh stops it).
PREBUILD_AFTER_RATCHET = os.environ.get("HCTF_PREBUILD_AFTER_RATCHET", "1") != "0"
# Hall of Fame keeps each team's FASTEST eligible timed attempt: after the run, spend a few extra ranked attempts per
# passed timed mode where the fresh pool is plentiful (user, 2026-10-12: up to 3, only at >= 8 left, keep 5 in reserve).
HOF_RACE = int(os.environ.get("HCTF_HOF_RACE", "3"))
HOF_RACE_MIN = int(os.environ.get("HCTF_HOF_RACE_MIN", "8"))
HOF_RESERVE = int(os.environ.get("HCTF_HOF_RESERVE", "5"))


def _gm_ms(cid):
    """GM-measured time of this mode's latest attempt (status solved_by.at - started_at) in ms, or None."""
    import datetime as dt
    try:
        b = cli.call(cid, "status", cid)["body"] or {}
        t = lambda x: dt.datetime.fromisoformat(x.replace("Z", "+00:00"))  # noqa: E731
        return round((t(b["solved_by"]["at"]) - t(b["started_at"])).total_seconds() * 1000)
    except Exception:  # noqa: BLE001
        return None


def _race_left(last):
    """Fresh ranked attempts after the current one (dual-pool routes report ranked_*, legacy routes unique_*)."""
    v = last.get("ranked_attempts_remaining")
    return last.get("attempts_remaining") if v is None else v


def hof_race(groups):
    """Best-of-N for the Hall of Fame: per chain, Mastery first (a failed Time Trial race can't then block Mastery's
    prerequisite), up to HOF_RACE fresh eligible retries while >= HOF_RACE_MIN remain and never below HOF_RESERVE.
    Stops a mode on its first non-correct race (the variant is still saved as a regression case; no generalize).
    Scoring is safe: the CourseStack solve is sticky, only the GM's latest-attempt status changes."""
    gm_url = os.environ.get("HUNTRESS_GAME_MASTER_URL", "")
    if "127.0.0.1" in gm_url or "localhost" in gm_url:
        say("[hof] replay GM proxy in use: no Hall of Fame race (it would spend the real ranked pool)")
        return

    def one(base, entries):
        ids = {e["mode"]: e["id"] for e in entries}
        sdir = paths.solver_dir(base)
        if "mastery" in ids and not cli.gm_solved(ids["mastery"]):
            return
        for mode in ("mastery", "time_trial"):
            cid = ids.get(mode)
            if not cid or not cli.gm_solved(cid):
                continue
            best = None
            for i in range(HOF_RACE):
                last = timed.last_result(cid) or {}
                left = _race_left(last)
                if last.get("untimed") or last.get("hall_of_fame_eligible") is False:
                    say(f"[hof] {cid}: not Hall of Fame eligible (GM: hall_of_fame_eligible false / untimed): no race")
                    break
                if left is None or left < max(HOF_RACE_MIN, HOF_RESERVE + 1):
                    say(f"[hof] {cid}: {left} fresh attempt(s) left (< {max(HOF_RACE_MIN, HOF_RESERVE + 1)}): no race")
                    break
                if i == 0:
                    best = _gm_ms(cid)   # GM status round trip only when a race actually runs (D14: ~5 s for nothing)
                set_state(base, stage=f"{mode}:hof-race")
                res = timed.run(cid, sdir, log=say, op="retry")
                ms = _gm_ms(cid) if res == "correct" else None
                say(f"[hof] {cid} race {i + 1}/{HOF_RACE}: {res}"
                    + (f", GM {ms} ms (best so far {min(x for x in (best, ms) if x is not None)} ms)" if ms else ""))
                if res != "correct":
                    break
                best = ms if best is None or (ms is not None and ms < best) else best
        set_state(base, stage="done")

    say(f"[hof] racing passed timed modes for the Hall of Fame (up to {HOF_RACE} each, >= {HOF_RACE_MIN} left, "
        f"reserve {HOF_RESERVE})")
    with ThreadPoolExecutor(max_workers=max(1, len(groups))) as ex:
        for f in [ex.submit(one, b, e) for b, e in sorted(groups.items())]:
            try:
                f.result()
            except Exception as e:  # noqa: BLE001 - one chain's race never stops the others
                say(f"[hof] race note: {e}")


RATCHET_TIMEOUT = float(os.environ.get("HCTF_RATCHET_TIMEOUT", str(15 * 60)))


RATCHET_GATE = ("tests/test_orchestrate.py", "tests/test_day6_fixes.py", "tests/test_day7_fixes.py", "tests/test_codec.py",
                "tests/test_meta_lane.py")   # lib/meta: every metadata case D1..today + prebuilt fixtures


def _lib_changed(backup):
    """True when lib/ differs from the pre-ratchet snapshot (any file added, removed or edited; __pycache__ ignored)."""
    import filecmp

    def walk(c):
        return (c.left_only or c.right_only or c.diff_files or c.funny_files
                or any(walk(sub) for name, sub in c.subdirs.items() if name != "__pycache__"))
    return bool(walk(filecmp.dircmp(ROOT / "lib", backup, ignore=["__pycache__"])))


def ratchet_gate(tag, log=None):
    """The lib/ merge gate: the suites the ratchet prompt names + the ATT&CK coverage check all pass. The suites run in
    PARALLEL (independent processes; serially ~3-5 min, and the ratchet worker ran them itself 2-3x per night).
    The worker runs this same gate: `python3 -m hctf.orchestrate ratchet-gate dayNN` (prints failing tails)."""
    import subprocess as _sp
    log = log or say
    cmds = [[sys.executable, t] for t in RATCHET_GATE if (ROOT / t).exists()]
    cmds.append([sys.executable, "-m", "lib.refs.coverage", str(int(tag[3:]))])
    procs = [(cmd, _sp.Popen(cmd, cwd=ROOT, stdout=_sp.PIPE, stderr=_sp.STDOUT, text=True)) for cmd in cmds]
    ok, end = True, time.time() + 600
    for cmd, p in procs:
        try:
            out, _ = p.communicate(timeout=max(1.0, end - time.time()))
            bad = p.returncode
        except _sp.TimeoutExpired:
            p.kill()
            out, _ = p.communicate()
            bad = "timeout"
        if bad:
            tail = " | ".join((out or "").strip().splitlines()[-4:])[:500]
            log(f"[ratchet] {tag}: `{' '.join(cmd[1:])}` fails after the merge ({bad}): {tail}")
            ok = False
    return ok


_PROPOSALS_RE = re.compile(r"^##\s*Proposed lib additions\s*$(.*?)(?=^##\s|\Z)", re.M | re.S)


def _proposal_blocks(notes):
    """The `## Proposed lib additions` bullets of a NOTES.md (a bullet = a `- ` line + its indented continuation)."""
    try:
        m = _PROPOSALS_RE.search(Path(notes).read_text(errors="replace"))
    except OSError:
        return []
    blocks = []
    for ln in (m.group(1).strip().splitlines() if m else []):
        if ln.startswith(("- ", "* ")) or not blocks:
            blocks.append(ln.rstrip())
        else:
            blocks[-1] += "\n" + ln.rstrip()
    return [b for b in blocks if b.strip()]


def _new_proposals(notes, day):
    """This day's proposal bullets minus any an EARLIER day's NOTES.md of the same lane already carried: the solver dir
    (NOTES.md included) is copied forward daily, so D11's ratchet re-reviewed D10's two sections verbatim -- one of them
    (`rate_limited` download retry) shipped back in D7 (hctf/hb_timed.py)."""
    norm = lambda b: " ".join(b.split())
    try:
        lane = json.loads((Path(notes).parents[1] / "meta.json").read_text()).get("lane")
    except (OSError, ValueError):
        lane = None
    seen = set()
    for old in paths.CHALLENGES.glob("day*/*/solver/NOTES.md"):
        m = re.match(r"day(\d+)$", old.parents[2].name)
        if not m or int(m.group(1)) >= day:
            continue
        try:
            if lane and json.loads((old.parents[1] / "meta.json").read_text()).get("lane") != lane:
                continue
        except (OSError, ValueError):
            pass
        seen |= {norm(b) for b in _proposal_blocks(old)}
    return [b for b in _proposal_blocks(notes) if norm(b) not in seen]


def ratchet_digest(tag, until=None):
    """{chal dir name: one-line digest} of a finished day (lane, per-mode result, timed attempts, generalize workers,
    untimed fallback), lanes that had trouble first -- pre-injected so the ratchet workers don't spend turns dumping
    files (D14: 6 orientation turns of an 80-turn budget)."""
    rows = []
    for meta in sorted((paths.CHALLENGES / tag).glob("*/meta.json")):
        cd = meta.parent
        try:
            lane = json.loads(meta.read_text()).get("lane") or "?"
        except (OSError, ValueError):
            lane = "?"
        try:
            chain = json.loads((cd / "chain.json").read_text())
        except (OSError, ValueError):
            chain = {}
        parts, trouble = [], 0
        done_at = until or time.strftime("%Y%m%dT%H%M%S")   # YYYYMMDDTHHMMSS, as in worker log names
        for mode in ("single_solve", "time_trial", "mastery"):
            md = cd / mode
            if not md.is_dir():
                continue
            # generalize workers before `until` only (the post-run speed-harden's logs land in the same dirs)
            gens = len([p for p in md.glob("worker-generalize-*.log") if p.stem.rsplit("-", 1)[-1] <= done_at])
            atts = len([p for p in (md / "attempts").glob("*") if p.is_dir()]) if (md / "attempts").is_dir() else 0
            try:
                last = json.loads((md / "last_timed.json").read_text())
            except (OSError, ValueError):
                last = {}
            res = chain.get(f"{mode}_result") or ("correct" if mode == "single_solve" and (md / "confirmed.json").exists()
                                                  else last.get("result") or "?")
            extra = [f"{atts} timed attempt(s)" if atts > 1 else "", f"{gens} generalize" if gens else "",
                     "UNTIMED fallback" if last.get("untimed") else ""]
            trouble += gens + max(atts - 1, 0) + bool(last.get("untimed"))
            parts.append(f"{mode}={res}" + (f" ({', '.join(x for x in extra if x)})" if any(extra) else ""))
        rows.append((-trouble, cd.name, lane, f"- {cd.name} [{lane}]: " + "; ".join(parts)
                     + (" <- had trouble" if trouble else " (all first try)")))
    rows.sort()
    return {name: (lane, line) for _t, name, lane, line in rows}


def _tests_snapshot(dst):
    shutil.rmtree(dst, ignore_errors=True)
    if (ROOT / "tests").is_dir():
        shutil.copytree(ROOT / "tests", dst, ignore=shutil.ignore_patterns("__pycache__"))
    else:
        Path(dst).mkdir(parents=True)


def _edited_tests(snap):
    """Existing tests/*.py whose original lines are no longer all present, in order (an assertion modified or deleted
    rather than only added to). D14: the ratchet re-baselined 2 assertions in the suites that gate it."""
    out = []
    for old in sorted(Path(snap).glob("*.py")):
        new = ROOT / "tests" / old.name
        a = old.read_text(errors="replace")
        b = new.read_text(errors="replace") if new.exists() else ""
        if a == b:
            continue
        it = iter(b.splitlines())
        if not all(line in it for line in a.splitlines()):
            out.append(old.name)
    return out


def _restore_tests(snap):
    if not any(Path(snap).iterdir()) and not (ROOT / "tests").exists():
        return
    shutil.rmtree(ROOT / "tests", ignore_errors=True)
    shutil.copytree(snap, ROOT / "tests")


RATCHET_LOGS = os.environ.get("HCTF_RATCHET_LOGS", "1") != "0"   # per-lane technique-log workers beside the lib ratchet
RATCHET_LOG_TIMEOUT = float(os.environ.get("HCTF_RATCHET_LOG_TIMEOUT", str(10 * 60)))


def _ratchet_logs(tag, digest):
    """One `ratchet_log` worker per lane, in parallel; each writes only reference/techniques/<lane>.md (D14: the single
    ratchet ran out of turns before the script/binary/mobile logs). -> [thread]."""
    by_lane = {}
    for name, (lane, line) in digest.items():
        if lane != "?":
            by_lane.setdefault(lane, []).append((name, line))
    threads = []
    for lane, items in sorted(by_lane.items()):
        prompt = workers.render("ratchet_log", day=tag, lane=lane,
                                challenges="\n".join(f"- challenges/{tag}/{n}" for n, _l in items),
                                digest="\n".join(line for _n, line in items))

        def go(lane=lane, prompt=prompt, cd=paths.CHALLENGES / tag / items[0][0]):
            try:
                rc, log = workers.run_local(cd, "ratchet_log", prompt, {"HCTF_STAGE": "ratchet_log", "HCTF_LANE": lane},
                                            RATCHET_LOG_TIMEOUT)
                say(f"[ratchet-log] {tag} {lane}: worker exit {rc} ({Path(log).name})")
            except Exception as e:  # noqa: BLE001 - post-run best-effort
                say(f"[ratchet-log] {tag} {lane}: skipped ({e})")
        t = threading.Thread(target=go, daemon=True)
        t.start()
        threads.append(t)
    return threads


def ratchet(day):
    """Post-run, single-writer knowledge merge: collect every `## Proposed lib additions` section the day's workers
    wrote in solver/NOTES.md and let ONE worker fold the GM-confirmed ones into lib/ (workers no longer edit lib/
    mid-run: Day 6's script worker rewrote lib/knowledge.py + lib/scripts.py while four other lanes imported them).
    The technique logs are written by per-lane `ratchet_log` workers in parallel (they only touch reference/)."""
    tag = f"day{int(day):02d}"
    props = []
    for notes in sorted((paths.CHALLENGES / tag).glob("*/solver/NOTES.md")):
        fresh = _new_proposals(notes, int(day))
        if fresh:
            props.append(f"### {notes.relative_to(ROOT)}\n" + "\n".join(fresh))
    chals = sorted(str(p.relative_to(ROOT)) for p in (paths.CHALLENGES / tag).glob("*/meta.json"))
    if not chals:
        say(f"[ratchet] {tag}: nothing to learn from")
        return
    digest = ratchet_digest(tag)
    prompt = workers.render("ratchet", day=tag, day_num=int(day), challenges="\n".join(f"- {c}" for c in chals),
                            digest="\n".join(line for _lane, line in digest.values()),
                            proposals="\n\n".join(props) or "(no `## Proposed lib additions` this day)")
    log_threads = _ratchet_logs(tag, digest) if RATCHET_LOGS else []
    say(f"[ratchet] {tag}: lib ratchet ({len(props)} proposal section(s)) + {len(log_threads)} technique-log worker(s)")
    # Transactional: a killed/timed-out ratchet left lib/ half-edited on the rehearsal replay (an unvalidated helper that
    # extracted 0 files). Snapshot lib/ + tests/, and restore both unless the test suites still pass. The TESTS are
    # the gate, not the exit code: D8 + D10 hit max_turns and threw away GM-confirmed lib edits (D10: the u32
    # hex-width law, re-applied by hand afterwards).
    backup = ROOT / ".run" / f"ratchet-lib-{tag}"
    tsnap = ROOT / ".run" / f"ratchet-tests-{tag}"
    shutil.rmtree(backup, ignore_errors=True)
    shutil.copytree(ROOT / "lib", backup, ignore=shutil.ignore_patterns("__pycache__"))
    _tests_snapshot(tsnap)
    rc, log = workers.run_local(paths.CHALLENGES / tag, "ratchet", prompt, {"HCTF_STAGE": "ratchet"}, RATCHET_TIMEOUT)
    changed = _lib_changed(backup)
    edited = _edited_tests(tsnap)
    if edited:
        # The gate must not be weakened by the worker it gates: try the ORIGINAL assertions first.
        import difflib
        patch = ROOT / ".run" / f"ratchet-tests-{tag}.patch"
        patch.write_text("".join(
            "".join(difflib.unified_diff((tsnap / n).read_text(errors="replace").splitlines(True),
                                         (ROOT / "tests" / n).read_text(errors="replace").splitlines(True)
                                         if (ROOT / "tests" / n).exists() else [],
                                         f"a/tests/{n}", f"b/tests/{n}")) for n in edited))
        mine = {n: (ROOT / "tests" / n).read_text(errors="replace") if (ROOT / "tests" / n).exists() else None
                for n in edited}
        for n in edited:
            shutil.copy2(tsnap / n, ROOT / "tests" / n)
        if not changed or ratchet_gate(tag):
            say(f"[ratchet] {tag}: the worker modified existing assertions in {edited}; the gate passes with the "
                f"ORIGINAL tests, so those stay (worker's diff: {patch.relative_to(ROOT)})")
            ok = True
        else:
            for n, txt in mine.items():
                if txt is not None:
                    (ROOT / "tests" / n).write_text(txt)
            ok = ratchet_gate(tag)
            if ok:
                say(f"!!! [ratchet] {tag}: the lib edits only pass with MODIFIED existing assertions in {edited}: kept "
                    f"-- REVIEW {patch.relative_to(ROOT)} before the next drop")
    else:
        ok = not changed or ratchet_gate(tag)
    if not changed:
        say(f"[ratchet] {tag}: lib/ unchanged (worker exit {rc}; {Path(log).name})")
    elif ok:
        say(f"[ratchet] {tag}: merged{'' if rc == 0 else f' (worker exit {rc}, tests green: edits kept)'} ({Path(log).name})")
    else:
        shutil.rmtree(ROOT / "lib")
        shutil.copytree(backup, ROOT / "lib")
        _restore_tests(tsnap)
        say(f"[ratchet] {tag}: REVERTED lib/ + tests/ (worker exit {rc}, tests fail); proposals stay in solver/NOTES.md "
            f"({Path(log).name})")
    shutil.rmtree(backup, ignore_errors=True)
    shutil.rmtree(tsnap, ignore_errors=True)
    for t in log_threads:   # reference/ must be quiet before the prebuild starts (its allowlist flags outside edits)
        t.join(timeout=max(1.0, RATCHET_LOG_TIMEOUT))
    _join_captures(tag)     # speed-harden times every case: today's pass captures must be on disk first
    if SPEED_HARDEN:
        try:
            speed_harden(day=day)
        except Exception as e:  # noqa: BLE001 - post-run best-effort
            say(f"[speed-harden] {tag}: skipped ({e})")
    if TRAIN:
        # Offline training on every earlier day (hctf/train.py): tomorrow's seed solvers vs ALL earlier GM-verified
        # cases + answer-invariant mutations; misses -> adopted cases + a transactional generalize. Before the prebuild.
        try:
            from . import train as _train
            _train.run(day, log=say)
        except Exception as e:  # noqa: BLE001 - post-run best-effort
            say(f"[train] {tag}: skipped ({e})")


def prebuild(lane="metadata-forensics", n=None, targets=None, budget_usd=None, deadline=None, log=None, runner=None):
    """Off-peak, single-writer LLM breadth for a lane (modelled on ratchet()): one `prebuild`-stage worker per ranked
    target writes a SPECULATIVE extractor module + independently generated fixtures; hctf/prebuild.py snapshots lib/ +
    tests/data/, gates the edit (path allowlist, AST import allowlist, fixtures, test_meta_lane + RATCHET_GATE) and
    restores the snapshot on any failure. Never at drop time: bin/day.sh stops a running batch before a run."""
    from . import prebuild as _prebuild
    return _prebuild.run(lane, n=n, only=targets, budget_usd=budget_usd, deadline=deadline, log=log or say,
                         runner=runner)


SPEED_HARDEN = os.environ.get("HCTF_SPEED_HARDEN", "1") != "0"
TRAIN = os.environ.get("HCTF_TRAIN", "1") != "0"
PARALLEL_PER_SET = float(os.environ.get("HCTF_PARALLEL_PER_SET", "0.3"))   # s/set above which sets must run in parallel
_PARALLEL_MARKERS = ("group_by_set", "ProcessPoolExecutor", "multiprocessing")


def _parallel_sets_need(sdir, results):
    """A multi-set (Mastery-shaped) regression case whose per-set time is >= PARALLEL_PER_SET while the solver solves
    sets sequentially -> {case, sets, seconds, per_set}; else None. Copied cumulative solvers (binary/script) never
    picked up the skeleton's parallel main() (rehearsal blind D8: binary Mastery solve 8.3 s for 5 sets, sequential)."""
    src = "".join(p.read_text(errors="replace") for p in Path(sdir).glob("*.py"))
    if any(m in src for m in _PARALLEL_MARKERS):
        return None
    from lib.common import group_by_set
    best = None
    for r in results:
        try:
            c = json.loads((Path(sdir) / "cases" / r["case"] / "contract.json").read_text())
        except (OSError, ValueError):
            continue
        ids = c.get("answer_ids") or [q.get("id") for q in c.get("questions") or [] if q.get("id")]
        sets = len([k for k in group_by_set([(a, {}) for a in ids]) if k != "_"])
        if sets >= 2 and r["seconds"] / sets >= PARALLEL_PER_SET:
            cand = {"case": r["case"], "sets": sets, "seconds": r["seconds"], "per_set": round(r["seconds"] / sets, 2)}
            if not best or cand["seconds"] > best["seconds"]:
                best = cand
    return best


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
        bad = [r["case"] for r in res if not r.get("ok") and not r.get("unverified")]
        from . import prebuild as _pb
        if bad and time.time() > _pb.default_deadline().timestamp():
            log(f"[speed-harden] {base}: {len(bad)} failing case(s) but past the pre-drop deadline: skipped")
            bad = []
        if bad:
            # GM-verified cases the solver fails: modes passed by in-attempt fixes (localize + resubmit / reconnect)
            # that no generalize ever taught it. Tomorrow's reuse race copies this solver: fix it now, off the clock.
            log(f"[speed-harden] {base}: {len(bad)} GM-verified case(s) fail ({', '.join(bad[:3])}) -> correctness generalize")
            chain_for(base, pools, gov).generalize(base, wrong=None, fixed=None, diag={})
            res = solvers.test_solver(sdir)
        timed_ok = [r for r in res if not r.get("unverified") and not r.get("error")]
        slow = max((r["seconds"] for r in timed_ok), default=0.0)
        worst = max(timed_ok, key=lambda r: r["seconds"], default=None)
        par = _parallel_sets_need(sdir, timed_ok)
        if slow <= SINGLE_SPEED_BUDGET and not par:
            log(f"[speed-harden] {base}: slowest case {slow:.1f}s <= {SINGLE_SPEED_BUDGET:g}s, nothing to do")
            out[base] = (slow, None)
            continue
        diag = {}
        if slow > SINGLE_SPEED_BUDGET:
            log(f"[speed-harden] {base}: slowest case {worst['case']} {slow:.1f}s > {SINGLE_SPEED_BUDGET:g}s -> speed generalize")
            diag.update(solver_too_slow=True, single_seconds=round(slow, 2))
        if par:
            log(f"[speed-harden] {base}: Mastery case {par['case']} solves {par['sets']} sets sequentially "
                f"({par['per_set']:.2f}s/set) -> parallel-sets generalize")
            diag["parallel_sets"] = par
        chain = chain_for(base, pools, gov)
        chain.generalize(base, wrong=None, fixed=None, diag=diag)
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
    hdr = ("chain", "lane", "stage", "worker", "single", "tt", "mastery", "cost", "updated")
    rows = []
    cost = workers.chain_cost()
    for p in sorted(paths.CHALLENGES.glob("day*/*/chain.json")):
        s = json.loads(p.read_text())
        try:
            meta = json.loads((p.parent / "meta.json").read_text()) or {}
        except (OSError, ValueError):
            meta = {}
        ids = meta.get("ids", {})
        usd = cost.get(meta.get("base", ""))
        # Per-mode solved from local truth, falling back to the chain's recorded result (never the stale stage).
        single = "correct" if ids.get("single_solve") and _mode_solved_local(ids["single_solve"]) else ""
        tt = "correct" if (ids.get("time_trial") and _mode_solved_local(ids["time_trial"])) else s.get("time_trial_result", "")
        mastery = "correct" if (ids.get("mastery") and _mode_solved_local(ids["mastery"])) else s.get("mastery_result", "")
        rows.append((str(p.parent.relative_to(paths.CHALLENGES)), s.get("lane", ""), s.get("stage", ""),
                     s.get("worker") or "", single, tt, mastery, f"${usd:.2f}" if usd else "", s.get("updated", "")))
    w = [max(len(str(r[i])) for r in rows + [hdr]) for i in range(len(hdr))]
    for r in [hdr] + rows:
        print("  ".join(str(x).ljust(w[i]) for i, x in enumerate(r)))


if __name__ == "__main__" and len(sys.argv) == 3 and sys.argv[1] == "ratchet-gate":
    # the ratchet worker's own gate run (hctf/prompts/ratchet.md): parallel suites, failing tails only
    _ok = ratchet_gate(sys.argv[2], log=print)
    print("ratchet gate: GREEN" if _ok else "ratchet gate: FAILING (see above)")
    sys.exit(0 if _ok else 1)
