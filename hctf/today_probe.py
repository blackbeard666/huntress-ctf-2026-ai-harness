"""Today-probe: test the Single's solver on a Mastery that mixes TODAY's codec into yesterday's verified sets -- BEFORE the
Mastery clock.

Warmups D12 + D13: the solver was right on the Single and the Time Trial (one codec, whole blob) and then failed the first
Mastery attempt, where line N is today's codec cut mid-word among the earlier days' lines (D12: reversal read as rot-N on
11/58 sets; D13: Atbash vs rot13 vs reversal on 24/63). Every failure cost a timed attempt + evidence pull + a generalize
worker (~45-400 s). The Mastery shape is predictable: yesterday's verified Mastery case + one line. So:

  base_case(sdir)  newest EARLIER-day `auto-mastery-*` case of the lane whose expected answers cover every answer_id
  synth(...)       per set: decode yesterday's lines with lib.warmups_codecs.DAYS (skip the set unless re-encoding
                   reproduces the GM bytes and the sentence ends in the verified slug), re-split the sentence into N+1
                   pieces, encode piece k with day k's codec and the LAST with today's codec inferred from the Single
                   (lib.warmups_codecs.infer: the encoder E with E(plaintext) == blob). Two cases: `-even` cuts and
                   `-edge` cuts (shifted +-2 chars, seeded) -- zip under the base's member names, base contract,
                   base expected (the slugs don't change), plus truth.json (per line: codec, plain piece, bytes).
  probe(sdir, deadline)   runs the solver on the unmodified base case + both synthetic cases; misses count only when
                   the base case itself passes (else the solver is broken in another way the compound probe reports).
  summary(res) / adopt(sdir, res)  prompt text (line, codec, truth) / copy failing cases into cases/.

Today's codec not identifiable -> status "unidentified", no cases (never a guess). Runtime ~1-2 s (solver runs).
CLI: python -m hctf.today_probe <solver_dir> [--out DIR]
"""
import io
import json
import random
import re
import shutil
import time
import zipfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from . import paths, solvers

ROOT = paths.ROOT
PREFIX = "compound-today-"


def _day(chal_dir):
    try:
        return int(Path(chal_dir).parent.name[3:])
    except ValueError:
        return -1


def _meta(chal_dir):
    try:
        return json.loads((Path(chal_dir) / "meta.json").read_text())
    except (OSError, ValueError):
        return {}


def _ids(contract):
    return contract.get("answer_ids") or [q.get("id") for q in contract.get("questions") or [] if q.get("id")]


MIN_SETS = 10   # prefer a base with this many verified sets (D5-D11 auto cases were trimmed to 1 set: too few cuts)


def base_case(sdir, prefix="auto-mastery-"):
    """Newest earlier-day `auto-mastery-*` case of this solver's lane with a COMPLETE verified expected.json -- one with
    >= MIN_SETS sets first (lines of skipped days are filled from lib.warmups_codecs.DAYS) -- or None."""
    chal = Path(sdir).parent
    lane, today = _meta(chal).get("lane"), _day(chal)
    best = None
    for m in paths.CHALLENGES.glob("day*/*/meta.json"):
        od = m.parent
        if od == chal or _day(od) >= today or _meta(od).get("lane") != lane:
            continue
        for case in (od / "solver" / "cases").glob(prefix + "*/"):
            try:
                contract = json.loads((case / "contract.json").read_text())
                expected = json.loads((case / "expected.json").read_text())
            except (OSError, ValueError):
                continue
            ids = _ids(contract)
            if not ids or not set(ids) <= set(expected):
                continue
            key = (len(ids) >= MIN_SETS, _day(od), case.stat().st_mtime)
            if best is None or key > best[0]:
                best = (key, case)
    return best[1] if best else None


def today_codec(sdir):
    """(name, enc) of today's codec from the Single Solve case (contract + bytes + GM-verified slug), or None."""
    from lib import warmups_codecs
    chal = Path(sdir).parent
    hint = _meta(chal).get("name") or ""
    got = warmups_codecs.infer_case(Path(sdir) / "cases" / "single_solve", hints=(hint,))
    return (got[0], got[1]) if got else None


