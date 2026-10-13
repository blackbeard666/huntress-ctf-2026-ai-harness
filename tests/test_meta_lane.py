"""Metadata lane solver + lib.meta registry (offline: no GM / no Homebase / no workers).

  0) baseline: the GM-verified day solvers lib.meta was copied from (D10 covers D1-D10, D11, D12, D13) still pass
     their own days' verified cases -- the copy's source of truth is green
  1) EVERY metadata regression case D1..today through solvers.run_solver with the lane solver: every value it emits
     for a registered field matches expected.json exactly, < 1 s per case. A field lib.meta has no entry for is a
     coverage GAP (reported; fails only with HCTF_META_STRICT=1) -- the ratchet folds a new day's field in tonight
  2) registry: no prebuilt conflicts, every extractor resolves, verified entries carry days, a prebuilt module can't
     shadow a verified key, HCTF_META_MAX_DAY drops later days, parse_field grammar
  3) spell + alternates (GM-rejected spellings never offered)
  4) reuse_plan runs the lane solver FIRST (outside the newest-N slice), not at all with HCTF_META_LANE_SOLVER=0;
     verified-field confidence keyed on (fmt, field), synthetic cases never count
  5) _race_snapshot with the lane solver as the seed (the .run/spec-dayNN/<chal>-race copy runs: parents[4] root)
  6) prebuilt fixtures (tests/data/meta_fixtures) through lib.meta.answer + prebuilt module structure

Run:  source bin/env.sh && python3 tests/test_meta_lane.py      (exit 0 = all pass)
"""
import json
import os
import shutil
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
for k in ("HCTF_META_MAX_DAY", "HCTF_META_LANE_SOLVER", "HCTF_LANE_SOLVERS", "HCTF_META_PREBUILT"):
    os.environ.pop(k, None)
from hctf import cli, orchestrate, paths, prebuild, solvers  # noqa: E402
from lib import meta  # noqa: E402
from lib.meta import spell  # noqa: E402

LANE = paths.CHALLENGES / "_lane" / "metadata-forensics" / "solver"
VERIFIED = solvers.LANE_VERIFIED_PREFIXES
STRICT = os.environ.get("HCTF_META_STRICT", "0") == "1"


def meta_cases():
    out = []
    for sdir in sorted(paths.all_solver_dirs()):
        if solvers._lane_of(sdir) != "metadata-forensics":
            continue
        for c in sorted((sdir / "cases").glob("*/")):
            if (c / "contract.json").exists() and (c / "expected.json").exists():
                out.append(c)
    return out


def run_case(sdir, case):
    contract = json.loads((case / "contract.json").read_text())
    expected = json.loads((case / "expected.json").read_text())
    got, err, dt = solvers.run_solver(Path(sdir), contract, case / "artifacts", timeout=60)
    return contract, expected, got, err, dt


CASES = meta_cases()
assert len(CASES) >= 49, f"only {len(CASES)} metadata cases found"
assert (LANE / "solve.py").exists() and solvers._lane_of(LANE) == "metadata-forensics"

# 0) baseline: the day solvers the registry was copied from pass their own verified cases
src = {d: next(paths.CHALLENGES.glob(f"day{d:02d}/metadata-*/solver")) for d in (10, 11, 12, 13)}
jobs = [(src[10], c) for c in CASES if solvers._day_key(c) <= 10 and c.name.startswith(VERIFIED)
        and "d8dfe119" not in c.name]   # D2 TT d8dfe119: stale question text, only D2's own hinted lookup reads it
jobs += [(src[d], c) for d in (11, 12, 13) for c in CASES if solvers._day_key(c) == d]
with ThreadPoolExecutor(max_workers=8) as ex:
    base = list(ex.map(lambda j: (j[1], run_case(*j)), jobs))
bad = [(c.relative_to(paths.CHALLENGES), [k for k, v in e.items() if g.get(k) != v][:3], err)
       for c, (_ct, e, g, err, _dt) in base if err or any(g.get(k) != v for k, v in e.items())]
