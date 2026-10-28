"""Generic web-exploitation solver (B1): one solver that handles every web challenge of the known kit, so a web day
needs NO drop-time generalize.

The apps since D05 are one kit: `GET /api/clues` returns a JSON object whose single concept-specific KEY names the
vuln class. `solve_target` dispatches on that key (never the value -- the documented pitfall), races the matching
class handler(s), and returns the `proof_<hex>`. Handlers come from three sources, raced together so the first proof
wins and an unknown class still gets a real try:
  1. built-in class handlers in lib/web/handlers/ (lifted from the proven Day-21 solvers),
  2. every earlier web day's own solver `answer()` (compounded Mastery targets mix earlier classes in),
  3. a `default` general ladder (R1) driven by the invariant kit shape -- the no-fail path for a never-seen class.

Hardened off-peak against free earlier-day Time Trial targets (hctf web-harden), so it is first-try-correct at the
drop. LLM-first: this is dispatch + proven exploit code, not a re-implemented parser; a genuinely new class is the
adaptive worker's job and the ratchet folds its fix back here.
"""
import json
import os
import re
import sys
import threading
import time
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from lib import solverrt, websolve  # noqa: E402
from lib.web import handlers  # noqa: E402


_PRIOR = None
# A target whose class no built-in handler and no earlier web solver knows only gets the `default` ladder, which failed
# every never-seen class on D22 at the full 40 s (4/4 TT attempts, Masteries 53-59 s) before the attempt blocked and a
# live answer took over: cap that race. 0 = off. (D22 post-mortem #7)
UNKNOWN_KEY_BUDGET = float(os.environ.get("HCTF_WEB_UNKNOWN_KEY_BUDGET", "12"))
# A known class's race (no explicit budget): every winner on record took <= 6.3 s (.run/web_race.jsonl, D20-D24), so the
# old 40 s only delayed the handover to a live answer when the known handler missed a variant. 40 = the old behaviour.
KNOWN_BUDGET = float(os.environ.get("HCTF_WEB_KNOWN_BUDGET", "20"))
# A RUN_ALONE one-shot kit (D27 Double Spent) races only its own handler -- no ladder to cap it -- but needs room for the
# barrier-synced POST burst (8 s barrier) + two audit rounds; the all-furniture kit reads class_known=False, whose 12 s
# would clip the second round.
RUN_ALONE_BUDGET = float(os.environ.get("HCTF_WEB_RUN_ALONE_BUDGET", "25"))
# class_known counts only handlers a CONCEPT clue key names (handlers.concept_handlers); 0 = any for_key match (old).
CONCEPT_KNOWN = os.environ.get("HCTF_WEB_CONCEPT_KNOWN", "1") != "0"
# Clue keys class_known never counts through the earlier solvers' SOURCE TEXT: plain words those solvers parse as data
# (D25: Day 18's GraphQL kit {current_user, note, protected_reference} read "known" because current_user / note appear
# in the D02/D03/D20 solvers -> the 20 s known budget on a never-seen class). Comma list; empty = count every key.
KNOWN_IGNORE_KEYS = frozenset(k.strip().lower() for k in os.environ.get(
    "HCTF_WEB_KNOWN_IGNORE_KEYS", "current_user,note").split(",") if k.strip())
# D28 post-mortem #7: a clue-less target (no /api/clues) whose home page fingerprints as the lane-day 04 viewer
# (handlers.lfi_fingerprint: a `?doc=`/`?file=`/`?page=` link, a reader/notes .php page) is a KNOWN class -- the known
# budget and the traversal probe raced first -- not the 12 s unknown cap: D27 + D28 Target 4 timed out at 12 s every
# time (the prior day-20 solver keyed on a path the compounded prompt never named; the ladder dropped `?doc=` links).
# 0 = off (the old unknown-class routing).
CLUELESS_LFI = os.environ.get("HCTF_WEB_CLUELESS_LFI", "1") != "0"


