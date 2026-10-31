"""Phase 3 leak gate: fail if the published retrospective pages carry anything private.

Usage: python3 reference/writeup/leakcheck.py <built html or md> [...]
Checks: internal IPs, account / host identifiers, credentials, organizer infra ids, rival team names (from the
captured scoreboard and speed board), GM flags and our non-public account names.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
OURS = {"_blackb3ard_and_friends", "_blackb3ard"}

PATTERNS = {
    "internal ip": r"\b10\.\d{1,3}\.\d{1,3}\.\d{1,3}\b",
    "credentials": r"Bearer\s+[A-Za-z0-9._-]{8,}|pairing_token|gm_pairing|\.ovpn\b",
    "aws ids": r"\bami-[0-9a-f]{8,}|\bi-0[0-9a-f]{8,}|EC2BedrockInvoke",
    "uuid": r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b",
    "homebase ssh user": r"HuntressCTF",
    "personal path": r"/mnt/c/Users|/home/\w+",
    "mobile answer": r"\bANS-[0-9a-fA-F]{16}\b",
    "web proof": r"\bproof_[0-9a-f]{8,}",
    "warmups slug": r"\b[a-z]{3,}-[a-z]{3,}-(?!day-)[a-z]{3,}-\d{2}\b",   # not heading anchors (...-day-17)
}
# Identity-specific patterns (account handles, org, local user, outside-help words) live in an untracked file so the
# public repository never names them: {"label": "regex", ...}. Missing file -> only the generic patterns run.
PRIVATE = os.path.expanduser("~/.config/hctf-writeup/private_patterns.json")
if os.path.exists(PRIVATE):
    PATTERNS.update(json.load(open(PRIVATE)))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
# Harness vocabulary the post may name on purpose (API fields, file names): never a GM answer.
GM_OK = {"accepted_values", "answer_format", "exact_text", "answer_id", "answer_ids", "field_family", "solve.py",
         "expected.json", "contract.json", "chain.json", "vocab.json", "knowledge.py", "playbook.py", "mitre_attack_id",
         "time_trial", "single_solve", "triage.md", "NOTES.md", "HELP.md"}
COMMON = {"crash", "team", "admin", "test", "hacker", "hackers", "ninja", "root", "null", "none", "default", "player",
          "ctf", "huntress", "homebase", "unknown", "anonymous", "solo", "the", "and", "friends", "lane", "web", "binary",
          "script", "mobile", "warmups", "metadata", "solve.py", "master"}


def names():
    out = set()
    sb = json.load(open(os.path.join(DATA, "coursestack", "huntress_scoreboard.json")))
    # only teams that matter for "naming rivals": anyone who scored
    for t in sb["scoreboard"]:
        n = (t.get("group_name") or "").strip()
        if t["total_points"] > 0 and n and n not in OURS and len(n) >= 5 and n.lower() not in COMMON:
            out.add(n)
    for mode in ("time_trial", "mastery"):
        for r in json.load(open(os.path.join(DATA, f"hof_{mode}_leaders.json")))["rows"]:
            n = (r.get("team_name") or "").strip()
            if n and n not in OURS and len(n) >= 5 and n.lower() not in COMMON:
                out.add(n)
    return out


def gm_terms():
    """GM-confirmed / rejected label spellings and concrete values: every identifier-like string in lib/vocab.json,
    lib/knowledge.py and lib/playbook.py (literals, and snake_case tokens inside the playbook's prose)."""
    import ast
    out = set()

    def walk(v):
        if isinstance(v, str):
            out.add(v)
        elif isinstance(v, dict):
            for k, x in v.items():
                walk(x)
        elif isinstance(v, (list, tuple)):
            for x in v:
                walk(x)
    try:
        walk(json.load(open(os.path.join(REPO, "lib", "vocab.json"))))
    except OSError:
        pass
    for name in ("knowledge.py", "playbook.py"):
        try:
            tree = ast.parse(open(os.path.join(REPO, "lib", name), encoding="utf-8").read())
        except OSError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                out.add(node.value)
                out.update(re.findall(r"[A-Za-z0-9]+(?:_[A-Za-z0-9]+)+", node.value))
    ident = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{4,}$")
    return {t for t in out if ident.match(t) and re.search(r"[_.\d]", t) and t not in GM_OK}


def flags():
    out = set()
    days = json.load(open(os.path.join(DATA, "gm_list_by_day.json")))
    for b in days.values():
        for c in (b or {}).get("challenges", []):
            if c.get("flag"):
                out.add(c["flag"])
    return out


def main(paths):
    team_names, fl, terms = names(), flags(), gm_terms()
    bad = 0
    for p in paths:
        text = open(p, encoding="utf-8", errors="replace").read()
        low = text.lower()
        for what, rx in PATTERNS.items():
            for m in re.finditer(rx, text, re.I):
                print(f"LEAK {what}: {p}: …{text[max(0, m.start() - 40):m.end() + 40]!r}")
                bad += 1
        for f in fl:
            if f in text:
                print(f"LEAK flag: {p}: {f}")
                bad += 1
        for t in terms:
            if re.search(r"(?<![\w.-])" + re.escape(t) + r"(?![\w-])", text):
                print(f"LEAK GM label/value: {p}: {t!r}")
                bad += 1
        for n in team_names:
            if re.search(r"(?<![\w-])" + re.escape(n.lower()) + r"(?![\w-])", low):
                print(f"LEAK rival team name: {p}: {n!r}")
                bad += 1
    print(f"leakcheck: {len(paths)} file(s), {len(team_names)} rival names, {len(fl)} flags, {len(terms)} GM terms checked -> "
          f"{'FAIL ' + str(bad) if bad else 'clean'}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
