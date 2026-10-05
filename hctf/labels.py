"""Resolve the GM's exact label for a non-flag field the solver understands but cannot spell.

The GM's labels are generator vocabulary composed from real terms, not analyst synonyms (Day 3: the `.NET` format
was `pe_cli` = container + runtime; `if defined X` was `if_guard` = cmd keyword + the `_guard` ending already
confirmed as `errorlevel_guard`). Guessing synonyms burned ~1.5h. This module ranks candidates the way those
answers were actually found, then probes them one at a time:

  1. labels the GM already confirmed for sibling fields (same field ending, any challenge/day, lib/vocab.json)
  2. artifact term + an ending/beginning seen in those sibling labels   (if -> if_guard)
  3. the artifact terms alone
  4. pairs of artifact terms                                           (pe + cli -> pe_cli)
  5. a beginning seen in sibling labels + an artifact term

Every confirmed label is appended to lib/vocab.json under its field ending, so the next challenge (and the timed
runner's in-attempt correction) starts from it. Flags are never probed.
"""
import json
import re
import time
from collections import Counter
from pathlib import Path

from . import cli, paths

try:
    from lib import playbook
except ImportError:  # lib may not be importable in every context; the resolver still works without the playbook
    playbook = None

VOCAB = paths.ROOT / "lib" / "vocab.json"
FLAG_HINT = re.compile(r"md5|\[0-9a-f\]\{32\}|32 lowercase hex|flag", re.I)


def ending(aid):
    """Field ending that groups sibling fields: 'batch-launcher-control' -> 'control', 'd03_analysis_format' ->
    'format', 'set2.batch-benign-expansion' -> 'expansion'."""
    last = aid.rsplit(".", 1)[-1]
    parts = [p for p in re.split(r"[-_]", last) if p]
    return parts[-1].lower() if parts else last.lower()


def _tokens(s):
    return [t for t in re.split(r"[^A-Za-z0-9]+", s or "") if t]


def _usable(v):
    v = str(v)
    return 0 < len(v) <= 48 and "\n" not in v and not v.startswith(("[", "{")) and not re.fullmatch(r"[0-9a-f]{32}", v)


def load_vocab():
    try:
        return json.loads(VOCAB.read_text())
    except (OSError, ValueError):
        return {}


def record(aid, value):
    """Remember a GM-confirmed label under its field ending (both keys the timed runner and this module read)."""
    vocab = load_vocab()
    for key in {ending(aid), _suffix_key(aid)}:
        if key and value not in vocab.setdefault(key, []):
            vocab[key].append(value)
    VOCAB.write_text(json.dumps(vocab, indent=2, sort_keys=True) + "\n")


def _suffix_key(aid):
    m = re.search(r"([-_][A-Za-z0-9]+)$", aid.rsplit(".", 1)[-1])
    return m.group(1) if m else None


def _question(cid, aid):
    """The question dict for an answer_id, from the saved start.json/contract (for its answer_format)."""
    start = cli.load(cid, "start.json") or cli.load(cid, "contract.json") or {}
    ids = start.get("answer_ids") or [q.get("id") for q in start.get("questions", [])]
    qs = start.get("questions") or []
    if aid in ids and ids.index(aid) < len(qs):
        return qs[ids.index(aid)]
    return {}


def accepted_values(cid, aid):
    """If this field is an enum, the GM HANDS us the closed vocabulary in the contract — no derivation/probing of
    synonyms needed. Returns the accepted_values list, else []."""
    af = _question(cid, aid).get("answer_format") or {}
    return [str(x) for x in af["accepted_values"]] if af.get("kind") == "enum" and af.get("accepted_values") else []


def lane_of(cid):
    """Lane for a challenge id (for the per-lane playbook): the base dir's meta.json, else challenges/index.json."""
    try:
        return json.loads((cli.cdir(cid).parent / "meta.json").read_text()).get("lane")
    except (OSError, ValueError, AttributeError):
        pass
    try:
        idx = json.loads((paths.CHALLENGES / "index.json").read_text())
        base = paths.base_id(cid)
        for e in (idx.values() if isinstance(idx, dict) else idx):
            if isinstance(e, dict) and (e.get("base") == base or e.get("id") == cid):
                return e.get("lane")
    except (OSError, ValueError, AttributeError):
        pass
    return None


