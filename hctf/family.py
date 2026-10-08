"""Synthetic "family" regression cases for codec-carrying lanes (script-analysis).

Rehearsal Day 7 replay: a generalize worker fixed exactly the codecs its 4 variants used (reversed_base64 x3, decimal_csv) and
the next Time Trial variant drew xor_hex -- a second cycle for one more member of the SAME codec family. A family case
is a passing case with every self-describing fixture re-encoded under ANOTHER known rep x transform (lib.codec.encode,
format copied from a real material of that rep, round-trip verified). The plaintext -- and so every answer -- is
unchanged, except the `*-representation` / `*-transform` fields, which name the codec and are rewritten. A solver that
routes codecs through lib.codec passes them untouched; one with a per-name table fails offline, inside the generalize,
instead of on the next timed variant.

NOT regression cases: they live in .run/family/ and never gate a generalize, because a solver that EMULATES the
fixture's own decode routine (vbsplan interprets the VBScript) legitimately disagrees with a recoded material whose
routine was left unchanged (main D7 solver: VBS fixtures "fail", bash/Node pass). The harness probes only the failing
fixture's language and reports per fixture, as information for the generalize worker.

Runs under the venv (AES zips need pyzipper):
    .venv/bin/python -m hctf.family probe <solver_dir> [--ext sh] [--n 2] [--out DIR]      (JSON summary)
"""
import argparse
import hashlib
import io
import json
import random
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from lib import codec  # noqa: E402

PREFIX = "family-"
PASSWORD = b"infected"
SAFE_SUFFIXES = {"representation", "transform"}   # the only answers that depend on the codec itself


def _suffix(aid):
    return re.sub(r"^set\d+\.", "", aid).split("-")[-1]


def _open_zip(data):
    import pyzipper
    z = pyzipper.AESZipFile(io.BytesIO(data))
    z.setpassword(PASSWORD)
    return z


def _write_zip(members):
    import pyzipper
    buf = io.BytesIO()
    with pyzipper.AESZipFile(buf, "w", compression=pyzipper.ZIP_DEFLATED, encryption=pyzipper.WZ_AES) as z:
        z.setpassword(PASSWORD)
        for name, data in members:
            z.writestr(name, data)
    return buf.getvalue()


def rep_samples(cases):
    """rep -> one real material written in it (the format template for encode())."""
    out = {}
    for case in cases:
        for f in (case / "artifacts").glob("*"):
            try:
                z = _open_zip(f.read_bytes())
                names = z.namelist()
            except Exception:  # noqa: BLE001 - not a (readable) zip
                continue
            for n in names:
                try:
                    t = z.read(n).decode("utf-8", "replace")
                except Exception:  # noqa: BLE001
                    continue
                if "odec_" not in t and "ODEC_" not in t:
                    continue
                for c in codec.find_codecs(t):
                    if c.get("plain") and c.get("material") and c["rep"] not in out:
                        out[c["rep"]] = c["material"]
    return out


def _base_case(cases):
    """Newest verified case whose single artifact is a flat AES zip of fixtures (no nested bundles)."""
    for case in cases:
        if case.name.startswith(PREFIX) or not (case.name == "single_solve" or case.name.startswith("auto-time_trial")):
            continue
        try:
            exp = json.loads((case / "expected.json").read_text())
        except (OSError, ValueError):
            continue
        arts = [f for f in (case / "artifacts").glob("*") if f.is_file()]
        if not exp or len(arts) != 1:
            continue
        try:
            z = _open_zip(arts[0].read_bytes())
            if any(n.lower().endswith(".zip") for n in z.namelist()):
                continue
        except Exception:  # noqa: BLE001
            continue
        return case, arts[0], exp
    return None