def _members(case):
    """(container file name or None, {member name: bytes}) of a warmups case: ONE zip saved under the first member's
    name (D2-D13 Mastery), or plain per-set files (D4 auto cases)."""
    files = sorted(f for f in (Path(case) / "artifacts").iterdir() if f.is_file())
    if len(files) == 1 and zipfile.is_zipfile(files[0]):
        with zipfile.ZipFile(files[0]) as z:
            return files[0].name, {Path(n).name: z.read(n) for n in z.namelist() if not n.endswith("/")}
    return None, {f.name: f.read_bytes() for f in files}


def _cuts(n_chars, n, variant, rng):
    """n-1 interior cut positions: evenly spaced, or (edge) each shifted +-2 chars; every piece non-empty."""
    cuts = [round(i * n_chars / n) for i in range(1, n)]
    if variant == "edge":
        cuts = [c + rng.choice((-2, 2)) for c in cuts]
    out, prev = [], 0
    for i, c in enumerate(cuts):
        c = max(prev + 1, min(c, n_chars - (n - 1 - i)))
        out.append(c)
        prev = c
    return out


def synth(sdir, today_enc, today_name, base=None, variants=("even", "edge"), out_dir=None, seed=None):
    """Write the synthetic cases -> [case dirs]. Needs lib.warmups_codecs.DAYS for every line below the new one."""
    from lib import decode, warmups_codecs as W
    base = Path(base or base_case(sdir) or "")
    if not base.name:
        return []
    today = _day(Path(sdir).parent)
    contract = json.loads((base / "contract.json").read_text())
    expected = json.loads((base / "expected.json").read_text())
    container, members = _members(base)
    by_art = {}
    for aid, q in solvers.paired_questions(contract):
        by_art.setdefault(str(q.get("artifact") or "").split("->")[0].strip(), []).append(aid)
    out_dir = Path(out_dir or ROOT / ".run" / "today_probe" / Path(sdir).parent.name)
    made = []
    for variant in variants:
        rng = random.Random(seed if seed is not None else (today * 1000 + len(variant)))
        new_members, truth, skipped = dict(members), {}, []
        for art, aids in by_art.items():
            raw = members.get(Path(art).name)
            if raw is None:
                skipped += aids
                continue
            rows = []
            for ln in raw.decode("utf-8", "replace").splitlines():
                m = decode._CHUNK.match(ln.rstrip("\r\n"))
                if m:
                    rows.append((int(m.group(1)), m.group(2)))
            n_base = len(rows)
            ok = n_base >= 1 and [k for k, _ in rows] == list(range(1, n_base + 1))
            pieces = []
            for k, frag in rows if ok else []:
                c = W.day_codec(k)
                plain = W.safe(c[2], frag) if c else None
                if plain is None or c[1](plain) != frag:
                    ok = False
                    break
                pieces.append(plain)
            sentence = "".join(pieces)
            last = [ln for ln in sentence.splitlines() if ln.strip()]
            slugs = {expected.get(a) for a in aids}
            if not ok or not last or not any(s and last[-1].rstrip().endswith(s) for s in slugs):
                skipped += aids
                continue
            n_new = today if today > n_base and all(W.day_codec(k) for k in range(n_base + 1, today)) else n_base + 1
            cuts = _cuts(len(sentence), n_new, variant, rng)
            parts = [sentence[a:b] for a, b in zip([0] + cuts, cuts + [len(sentence)])]
            lines, info = [], []
            for k, piece in enumerate(parts, 1):
                name, enc = (today_name, today_enc) if k == n_new else W.day_codec(k)[:2]
                frag = enc(piece)
                lines.append(f"{k:02d}\t{frag}")
                info.append({"line": k, "codec": name, "today": k == n_new, "plain": piece, "encoded": frag})
            new_members[Path(art).name] = "\n".join(lines).encode()
            for a in aids:
                truth[a] = {"slug": expected.get(a), "member": Path(art).name, "lines": info}
        if not truth:
            continue
        case = out_dir / f"{PREFIX}d{today:02d}-{variant}"
        if case.exists():
            shutil.rmtree(case)
        (case / "artifacts").mkdir(parents=True)
        if container:
            buf = io.BytesIO()
            with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
                for name in members:   # the base's member order
                    z.writestr(name, new_members[name])
            (case / "artifacts" / container).write_bytes(buf.getvalue())
        else:
            for name, data in new_members.items():
                (case / "artifacts" / name).write_bytes(data)
        (case / "contract.json").write_text(json.dumps(contract, indent=2, ensure_ascii=False))
        (case / "expected.json").write_text(json.dumps(expected, indent=2, ensure_ascii=False))
        (case / "truth.json").write_text(json.dumps({
            "what": f"Day {today} Mastery rehearsal: base `{base.relative_to(ROOT) if base.is_relative_to(ROOT) else base}`"
                    f" ({variant} cuts) with today's codec `{today_name}` on the new last line; slugs unchanged",
            "today": {"day": today, "codec": today_name}, "base": str(base), "variant": variant,
            "skipped": skipped, "sets": truth}, indent=1, ensure_ascii=False))
        made.append(case)
    return made