def sibling_labels(aid, without=()):
    """Values the GM confirmed for fields with the same ending, across every challenge and day, most common first.
    (Includes the same field from earlier days: a label that recurs is the best first guess.)"""
    want = ending(aid)
    seen = Counter()
    for cf in paths.CHALLENGES.glob("day*/*/*/confirmed.json"):
        try:
            data = json.loads(cf.read_text())
        except ValueError:
            continue
        for answers in data.values():
            if not isinstance(answers, dict):
                continue
            for k, v in answers.items():
                if ending(k) == want and _usable(v):
                    seen[str(v)] += 1
    for key in (want, _suffix_key(aid)):
        for v in load_vocab().get(key or "", []):
            seen[v] += 1
    return [v for v, _ in seen.most_common() if v not in without]


# Field families whose values are generator VOCABULARY (small, closed-ish label sets worth caching in
# vocab.json), as opposed to per-variant derived values (symbol/disassembly/campaign/url/path/adapter/note),
# which must NEVER be cached — the in-attempt corrector reads vocab.json and would try them on other variants.
CACHEABLE_FAMILIES = {"control", "expansion", "format", "representation", "transform",
                      "endianness", "machine", "class", "type"}


def record_from_confirmed(cid, lane=None, log=None):
    """Promote the CLOSED-vocab labels the GM just confirmed (confirmed.json) into vocab.json, so that
      - hb_timed._localize (which reads vocab.json ONLY) can correct the same construct IN-WINDOW next time
        without a single offline generalize cycle, and
      - the resolver/playbook show them as confirmed.
    Only CACHEABLE_FAMILIES are recorded (never per-variant values); enum/mitre fields are skipped (their
    vocab is already in the contract). Returns the [(aid, value)] newly added. This closes the loop that left
    `error_guard` (Day 4 VBScript On-Error control) confirmed-by-the-GM but absent from vocab.json.

    Scans EVERY confirmed attempt (not just the current start.json one): a later attempt can drift start.json
    off the attempt that banked the label, and every value in confirmed.json was GM-accepted, so all are safe."""
    all_conf = cli.load(cid, "confirmed.json") or {}
    conf = {}
    for answers in all_conf.values():
        if isinstance(answers, dict):
            conf.update(answers)
    return record_values(cid, conf, log=log)


def record_values(cid, conf, log=None):
    """Cache GM-VERIFIED {answer_id: value} pairs (from confirmed.json, or the `verified` set of ANY timed attempt,
    correct or not) into vocab.json — closed-vocab families only. Returns the [(aid, value)] newly added."""
    if not conf:
        return []
    existing = {k: set(v) for k, v in load_vocab().items()}
    added = []
    for aid, val in conf.items():
        if ending(aid) not in CACHEABLE_FAMILIES or not _usable(val):
            continue
        af = (_question(cid, aid).get("answer_format") or {})
        if af.get("kind") in ("enum", "mitre_attack_id"):
            continue
        if str(val) in existing.get(ending(aid), set()):
            continue
        record(aid, str(val))
        added.append((aid, str(val)))
    if added and log:
        log(f"[{cid}] recorded {len(added)} confirmed label(s) to vocab.json: "
            + ", ".join(f"{a.rsplit('.', 1)[-1]}={v}" for a, v in added))
    return added


def judged_wrong(cid, aid):
    """Values already judged incorrect for this field in any attempt of this challenge mode."""
    p = cli.cdir(cid) / "submissions.jsonl"
    bad = set()
    if p.exists():
        for line in p.read_text().splitlines():
            try:
                h = json.loads(line)
            except ValueError:
                continue
            if h.get("kind") == "incorrect" and len(h.get("answers", {})) == 1 and aid in h["answers"]:
                bad.add(str(h["answers"][aid]))
    return bad


