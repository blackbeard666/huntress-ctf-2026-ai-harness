"""Retrieval of past solves by challenge fingerprint (CTFAgent, CCS 2025: +80% from retrieving technique knowledge;
SageCTF's DEF CON 2026 near-misses were blamed on missing writeup retrieval).

Fingerprint = tokens of the contract (prompt + questions + answer formats), the artifact names, and the "## Artifacts"
section of triage.md (file types, magic, extracted members, recognized codecs). Similarity = cosine over binary
IDF-weighted token vectors, so rare shared tokens (`autoit`, `hermes`, `pyinstaller`, `evtx`) dominate common ones.

  * index:  reference/solutions_index.json, rebuilt by `hctf solutions` and in the background at every `hctf run`
  * query:  top-k past challenges for a live challenge -> a prompt block (single + generalize) and a ranking for the
            reuse race's solver selection (solvers.reuse_plan(rank=...))
Stdlib only; never raises into the caller (best effort everywhere).
"""
import json
import math
import re
import threading
from pathlib import Path

from . import paths

ROOT = paths.ROOT
INDEX = ROOT / "reference" / "solutions_index.json"
TOKEN_RE = re.compile(r"[a-z][a-z0-9_+]{2,29}")
STOP = set("""the and for with that this from are was were which what when where who how its into your you our not
but all any can each per one two has have had out use used uses using via then than them they their there these those
been being will would should could does did done answer answers question questions value values format formats string
strings field fields file files artifact artifacts give return provide exact exactly name names number numbers first
last only also more most some such other same set sets case cases line lines text data bytes byte list item items
single solve solved mode time trial mastery challenge challenges submit submitted lowercase uppercase hex decimal
integer json null none true false norm normalization syntax accepted accept fmt one_of member members""".split())
_lock = threading.Lock()
_cache = {"mtime": None, "rows": None}


def tokens(text):
    out = set()
    for t in TOKEN_RE.findall((text or "").lower()):
        if t in STOP or t.isdigit() or re.fullmatch(r"[0-9a-f]{8,}", t) or re.fullmatch(r"d\d\d.*", t):
            continue
        out.add(t)
    return out


def _load(p):
    try:
        return json.loads(Path(p).read_text())
    except (OSError, ValueError):
        return None


def _contract_text(c):
    c = c or {}
    parts = [str(c.get("prompt") or "")]
    for q in c.get("questions") or []:
        if isinstance(q, dict):
            parts.append(str(q.get("question") or ""))
            fmt = q.get("answer_format") or {}
            if isinstance(fmt, dict):
                parts.append(" ".join(str(v) for v in (fmt.get("accepted_values") or [])[:40]))
    return "\n".join(parts)


def _artifact_section(triage_md):
    try:
        t = Path(triage_md).read_text(errors="replace")
    except OSError:
        return ""
    i = t.find("## Artifacts")
    if i < 0:
        return ""
    return t[i:i + 12000]


def _artifact_names(mode_dir):
    latest = Path(mode_dir) / "artifacts" / "latest"
    try:
        return " ".join(p.name for p in latest.iterdir())
    except OSError:
        return ""


def fingerprint(mode_dir, contract=None, with_triage=True):
    mode_dir = Path(mode_dir)
    c = contract or _load(mode_dir / "start.json") or _load(mode_dir / "contract.json") or {}
    text = _contract_text(c) + "\n" + _artifact_names(mode_dir).replace(".", " ").replace("_", " ")
    if with_triage:
        text += "\n" + _artifact_section(mode_dir / "triage.md")
    return tokens(text)


def _concept(chal):
    """What THIS challenge was + how it was solved. Cumulative lanes copy NOTES.md forward day to day, so its first
    lines describe the lane's first day: prefer the challenge's own prompt and the NOTES lines naming its own day."""
    notes = chal / "solver" / "NOTES.md"
    try:
        text = notes.read_text(errors="replace")
    except OSError:
        text = ""
    lines = []
    c = _load(chal / "single_solve" / "start.json") or _load(chal / "single_solve" / "contract.json") or {}
    if c.get("prompt"):
        lines.append("Prompt: " + " ".join(str(c["prompt"]).split())[:240])
    dm = re.match(r"day(\d+)$", chal.parent.name)
    if dm and text:
        n = int(dm.group(1))
        tag = re.compile(rf"\b(?:d0?{n}|day[ _-]?0?{n})\b", re.I)
        own = [ln.strip()[:220] for ln in text.splitlines() if tag.search(ln) and len(ln.strip()) > 20]
        lines += own[:4]
    if len(lines) >= 3:
        return lines[:5]
    body = text
    if text.startswith("---"):
        end = text.find("\n---", 3)
        body = text[end + 4:] if end >= 0 else text
    for ln in body.splitlines():
        s = ln.strip()
        if s and not s.startswith("```") and not s.startswith("|---"):
            lines.append(s[:200])
        if len(lines) >= 5:
            break
    if len(lines) <= 1:   # no NOTES.md: the solver's module docstring
        try:
            src = (chal / "solver" / "solve.py").read_text(errors="replace")
            m = re.search(r'^\s*(?:#!.*\n)?\s*[ru]?"""(.*?)"""', src, re.S)
            if m:
                lines = [s.strip()[:200] for s in m.group(1).strip().splitlines() if s.strip()][:6]
        except OSError:
            pass
    return lines


