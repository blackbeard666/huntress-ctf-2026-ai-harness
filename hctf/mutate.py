"""Answer-invariant mutation probe: does the single's solver survive the cheap, lane-agnostic changes a Time Trial /
Mastery variant makes, BEFORE an attempt is spent on it?

Organizer (Day 8): "Time Trial and Mastery Mode are supposed to be giving you all new, dynamic variations/mutations on
the tasks, so you're encouraged to build a general purpose solver that could work against new unseen effects."
The single's stop gate only replays the single's own bytes, so a solver keyed to the delivery's file name, the question
order, the exact question set, or a one-set contract passes it -- and then burns a timed attempt + a generalize cycle.

Every mutation here keeps the ANSWERS unchanged (same member bytes, same member names), so expected.json carries over:
  renamed        the delivery file gets another name (contract artifact strings + artifacts[] follow, as the GM does)
  reordered      answer_ids/questions reversed
  subset         only every other question asked
  unknown-field  one question the solver has never seen is added (it must still answer every known field, no crash)
  mastery-shape  two sets (`set1.`/`set2.` ids, the real Mastery naming when known, else `delivery N: <name>`)
  wrapped        (SOFT) the delivery arrives inside one more zip under its own name (warmups D7 Mastery did this)
HARD mutations failing = a real fragility (adopted as `mutation-*` regression cases, pre-attempt generalize).
SOFT ones are information for a generalize only.

Runs under the venv (wrapped needs pyzipper for the AES zip):
    .venv/bin/python -m hctf.mutate probe <solver_dir> [--mastery-contract P] [--out DIR]     (JSON summary)
"""
import argparse
import hashlib
import io
import json
import re
import shutil
import sys
from pathlib import Path

from .procgov import Executor as _BgExecutor

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

PREFIX = "mutation-"
HARD = ("renamed", "reordered", "subset", "unknown-field", "mastery-shape")
SOFT = ("wrapped",)
SKIP_FILES = {"manifest.json", "contract.json", "result.json"}
SET_RE = re.compile(r"^(set|slot)[._-]?\d+[._-]")


def _files(art):
    return sorted(p for p in Path(art).iterdir() if p.is_file() and p.name not in SKIP_FILES) if Path(art).is_dir() else []


def _container(q):
    """Delivery (container) name of a question's artifact string: 'x.zip -> member' -> 'x.zip'."""
    return ((q or {}).get("artifact") or "").split("->", 1)[0].strip()


def _member(q):
    a = (q or {}).get("artifact") or ""
    return a.split("->", 1)[1].strip() if "->" in a else ""


def base_case(sdir):
    """(case dir, contract, expected, files): the single's verified case, else the newest verified one-set case."""
    cases = Path(sdir) / "cases"
    order = [cases / "single_solve"] + sorted((p for p in cases.glob("*/") if p.name != "single_solve"),
                                              key=lambda p: p.stat().st_mtime, reverse=True)
    for case in order:
        try:
            contract = json.loads((case / "contract.json").read_text())
            expected = json.loads((case / "expected.json").read_text())
        except (OSError, ValueError):
            continue
        ids = contract.get("answer_ids") or []
        if not expected or not ids or any(SET_RE.match(a) for a in ids) or case.name.startswith(PREFIX):
            continue
        if not (contract.get("questions") and len(contract["questions"]) == len(ids)):
            continue
        return case, contract, expected, _files(case / "artifacts")
    return None


def _write(out, name, contract, expected, files, note):
    """files: [(dest name, bytes)]."""
    d = Path(out) / f"{PREFIX}{name}"
    shutil.rmtree(d, ignore_errors=True)
    (d / "artifacts").mkdir(parents=True)
    for fn, data in files:
        (d / "artifacts" / fn).write_bytes(data)
    (d / "contract.json").write_text(json.dumps(contract, indent=2, ensure_ascii=False))
    (d / "expected.json").write_text(json.dumps(expected, indent=2, ensure_ascii=False))
    (d / "mutation.json").write_text(json.dumps({"mutation": name, "note": note,
                                                 "hard": name in HARD}, indent=1))
    return d


def _rename_contract(contract, old, new):
    """The contract as the GM would hand it with the delivery called `new`: artifact strings, question text, artifacts[]."""
    c = json.loads(json.dumps(contract))
    for q in c.get("questions") or []:
        if _container(q) == old:
            q["artifact"] = new + (" -> " + _member(q) if _member(q) else "")
        if old in (q.get("question") or ""):
            q["question"] = q["question"].replace(old, new)
    for a in c.get("artifacts") or []:
        if isinstance(a, dict) and a.get("filename") == old:
            a["filename"] = new
    if c.get("filename") == old:
        c["filename"] = new
    return c