def _prior_web_solvers():
    """(day-id, module) for every earlier web day's solver that exposes answer(), newest first. Loaded once per
    process (it was re-imported for every target) and re-loaded only for a solve.py that appeared / changed since
    (handlers.HOT_RELOAD: one glob + stat per solver; a long-lived process sees a solver promoted mid-run); a
    compounded Mastery target may be any earlier class, so racing their answer() covers the whole history for free."""
    global _PRIOR
    if _PRIOR is None or (handlers.HOT_RELOAD and _prior_sig() != _PRIOR_SIG.get("sig")):
        _PRIOR = _load_prior_web_solvers()
    return _PRIOR


_PRIOR_SIG = {}       # "sig": the solve.py set _PRIOR was built from; path -> (mtime_ns, size, entry or None)


def _prior_dirs():
    base = ROOT / "challenges"
    return sorted((p for p in base.glob("day*/web-*/solver") if (p / "solve.py").exists()),
                  key=lambda p: p.parts, reverse=True)


def _stat_sig(p):
    try:
        st = p.stat()
        return st.st_mtime_ns, st.st_size
    except OSError:
        return None


def _prior_sig():
    return tuple((str(d), _stat_sig(d / "solve.py")) for d in _prior_dirs())


def _load_prior_web_solvers():
    import importlib.util
    mods = []
    base = ROOT / "challenges"
    sig = _prior_sig()
    for d, st in sig:
        d = Path(d)
        old = _PRIOR_SIG.get(str(d))
        if old and old[0] == st:            # unchanged since the last load: keep the module (no re-exec)
            if old[1]:
                mods.append(old[1])
            continue
        entry = None
        try:
            name = "webprior_" + re.sub(r"\W", "_", str(d.relative_to(base)))
            spec = importlib.util.spec_from_file_location(name, d / "solve.py")
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            if hasattr(mod, "answer"):
                entry = (str(d.relative_to(base).parent), mod)
                mods.append(entry)
        except Exception as e:  # noqa: BLE001 - a broken prior solver must not sink the dispatch
            print(f"prior web solver {d}: {e!r}", file=sys.stderr)
            if old and old[1]:              # caught mid-rewrite: keep racing the last good module until it changes
                entry = old[1]
                mods.append(entry)
        _PRIOR_SIG[str(d)] = (st, entry)
    _PRIOR_SIG["sig"] = sig
    return mods


def candidates(base, clues_json, dispatch_key, question=None, contract=None, home=None):
    """Ordered (name, fn) probes to race for one target: the clue-less traversal probe when the home page fingerprints
    as the lane-day 04 viewer (`home`: its body), the built-in handler for the clue key, then the general `default`
    ladder, then every earlier web day's answer()."""
    out = []
    if home is not None and CLUELESS_LFI and handlers.lfi_fingerprint(home):
        out.append(("lfi", lambda: handlers.lfi(base, clues_json, home=home)))
    for name, fn in handlers.for_key(dispatch_key, clues_json):
        out.append((name, lambda fn=fn: fn(base, clues_json)))
    out.append(("default", lambda: handlers.default(base, clues_json)))
    if question is not None and contract is not None:
        for day, mod in _prior_web_solvers():
            out.append((f"prior:{day}", lambda mod=mod: _safe_answer(mod, question, contract)))
    return out


def _credit_kit_probe(base, clues_json):
    """One side-effect-free GET of the audit (`secondary_route`): True when the target looks like a one-credit overspend
    kit (a credit audit not yet overspent). For an UNFLAGGED future credit kit (no RUN_ALONE plugin yet) this still
    forces the solo path BEFORE the default ladder's sequential POST burns the one credit. GET only -- never spends it;
    skipped once the proof is already present (then the normal path returns it)."""
    if not isinstance(clues_json, dict):
        return False
    audit = clues_json.get("secondary_route")
    if not (isinstance(audit, str) and audit.startswith("/")):
        return False
    _, body, _ = websolve.fetch(urllib.parse.urljoin(base, audit))
    b = (body or "").lower()
    return ("credit" in b or "overspent" in b or "overspend" in b) and "proof_" not in b


def _safe_answer(mod, question, contract):
    try:
        v = mod.answer(None, question, None, contract)
    except Exception:  # noqa: BLE001
        return None
    return v if v and websolve.PROOF_RE.fullmatch(str(v).strip()) else None


