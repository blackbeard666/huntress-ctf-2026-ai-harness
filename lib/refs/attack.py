"""MITRE ATT&CK Enterprise lookup — a PUBLIC candidate generator for `*-attack` answer fields.

Data is built from the official MITRE STIX bundle by build_attack.py (attack_data.json). This resolves a
technique id to its canonical name/tactic and maps observed behavior text to candidate ids, so solvers/workers
fill ATT&CK fields deterministically instead of guessing. It is NOT GM ground truth: a candidate here is still
validated by the GM on submit (and cached, once verified, in the GM-only knowledge/vocab layer).
"""
import json
import re
from functools import lru_cache
from pathlib import Path

_DATA = Path(__file__).resolve().parent / "attack_data.json"
_STOP = {"the", "a", "an", "to", "of", "or", "and", "for", "with", "from", "in", "on", "by", "via",
         "is", "are", "be", "as", "that", "this", "it", "its", "may", "can", "use", "used", "using",
         "data", "file", "files", "system", "information", "adversary", "adversaries"}


@lru_cache(maxsize=1)
def _db():
    try:
        return json.loads(_DATA.read_text())
    except (OSError, ValueError):
        return {}


def _norm_id(tid):
    """Canonicalize a technique id: upper-case, strip, tolerate 't1059.7' -> 'T1059.007'."""
    s = str(tid).strip().upper()
    m = re.fullmatch(r"T?(\d{4})(?:\.(\d{1,3}))?", s)
    if not m:
        return s
    return f"T{m.group(1)}" + (f".{int(m.group(2)):03d}" if m.group(2) else "")


def is_valid(tid):
    """True if tid is a known (non-deprecated) ATT&CK technique/sub-technique id."""
    e = _db().get(_norm_id(tid))
    return bool(e) and not e.get("deprecated")


def info(tid):
    """Full record for an id: {name, tactics, desc, deprecated} or None."""
    return _db().get(_norm_id(tid))


def name(tid):
    e = info(tid)
    return e["name"] if e else None


def tactics(tid):
    e = info(tid)
    return e["tactics"] if e else []


@lru_cache(maxsize=1)
def _by_name():
    """Exact canonical-name -> id (lower-cased), so a worker that produced a technique NAME maps to the id."""
    return {v["name"].lower(): k for k, v in _db().items() if not v.get("deprecated")}


def id_for_name(text):
    """Map an exact ATT&CK technique name to its id (case-insensitive), else None."""
    return _by_name().get(str(text).strip().lower())


def _tokens(text):
    return [w for w in re.findall(r"[a-z0-9]+", str(text).lower()) if w not in _STOP and len(w) > 2]


_TID_RE = re.compile(r"T\d{4}(\.\d{3})?")


def looks_like_technique(val):
    """True if a value is shaped like an ATT&CK technique id (so it was meant to be one)."""
    return bool(_TID_RE.fullmatch(str(val).strip()))


def validate_answers(answers, attack_suffix="-attack"):
    """Pre-submit guard. Returns [(answer_id, value, reason)] for answers that are meant to be ATT&CK
    techniques but are NOT valid ids — i.e. an id-shaped value that ATT&CK doesn't know (a hallucination
    or typo the GM would reject, wasting an attempt), or an *-attack field whose non-'none' value isn't a
    technique id at all. Semantically-wrong-but-real ids (e.g. T1005 where T1555.003 was wanted) are NOT
    flagged — only the GM/role-table knows the right one; this catches malformed values, conservatively."""
    bad = []
    for aid, val in (answers or {}).items():
        s = str(val).strip()
        is_attack_field = str(aid).endswith(attack_suffix)
        if looks_like_technique(s):
            if not info(s):  # id-shaped but unknown to ATT&CK -> almost certainly wrong
                bad.append((aid, s, "not a known ATT&CK technique id"))
        elif is_attack_field and s.lower() not in ("none", ""):
            bad.append((aid, s, "attack field value is not an ATT&CK technique id or 'none'"))
    return bad


def audit_knowledge():
    """Validate every ATT&CK id in lib/knowledge.py's confirmed role/scenario tables against this reference.
    Returns [(table, key, id, problem)]; empty = clean. Run as: python3 -m lib.refs.attack"""
    from lib import knowledge as K
    tables = {
        "SCENARIO_ATTACK": getattr(K, "SCENARIO_ATTACK", {}),
        "JSCRIPT_ROLE": getattr(K, "JSCRIPT_ROLE_ATTACK_CONFIRMED", {}),
        "BATCH_ROLE": getattr(K, "BATCH_ROLE_ATTACK_CONFIRMED", {}),
        "VBS_ROLE": getattr(K, "VBS_ROLE_ATTACK_CONFIRMED", {}),
        "PY_ROLE": getattr(K, "PY_ROLE_ATTACK_CONFIRMED", {}),
    }
    bad = []
    for tname, t in tables.items():
        for key, tid in t.items():
            if tid == "none":
                continue
            if not info(tid):
                bad.append((tname, key, tid, "unknown ATT&CK id"))
            elif not is_valid(tid):
                bad.append((tname, key, tid, "deprecated/revoked"))
    return bad


def search(behavior, limit=5, tactic=None):
    """Rank candidate technique ids for a free-text behavior description (e.g. 'downloads a payload over http').
    Scores token overlap against each technique's name (weighted) + description. Optional tactic filter
    (e.g. 'command-and-control'). Returns [(id, name, score), ...] best first — candidates, not an answer."""
    q = set(_tokens(behavior))
    if not q:
        return []
    out = []
    for tid, e in _db().items():
        if e.get("deprecated"):
            continue
        if tactic and tactic not in e.get("tactics", []):
            continue
        nm = set(_tokens(e["name"]))
        ds = set(_tokens(e.get("desc", "")))
        score = 3 * len(q & nm) + len(q & ds)
        if score:
            out.append((tid, e["name"], score))
    out.sort(key=lambda r: (-r[2], r[0]))
    return out[:limit]


if __name__ == "__main__":
    import sys
    _problems = audit_knowledge()
    if _problems:
        for _p in _problems:
            print("INVALID:", *_p)
        sys.exit(1)
    print(f"ATT&CK knowledge audit: all confirmed ids valid ({len(_db())} ids in reference)")