assert not bad, f"baseline day solvers fail their own verified cases: {bad}"
print(f"ok  0) baseline: D10/D11/D12/D13 day solvers pass {len(base)} verified case(s) of D1-D13")

# 1) every metadata case through the lane solver
with ThreadPoolExecutor(max_workers=4) as ex:
    res = list(ex.map(lambda c: (c, run_case(LANE, c)), CASES))
for i, (case, r) in enumerate(res):        # a case over budget under the 4-way load is re-timed alone
    if r[4] > 1.0:
        res[i] = (case, run_case(LANE, case))
fails, gaps, slow, n_vals = [], [], [], 0
for case, (contract, expected, got, err, dt) in res:
    rel = case.relative_to(paths.CHALLENGES)
    if err:
        fails.append(f"{rel}: {err[:300]}")
        continue
    if dt > 1.0:
        slow.append(f"{rel}: {dt:.2f}s")
    qs = dict(solvers.paired_questions(contract))
    for aid, want in expected.items():
        f = meta.parse_field(aid, qs.get(aid) or {})
        ext = meta.lookup(f.fmt, f.field)[0] if f else None
        if aid not in got:
            if ext is None:
                gaps.append(f"{rel}: {aid} ({f and f'{f.fmt}.{f.field}'})")
            else:
                fails.append(f"{rel}: {aid} registered ({f.fmt}.{f.field}) but no answer")
            continue
        n_vals += 1
        if got[aid] != want:
            fails.append(f"{rel}: {aid} = {got[aid]!r}, GM expected {want!r}")
assert not fails, "lane solver mismatches:\n  " + "\n  ".join(fails[:20])
assert not slow, f"lane solver over 1 s: {slow}"
assert not (STRICT and gaps), f"coverage gaps (HCTF_META_STRICT=1): {gaps[:10]}"
days = sorted({solvers._day_key(c) for c in CASES})
print(f"ok  1) lane solver: {len(CASES)} metadata cases D{days[0]}-D{days[-1]}, {n_vals} values exact, 0 wrong, "
      f"max {max(r[1][4] for r in res):.2f}s/case" + (f"; {len(gaps)} coverage gap(s): {gaps[:3]}" if gaps else ""))

# 2) registry
assert not meta.CONFLICTS, f"prebuilt registry conflicts: {meta.CONFLICTS}"
for key, e in meta.REGISTRY.items():
    assert e.tier in (meta.VERIFIED, meta.SPECULATIVE), (key, e)
    assert callable(meta._load(e.fn)), (key, e.fn)
    assert (e.tier == meta.VERIFIED) == bool(e.days), f"{key}: verified entries need days, speculative none ({e})"
    if e.fn.startswith("lib.meta.prebuilt."):
        assert e.tier == meta.SPECULATIVE, f"{key}: prebuilt entries are never verified"
verified_days = sorted({d for e in meta.REGISTRY.values() for d in e.days})
assert verified_days == list(range(1, 14)) or verified_days[:13] == list(range(1, 14)), verified_days
with tempfile.TemporaryDirectory() as d:   # a prebuilt module may not shadow any built-in key
    (Path(d) / "msi.py").write_text('FIELDS = {("msi", "product_code_guid"): "f", ("msi", "package_code_guid"): "g"}\n'
                                    "def f(data, ctx):\n    return 'x'\ndef g(data, ctx):\n    return 'y'\n")
    (Path(d) / "bad.py").write_text('FIELDS = {("msi", "package_code_guid"): "h", "oops": 3}\n')
    saved, saved_conf = meta.PREBUILT_DIR, list(meta.CONFLICTS)
    try:
        meta.PREBUILT_DIR = Path(d)
        extra = meta._load_prebuilt(meta._BUILTIN)
        assert ("msi", "product_code_guid") not in extra and ("msi", "package_code_guid") in extra, extra
        assert extra[("msi", "package_code_guid")].tier == meta.SPECULATIVE
        reasons = [c[2] for c in meta.CONFLICTS[len(saved_conf):]]
        assert any("already registered (verified)" in r for r in reasons), reasons
        assert any("also registered" in r for r in reasons) and any("malformed" in r for r in reasons), reasons
    finally:
        meta.PREBUILT_DIR = saved
        meta.CONFLICTS[:] = saved_conf
