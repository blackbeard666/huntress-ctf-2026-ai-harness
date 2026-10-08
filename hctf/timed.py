"""Scripted Time Trial / Mastery runs: start -> download -> run solve.py -> submit (hctf/hb_timed.py does the window).

No LLM runs inside the clock: the window only runs the offline-built solver, submits (the answered subset too when the
solver is incomplete -- the GM keeps correct partial progress) and localizes wrong fields. A failed attempt is turned
into a regression case and fixed OFFLINE by a generalize worker (hctf/orchestrate.py) before the next attempt.
"""
import datetime as dt
import json
import re
import time
from pathlib import Path

from . import cli, solvers

SUBMIT_MARGIN = 8          # seconds kept in reserve for the final submit round-trip (~1-3s over ssh)
MAX_WRONG_TIMED = 6        # incorrect submissions allowed per timed attempt (several sets per bundle)


def seconds_left(contract):
    d = (contract or {}).get("deadline")
    if not d:
        return None
    end = dt.datetime.fromisoformat(d.replace("Z", "+00:00"))
    return (end - dt.datetime.now(dt.timezone.utc)).total_seconds()


def _set_key(aid):
    m = re.match(r"(set\d+)\.", aid)
    return m.group(1) if m else "_"


def latest_artifacts(cid):
    p = cli.cdir(cid) / "artifacts" / "latest"
    return p.resolve() if p.exists() else None


# answer_id field-name fragments that tend to carry GM-specific vocabulary (the usual wrong answers),
# as opposed to deterministic values (sha256/crc32/addresses). Probed first so a tight clock still
# reaches the likely culprits.
_PROBE_SUSPECT = ("format", "symbol", "vtable", "score", "attack", "technique", "scenario", "role",
                  "style", "machine", "endian", "adapter", "kind", "type", "extension", "note", "mutex",
                  "marker", "campaign", "family", "class")


def _probe_rank(aid):
    f = aid.rsplit(".", 1)[-1].lower()
    return (0 if any(s in f for s in _PROBE_SUSPECT) else 1, aid)


def probe_fields(cid, sdir, log=print):
    """Turn the GM's per-SET feedback into per-FIELD signal on the current started attempt by BINARY SEARCH:
    submit a group; if the GM accepts it every field in it is right, otherwise split it and recurse. ~2*log2(n)
    submits per wrong field instead of n, so even a 6s clock localizes most failures (the old one-by-one probe
    reached 2 of 159 fields). Sequential on purpose: concurrent submits race and give false negatives.
    Returns [(answer_id, solver_value)] the GM rejected. Writes diagnosis.json, including which fields were never
    judged (probe cut short by the deadline), so nobody mistakes an incomplete probe for "all fields correct"."""
    if cli.is_complete(cid):   # never start/burn a fresh attempt on an already-solved challenge
        return []
    contract = cli.load(cid, "start.json")
    art = latest_artifacts(cid)
    if not contract or not art:
        return []
    ids = contract.get("answer_ids", []) or []
    try:
        answers, _ = solvers.solve_contract(contract, art, default_solver=sdir)
    except Exception as e:  # noqa: BLE001 - probing is best-effort diagnostics
        log(f"[{cid}] probe: solver error {e}")
        answers = {}
    wrong = [(a, None) for a in ids if a not in answers]
    ok_fields, complete = set(), True

    def narrow(group):
        nonlocal complete
        if not group:
            return
        left = seconds_left(contract)
        if left is not None and left <= 1.0:
            complete = False
            return
        kind, _body, _ = cli.submit(cid, {k: answers[k] for k in group}, force=True)
        if kind in ("correct", "accepted"):
            ok_fields.update(group)
            return
        if kind != "incorrect":          # expired / error: stop, the rest stays unjudged
            complete = False
            return
        if len(group) == 1:
            wrong.append((group[0], answers[group[0]]))
            return
        mid = len(group) // 2
        narrow(group[:mid])
        narrow(group[mid:])

    groups = {}
    for a in sorted((a for a in ids if a in answers), key=_probe_rank):
        groups.setdefault(_set_key(a), []).append(a)
    for g in groups.values():
        narrow(g)
    judged = ok_fields | {a for a, _ in wrong}
    diag = {"attempt": cli.attempt_id(contract), "probed": len(judged), "total": len(ids), "complete": complete,
            "ok": len(ok_fields), "wrong": [{"id": a, "solver_value": v} for a, v in wrong],
            "unjudged": [a for a in ids if a not in judged]}
    (cli.cdir(cid) / "diagnosis.json").write_text(json.dumps(diag, indent=2, ensure_ascii=False))
    log(f"[{cid}] probe: {len(ok_fields)} ok, {len(wrong)} wrong of {len(judged)}/{len(ids)} judged"
        + ("" if complete else " (cut short by the deadline)")
        + (f" -> {[a for a, _ in wrong][:8]}" if wrong else ""))
    return wrong