def solve_target(question, contract, budget=None, clues=None):
    """Proof for one live target (a contract question whose `artifact` is a Target), or None. `budget` None = by class:
    KNOWN_BUDGET for a known class, UNKNOWN_KEY_BUDGET otherwise (an explicit budget is still capped for an unknown
    class); HCTF_SOLVE_DEADLINE caps either. `clues`: an already fetched /api/clues dict (skips the refetch). A target whose clues name no route and whose home page is not 2xx/3xx
    is gone (expired = 410 `{"state":"completed"}`): None at once instead of burning the race budget (D22: 9-40 s)."""
    base = websolve.base_of(question, contract)
    if not base:
        return None
    handlers.refresh()      # a plugin promoted mid-attempt is raced by this very process (D28 TT; HCTF_WEB_HOT_RELOAD)
    if isinstance(clues, dict):
        clues_json, key = clues, websolve.dispatch_key(clues)
    else:
        clues_json, key = websolve.clues(base)
    home = None
    if not any(isinstance(v, str) and v.startswith("/") for v in clues_json.values()):
        st, home, _ = websolve.fetch(base)
        if not 200 <= st < 400:
            _note_state(responded=False, status=st)
            return None
    # a clue-less lane-day 04 viewer is a known class (CLUELESS_LFI): known budget, traversal probe first
    lfi = bool(CLUELESS_LFI and home is not None and handlers.lfi_fingerprint(home))
    known = lfi or class_known(clues_json, key)
    # D27: a one-shot credit kit must race its handler ALONE -- the default ladder / prior solvers each do a sequential
    # POST to feature_route that spends the single credit before the burst (Day-27 burn). Detected by the plugin's
    # RUN_ALONE flag, or (for an unflagged future kit) a side-effect-free audit probe, done only for an unknown class so
    # it never adds a GET to a recognised target's hot path.
    ra = handlers.run_alone_handlers(key, clues_json)
    # Credit kit? The RUN_ALONE handler keys on `secondary_route`, which is kit furniture many non-credit kits also ship,
    # so the flag alone over-triggers -- a side-effect-free audit probe (GET the audit route, see `credit`/`overspent`)
    # is the authority. We probe when a run-alone handler matched OR the class is unknown (which also catches an UNFLAGGED
    # future credit kit before the ladder burns its one credit); the probe no-ops when there is no audit route.
    solo = (bool(ra) or not known) and _credit_kit_probe(base, clues_json)
    if solo:
        # ONLY the run-alone handler(s) -- never the default ladder, prior solvers, or the other furniture-key handlers
        # an all-furniture kit also matches (their sequential POST would burn the one credit). A probe-confirmed but
        # UNFLAGGED kit has no run-alone handler -> probes empty -> return None without ever POSTing (no burn): the
        # adaptive worker then writes the plugin on a fresh/reset target.
        probes = [(name, (lambda fn=fn: fn(base, clues_json))) for name, fn in ra]
    else:
        probes = candidates(base, clues_json, key, question, contract, **({"home": home} if lfi else {}))
    if budget is None:
        budget = KNOWN_BUDGET
    if solo:
        budget = max(budget, RUN_ALONE_BUDGET)      # no ladder to cap: give the burst + audit room
    elif not known and UNKNOWN_KEY_BUDGET > 0:
        budget = min(budget, UNKNOWN_KEY_BUDGET)
    rep = {}
    gen = handlers.GENERATION
    v = websolve.race(probes, budget=budget, report=rep)
    # the target answered (clues JSON or a 2xx/3xx home) and ran its race: what MISS-RETRY needs to tell a real miss
    # on a live app from a still-provisioning target
    _note_state(responded=True, timed_out=bool(rep.get("timed_out")), gen=gen)
    _log_race({"qid": (question or {}).get("id"), "key": key, "known": known, "solo": bool(solo), "budget": budget,
               "winner": rep.get("winner"), "elapsed": rep.get("elapsed"), "timed_out": rep.get("timed_out"),
               "keys": sorted(clues_json)[:12], **({"fp": "lfi"} if lfi else {})})
    return v


_TLS = threading.local()    # .state: the last solve_target's readiness on this thread (read by _run_target)


def _note_state(**state):
    _TLS.state = state


