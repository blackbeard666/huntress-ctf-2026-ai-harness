#!/usr/bin/env python3
"""Measure ATT&CK coverage/generalization for a given day's solves.

Run:  python3 -m lib.refs.coverage <DAY>     (e.g. 6)

Reports, from that day's challenges/dayNN/*/*/confirmed.json + submissions.jsonl:
  1) reference completeness  — % of *-attack values that are valid ATT&CK ids (did the reference cover them?)
  2) vocabulary overlap      — % of unique ids already in lib/knowledge.py's confirmed role/scenario tables
                               (high => the technique vocab is stable, so the role tables transfer)
  3) novel ids               — attack ids NOT yet in our tables (where the reference fallback / LLM earns its keep)
  4) first-try resolution    — % of *-attack fields that were CORRECT with no prior 'incorrect' submission
                               (the real "did we resolve it deterministically / without burning tries" signal)
This is the generalization gate: run it after a new day solves to decide whether to expand to more taxonomies.
"""
import json
import re
import sys
from pathlib import Path

from . import attack

ROOT = Path(__file__).resolve().parents[2]
TID = re.compile(r"T\d{4}(\.\d{3})?")


def _known_ids():
    from lib import knowledge as K
    ids = set()
    # Every *_ROLE_ATTACK_CONFIRMED table, discovered (a hard-coded list missed Day 6's new Bash table).
    tables = ["SCENARIO_ATTACK"] + sorted(n for n in dir(K) if n.endswith("_ROLE_ATTACK_CONFIRMED"))
    for t in tables:
        ids |= {v for v in getattr(K, t, {}).values() if v != "none"}
    return ids


def _flat(o, out):
    if isinstance(o, dict):
        for k, v in o.items():
            if isinstance(v, (dict, list)):
                _flat(v, out)
            elif isinstance(v, str):
                out[k] = v
    elif isinstance(o, list):
        for v in o:
            _flat(v, out)


def measure(day):
    tag = f"day{int(day):02d}"
    conf_files = sorted((ROOT / "challenges" / tag).glob("*/*/confirmed.json"))
    if not conf_files:
        print(f"no confirmed.json under challenges/{tag} yet — solve the day first.")
        return 1
    attack_fields = {}  # answer_id -> value (last seen)
    for f in conf_files:
        try:
            d = json.loads(f.read_text())
        except ValueError:
            continue
        ans = {}
        _flat(d, ans)
        for k, v in ans.items():
            if k.endswith("-attack") or TID.fullmatch(str(v).strip()):
                attack_fields[f"{f.parent.parent.name}/{f.parent.name}:{k}"] = str(v).strip()

    vals = [v for v in attack_fields.values() if v.lower() != "none"]
    uniq = sorted(set(vals))
    if not vals:
        print(f"{tag}: no ATT&CK fields found.")
        return 0
    known = _known_ids()
    valid = [v for v in uniq if attack.is_valid(v)]
    unknown = [v for v in uniq if not attack.info(v)]
    novel = [v for v in uniq if v not in known and attack.info(v)]

    print(f"=== {tag} ATT&CK coverage ({len(vals)} fields, {len(uniq)} unique ids) ===")
    print(f"[1] reference completeness : {len(valid)}/{len(uniq)} unique ids valid "
          f"({100*len(valid)//len(uniq)}%)" + (f"  UNKNOWN: {unknown}" if unknown else ""))
    print(f"[2] vocabulary overlap     : {len(uniq)-len(novel)-len(unknown)}/{len(uniq)} already in knowledge.py tables")
    print(f"[3] novel ids (fallback)   : {novel or 'none'}")
    for t in novel:
        print(f"      {t}  {attack.name(t)}  tactics={attack.tactics(t)}  (add a confirmed role mapping)")

    # 4) first-try resolution from submissions.jsonl
    first_try = wrong_then_right = 0
    for sub in sorted((ROOT / "challenges" / tag).glob("*/*/submissions.jsonl")):
        try:
            rows = [json.loads(l) for l in sub.read_text().splitlines()]
        except (OSError, ValueError):
            continue
        wrong_fields = set()
        for r in rows:
            if r.get("kind") == "incorrect":
                wrong_fields |= {k for k in r.get("answers", {}) if k.endswith("-attack")}
        for r in rows:
            if r.get("kind") == "correct":
                for k in r.get("answers", {}):
                    if k.endswith("-attack"):
                        if k in wrong_fields:
                            wrong_then_right += 1
                        else:
                            first_try += 1
    tot = first_try + wrong_then_right
    if tot:
        print(f"[4] first-try resolution   : {first_try}/{tot} attack fields correct with no prior wrong "
              f"({100*first_try//tot}%); {wrong_then_right} needed a retry")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: python3 -m lib.refs.coverage <DAY>")
    sys.exit(measure(sys.argv[1]))