def resolve_labels_online(cid, sdir, wrong_aids, lane=None, log=print, budget=8):
    """Resolve unconfirmed CLOSED-VOCAB labels by probing the GM directly (the only authority on the spelling),
    instead of letting an OFFLINE generalize worker GUESS a label and burn a whole timed attempt testing it (the
    Q6 pain: Day-4 vbscript control took 3 generalize cycles to reach `error_guard`). Uses/starts a fresh attempt,
    runs the solver to see which wrong fields carry an UNCONFIRMED label IN THIS VARIANT (solver value not yet in
    vocab.json for its family — i.e. this variant really does use the new construct), and submits the playbook's
    ranked candidates one at a time on that attempt until the GM accepts one (banked + recorded to vocab.json by
    labels.probe). Returns the set of answer_ids resolved. Only touches playbook label families; never flags/free text.
    Safe: bounded by `budget` and the live deadline; any failure returns what resolved so far."""
    from . import labels
    try:
        from lib import playbook
    except ImportError:
        playbook = None
    if not wrong_aids or playbook is None:
        return set()
    if lane is None:
        lane = labels.lane_of(cid)
    targets = [a for a in wrong_aids if lane and playbook.entry_for(lane, a)]
    if not targets:
        return set()
    body, _ = ensure_started(cid)
    contract = cli.load(cid, "start.json")
    art = latest_artifacts(cid)
    if not body or not contract or not art:
        return set()
    try:
        answers, _ = solvers.solve_contract(contract, art, default_solver=sdir)
    except Exception as e:  # noqa: BLE001
        log(f"[{cid}] online-resolve solve error: {e}")
        answers = {}
    vocab = labels.load_vocab()
    resolved = set()
    for aid in targets:
        sv = answers.get(aid)
        if sv and sv in vocab.get(labels.ending(aid), []):
            continue  # this variant uses an already-confirmed construct for this field; nothing to resolve
        left = seconds_left(contract)
        if left is not None and left < 2:
            break
        cands = [c for c in playbook.seed_candidates(lane, aid, solver_value=sv) if c not in labels.judged_wrong(cid, aid)]
        if not cands:
            continue
        r = labels.probe(cid, aid, cands, budget=budget, delay=0.3, log=log)
        if r.get("accepted"):
            resolved.add(aid)
            log(f"[{cid}] online-resolved label {aid} = {r['accepted']} (cached to vocab.json)")
    return resolved


MAX_AUTO_CASES = int(__import__("os").environ.get("HCTF_MAX_AUTO_CASES", "40"))


def present_only(contract, art_dir, answers):
    """Keep only answers whose question's container file is actually in art_dir. A Mastery case saved without
    evidence-02.zip once made the solver 'answer' set 2 from set 1's bytes and froze worker guesses as expected."""
    skip = {"manifest.json", "contract.json", "result.json"}
    have = ({p.name for p in Path(art_dir).iterdir() if p.is_file() and p.name not in skip}
            if art_dir and Path(art_dir).exists() else set())
    ids = contract.get("answer_ids") or []
    qs = contract.get("questions") or []
    containers = {}
    for i, aid in enumerate(ids):
        art = (qs[i].get("artifact") if i < len(qs) and isinstance(qs[i], dict) else "") or ""
        containers[aid] = art.split(" -> ", 1)[0].strip()
    # one delivery for every question: the file may be saved under another name (artifacts/latest), keep all
    single = len({c for c in containers.values() if c}) <= 1 and len(have) >= 1
    have |= _bundled(art_dir, have)
    return {aid: v for aid, v in answers.items()
            if single or not containers.get(aid) or containers[aid] in have}