def _run(sdir, case, timeout):
    case = Path(case).resolve()
    contract = json.loads((case / "contract.json").read_text())
    expected = json.loads((case / "expected.json").read_text())
    got, err, dt = solvers.run_solver(Path(sdir).resolve(), contract, case / "artifacts", timeout)
    wrong = {k: {"expected": v, "got": got.get(k)} for k, v in expected.items() if got.get(k) != v}
    return {"case": case.name, "path": str(case), "expected": len(expected), "correct": len(expected) - len(wrong),
            "wrong": wrong, "error": err, "seconds": round(dt, 2)}


def probe(sdir, deadline=None, out_dir=None):
    """-> {"status": clean|miss|unidentified|no-base|base-fails|no-cases, "codec", "base", "results", "hard"}."""
    t0 = time.time()
    sdir = Path(sdir).resolve()
    res = {"status": "unidentified", "codec": None, "base": None, "results": [], "hard": []}
    codec = today_codec(sdir)
    if not codec:
        return dict(res, seconds=round(time.time() - t0, 2))
    res["codec"] = codec[0]
    base = base_case(sdir)
    if base is None:
        return dict(res, status="no-base", seconds=round(time.time() - t0, 2))
    res["base"] = str(base)
    cases = synth(sdir, codec[1], codec[0], base=base, out_dir=out_dir)
    if not cases:
        return dict(res, status="no-cases", seconds=round(time.time() - t0, 2))
    timeout = max(5.0, (deadline - time.time()) if deadline else 30.0)
    with ThreadPoolExecutor(max_workers=1 + len(cases)) as ex:
        runs = list(ex.map(lambda c: _run(sdir, c, timeout), [base] + cases))
    base_run, synth_runs = runs[0], runs[1:]
    res["results"] = synth_runs
    res["base_ok"] = not base_run["error"] and not base_run["wrong"]
    hard = [r["path"] for r in synth_runs if r["error"] or r["wrong"]]
    if not res["base_ok"]:
        res["status"] = "base-fails"
    else:
        res["status"] = "miss" if hard else "clean"
        res["hard"] = hard
    res["seconds"] = round(time.time() - t0, 2)
    return res


def summary(res, limit=6):
    """Prompt/log text: which sets the solver got wrong, with the line, codec and plain text of every line."""
    st = res.get("status")
    if st == "unidentified":
        return "today-probe: today's codec could not be identified from the Single (no rehearsal cases)"
    if st != "miss":
        return ""
    out = [f"today-probe: today's codec is `{res['codec']}` (inferred from the Single: E(plaintext) == blob); "
           f"rehearsal of a Mastery with it on the NEW LAST line, built from `{Path(res['base']).name}` "
           f"({Path(res['base']).parents[2].name}):"]
    for r in res.get("results") or []:
        if not (r["error"] or r["wrong"]):
            continue
        name = Path(r["path"]).name
        out.append(f"  - `cases/{name}`: {r['correct']}/{r['expected']} sets right"
                   + (f"; solver error: {str(r['error'])[:160]}" if r["error"] else ""))
        try:
            truth = json.loads((Path(r["path"]) / "truth.json").read_text())["sets"]
        except (OSError, ValueError, KeyError):
            truth = {}
        for aid, w in list(r["wrong"].items())[:limit]:
            t = truth.get(aid) or {}
            today = next((x for x in t.get("lines") or [] if x.get("today")), None)
            out.append(f"      {aid}: expected {w['expected']!r} got {w['got']!r}"
                       + (f"; line {today['line']} ({today['codec']}): {today['encoded']!r} = {today['plain']!r}"
                          if today else ""))
    out.append("  Every line's codec + plain piece: `truth.json` in each case. Fix it in LIB, generically: register "
               "today's free-text codec with `lib.decode.register_free(name, day, cands_fn)` (or a strict branch in "
               "`lib.decode.decode_chunk` for an alphabet-signature codec) so `decode_chunked` handles the mix.")
    return "\n".join(out)