def candidates(cid, aid, terms=(), solver_value=None, without=(), skip_judged=True, lane=None):
    """Ranked candidate labels. `without`/`skip_judged=False` exist to replay a past field as if unsolved.
    The per-lane playbook (lib/playbook.py) seeds the highest-priority candidates from the field's derivation
    RULE (closed vocab, container+runtime / keyword+ending compounds) and contributes its known-rejected
    spellings to the skip set, so we probe the rule first and never re-probe a proven-wrong label."""
    # Enum fields: the contract's accepted_values ARE the complete allowed set. Use it directly (minus anything
    # already judged wrong) and skip synonym ranking entirely — probing an off-list value only wastes budget.
    av = accepted_values(cid, aid)
    if av:
        bad = judged_wrong(cid, aid) if skip_judged else set()
        if solver_value:
            bad.add(str(solver_value))
        picked = [v for v in av if v not in bad and v not in without]
        if picked:
            return picked
    if lane is None:
        lane = lane_of(cid)
    pb_seed, pb_bad = [], set()
    if playbook is not None and lane:
        pb_seed = playbook.seed_candidates(lane, aid, terms=terms, solver_value=solver_value)
        pb_bad = playbook.rejected(lane, aid)
    sib = sibling_labels(aid, without=without)
    seps = Counter(m for v in sib for m in re.findall(r"[-_]", v))
    sep = seps.most_common(1)[0][0] if seps else "_"
    lower = all(v == v.lower() for v in sib) if sib else True
    heads, tails = [], []
    for v in sib:
        parts = [p for p in re.split(r"[-_]", v) if p]
        if len(parts) >= 2:
            heads.append(parts[0])
            tails.append(parts[-1])
    heads = [h for h, _ in Counter(heads).most_common()]
    tails = [t for t, _ in Counter(tails).most_common()]
    tset = []
    for t in list(terms) + _tokens(solver_value):
        t = t.lower() if lower else t
        if t and t not in tset:
            tset.append(t)
    ranked = []
    ranked += pb_seed                                                   # 0 playbook rule (closed vocab / compounds)
    ranked += sib                                                       # 1 known labels
    ranked += [f"{t}{sep}{x}" for t in tset for x in tails if t != x]   # 2 term + known ending
    ranked += tset                                                      # 3 terms alone
    ranked += [f"{a}{sep}{b}" for a in tset for b in tset if a != b]    # 4 term pairs
    ranked += [f"{h}{sep}{t}" for h in heads for t in tset if h != t]   # 5 known beginning + term
    bad = judged_wrong(cid, aid) if skip_judged else set()
    bad |= pb_bad                                                       # never reprobe a playbook-rejected spelling
    if solver_value:
        bad.add(str(solver_value))
    out = []
    for c in ranked:
        if c and c not in out and c not in bad:
            out.append(c)
    return out


def probe(cid, aid, cands, budget=25, delay=1.0, log=print):
    """Submit candidates one at a time (sequential, rate-limited) until the GM accepts one. Returns a result dict."""
    start = cli.load(cid, "start.json") or {}
    qs = start.get("questions") or []
    ids = start.get("answer_ids") or []
    q = qs[ids.index(aid)] if aid in ids and ids.index(aid) < len(qs) else {}
    if FLAG_HINT.search(json.dumps(q.get("answer_format", ""))):
        return {"accepted": None, "refused": "flag-type field: flags are never probed"}
    if start.get("deadline"):
        log("note: this mode has a clock; prefer resolving labels on the Single Solve")
    prior = len(judged_wrong(cid, aid))
    tried = []
    for c in cands[:budget]:
        kind, body, problems = cli.submit(cid, {aid: c}, max_wrong=prior + budget + 1,
                                          global_cap=cli.GLOBAL_WRONG_CAP + budget)
        if problems:
            tried.append({"value": c, "result": "refused", "why": problems[0]})
            continue
        tried.append({"value": c, "result": kind})
        if kind in ("correct", "accepted"):
            record(aid, c)
            return {"accepted": c, "tried": tried, "recorded_in": str(VOCAB.relative_to(paths.ROOT))}
        if kind not in ("incorrect",):
            break  # expired / error: stop
        time.sleep(delay)
    return {"accepted": None, "tried": tried,
            "hint": "add better --term values (keywords, magic, spec names seen in the bytes) and rerun"}