def _slots(z, contract, expected):
    """Recodable fixtures: (member, text, codec dict, spec match span, quote, field count)."""
    by_member = {}
    for q in contract.get("questions") or []:
        by_member.setdefault(str(q.get("artifact", "")).split("->")[-1].strip(), []).append(q["id"])
    out = []
    for n in z.namelist():
        text = z.read(n).decode("utf-8", "replace")
        matches = list(codec._CODEC_RE.finditer(text))
        if len(matches) != 1:
            continue
        c = codec.find_codecs(text)
        if len(c) != 1 or not c[0].get("plain") or not c[0].get("material"):
            continue
        c, m = c[0], matches[0]
        mat = c["material"]
        i = text.find(mat)
        if text.count(mat) != 1 or i < 1 or text[i - 1] not in "'\"" or text[i + len(mat):i + len(mat) + 1] != text[i - 1]:
            continue   # multi-piece / unquoted material: leave it alone
        ids = by_member.get(Path(n).name, [])
        olds = {c["rep"], c["transform"], c["key"]} - {""}
        if any(_suffix(a) == "obfuscation" or (_suffix(a) not in SAFE_SUFFIXES and str(expected.get(a)) in olds)
               for a in ids):
            continue   # an answer depends on the encoding beyond representation/transform
        out.append({"member": n, "text": text, "codec": c, "span": m.span("spec"), "quote": text[i - 1],
                    "fields": len(m.group("spec").split("|")), "ids": ids})
    return out


def _combos(fields, samples, rng):
    """Every (rep, transform, key) that encodes, ordered so each rep and transform is covered early."""
    reps = [r for r in codec.REPS if codec.known(r) and (r in samples or "base64" in r or r == "percent_hex")]
    if fields == 2:   # short bash style: `rep|` (identity) or `xor_hex|<key>`
        trs = ["identity"]
    else:
        trs = [t for t in codec.TRANSFORMS if codec.known(None, t)]
    combos = [(r, t) for r in reps for t in trs]
    rng.shuffle(combos)
    ordered, seen_r, seen_t = [], set(), set()
    while combos:
        best = max(combos, key=lambda rt: (rt[0] not in seen_r) + (rt[1] not in seen_t))
        combos.remove(best)
        ordered.append(best)
        seen_r.add(best[0])
        seen_t.add(best[1])
    return ordered


def _key_for(rep, tr, rng):
    if rep == "xor_hex":
        return f"{rng.randrange(1, 256):02x}"
    if tr in ("single_byte_xor", "add_modulo_256", "subtract_modulo_256", "rolling_xor", "rotate_left"):
        return f"{rng.randrange(1, 256):02x}"
    if tr in ("repeating_key_xor", "reverse_then_xor"):
        return "".join(f"{rng.randrange(1, 256):02x}" for _ in range(rng.randrange(2, 5)))
    return ""


def _recode(sl, rep, tr, key, samples):
    """(new fixture text, spec) re-encoding slot `sl`'s plaintext under rep/tr/key in the slot's own spec style, or
    None if it can't be written safely inside the fixture's quotes or doesn't round-trip through lib.codec."""
    if sl["fields"] == 2:   # `rep|` = identity; `xor_hex|cd` = the 2nd field IS the key
        key = key if rep == "xor_hex" else ""
        mat = codec.encode(sl["codec"]["plain"], rep, key, None, samples.get(rep))
    else:
        mat = codec.encode(sl["codec"]["plain"], rep, tr, key, samples.get(rep))
    if not mat or sl["quote"] in mat or "\\" in mat or "\n" in mat:
        return None
    spec = f"{rep}|{key}" if sl["fields"] == 2 else f"{rep}|{tr}|{key}"
    a, b = sl["span"]
    text = sl["text"][:a] + spec + sl["text"][b:]
    text = text.replace(sl["codec"]["material"], mat, 1)
    check = codec.find_codecs(text)
    if len(check) != 1 or check[0].get("plain") != sl["codec"]["plain"]:
        return None
    return text, spec