# HCTF_META_MAX_DAY: fair runs see no field first verified on/after that day
os.environ["HCTF_META_MAX_DAY"] = "12"
try:
    assert meta.lookup("msi", "product_code_guid")[0] is None and meta.lookup("dotnet", "mvid_guid")[0] is None
    assert meta.lookup("pe", "version_original_filename")[0].tier == meta.VERIFIED
    assert meta.lookup("pe", "version_company_name")[0].tier == meta.SPECULATIVE      # family entry (speculative)
finally:
    del os.environ["HCTF_META_MAX_DAY"]
# parse_field: question grammar (tag stripped), dNN id (reused d09 on D10/D11), suffix + identity forms
P = meta.parse_field
assert P("set1.d13-msi-003-msi-product-code-guid", {"question": "Determine msi.product_code_guid for i.msi."}) \
    == ("msi", "product_code_guid", None)
assert P("x", {"question": "Determine pe.coff_machine_u16_hex for a.exe. [assigned-artifact-sha256:ab12]"})[:2] \
    == ("pe", "coff_machine_u16_hex")
assert P("set2.d09-pe-004-pe-version-original-filename", {})[:2] == ("pe", "version_original_filename")
assert P("evidence-note-text-utf8-bom-present", {})[:2] == ("text", "utf8_bom_present")
assert P("set3.evidence-note-copy-magic-prefix-hex-16", {})[:2] == ("file", "magic_prefix_hex_16")
assert P("evidence-note-copy-sha256", {})[:2] == ("file", "sha256") and P("note-filename", {})[:2] == ("file", "filename")
assert P("d14-cab-001-cab-cfheader-folder-count", {})[:2] == ("cab", "cfheader_folder_count")
assert meta.lookup("file", "magic_prefix_hex_32") == (meta.REGISTRY[("file", "magic_prefix_hex_*")], "32")
assert meta.lookup("pe", "version_file_version")[1] == "file_version"
assert P("totally-unknown", {}) is None and meta.answer("totally-unknown", {}, b"x") == (None, None)
print(f"ok  2) registry: {len(meta.REGISTRY)} entries ({sum(e.tier == meta.VERIFIED for e in meta.REGISTRY.values())} "
      f"verified D1-D13), no conflicts, prebuilt can't shadow verified, MAX_DAY filter, parse_field grammar")

# 3) spell + alternates
H, G, D = spell.Hex, spell.Guid, spell.Dims
assert spell.spell("pe", "coff_machine_u16_hex", H(0x14c, 4)) == "0x014c"
assert spell.spell("pe", "address_of_entry_point_rva_hex", 0x65bd0) == "0x00065bd0"   # u32 width from the name
assert spell.spell("pe", "image_base_hex", H(0x400000, 16)) == "0x0000000000400000"
assert spell.spell("x", "size_hex", 255) == "0xff"
assert spell.spell("msi", "product_code_guid", G("text", " {DD1A80D5-0250-4F4D-B289-13096D633C61} ")) \
    == "{DD1A80D5-0250-4F4D-B289-13096D633C61}"
