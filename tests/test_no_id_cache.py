#!/usr/bin/env python3
"""Lint: no cache keyed on a bare id() in lib/ or any challenge solver (D25 post-mortem, Track A1).

D25 binary Mastery failed its first try (46 fields): the solver cached facts in module dicts keyed on id(member bytes).
A Homebase pool process (2 vCPUs) solves several sets in turn; a freed member's address came back as the next set's
member, which read the earlier set's facts. The detector is hctf.solvers.id_cache_findings (also run by the single /
generalize stop gate and `hctf solver-test`): a lookup keyed on id(...) in a container that outlives the call (module
global or attribute) is unsafe unless the function checks `entry[0] is obj`. Reviewed exceptions: `# id-cache-ok`.

Run:  source bin/env.sh && python3 tests/test_no_id_cache.py      (exit 0 = all pass)
"""
import sys
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from hctf import solvers  # noqa: E402

failures = []


def check(name, cond, detail=""):
    print(("ok  " if cond else "FAIL ") + name + ("" if cond else f"  -- {detail}"))
    if not cond:
        failures.append(name)


def found(src):
    return solvers.id_cache_findings(textwrap.dedent(src))


# --- the detector itself
check("D25 pattern: module dict, `id(x) not in` + `[id(x)]` read -> flagged", len(found('''
    _FACTS = {}
    def facts(data):
        if id(data) not in _FACTS:
            _FACTS[id(data)] = _facts(data)
        return _FACTS[id(data)]
    ''')) == 2)
check("module dict .get(id(b)) -> flagged", len(found('''
    _SHA = {}
    def sha(b):
        return _SHA.get(id(b)) or h(b)
    ''')) == 1)
check("tuple key holding id() -> flagged", len(found('''
    _CFG, _A = {}, {}
    def cfg(b, mg):
        return _CFG[("ov", id(b), mg)]
    ''')) == 1)
check("attribute cache self._c[id(x)] -> flagged", len(found('''
    class C:
        def get(self, x):
            return self._c[id(x)]
    ''')) == 1)
check("identity-verified (obj, value) entry -> clean", found('''
    _ZIPS = {}
    def _memo(cache, b, make):
        e = cache.get(id(b))
        if e is None or e[0] is not b:
            e = cache[id(b)] = (b, make())
        return e[1]
    def memo2(b):
        e = _ZIPS.get(id(b))
        if e is None or e[0] is not b:
            e = _ZIPS[id(b)] = (b, 1)
        return e[1]
    ''') == [])
check("a plain `x is None` does not excuse a global id() lookup", len(found('''
    _F = {}
    def answer(b, v):
        if v is None:
            return _F.get(id(b))
    ''')) == 1)
check("function-local dict keyed on id() (objects alive for the call) -> clean", found('''
    def walk(info):
        byp, seen = {id(x): x for x in info}, set()
        for x in info:
            if id(x) not in seen:
                seen.add(id(x))
            byp[id(x)]
    ''') == [])
check("a local shadowing a module name is local", found('''
    seen = set()
    def f(xs):
        seen = set()
        return [x for x in xs if id(x) not in seen]
    ''') == [])
check("`# id-cache-ok` pragma -> clean", found('''
    _K = {}
    def f(x):
        return _K[id(x)]   # id-cache-ok: _K pins its keys for the process lifetime
    ''') == [])
check("unparsable source -> [] (never raises)", solvers.id_cache_findings("def (:") == [])

# --- the stop-gate hook reports it per solver dir
import tempfile  # noqa: E402
with tempfile.TemporaryDirectory() as td:
    (Path(td) / "solve.py").write_text("_F = {}\ndef f(b):\n    return _F[id(b)]\n")
    (Path(td) / "make_cases.py").write_text("_F = {}\ndef f(b):\n    return _F[id(b)]\n")
    probs = solvers.id_cache_problems(td)
    check("id_cache_problems: solve.py flagged with file:line, case generators skipped",
          len(probs) == 1 and probs[0].startswith("solve.py:3:"), probs)

# --- the tree: lib/ and every challenge solver
files = sorted(ROOT.glob("lib/**/*.py")) + sorted(ROOT.glob("challenges/day*/*/solver/*.py"))
files = [f for f in files if not f.name.startswith(("make_", "test_", "gen_"))]
bad = []
for f in files:
    src = f.read_text(errors="replace")
    if "id(" in src:
        bad += [f"{f.relative_to(ROOT)}:{ln}: {text}" for ln, text in solvers.id_cache_findings(src, f.name)]
check(f"no unsafe id()-keyed cache in lib/ + challenge solvers ({len(files)} files)", not bad, "\n  " + "\n  ".join(bad[:20]))

if failures:
    print(f"\n{len(failures)} FAILED: {failures}")
    sys.exit(1)
print("\nall id-cache lint checks passed")