def make(sdir, out_dir, n=2, seed=None, exts=None, exclude=None, plan=None):
    """Write up to `n` family cases of `sdir`'s newest flat verified case into `out_dir` (replaced). `exts`: recode only
    fixtures with these extensions (the failing fixture's language). Returns a summary with, per case, the recoded
    members and the answer_ids that belong to each."""
    sdir, out_dir = Path(sdir).resolve(), Path(out_dir).resolve()   # relative solver dirs can't be launched
    shutil.rmtree(out_dir, ignore_errors=True)
    cases = sorted((Path(sdir) / "cases").glob("*/"), key=lambda p: p.stat().st_mtime, reverse=True)
    base = _base_case(cases)
    if not base:
        return {"made": [], "note": "no flat verified case to recode"}
    case, art, expected = base
    contract_text = (case / "contract.json").read_text()
    contract = json.loads(contract_text)
    z = _open_zip(art.read_bytes())
    slots = _slots(z, contract, expected)
    if exts:
        exts = {e.lower().lstrip(".") for e in exts}
        slots = [x for x in slots if Path(x["member"]).suffix.lower().lstrip(".") in exts]
    if exclude:
        exclude = {e.lower().lstrip(".") for e in exclude}
        slots = [x for x in slots if Path(x["member"]).suffix.lower().lstrip(".") not in exclude]
    if not slots:
        return {"made": [], "note": f"no recodable fixtures in {case.name}" + (f" with {sorted(exts)}" if exts else "")}
    samples = rep_samples(cases[:24])
    rng = random.Random(seed if seed is not None else int(hashlib.sha256(case.name.encode()).hexdigest(), 16))
    queues = {f: _combos(f, samples, rng) for f in {x["fields"] for x in slots}}
    old_sha = hashlib.sha256(art.read_bytes()).hexdigest()
    made, used = [], []
    for k in range(1, n + 1):
        exp = dict(expected)
        members, recoded = {nm: z.read(nm) for nm in z.namelist()}, []
        for si, sl in enumerate(slots):
            if plan is not None:   # explicit (rep, tr, key) candidates per slot (control cases)
                cands = list(plan.get(sl["member"], []))
            else:
                q = queues[sl["fields"]]
                cands = [(rep, tr, None) for rep, tr in q
                         if (rep, tr) != (sl["codec"]["rep"], sl["codec"]["transform"] or "identity")]
                q.append(q.pop(0))   # rotate ONE step per slot: the next slot / case starts from the next combo
            for rep, tr, key in cands:
                key = _key_for(rep, tr, rng) if key is None else key
                got = _recode(sl, rep, tr, key, samples)
                if not got:
                    continue
                text, spec = got
                members[sl["member"]] = text.encode("utf-8")
                for aid in sl["ids"]:
                    if _suffix(aid) == "representation" and aid in exp:
                        exp[aid] = rep
                    elif _suffix(aid) == "transform" and aid in exp:
                        exp[aid] = tr
                recoded.append({"member": Path(sl["member"]).name, "was": "|".join(
                    x for x in (sl["codec"]["rep"], sl["codec"]["transform"]) if x), "spec": spec, "ids": sl["ids"]})
                used.append((rep, tr))
                break
        if not recoded:
            continue
        blob = _write_zip(members.items())
        out = out_dir / f"{PREFIX}{k}"
        (out / "artifacts").mkdir(parents=True, exist_ok=True)
        (out / "artifacts" / art.name).write_bytes(blob)
        (out / "contract.json").write_text(contract_text.replace(old_sha, hashlib.sha256(blob).hexdigest()))
        (out / "expected.json").write_text(json.dumps(exp, indent=2, ensure_ascii=False))
        (out / "recoded.json").write_text(json.dumps(recoded, indent=1))
        made.append({"case": str(out), "recoded": recoded})
    return {"made": made, "base": case.name, "slots": len(slots),
            "reps": sorted({r for r, _ in used}), "transforms": sorted({t for _, t in used})}


def probe(sdir, out_dir, n=2, seed=None, exts=None, timeout=20, exclude=None):
    """make() + run the solver on each family case; per recoded fixture: did the solver reproduce its answers?"""
    sys.path.insert(0, str(ROOT))
    from hctf import solvers
    sdir = Path(sdir).resolve()
    summary = make(sdir, out_dir, n, seed, exts, exclude)
    results = []
    for m in summary.get("made", []):
        case = Path(m["case"])
        contract = json.loads((case / "contract.json").read_text())
        exp = json.loads((case / "expected.json").read_text())
        got, err, _dt = solvers.run_solver(Path(sdir), contract, case / "artifacts", timeout)
        for r in m["recoded"]:
            bad = [a for a in r["ids"] if a in exp and got.get(a) != exp[a]]
            results.append({"case": case.name, "member": r["member"], "was": r["was"], "spec": r["spec"],
                            "ok": not bad and not err, "wrong": len(bad), "empty": sum(1 for a in bad if got.get(a) in (None, "")),
                            "of": len([a for a in r["ids"] if a in exp])})
    summary["results"] = results
    return summary


