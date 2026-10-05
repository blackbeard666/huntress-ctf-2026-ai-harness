"""Solver library: lookup, dispatch, regression cases.

Solver contract (every challenge, every mode):
  challenges/dayNN/<lane>-<title>/solver/solve.py --contract <contract.json> --artifacts <dir>
    -> prints JSON {answer_id: value} on stdout for every question it can answer.
  The contract is the GM start/status body: questions[] (id, question, artifact, answer_format,
  normalization, set) aligned with answer_ids[]. Solvers must read inputs from the contract and the
  artifact bytes, never hard-code values: Time Trial / Mastery hand out different variants.

Regression cases: .../solver/cases/<case>/{contract.json, artifacts/, expected.json}
  expected.json holds only answers the GM confirmed (CORRECT/accepted).
"""
import difflib
import json
import os
import re
import shutil
import subprocess
import time
from pathlib import Path

from .paths import ROOT, TMP, VENV_PY, all_solver_dirs, base_id, mode_of, solver_dir  # noqa: F401 (re-exported)


def _norm(text):
    return re.sub(r"\s+", " ", re.sub(r"\d+", "#", (text or "").lower())).strip()


def question_index():
    """normalized question text -> solver dir, built from every solver's regression cases."""
    idx = {}
    for sdir in all_solver_dirs():
        for contract in sdir.glob("cases/*/contract.json"):
            for q in json.loads(contract.read_text()).get("questions", []):
                idx.setdefault(_norm(q.get("question")), sdir)
    return idx


def paired_questions(contract):
    """[(answer_id, question)]: exact question id, else the question id the answer id ends with (bundles like
    answer_ids slot0_marker..slot3_marker sharing one 'marker' question), else by position."""
    ids, qs = contract.get("answer_ids", []), contract.get("questions", [])
    out = []
    for i, aid in enumerate(ids):
        q = next((q for q in qs if q.get("id") == aid), None)
        if q is None:
            sufs = [q for q in qs if q.get("id") and re.search(rf"(^|[._-]){re.escape(q['id'])}$", aid)]
            q = max(sufs, key=lambda q: len(q["id"]), default=None)
        if q is None and i < len(qs):
            q = qs[i]
        out.append((aid, q or {}))
    return out


def dispatch(contract, default_solver=None):
    """Group the contract's answer_ids by the solver that should answer them.
    Returns ({solver_dir: [answer_id, ...]}, [unmatched answer_ids])."""
    idx = question_index()
    keys = list(idx)
    # The challenge's own solver wins for questions its cases cover: identical wording is reused across days for a
    # different artifact type (Day 4 VBScript "Recover the primary MITRE ATT&CK technique ID, or none." = Day 3 Batch).
    own = set()
    if default_solver is not None:
        for c in Path(default_solver).glob("cases/*/contract.json"):
            own.update(_norm(q.get("question")) for q in json.loads(c.read_text()).get("questions", []))
    groups, unmatched = {}, []
    for aid, q in paired_questions(contract):
        n = _norm(q.get("question"))
        sdir = default_solver if n in own else idx.get(n)
        if sdir is None and keys:
            close = difflib.get_close_matches(n, keys, n=1, cutoff=0.85)
            sdir = idx[close[0]] if close else None
        sdir = sdir or default_solver
        if sdir is None:
            unmatched.append(aid)
        else:
            groups.setdefault(sdir, []).append(aid)
    return groups, unmatched


def sub_contract(contract, answer_ids):
    """The contract restricted to some answer_ids (lets one bundle be split across several solvers)."""
    ids = contract.get("answer_ids", [])
    qs = contract.get("questions", [])
    if len(ids) == len(qs) and all(q.get("id") in (None, a) for a, q in zip(ids, qs)):
        keep = [i for i, a in enumerate(ids) if a in answer_ids]
        c = dict(contract)
        c["answer_ids"] = [ids[i] for i in keep]
        c["questions"] = [qs[i] for i in keep if i < len(qs)]
        return c
    # answer_ids and questions not 1:1 (shared questions) -> keep the ids plus the questions they reference
    c = dict(contract)
    c["answer_ids"] = [a for a in ids if a in answer_ids]
    used = [id(q) for a, q in paired_questions(contract) if a in answer_ids]
    c["questions"] = [q for q in qs if id(q) in used]
    return c