def _wrap_zip(name, data):
    import pyzipper
    buf = io.BytesIO()
    with pyzipper.AESZipFile(buf, "w", compression=pyzipper.ZIP_DEFLATED, encryption=pyzipper.WZ_AES) as z:
        z.setpassword(b"infected")
        z.writestr(name, data)
    return buf.getvalue()


def _mastery_names(mc, container):
    """(set-1 name, set-2 name) for the delivery, from the real Mastery contract's artifact strings when known."""
    names = {}
    for q in (mc or {}).get("questions") or []:
        s = q.get("set")
        c = _container(q)
        if s in (1, 2) and c and s not in names:
            names[s] = c
    if len(names) == 2 and names[1] != names[2]:
        return names[1], names[2]
    return f"delivery 1: {container}", f"delivery 2: {container}"


def make(sdir, out_dir, mastery_contract=None, soft=True):
    """Write every applicable mutation of sdir's base case into out_dir (replaced). Returns a summary."""
    sdir, out_dir = Path(sdir).resolve(), Path(out_dir).resolve()
    shutil.rmtree(out_dir, ignore_errors=True)
    out_dir.mkdir(parents=True)
    b = base_case(sdir)
    if not b:
        return {"made": [], "note": "no verified one-set case to mutate"}
    case, contract, expected, files = b
    ids, qs = contract["answer_ids"], contract["questions"]
    fdata = [(p.name, p.read_bytes()) for p in files]
    conts = sorted({_container(q) for q in qs if _container(q)})
    one = len(files) == 1 and len(conts) == 1
    made = []

    def add(name, c, exp, fl, note):
        made.append({"case": str(_write(out_dir, name, c, exp, fl, note)), "mutation": name, "note": note})

    # renamed: only when no answer can depend on the delivery's own name
    if one:
        old = conts[0]
        stem = Path(old).stem.lower()
        if not any(stem and stem in str(v).lower() for v in expected.values()):
            ext = "".join(Path(old).suffixes[-1:])
            new = f"variant-{hashlib.sha256(old.encode()).hexdigest()[:6]}{ext}"
            add("renamed", _rename_contract(contract, old, new), dict(expected), [(new, fdata[0][1])],
                f"delivery `{old}` renamed to `{new}` (members and bytes unchanged)")
    if len(ids) >= 2:
        c = dict(contract, answer_ids=ids[::-1], questions=qs[::-1])
        add("reordered", c, dict(expected), fdata, "questions/answer_ids in reverse order")
    if len(ids) >= 3:
        keep = list(range(1, len(ids), 2))
        c = dict(contract, answer_ids=[ids[i] for i in keep], questions=[qs[i] for i in keep])
        exp = {ids[i]: expected[ids[i]] for i in keep if ids[i] in expected}
        if exp:
            add("subset", c, exp, fdata, f"only {len(keep)}/{len(ids)} of the questions asked (every other one)")
    uq = {"id": "zz-probe-unknown-field",
          "question": "What is the exact value for field zz_probe_unknown_field in the delivered evidence set?",
          "artifact": qs[0].get("artifact"),
          "answer_format": {"kind": "exact_text", "syntax": "exact artifact-derived value only"},
          "normalization": "exact"}
    add("unknown-field", dict(contract, answer_ids=ids + [uq["id"]], questions=qs + [uq]), dict(expected), fdata,
        "one never-seen question added: every known field must still be answered (None for the unknown one is fine)")
    if one:
        n1, n2 = _mastery_names(mastery_contract, conts[0])
        sha = hashlib.sha256(fdata[0][1]).hexdigest()
        mids, mqs, mexp = [], [], {}
        for s, nm in ((1, n1), (2, n2)):
            for aid, q in zip(ids, qs):
                nq = dict(q, id=f"set{s}.{aid}", set=s, artifact=nm + (" -> " + _member(q) if _member(q) else ""))
                mids.append(nq["id"])
                mqs.append(nq)
                if aid in expected:
                    mexp[nq["id"]] = expected[aid]
        c = {k: v for k, v in contract.items() if k not in ("download", "downloads", "sha256", "artifacts")}
        c.update(mode="mastery", answer_ids=mids, questions=mqs,
                 artifacts=[{"download": f"/mutation/{s}", "sha256": sha, "filename": nm.split(": ", 1)[-1]}
                            for s, nm in ((1, n1), (2, n2))])
        add("mastery-shape", c, mexp, [(n1, fdata[0][1]), (n2, fdata[0][1])],
            f"two Mastery sets (`set1.`/`set2.` ids) delivered as `{n1}` and `{n2}` (same bytes)")
    if soft and one and fdata[0][1][:2] != b"PK":
        try:
            add("wrapped", contract, dict(expected), [(fdata[0][0], _wrap_zip(fdata[0][0], fdata[0][1]))],
                f"`{fdata[0][0]}` delivered inside a zip (AES, password infected) under its own name")
        except ImportError:
            pass
    return {"made": made, "base": case.name}