raw = bytes.fromhex("c7bc5826 7cf0 b148 8cb92bb645f8680e".replace(" ", ""))
assert spell.spell("dotnet", "mvid_guid", G("bytes_le", raw)) == "2658bcc7-f07c-48b1-8cb9-2bb645f8680e"
assert spell.spell("png", "ihdr_dimensions_pixels", D(295, 171)) == "295x171"
assert spell.spell("text", "utf8_bom_present", True) == "true" and spell.spell("t", "x_present", False) == "false"
assert spell.spell("zip", "central_directory_member_names", ["a/é.txt", "b"]) == '["a/é.txt","b"]'
assert spell.spell("zip", "eocd_total_entries", 3) == "3" and spell.spell("pdf", "x_version", (1, 7)) == "1.7"
assert spell.spell("x", "kind", "Little", {"answer_format": {"accepted_values": ["little", "big"]}}) == "little"
alts = spell.alternates("set1.d13-msi-003-msi-product-code-guid", "{DD1A80D5-0250-4F4D-B289-13096D633C61}")
assert "DD1A80D5-0250-4F4D-B289-13096D633C61" not in alts, "GM-REJECTED bare form offered"   # knowledge *_REJECTED
assert "{dd1a80d5-0250-4f4d-b289-13096d633c61}" in alts and "dd1a80d5-0250-4f4d-b289-13096d633c61" in alts
a2 = spell.alternates("d09-pe-001-pe-address-of-entry-point-rva-hex", "0x00065bd0")
assert "0x65bd0" not in a2 and "0x0000000000065bd0" in a2 and "0x00065BD0" in a2, a2
assert spell.alternates("x-dimensions-pixels", "295x171")[0] == "295 x 171"
assert "True" in spell.alternates("x-present", "true") and spell.alternates("x", "none") == []
assert "0x014c" not in spell.alternates("x-u16-hex", "0x014c")
print("ok  3) spell: hex widths by suffix/struct, GUID by source (text verbatim / bytes_le), dims, bools, json; "
      "alternates skip GM-rejected spellings")

# 4) reuse_plan: lane solver first + outside the newest-N slice; off with HCTF_META_LANE_SOLVER=0
case13 = next(c for c in CASES if solvers._day_key(c) == 13 and c.name == "single_solve")
contract13 = json.loads((case13 / "contract.json").read_text())
calls = []
saved_run = solvers.run_solver


def fake_run(sdir, contract, art, timeout=60):
    calls.append(Path(sdir))
    return saved_run(sdir, contract, art, timeout)


try:
    solvers.run_solver = fake_run
    excl = [case13.parent.parent]
    plan = solvers.reuse_plan(contract13, case13 / "artifacts", "metadata-forensics", exclude=excl, limit=1,
                              by_question=False, max_parallel=1)
    assert calls[0] == LANE and len(calls) == 2, calls          # lane + the newest dated one (limit=1)
    assert solvers._day_key(calls[1]) == 12, calls
    exp13 = json.loads((case13 / "expected.json").read_text())
    assert plan["high"] == exp13 and plan["source"][next(iter(exp13))] == LANE, plan   # D13 field verified (D13 cases)
    assert plan["best"] == LANE
    # fair run: with MAX_DAY=13 the D13 field is neither registered nor known -> nothing from the lane solver
    os.environ["HCTF_META_MAX_DAY"] = "13"
    plan_f = solvers.reuse_plan(contract13, case13 / "artifacts", "metadata-forensics", exclude=excl, limit=1,
                                by_question=False, max_parallel=1)
    assert not plan_f["high"] and not plan_f["spec"], plan_f
    del os.environ["HCTF_META_MAX_DAY"]
    calls.clear()
    os.environ["HCTF_META_LANE_SOLVER"] = "0"
    solvers.reuse_plan(contract13, case13 / "artifacts", "metadata-forensics", exclude=excl, limit=1,
                       by_question=False, max_parallel=1)
    assert LANE not in calls and len(calls) == 1, calls
    del os.environ["HCTF_META_LANE_SOLVER"]
    calls.clear()
    solvers.reuse_plan(contract13, case13 / "artifacts", "script-analysis", limit=1, by_question=False, max_parallel=1)
    assert LANE not in calls                                    # other lanes: no lane solver
finally:
    solvers.run_solver = saved_run
    os.environ.pop("HCTF_META_MAX_DAY", None)
    os.environ.pop("HCTF_META_LANE_SOLVER", None)