def trim_to_present(contract, art_dir):
    """The contract restricted to the questions whose container is in art_dir (+ artifacts[] to the deliveries present,
    matched by sha256 when the contract lists one). A failed Homebase variant is now pulled back SCOPED (only the
    deliveries of the failing sets): the case's contract must match, or the fill check can never pass and a solver's
    "N-th zip" fallback pairs delivery 3's question with delivery 2's bytes. Unchanged when everything is present."""
    ids = contract.get("answer_ids") or []
    keep = set(present_only(contract, art_dir, {a: "" for a in ids}))
    if len(keep) == len(ids):
        return contract
    from . import solvers
    c = solvers.sub_contract(contract, keep)
    arts = contract.get("artifacts")
    if isinstance(arts, list) and arts and all(isinstance(x, dict) and x.get("sha256") for x in arts):
        import hashlib
        skip = {"manifest.json", "contract.json", "result.json"}
        shas = {hashlib.sha256(p.read_bytes()).hexdigest() for p in Path(art_dir).iterdir()
                if p.is_file() and p.name not in skip}
        c["artifacts"] = [x for x in arts if x["sha256"] in shas]
    return c


def _bundled(art_dir, names):
    """Per-set containers delivered INSIDE a bundle zip (D7 metadata Mastery: one ...-mastery.zip = {evidence-01.zip,
    evidence-02.zip}, saved as evidence-01.zip): set 2's container is present even though no file carries its name --
    dropping it left every bundled auto-mastery case verifying set 1 only. Only a real bundle counts (>= 2 members,
    all archives); first level only (member names, nothing decompressed)."""
    import zipfile
    arch = (".zip", ".7z", ".apk", ".jar", ".tar", ".gz", ".tgz")
    out = set()
    for n in names:
        try:
            with zipfile.ZipFile(Path(art_dir) / n) as z:
                inner = [Path(i.filename).name for i in z.infolist() if not i.is_dir()]
        except (zipfile.BadZipFile, OSError, ValueError):
            continue
        if len(inner) >= 2 and all(x.lower().endswith(arch) for x in inner):
            out.update(inner)
    return out


def last_result(cid):
    """The last timed attempt's result (from hb_timed), kept for the generalize worker's diagnosis."""
    p = cli.cdir(cid) / "last_timed.json"
    try:
        return json.loads(p.read_text())
    except (OSError, ValueError):
        return None


def _keep_failed_attempt(cid, res, log=print):
    """Copy a FAILED attempt's contract + result + bytes to <mode dir>/attempts/<attempt8>/ before anything reuses the
    timed download dir: the next probe/retry overwrites it, which destroyed the evidence for replay run 2's
    Homebase-only script TT failure (7 fields missing, cause never determined). Keeps the newest 5."""
    import shutil
    tdir = timed_dir(cid)
    att = (res.get("attempt_id") or "")[:8] or time.strftime("%H%M%S")
    dst = cli.cdir(cid) / "attempts" / att
    try:
        try:   # only archive bytes that belong to THIS attempt (a skipped/background pull leaves an older attempt's)
            same = cli.attempt_id(json.loads((tdir / "contract.json").read_text())) == res.get("attempt_id")
        except (OSError, ValueError):
            same = False
        if not same:
            dst.mkdir(parents=True, exist_ok=True)
            (dst / "last_timed.json").write_text(json.dumps({k: v for k, v in res.items() if not callable(v)},
                                                            indent=2, default=str))
        elif tdir.exists() and not dst.exists():
            shutil.copytree(tdir, dst)
            (dst / "last_timed.json").write_text(json.dumps({k: v for k, v in res.items() if not callable(v)},
                                                            indent=2, default=str))
        olds = sorted((cli.cdir(cid) / "attempts").glob("*/"), key=lambda p: p.stat().st_mtime)
        for old in olds[:-5]:
            shutil.rmtree(old, ignore_errors=True)
    except Exception as e:  # noqa: BLE001 - forensics only
        log(f"[{cid}] keep-failed-attempt note: {e}")