def calibrate(sdir, out_dir, threshold=0.5, n=3):
    """Which fixture languages the family probe can JUDGE for this lane: probe a solver that already passed the GM's real
    variants (the previous day's final solver); a language it reproduces < threshold is synthetic noise -- the solver
    emulates that fixture's own decode routine, which the recoding leaves unchanged (VBScript ~0.3 on every day's final
    solver; bash ~0.8, Node 1.0). n=3 cases: with n=1 the D6 bash ratio swung to 0.4. Returns {"noise", "ratio"}.
    (A same-case 'borrowed codec' control does NOT separate them: vbsplan's Codec_ fallback knows borrowed codecs.)"""
    per, base = {}, None
    for e in fixture_exts(sdir):   # ONE language per case: D6+ fixtures form cross-language graphs, so recoding the
        summary = probe(sdir, Path(out_dir) / e, n=n, exts=[e])   # VBS step breaks the bash fixture's answers too
        base = summary.get("base") or base
        for r in summary.get("results", []):
            ok, tot = per.get(e, (0, 0))
            per[e] = (ok + bool(r["ok"]), tot + 1)
    ratio = {e: round(ok / tot, 2) for e, (ok, tot) in per.items() if tot}
    return {"noise": sorted(e for e, r in ratio.items() if r < threshold), "ratio": ratio, "base": base}


def fixture_exts(sdir):
    """Extensions of the recodable fixtures in sdir's newest flat verified case."""
    cases = sorted((Path(sdir).resolve() / "cases").glob("*/"), key=lambda p: p.stat().st_mtime, reverse=True)
    base = _base_case(cases)
    if not base:
        return []
    case, art, expected = base
    slots = _slots(_open_zip(art.read_bytes()), json.loads((case / "contract.json").read_text()), expected)
    return sorted({Path(x["member"]).suffix.lower().lstrip(".") for x in slots} - {""})


def probe_each(sdir, out_dir, exts, n=2):
    """probe() one language at a time (see calibrate); merged results."""
    merged = {"made": [], "results": [], "base": None}
    for e in sorted(exts):
        s = probe(sdir, Path(out_dir) / e, n=n, exts=[e])
        merged["base"] = s.get("base") or merged["base"]
        merged["made"] += s.get("made", [])
        merged["results"] += [dict(r, ext=e, case_dir=str(Path(out_dir) / e / r["case"])) for r in s.get("results", [])]
    return merged


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("action", choices=["make", "probe", "calibrate", "probe-each"])
    ap.add_argument("solver_dir")
    ap.add_argument("--out", help="where the family cases go (default .run/family/<challenge>)")
    ap.add_argument("--n", type=int, default=2)
    ap.add_argument("--seed", type=int)
    ap.add_argument("--ext", action="append", help="recode only fixtures with this extension (repeatable)")
    ap.add_argument("--exclude-ext", action="append", help="never recode fixtures with this extension (repeatable)")
    a = ap.parse_args()
    out = a.out or str(ROOT / ".run" / "family" / Path(a.solver_dir).resolve().parent.name)
    if a.action == "calibrate":
        print(json.dumps(calibrate(a.solver_dir, out)))
        return
    if a.action == "probe-each":
        exts = a.ext or [e for e in fixture_exts(a.solver_dir) if e not in set(a.exclude_ext or [])]
        print(json.dumps(probe_each(a.solver_dir, out, exts, a.n)))
        return
    fn = probe if a.action == "probe" else make
    print(json.dumps(fn(a.solver_dir, out, a.n, a.seed, a.ext, exclude=a.exclude_ext)))


if __name__ == "__main__":
    main()
