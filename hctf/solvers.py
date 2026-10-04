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
    groups, unmatched = {}, []
    for aid, q in paired_questions(contract):
        n = _norm(q.get("question"))
        sdir = idx.get(n)
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


def solve_contract(contract, artifacts, default_solver=None, timeout=120):
    """Dispatch a whole contract across solvers. Returns (answers, problems list)."""
    groups, unmatched = dispatch(contract, default_solver)
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
        if f.is_file() and f.name not in ("manifest.json", "contract.json"):
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