def _remember(cid, res):
    keep = {k: res.get(k) for k in ("result", "full_result", "attempt_id", "window", "elapsed", "in_window", "phases", "solver_too_slow", "hb_env_mismatch",
                                     "per_set", "bad_sets", "wrong", "fixed", "localize_complete", "routed", "missing",
                                     "localize_tried", "novel_labels", "deadline", "detail", "verified",
                                     "partial_submit", "partial_wrong", "partial_fixed", "attempts_remaining",
                                     "run_for_time", "hall_of_fame_eligible", "ranked_attempts_remaining",
                                     "variant_fresh", "clock_short", "submit_transport_error", "submit_resent",
                                     "start_refused", "rerolled_short", "capture_note")
            if k in res}
    (cli.cdir(cid) / "last_timed.json").write_text(json.dumps(keep, indent=2, ensure_ascii=False))
    if res.get("window"):
        p = cli.cdir(cid) / "window.json"
        try:
            d = json.loads(p.read_text())   # keep the local_expired flag set by the dispatcher
        except (OSError, ValueError):
            d = {}
        d["seconds"] = res["window"]
        p.write_text(json.dumps(d))


def capture_case(cid, solver_dir, res):
    """Turn the attempt that just ran into a regression case `auto-<mode>-<attempt8>`: its exact bytes + contract,
    expected = ONLY the answers the GM verified on that attempt (all of them when correct; accepted sets, fields
    a localization subset proved right, and labels the GM accepted as corrections otherwise). Keeps the newest
    HCTF_MAX_AUTO_CASES auto cases. Returns the case name or None."""
    verified = res.get("verified") or (res.get("submitted") if str(res.get("result")).lower() == "correct" else None)
    tdir = timed_dir(cid)
    if not verified or not (tdir / "contract.json").exists():
        return None
    contract = json.loads((tdir / "contract.json").read_text())
    att = cli.attempt_id(contract)
    if not att or att != res.get("attempt_id"):   # never pair a contract with another attempt's bytes
        return None
    verified = present_only(contract, tdir, verified)
    if not verified:
        return None
    name = f"auto-{solvers.mode_of(cid)}-{att[:8]}"
    solvers.add_case(solver_dir, name, trim_to_present(contract, tdir), tdir, verified)
    autos = sorted((Path(solver_dir) / "cases").glob("auto-*"), key=lambda p: p.stat().st_mtime)
    for old in autos[:-MAX_AUTO_CASES] if len(autos) > MAX_AUTO_CASES else []:
        import shutil
        shutil.rmtree(old, ignore_errors=True)
    return name


def timed_dir(cid):
    """Where the one-shot timed runner (hb_timed) keeps the attempt's contract.json + downloads."""
    return cli.ROOT / ".run" / "tmp-timed" / re.sub(r"[^A-Za-z0-9]+", "_", cid)


def artifacts_for(cid, contract):
    """Artifacts dir holding THIS attempt's bytes: artifacts/latest if its manifest names the attempt, else the
    timed runner's download dir if its contract.json is the same attempt, else a fresh download. Never pair a
    contract with another attempt's bytes (that seeded variant-mastery-efc3d9e4 with 6605fd8c's delivery 2)."""
    aid = cli.attempt_id(contract or {})
    art = latest_artifacts(cid)
    if art and (art / "manifest.json").exists():
        if json.loads((art / "manifest.json").read_text()).get("attempt") == aid:
            return art
    tdir = timed_dir(cid)
    if aid and (tdir / "contract.json").exists() and cli.attempt_id(json.loads((tdir / "contract.json").read_text())) == aid:
        return tdir
    class A:
        id, delivery = cid, None
    try:
        with cli.quiet():
            cli.c_artifact(A)
    except Exception:
        return None
    art = latest_artifacts(cid)
    m = art / "manifest.json" if art else None
    return art if m and m.exists() and json.loads(m.read_text()).get("attempt") == aid else None