def probe(sdir, out_dir, mastery_contract=None, timeout=20, soft=True):
    """make() + run the solver on the base case and every mutation (in parallel). Per mutation: ok / error / wrong /
    empty. Mutations are only judged when the solver reproduces the unmutated base case itself."""
    from hctf import solvers
    sdir = Path(sdir).resolve()
    summary = make(sdir, out_dir, mastery_contract, soft)
    if not summary.get("made"):
        summary["results"] = []
        return summary
    base = Path(sdir) / "cases" / summary["base"]

    def run(case):
        case = Path(case)
        contract = json.loads((case / "contract.json").read_text())
        exp = json.loads((case / "expected.json").read_text())
        got, err, dt = solvers.run_solver(sdir, contract, case / "artifacts", timeout)
        bad = [a for a, v in exp.items() if got.get(a) != v]
        return {"ok": not err and not bad, "error": (err or "")[-300:] or None, "wrong": len(bad),
                "empty": sum(1 for a in bad if got.get(a) in (None, "")), "of": len(exp), "seconds": round(dt, 2),
                "sample": [{"id": a, "expected": exp[a], "got": got.get(a)} for a in bad[:3]]}
    with _BgExecutor(max_workers=min(8, len(summary["made"]) + 1)) as ex:
        bfut = ex.submit(run, base)
        futs = [(m, ex.submit(run, m["case"])) for m in summary["made"]]
        b = bfut.result()
        res = [dict(m, hard=m["mutation"] in HARD, **f.result()) for m, f in futs]
    summary["base_ok"] = b["ok"]
    summary["base_seconds"] = b["seconds"]
    summary["results"] = res if b["ok"] else []
    if not b["ok"]:
        summary["note"] = f"solver fails its own base case {summary['base']} ({b['error'] or b['sample']}): not judged"
    return summary


def report(summary, out_dir=None):
    """(text for a generalize prompt, [failing HARD mutation case dirs])."""
    res = summary.get("results") or []
    if not res:
        return "", []
    miss = [r for r in res if not r["ok"]]
    hard = [r for r in miss if r["hard"]]
    if not miss:
        return "", []
    lines = [f"Mutation probe (answer-invariant changes of cases/{summary.get('base')}; expected answers unchanged): "
             f"the solver survives {len(res) - len(miss)}/{len(res)}."]
    for r in miss:
        what = r["error"] or (f"{r['empty']} empty + {r['wrong'] - r['empty']} wrong of {r['of']}; e.g. "
                              + json.dumps(r["sample"], ensure_ascii=False)[:300])
        lines.append(f"  - {'HARD' if r['hard'] else 'soft'} `{r['mutation']}` ({r['note']}): {what}")
    return "\n".join(lines), [r["case"] for r in hard]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("action", choices=["make", "probe"])
    ap.add_argument("solver_dir")
    ap.add_argument("--out")
    ap.add_argument("--mastery-contract")
    ap.add_argument("--timeout", type=float, default=20)
    ap.add_argument("--no-soft", action="store_true")
    a = ap.parse_args()
    out = Path(a.out or ROOT / ".run" / "mutation" / Path(a.solver_dir).resolve().parent.name)
    mc = None
    if a.mastery_contract:
        try:
            mc = json.loads(Path(a.mastery_contract).read_text())
        except (OSError, ValueError):
            mc = None
    if a.action == "make":
        print(json.dumps(make(a.solver_dir, out, mc, not a.no_soft)))
        return
    s = probe(a.solver_dir, out, mc, a.timeout, not a.no_soft)
    s["text"], s["hard_failed"] = report(s)
    print(json.dumps(s, ensure_ascii=False))


if __name__ == "__main__":
    main()