def run_solver(sdir, contract, artifacts, timeout=120):
    """Run one solver. Returns (answers dict, error string or None, seconds)."""
    if not (Path(sdir) / "solve.py").exists():
        return {}, f"no solver yet at {Path(sdir).relative_to(ROOT)}/solve.py", 0.0
    tmp = TMP / f"contract-{sdir.parent.name}-{time.time_ns()}.json"
    tmp.write_text(json.dumps(contract))
    py = str(VENV_PY) if VENV_PY.exists() else "python3"
    env = dict(os.environ)
    env["PYTHONPATH"] = f"{ROOT}:{env.get('PYTHONPATH', '')}"  # solvers can `import lib.*`
    t0 = time.time()
    try:
        r = subprocess.run([py, str(sdir / "solve.py"), "--contract", str(tmp), "--artifacts", str(artifacts)],
                           capture_output=True, text=True, timeout=timeout, cwd=sdir, env=env)
    except subprocess.TimeoutExpired:
        return {}, f"timeout after {timeout}s", time.time() - t0
    finally:
        tmp.unlink(missing_ok=True)
    dt = time.time() - t0
    if r.returncode:
        return {}, f"exit {r.returncode}: {r.stderr.strip()[-1500:]}", dt
    try:
        out = json.loads(r.stdout.strip().splitlines()[-1])
        return {k: str(v) for k, v in out.items()}, None, dt
    except (IndexError, ValueError):
        return {}, f"stdout is not JSON: {r.stdout[-500:]!r} stderr: {r.stderr[-800:]}", dt


def _day_key(sdir):
    m = re.search(r"day(\d+)", str(sdir))
    return int(m.group(1)) if m else -1


def whole_contract_solver(contract, artifacts, candidates, timeout=120):
    """The first candidate solver (NEWEST day first) that answers EVERY answer_id of the FULL contract, as
    (solver_dir, answers), else (None, {}). Question-text dispatch splits a compound bundle across days because
    question wording repeats (Day 4 'Dim and Dimmer' = Day 3 batch questions + VBScript): the Day 4 solver handles all
    231 ids on the whole contract but only 20/46 on its slice, so reuse-first missed and an LLM worker re-solved it."""
    ids = contract.get("answer_ids") or []
    for sdir in sorted(set(candidates), key=_day_key, reverse=True):
        got, err, _ = run_solver(sdir, contract, artifacts, timeout)
        if not err and ids and all(got.get(a) not in (None, "") for a in ids):
            return sdir, {a: got[a] for a in ids}
    return None, {}


def solve_contract(contract, artifacts, default_solver=None, timeout=120, try_whole=True):
    """Dispatch a whole contract across solvers. Returns (answers, problems list).
    When dispatch splits the bundle across several solvers, first try each of them on the FULL contract."""
    groups, unmatched = dispatch(contract, default_solver)
    if try_whole and len(groups) > 1:
        _, got = whole_contract_solver(contract, artifacts, list(groups), timeout)
        if got:
            return got, []
    answers, problems = {}, [f"{a}: no solver matches this question" for a in unmatched]
    for sdir, aids in groups.items():
        got, err, _ = run_solver(sdir, sub_contract(contract, aids), artifacts, timeout)
        if err:
            problems.append(f"{sdir.relative_to(ROOT)}: {err}")
        for a in aids:
            if a in got and got[a] != "":
                answers[a] = got[a]
            elif not err:
                problems.append(f"{a}: solver {sdir.name} returned no answer")
    return answers, problems


def add_case(sdir, name, contract, artifacts, expected):
    """Save a regression case (variant) into the solver's cases/ directory."""
    case = Path(sdir) / "cases" / name
    if case.exists():
        shutil.rmtree(case)
    (case / "artifacts").mkdir(parents=True)
    for f in Path(artifacts).iterdir():
        if f.is_file() and f.name not in ("manifest.json", "contract.json", "result.json"):
            shutil.copy2(f, case / "artifacts" / f.name)
    (case / "contract.json").write_text(json.dumps(contract, indent=2, ensure_ascii=False))
    (case / "expected.json").write_text(json.dumps(expected, indent=2, ensure_ascii=False))
    return case


def test_solver(sdir, timeout=120):
    """Run the solver on every case. Returns list of {case, ok, seconds, diff/error}."""
    results = []
    for case in sorted((Path(sdir) / "cases").glob("*/")):
        contract = json.loads((case / "contract.json").read_text())
        expected = json.loads((case / "expected.json").read_text()) if (case / "expected.json").exists() else {}
        got, err, dt = run_solver(Path(sdir), contract, case / "artifacts", timeout)
        diff = {k: {"expected": v, "got": got.get(k)} for k, v in expected.items() if got.get(k) != v}
        results.append({"case": case.name, "ok": not err and not diff and bool(expected), "seconds": round(dt, 2),
                        "error": err, "diff": diff, "unverified": not expected})
    return results