def ensure_started(cid):
    """Start (or resume: start is idempotent while the clock runs) and download the variant."""
    with cli.chal_lock(cid):
        env = cli.call(cid, "start", cid)
    body = env["body"] or {}
    if env["http"] != 200 or body.get("error"):
        return None, body
    if not cli.attempt_id(body):
        # 200 {"result": "expired"} (the timed run overshot its deadline): never save that over the contract.
        # Adopt the timed runner's contract instead, so capture_variant/solver-run see the attempt that just ran.
        tdir = timed_dir(cid)
        tc = json.loads((tdir / "contract.json").read_text()) if (tdir / "contract.json").exists() else None
        if cli.attempt_id(tc) and cli.attempt_id(tc) != cli.attempt_id(cli.load(cid, "start.json")):
            cli.save(cid, "start.json", tc)
            cli.save(cid, "contract.json", tc)
        return None, body
    cli.save(cid, "start.json", body)
    cli.save(cid, "contract.json", body)
    art = latest_artifacts(cid)
    manifest = json.loads((art / "manifest.json").read_text()) if art and (art / "manifest.json").exists() else {}
    if manifest.get("attempt") != cli.attempt_id(body):  # fetch this attempt's artifacts if we don't have them
        class A:  # argparse-like namespace for cli.c_artifact
            id, delivery = cid, None
        with cli.quiet():
            cli.c_artifact(A)
    return body, None


def run(cid, solver_dir, fix=None, log=print, op="start"):
    """Execute one timed attempt. The clock-critical start->download->solve->submit runs LOCALLY against
    the public GM (pairing token; direct HTTPS is fast enough for the ~6s windows), or on Homebase over SSH
    as a fallback. The solver must already be correct (built/generalised offline).
    Returns: correct | expired | blocked | error:<x>.
      correct            -> GM accepted everything
      blocked            -> solver incomplete/wrong for this variant (caller generalises offline, then retries)
      expired            -> the attempt's clock ran out before we could submit a complete answer
    """
    from . import workers
    global _inflight
    with _inflight_lock:
        _inflight += 1
    try:
        res = workers.run_timed_auto(solver_dir, cid, op=op, log=log)
    finally:
        with _inflight_lock:
            _inflight -= 1
    return process_result(cid, solver_dir, res, log=log)


# Live timed attempts in this process (any chain): background GM traffic (variant harvest) yields to a running clock.
# Day 7: 3 harvest start+downloads + another lane's timed runs -> GM 429 on the script TT's evidence download.
_inflight = 0
_inflight_lock = __import__("threading").Lock()


def inflight():
    return _inflight


CAPTURE_GRACE = float(__import__("os").environ.get("HCTF_CAPTURE_GRACE", "6"))
CAPTURE_YIELD_MAX = float(__import__("os").environ.get("HCTF_CAPTURE_YIELD_MAX", "180"))


def wait_idle(max_wait=None, poll=0.5):
    """Block while any timed attempt (incl. its Homebase solver push) is in flight, up to max_wait s. Background
    pulls of a passed attempt's evidence (several MB) otherwise share the slow VPN with the next clock-critical
    push: blind D7 replay, binary's 6.6 MB TT capture ran beside script's Mastery retry (68 s green -> result)."""
    import time as _t
    end = _t.time() + (CAPTURE_YIELD_MAX if max_wait is None else max_wait)
    while _inflight and _t.time() < end:
        _t.sleep(poll)