def _prior_sources():
    """Lower-cased source text of every earlier web day's solver (for class_known)."""
    out = []
    for _day, mod in _prior_web_solvers():
        try:
            out.append(Path(mod.__file__).read_text(errors="replace").lower())
        except (OSError, TypeError, AttributeError):
            pass
    return out


def class_known(clues_json, key):
    """Has this harness met the target's vuln class? A built-in handler maps one of its clue keys, or an earlier web
    day's solver names one of its concept keys (route-valued keys and the kit's common keys are furniture). A handler
    matched only through a furniture key (an all-furniture D23-style kit) does not make the class known."""
    if (handlers.concept_handlers if CONCEPT_KNOWN else handlers.for_key)(key, clues_json):
        return True
    concept = {str(k).lower() for k, v in (clues_json if isinstance(clues_json, dict) else {}).items()
               if k not in websolve.COMMON_KEYS and not (isinstance(v, str) and v.startswith("/"))}
    if key:
        concept.add(str(key).lower())
    # D25 D4: a key that only dispatches beside an absent companion (handlers.KEY_COMPANIONS) or a plain-word key is no
    # evidence the class was met before
    concept = {k for k in concept if len(k) >= 4 and k not in KNOWN_IGNORE_KEYS
               and not handlers.gated_only(k, clues_json)}
    return bool(concept) and any(k in src for src in _prior_sources() for k in concept)


def _log_race(rec):
    """One JSON line per target race -> $HCTF_WEB_RACE_LOG (default .run/web_race.jsonl). Never raises."""
    try:
        import time
        p = Path(os.environ.get("HCTF_WEB_RACE_LOG") or (ROOT / ".run" / "web_race.jsonl"))
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "a") as f:
            f.write(json.dumps({"t": round(time.time(), 1), **rec}) + "\n")
    except Exception:  # noqa: BLE001 - telemetry only
        pass


def _iter_pairs(contract):
    ids = contract.get("answer_ids") or [q.get("id") for q in contract.get("questions", [])]
    qs = contract.get("questions", [])
    return [(aid, qs[i] if i < len(qs) else {}) for i, aid in enumerate(ids)]


_STATE_KEY = "\0state:"    # _run_target's miss record (readiness) -- split off by _Sink, never an answer


def _run_target(job):
    """run_sets job (module level: the fork pool pickles it by name -- a local closure failed every target). A miss
    returns its readiness record (solve_target's _note_state) under a _STATE_KEY key, which _Sink keeps out of `out`."""
    aid, q, contract = job
    _TLS.state = None
    p = solve_target(q, contract)
    if p:
        return {aid: p}
    st = getattr(_TLS, "state", None)
    return {_STATE_KEY + str(aid): st} if st else {}


class _Sink:
    """The `out` run_sets merges each finished job into: answers go straight into the real `out` (the deadline
    watchdog prints that one, partials included); _STATE_KEY records go to `states` instead."""

    def __init__(self, out, states):
        self.out, self.states = out, states

    def update(self, d):
        for k, v in (d or {}).items():
            if isinstance(k, str) and k.startswith(_STATE_KEY):
                self.states[k[len(_STATE_KEY):]] = v
            else:
                self.out[k] = v


def _jobs(contract):
    return [(aid, q, contract) for aid, q in _iter_pairs(contract)]


# D27 web Mastery tail: the untimed solve has a ~60 s budget (hb_timed._solve_budget) but each target got ONE solve pass.
# A target still PROVISIONING during that pass returns a transient response and the handler gives up (None); the field is
# then handed to a ~2-min generalize/live-answer worker, though the target is solvable seconds later -- which is exactly
# how that worker got it. Re-attempt the missed targets within the remaining budget instead (deterministic, seconds not
# minutes). One-shot credit kits are NOT retried (a miss there is a real burn, not a not-ready race). HCTF_WEB_MISS_RETRY=0 off.
WEB_MISS_RETRY = int(os.environ.get("HCTF_WEB_MISS_RETRY", "4"))
WEB_MISS_RETRY_DELAY = float(os.environ.get("HCTF_WEB_MISS_RETRY_DELAY", "2.5"))
WEB_MISS_RETRY_MIN_LEFT = float(os.environ.get("HCTF_WEB_MISS_RETRY_MIN_LEFT", "4"))
# D28 post-mortem #8: the miss-retry re-raced Mastery Target 4 -- a LIVE (HTTP 200) app whose race had run out its
# budget -- 3x (~16.5 s each, ~45 s of the Mastery). It exists for a target still PROVISIONING (transport error / 5xx /
# not up during the pass); a target that answered and timed out its whole race is a real miss the same handlers will
# miss again, so it is skipped -- unless a plugin landed since its race (handlers.GENERATION, hot reload). A target
# that answered but whose race ended early (a transient response, D27) is still retried. 1 = retry every miss (old).
WEB_MISS_RETRY_LIVE = os.environ.get("HCTF_WEB_MISS_RETRY_LIVE", "0") == "1"