def build_index(write=True):
    """Every challenges/dayNN/<chal>/ with a solver/solve.py -> one row. Returns the rows."""
    rows = []
    for solve in sorted(paths.CHALLENGES.glob("day*/*/solver/solve.py")):
        chal = solve.parent.parent
        meta = _load(chal / "meta.json") or {}
        chain = _load(chal / "chain.json") or {}
        toks = fingerprint(chal / "single_solve")
        if not toks:
            continue
        notes = chal / "solver" / "NOTES.md"
        rows.append({"day": chal.parent.name, "dir": chal.name, "lane": meta.get("lane", ""),
                     "name": meta.get("name") or chain.get("name", ""),
                     "solver": str(solve.parent.relative_to(ROOT)),
                     "notes": str(notes.relative_to(ROOT)) if notes.exists() else "",
                     "summary": _concept(chal), "tokens": sorted(toks)})
    if write:
        INDEX.parent.mkdir(parents=True, exist_ok=True)
        tmp = INDEX.with_suffix(".tmp")
        tmp.write_text(json.dumps({"rows": rows}, indent=1, ensure_ascii=False))
        tmp.replace(INDEX)
    with _lock:
        _cache["rows"], _cache["mtime"] = rows, (INDEX.stat().st_mtime if INDEX.exists() else None)
    return rows


def build_async(log=None):
    def go():
        try:
            n = len(build_index())
            if log:
                log(f"retrieval index: {n} past challenge(s) -> {INDEX.relative_to(ROOT)}")
        except Exception as e:  # noqa: BLE001
            if log:
                log(f"retrieval index note: {e}")
    t = threading.Thread(target=go, name="retrieval-index", daemon=True)
    t.start()
    return t


def rows():
    with _lock:
        try:
            m = INDEX.stat().st_mtime
        except OSError:
            m = None
        if _cache["rows"] is not None and _cache["mtime"] == m:
            return _cache["rows"]
    data = _load(INDEX) or {}
    r = data.get("rows") or []
    with _lock:
        _cache["rows"], _cache["mtime"] = r, m
    return r


def _idf(rs):
    df = {}
    for r in rs:
        for t in r["tokens"]:
            df[t] = df.get(t, 0) + 1
    n = max(len(rs), 1)
    return {t: math.log(1 + n / c) for t, c in df.items()}, math.log(1 + n)


def query(q_tokens, lane=None, exclude=(), k=3, min_score=0.12):
    """[(score, row)] best first. `exclude`: challenge dir names to skip (today's own). Same lane gets a 1.2x bonus."""
    rs = [r for r in rows() if r["dir"] not in set(exclude)]
    if not rs or not q_tokens:
        return []
    idf, unseen = _idf(rs)
    qw = {t: idf.get(t, unseen) for t in q_tokens}
    qn = math.sqrt(sum(w * w for w in qw.values()))
    out = []
    for r in rs:
        rt = set(r["tokens"])
        dot = sum(qw[t] * qw[t] for t in rt & qw.keys())
        if not dot:
            continue
        rn = math.sqrt(sum(idf.get(t, unseen) ** 2 for t in rt))
        s = dot / (qn * rn) if qn and rn else 0.0
        boost = 1.2 if lane and r.get("lane") == lane else 1.0
        if s >= min_score:
            out.append((s * boost, round(s, 3), r))
    out.sort(key=lambda x: (x[0], x[2]["day"]), reverse=True)
    return [(s, r) for _, s, r in out[:k]]


def note_for(mode_dir, lane, chal_dir_name, k=3):
    """Prompt block: the k most similar past solves (or "" when nothing is similar enough)."""
    try:
        hits = query(fingerprint(mode_dir), lane=lane, exclude=(chal_dir_name,), k=k)
    except Exception:  # noqa: BLE001 - advisory
        return ""
    if not hits:
        return ""
    out = ["", "## Similar past solves (retrieved by artifact/question similarity -- leads, not answers)"]
    for s, r in hits:
        where = r["notes"] or r["solver"]
        out.append(f"- **{r['day']} {r['dir']}** ({r['lane']}, similarity {s:.2f}) -- `{where}`")
        for ln in r.get("summary", [])[:5]:
            out.append(f"    {ln}")
    out.append("Open a hit's NOTES.md / solve.py only if its technique matches what you see in the bytes; "
               "never reuse its values.")
    return "\n".join(out)


def solver_rank(mode_dir, lane, contract=None):
    """{solver dir (abs Path): score} for the reuse race (contract + artifact names: triage isn't ready yet)."""
    try:
        hits = query(fingerprint(mode_dir, contract, with_triage=False), lane=lane, k=50, min_score=0.0)
    except Exception:  # noqa: BLE001
        return {}
    return {(ROOT / r["solver"]).resolve(): s for s, r in hits}