def adopt(sdir, res):
    """Copy the failing synthetic cases into the solver's cases/ (verified expected = the base's GM slugs)."""
    n = 0
    for p in res.get("hard") or []:
        src = Path(p)
        if not (src / "expected.json").exists():
            continue
        dst = Path(sdir) / "cases" / src.name
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
        n += 1
    return n


# ---------------------------------------------------------------------------------------------- K: today-merge probe
# Lane-agnostic rehearsal (metadata / binary / script / mobile): TODAY's Single becomes set N+1 of yesterday's verified
# Mastery contract (contract + expected merged, today's bytes added under the base's delivery naming). A miss counts
# only when the solver passes the base case AND the Single alone -- what is left is the merge shape itself (one family
# per contract assumed, set numbering, a delivery-name convention).
_SETID = re.compile(r"^set(\d+)[._-](.+)$")


def _new_container(sample, single_cont, n):
    m = re.match(r"^delivery (\d+): (.+)$", sample)
    if m:
        return f"delivery {n}: {Path(single_cont).name}"
    m = re.match(r"^(.*?)(\d{2,})(\.[A-Za-z0-9]+)$", sample)
    if m:
        return f"{m.group(1)}{n:0{len(m.group(2))}d}{m.group(3)}"
    return f"set{n}-{Path(single_cont).name}"


def merge_case(sdir, base=None, out_dir=None):
    """Write `compound-merge-dNN` (base Mastery + today's Single as the next set) -> case dir, or None."""
    import hashlib
    sdir = Path(sdir)
    base = Path(base or base_case(sdir) or "")
    single = sdir / "cases" / "single_solve"
    if not base.name or not (single / "contract.json").exists() or not (single / "expected.json").exists():
        return None
    bc, be = json.loads((base / "contract.json").read_text()), json.loads((base / "expected.json").read_text())
    sc, se = json.loads((single / "contract.json").read_text()), json.loads((single / "expected.json").read_text())
    nums = [int(m.group(1)) for m in (_SETID.match(a) for a in _ids(bc)) if m]
    if not nums or not se:
        return None
    n = max(nums) + 1
    bq = [q for _a, q in solvers.paired_questions(bc)]
    sample = next((str(q.get("artifact") or "").split("->")[0].strip() for q in bq if q.get("artifact")), "")
    s_conts = []
    for _a, q in solvers.paired_questions(sc):
        c = str(q.get("artifact") or "").split("->")[0].strip()
        if c and c not in s_conts:
            s_conts.append(c)
    if not s_conts:
        return None
    rename = {c: (_new_container(sample, c, n) if len(s_conts) == 1 else f"set{n}-{Path(c).name}") for c in s_conts}
    today = _day(sdir.parent)
    case = Path(out_dir or ROOT / ".run" / "today_probe" / sdir.parent.name) / f"compound-merge-d{today:02d}"
    if case.exists():
        shutil.rmtree(case)
    shutil.copytree(base / "artifacts", case / "artifacts")
    from lib.common import find_artifact
    new_arts = []
    for c, nc in rename.items():
        try:
            data = find_artifact(single / "artifacts", c)
        except (KeyError, FileNotFoundError, OSError):
            shutil.rmtree(case, ignore_errors=True)
            return None
        (case / "artifacts" / nc).write_bytes(data)
        new_arts.append({"name": nc, "sha256": hashlib.sha256(data).hexdigest()})
    ids, qs = list(_ids(bc)), list(bc.get("questions") or [])
    for aid, q in solvers.paired_questions(sc):
        cont, _, member = str(q.get("artifact") or "").partition("->")
        q2 = dict(q, id=f"set{n}.{q.get('id') or aid}", set=n)
        if cont.strip() in rename:
            q2["artifact"] = rename[cont.strip()] + (f" -> {member.strip()}" if member.strip() else "")
        ids.append(f"set{n}.{aid}")
        qs.append(q2)
    merged = dict(bc, answer_ids=ids, questions=qs)
    if isinstance(bc.get("artifacts"), list) and all(isinstance(x, dict) for x in bc["artifacts"]):
        merged["artifacts"] = list(bc["artifacts"]) + new_arts
    expected = {**be, **{f"set{n}.{k}": v for k, v in se.items()}}
    (case / "contract.json").write_text(json.dumps(merged, indent=2, ensure_ascii=False))
    (case / "expected.json").write_text(json.dumps(expected, indent=2, ensure_ascii=False))
    (case / "truth.json").write_text(json.dumps({
        "what": f"Day {today} merge rehearsal: base `{base.name}` ({base.parents[2].name}, sets 1-{n - 1}) + today's "
                f"Single as set {n} ({', '.join(f'{c} -> {nc}' for c, nc in rename.items())}); answers = both GM-verified",
        "base": str(base), "set": n, "renamed": rename}, indent=1))
    return case