def _deadline_left():
    try:
        return float(os.environ["HCTF_SOLVE_DEADLINE"]) - time.time()
    except (KeyError, ValueError):
        return 9e9


def _is_one_shot(q, contract):
    """A target whose class must run alone (a one-shot credit kit): never retried on a miss (that is a burn, not a race)."""
    try:
        base = websolve.base_of(q, contract)
        if not base:
            return False
        cj, key = websolve.clues(base)
        return bool(handlers.run_alone_handlers(key, cj))
    except Exception:  # noqa: BLE001
        return False


def _retryable(state):
    """A missed target worth another pass: not known to be a live app that timed out its whole race (no record =
    retry, the old behaviour), or one whose race predates a plugin loaded since (handlers.GENERATION)."""
    if WEB_MISS_RETRY_LIVE or not isinstance(state, dict):
        return True
    if not (state.get("responded") and state.get("timed_out")):
        return True
    return int(state.get("gen") or 0) < handlers.GENERATION


def _solve_into(contract, out, pool):
    """First parallel pass over every target, then bounded re-attempts of the misses (a still-provisioning target) while
    budget remains -- so a slow-to-ready Mastery field is caught deterministically instead of by a 2-min worker. A live
    target that timed out its race is not re-raced (WEB_MISS_RETRY_LIVE); plugins are re-scanned before each pass."""
    jobs = _jobs(contract)
    states = {}
    sink = _Sink(out, states)
    handlers.refresh()      # before the fork: every pass's children inherit what is on disk now
    solverrt.run_sets(jobs, _run_target, sink, pool, io_bound=True)
    for _ in range(max(0, WEB_MISS_RETRY)):
        if _deadline_left() < WEB_MISS_RETRY_MIN_LEFT:
            break
        handlers.refresh()
        missed = [(aid, q, c) for (aid, q, c) in jobs if not out.get(aid) and not _is_one_shot(q, c)]
        missing = [j for j in missed if _retryable(states.get(str(j[0])))]
        if len(missing) < len(missed):
            retry_ids = {aid for aid, _q, _c in missing}
            _log_race({"miss_skip_live": [aid for aid, _q, _c in missed if aid not in retry_ids]})
        if not missing:
            break
        _log_race({"miss_retry": [aid for aid, _q, _c in missing], "left": round(_deadline_left(), 1)})
        time.sleep(min(WEB_MISS_RETRY_DELAY, max(0.0, _deadline_left() - WEB_MISS_RETRY_MIN_LEFT)))
        solverrt.run_sets(missing, _run_target, sink, pool, io_bound=True)
    return out


def solve(contract, artifacts=None):
    """{answer_id: proof} for every target in the contract. Targets run in parallel (I/O bound); partials are emitted
    at the deadline by the caller's emit path. Misses (a not-ready target) are re-attempted within the budget."""
    out, pool = {}, []
    solverrt.arm_deadline(out, pool)
    return _solve_into(contract, out, pool)


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--contract", required=True)
    ap.add_argument("--artifacts", required=False)
    a = ap.parse_args()
    contract = json.loads(Path(a.contract).read_text())
    out, pool = {}, []
    solverrt.arm_deadline(out, pool)
    # targets in parallel (D22: serial targets ran 40-47 s on a 3-target Mastery); misses re-attempted within budget (D27)
    _solve_into(contract, out, pool)
    solverrt.emit_and_exit(out, pool)


if __name__ == "__main__":
    main()