assert solvers._day_key(LANE) == 999 and solvers._day_key(paths.CHALLENGES / "day13" / "x" / "solver") == 13
known = solvers._known_ids(LANE)
assert ("msi", "product_code_guid") in known and ("file", "sha256") in known and ("pe", "version_original_filename") in known
os.environ["HCTF_META_MAX_DAY"] = "12"
try:
    assert ("dotnet", "mvid_guid") not in solvers._known_ids(LANE) and ("pe", "coff_machine_u16_hex") in solvers._known_ids(LANE)
finally:
    del os.environ["HCTF_META_MAX_DAY"]
d3 = next(paths.CHALLENGES.glob("day03/metadata-*/solver"))
syn = set(json.loads((d3 / "cases" / "synthetic-mastery" / "expected.json").read_text()))
real = set().union(*(json.loads(p.read_text()) for p in d3.glob("cases/[!s]*/expected.json")))
assert syn - real and not (syn - real) & solvers._known_ids(d3), "synthetic-* ids counted as GM-verified"
solvers.KNOWN_NO_SYNTHETIC = False
assert syn <= solvers._known_ids(d3)                            # flag off = the old behaviour
solvers.KNOWN_NO_SYNTHETIC = True
print("ok  4) reuse_plan: lane solver first + never sliced (limit=1 -> lane + newest dated), D13 field confident via "
      "(fmt, field), MAX_DAY hides it, HCTF_META_LANE_SOLVER=0 -> today's behaviour; synthetic cases not verified")

# 5) _race_snapshot with the lane solver as seed: the snapshot copy runs from .run/spec-day13/<chal>-race/solver
chal = case13.parent.parent.parent
cid = json.loads((chal / "meta.json").read_text())["ids"]["single_solve"]
snapdir = paths.RUN / "spec-day13" / f"{chal.name}-race"
existed = snapdir.exists()
saved_conf = cli.confirmed_answers
try:
    cli.confirmed_answers = lambda c, att=None: dict(exp13)
    me = SimpleNamespace(sdir=chal / "solver", root=chal)
    snap = orchestrate.Chain._race_snapshot(me, cid, LANE, contract13, case13 / "artifacts")
    assert snap == snapdir / "solver" and me._race_snap == snap, snap
    assert (snap / "solve.py").read_bytes() == (LANE / "solve.py").read_bytes() and (snap.parent / "meta.json").exists()
    got, err, _ = solvers.run_solver(snap, contract13, case13 / "artifacts")
    assert not err and got == exp13, (got, err)
    cli.confirmed_answers = lambda c, att=None: {k: "{WRONG}" for k in exp13}
    assert orchestrate.Chain._race_snapshot(SimpleNamespace(sdir=chal / "solver", root=chal), cid, LANE, contract13,
                                            case13 / "artifacts") is None
finally:
    cli.confirmed_answers = saved_conf
    if not existed:
        shutil.rmtree(snapdir, ignore_errors=True)
print("ok  5) _race_snapshot(seed = lane solver): .run/spec-day13/<chal>-race/solver reproduces the GM answers "
      "(parents[4] root), refused when it doesn't")

# 6) prebuilt fixtures + module structure (vacuous until the first prebuild batch lands)
t0 = time.time()
probs = prebuild.check_meta_fixtures() + prebuild.meta_structure_problems()
assert not probs, "prebuilt fixtures / modules:\n  " + "\n  ".join(probs[:20])
nfix = len(list((ROOT / "tests" / "data" / "meta_fixtures").glob("*/*.json")))
nmods = len([p for p in (ROOT / "lib" / "meta" / "prebuilt").glob("*.py") if not p.name.startswith("_")])
print(f"ok  6) prebuilt: {nmods} module(s), {nfix} fixture(s) exact through lib.meta.answer ({time.time() - t0:.1f}s)")
print("all metadata lane checks passed")