def merge_probe(sdir, deadline=None, out_dir=None):
    """-> {"status": clean|miss|no-base|base-fails|no-cases|error, "results", "hard", "seconds"}."""
    t0 = time.time()
    sdir = Path(sdir).resolve()
    res = {"status": "no-base", "base": None, "results": [], "hard": []}
    base = base_case(sdir)
    if base is None:
        return dict(res, seconds=round(time.time() - t0, 2))
    res["base"] = str(base)
    case = merge_case(sdir, base, out_dir=out_dir)
    if case is None:
        return dict(res, status="no-cases", seconds=round(time.time() - t0, 2))
    timeout = max(10.0, (deadline - time.time()) if deadline else 60.0)
    with ThreadPoolExecutor(max_workers=3) as ex:
        runs = list(ex.map(lambda c: _run(sdir, c, timeout), [base, sdir / "cases" / "single_solve", case]))
    res["results"] = [runs[2]]
    res["base_ok"] = all(not r["error"] and not r["wrong"] for r in runs[:2])
    if not res["base_ok"]:
        res["status"] = "base-fails"
    else:
        res["status"] = "miss" if (runs[2]["error"] or runs[2]["wrong"]) else "clean"
        res["hard"] = [runs[2]["path"]] if res["status"] == "miss" else []
    res["seconds"] = round(time.time() - t0, 2)
    return res


def merge_summary(res, limit=8):
    if res.get("status") != "miss":
        return ""
    r = res["results"][0]
    out = [f"today-merge probe: the solver passes yesterday's verified Mastery `{Path(res['base']).name}` and today's "
           f"Single separately, but NOT the two merged into one contract (`cases/{Path(r['path']).name}`, today's Single = "
           f"the last set; truth.json says how): {r['correct']}/{r['expected']} fields right"
           + (f"; solver error: {str(r['error'])[:200]}" if r["error"] else "")]
    for aid, w in list(r["wrong"].items())[:limit]:
        out.append(f"      {aid}: expected {w['expected']!r} got {w['got']!r}")
    return "\n".join(out)


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description="rehearse a Mastery mixing today's codec into yesterday's verified sets")
    ap.add_argument("sdir")
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    res = probe(a.sdir, out_dir=a.out)
    print(summary(res) or f"today-probe: {res['status']} (codec {res.get('codec')})")
    print(json.dumps({k: v for k, v in res.items() if k != "results"}, default=str))
    return 0 if res["status"] in ("clean", "unidentified", "no-base", "no-cases") else 1


if __name__ == "__main__":
    raise SystemExit(main())