def process_result(cid, solver_dir, res, log=print):
    """Post-attempt bookkeeping shared by run() and the scout: persist last_timed.json, save the variant as a
    regression case, cache GM-verified closed-vocab labels (from ANY attempt, not only correct ones), record a
    correct result locally. Returns correct | expired | blocked | error:<x>."""
    r = str(res.get("result", "")).lower()
    detail = str(res.get("detail", ""))
    if (r == "exec_error" and "solve.py" in detail and ("timed out" in detail or "TimeoutExpired" in detail)
            and not res.get("clock_short")):
        res["solver_too_slow"] = True  # set BEFORE _remember: the timed stage reads it from last_timed.json
    log(f"[{cid}] timed: {json.dumps({k: res.get(k) for k in ('result', 'remaining', 'elapsed', 'window', 'routed', 'missing', 'partial_submit', 'per_set', 'bad_sets', 'wrong', 'fixed', 'attempt_id') if k in res})}")
    pull = res.pop("_pull", None)

    def capture():
        try:
            if pull:
                # The NEXT mode's attempt starts ~1-4 s after this one returns (TT pass -> Mastery): a capture that
                # checked right away saw an idle VPN and then competed with that kickoff (D8 binary: 31 MB TT pull
                # beside Mastery). Give it the grace to start, then wait until no attempt is in flight.
                time.sleep(CAPTURE_GRACE)
                wait_idle()   # don't share the ~130 KB/s VPN with another attempt's solver push / downloads
                pull()  # Homebase pass: bring the attempt's bytes back first (off the critical path)
            case = capture_case(cid, Path(solver_dir), res)
            if case:
                log(f"[{cid}] saved this variant as regression case {case} ({len(res.get('verified') or res.get('submitted') or {})} GM-verified answers)")
        except Exception as e:  # noqa: BLE001 - capture is best-effort
            log(f"[{cid}] variant capture note: {e}")
    try:
        _remember(cid, res)
    except Exception as e:  # noqa: BLE001
        log(f"[{cid}] last_timed note: {e}")
    if r != "correct":
        _keep_failed_attempt(cid, res, log)
    if pull:
        import threading
        threading.Thread(target=capture, daemon=True).start()
    else:
        capture()
    if r != "correct" and res.get("verified"):
        # A failed attempt still carries GM-verified labels (accepted sets, localized subsets, in-window fixes):
        # cache them now so the next variant's in-window corrector already knows the spelling.
        try:
            from . import labels
            labels.record_values(cid, res["verified"], log=log)
        except Exception as e:  # noqa: BLE001
            log(f"[{cid}] label cache note: {e}")
    if r == "correct":
        # Record the confirmed answers + a correct submission locally (the timed runner submits to the GM
        # directly), so cli.is_complete and the dashboard reflect reality.
        cli.record_remote_result(cid, res.get("attempt_id"), res.get("submitted") or {}, "correct", res.get("detail"))
        # Promote any newly-confirmed closed-vocab labels (e.g. a VBScript control form the single never saw)
        # into vocab.json, so the in-window corrector fixes the same construct next time without generalizing.
        try:
            from . import labels
            labels.record_from_confirmed(cid, log=log)
        except Exception as e:  # noqa: BLE001 - label caching is best-effort
            log(f"[{cid}] label cache note: {e}")
        return "correct"
    if cli.is_complete(cid):
        return "correct"
    if "prerequisite" in r:   # GM 409 prerequisite_required: the previous mode's LATEST attempt isn't CORRECT
        return "error:prerequisite"
    if res.get("gm_rate_limited") or "rate_limited" in r:
        return "error:rate"    # GM 429 on start/download: transient -- back off and retry, never generalize
    if "rotation_exhausted" in r:
        return "error:exhausted"   # GM: no more variants for this mode today -- terminal; a generalize can't help
    if r == "no_answer_ids":
        det = res.get("detail") if isinstance(res.get("detail"), dict) else {}
        if str(det.get("result", "")).upper() == "CORRECT" and cli.gm_latest_correct(cid):
            # start/retry handed back a FINISHED attempt the GM judged CORRECT: a submit that timed out on our side was
            # judged late (rehearsal blind D8: binary TT submit took 4.4 s -> "expired", then this; ~20 s + 1 ranked attempt
            # spent re-rolling). The GM's latest attempt is the pass: record it.
            log(f"[{cid}] the GM judged the previous attempt CORRECT after our submit timed out: counting the pass")
            cli.record_remote_result(cid, det.get("attempt_id"), {}, "correct", det)
            return "correct"
        return "error:exec"    # the GM gave no live task (nothing for a solver to fix): retry, never generalize
    if r == "exec_error":
        if res.get("solver_too_slow"):
            # The SOLVER blew the clock (alt rehearsals: warmups solve.py >4.6s on 28 Mastery sets, on Homebase AND
            # local, twice). Retrying can't help -- it needs a faster solver: generalize with that diagnosis.
            return "blocked"
        return "error:exec"    # the RUNNER failed (ssh/VPN gap/kickoff), not the solver: retry, never generalize
    if r in ("solver_incomplete", "solver_error", "incorrect", "accepted"):
        return "blocked"       # the solver needs work; caller will generalise offline then retry
    if r in ("expired", "start_required") or "expired" in r:
        return "expired"
    if res.get("start_refused") or (not res.get("attempt_id") and not res.get("phases")):
        # The GM refused to hand out an attempt (Day 8: 503 training_rotation_invalid on the regular pool) or the
        # solver never ran: nothing for a generalize worker to fix (6 useless workers on Day 8). Back off and retry.
        return "error:start"
    return "blocked"
