"""Single source of truth for where things live. Everything stays inside the project root.

challenges/dayNN/<lane>-<title>/            one folder per challenge
    single_solve/ time_trial/ mastery/      per-mode state: contract.json, start.json, artifacts/, notes.md,
                                            submissions.jsonl, confirmed.json, log.jsonl, worker logs
    solver/                                 solve.py + cases/ (regression variants)
    chain.json meta.json                    orchestrator state
challenges/index.json                       challenge id -> folder (rebuilt from every GM list)
.run/                                       runtime only (ssh sockets, locks, tmp, caches, logs); gitignored
secrets/                                    VPN profile, Homebase SSH key; gitignored
tools/                                      toolbox installed by setup/install.sh; gitignored
"""
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHALLENGES = ROOT / "challenges"
INDEX = CHALLENGES / "index.json"
RUN = ROOT / ".run"
LOCKS = RUN / "locks"
TMP = RUN / "tmp"
LOGS = RUN / "logs"
SECRETS = ROOT / "secrets"
TOOLS = ROOT / "tools"
BIN = ROOT / "bin"
VENV_PY = ROOT / ".venv" / "bin" / "python"
MODES = ("single_solve", "time_trial", "mastery")

LANE_SHORT = {
    "welcome": "welcome", "warmups": "warmups", "metadata-forensics": "metadata", "metadata": "metadata",
    "script-analysis": "scripting", "mobile-android": "mobile", "mobile": "mobile",
    "binary-reverse-engineering": "binary", "binary": "binary", "web": "web",
}



def canonical_lane(lane):
    """The harness lane key for a GM `lane` field. Known lanes pass through unchanged (the GM sends long names:
    `mobile-android`, not the API enum's `mobile`); a not-yet-seen web lane (`web`, `web-exploitation`, ...) maps to
    `web`, the key of its skill/persona/technique log. Applied to every `list` reply (cli.call)."""
    lane = (lane or "").strip()
    if lane in LANE_SHORT:
        return lane
    if lane.lower().startswith("web"):
        return "web"
    return lane


for _d in (CHALLENGES, LOCKS, TMP, LOGS):
    _d.mkdir(parents=True, exist_ok=True)


def base_id(cid):
    return re.sub(r"/(time_trial|mastery)$", "", cid)


def mode_of(cid):
    m = re.search(r"/(time_trial|mastery)$", cid)
    return m.group(1) if m else "single_solve"


def slugify(text):
    text = unicodedata.normalize("NFKD", text or "").encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-") or "untitled"


def _load_index():
    return json.loads(INDEX.read_text()) if INDEX.exists() else {}


def register(challenges):
    """Record folders for challenges from a GM list response (idempotent; existing folders never move)."""
    idx = _load_index()
    changed = False
    for c in challenges:
        b = base_id(c["id"])
        if b in idx:
            continue
        day = int(c.get("day") or 0)
        lane = LANE_SHORT.get(c.get("lane", ""), slugify(c.get("lane", "misc")))
        idx[b] = {"dir": f"day{day:02d}/{lane}-{slugify(c.get('name') or c.get('title') or b)}",
                  "day": day, "lane": c.get("lane"), "name": c.get("name")}
        changed = True
    if changed:
        INDEX.write_text(json.dumps(idx, indent=2, ensure_ascii=False, sort_keys=True))
    return idx


def challenge_root(cid):
    """challenges/dayNN/<lane>-<title>/ for any mode id; unknown ids land in challenges/_unsorted/."""
    b = base_id(cid)
    entry = _load_index().get(b)
    d = CHALLENGES / (entry["dir"] if entry else f"_unsorted/{slugify(b)}")
    d.mkdir(parents=True, exist_ok=True)
    return d


def mode_dir(cid):
    d = challenge_root(cid) / mode_of(cid)
    d.mkdir(parents=True, exist_ok=True)
    return d


def solver_dir(cid):
    return challenge_root(cid) / "solver"


def all_solver_dirs():
    return [p.parent for p in CHALLENGES.glob("day*/*/solver/solve.py")]


LANE_SOLVERS = CHALLENGES / "_lane"   # challenges/_lane/<lane>/solver: cumulative, day-less lane solvers (race-only)


def lane_solver_dirs(lane):
    """The lane solver dirs the reuse race runs FIRST for `lane` (never counted against its newest-N slice).
    HCTF_LANE_SOLVERS = comma list of lanes that have one (default metadata-forensics); HCTF_META_LANE_SOLVER=0 drops
    the metadata one. Off = [] = today's behaviour (dated solvers only)."""
    import os
    lanes = {x.strip() for x in os.environ.get("HCTF_LANE_SOLVERS", "metadata-forensics").split(",") if x.strip()}
    if os.environ.get("HCTF_META_LANE_SOLVER", "1") == "0":
        lanes.discard("metadata-forensics")
    if lane not in lanes:
        return []
    d = LANE_SOLVERS / lane / "solver"
    return [d] if (d / "solve.py").exists() else []


def lookup(cid):
    return _load_index().get(base_id(cid))
