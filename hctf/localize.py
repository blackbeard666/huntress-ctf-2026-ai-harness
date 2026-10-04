#!/usr/bin/env python3
"""Localize the wrong answer_id(s) on a timed variant by BINARY SEARCH over subset submits.
Runs in ONE process next to the GM (set HUNTRESS_GAME_MASTER_URL to the inside proxy on Homebase).
Submitting a correct subset returns accepted/correct; a subset containing a wrong field returns incorrect.
Prints JSON: {wrong: [[id, solver_value], ...], phases, elapsed}.
Usage: HUNTRESS_GAME_MASTER_URL=... python3 localize.py <cid> <solver_dir_rel>
"""
import json, os, re, subprocess, sys, time, urllib.request
from pathlib import Path

GM = os.environ.get("HUNTRESS_GAME_MASTER_URL", "https://2026.huntress.ctf.games")
HW = Path(__file__).resolve().parent.parent


def _token():
    t = os.environ.get("HUNTRESS_GM_TOKEN")
    if t:
        return t.strip()
    try:
        return (HW / "secrets" / "gm_pairing_token").read_text().strip() or None
    except OSError:
        return None


def _auth(h=None):
    h = dict(h or {})
    if "10.0.0.219" not in GM:   # inside proxy uses network identity, no token
        tok = _token()
        if tok:
            h["Authorization"] = "Bearer " + tok
    return h


def _post(payload, timeout=20):
    req = urllib.request.Request(GM, data=json.dumps(payload).encode(),
                                 headers=_auth({"Content-Type": "application/json"}), method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


def _get(cap, timeout=20):
    req = urllib.request.Request(f"{GM}?op=download&capability={cap}", headers=_auth())
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


CAP_RE = re.compile(r"(?:/download/|[?&]capability=)([0-9a-f]{64})")


def main():
    cid, solver_rel = sys.argv[1], sys.argv[2]
    t0 = time.time()
    body = _post({"op": "start", "challenge": cid})
    if body.get("result") == "expired":
        body = _post({"op": "retry", "challenge": cid})
    ids = body.get("answer_ids") or []
    # download
    adir = HW / ".run" / "tmp-loc"
    adir.mkdir(parents=True, exist_ok=True)
    for f in adir.glob("*"):
        f.unlink()
    dl = body.get("download") or ""
    m = CAP_RE.search(dl)
    if m:
        (adir / "evidence.zip").write_bytes(_get(m.group(1)))
    contract = adir / "contract.json"
    contract.write_text(json.dumps(body))
    # solve
    env = dict(os.environ, PYTHONPATH=str(HW))
    r = subprocess.run([sys.executable, str(HW / solver_rel / "solve.py"),
                        "--contract", str(contract), "--artifacts", str(adir)],
                       capture_output=True, text=True, timeout=30, env=env)
    answers = json.loads(r.stdout.strip().splitlines()[-1])
    t_solved = time.time()
    # confirm it's wrong, then binary-search
    full = _post({"op": "submit", "challenge": cid, "answers": answers})
    fk = str(full.get("result", "")).lower()
    out = {"full_result": fk, "phases": {"solve": round(t_solved - t0, 2)}}
    if fk in ("correct", "accepted") and not full.get("remaining"):
        out["wrong"] = []
        keep = HW / ".run" / "variants" / str(body.get("attempt_id", "x"))
        keep.mkdir(parents=True, exist_ok=True)
        for f in adir.glob("*"):
            (keep / f.name).write_bytes(f.read_bytes())
        (keep / "answers.json").write_text(json.dumps(answers))
        print(json.dumps(out)); return

    def judge(subset):
        res = _post({"op": "submit", "challenge": cid, "answers": {k: answers[k] for k in subset}})
        return str(res.get("result", "")).lower()

    # find ALL wrong fields by recursive subset narrowing
    wrong = []
    def narrow(group):
        if not group:
            return
        if judge(group) in ("correct", "accepted"):
            return  # whole group correct
        if len(group) == 1:
            wrong.append(group[0]); return
        mid = len(group) // 2
        narrow(group[:mid]); narrow(group[mid:])
    cand = [a for a in ids if a in answers]
    narrow(cand)
    out["wrong"] = [[a, answers.get(a)] for a in wrong]
    # For closed-vocabulary fields, try the remaining values on this SAME attempt (same variant) so we learn
    # the right label, not just that the solver's was wrong.
    VOCAB = {"-expansion": ["percent", "delayed", "call_double", "for_indirect"],
             "-control": ["direct", "errorlevel_guard", "goto_dispatch", "call_subroutine", "if_guard"]}
    fixed = {}
    for aid, val in out["wrong"]:
        for suf, vocab in VOCAB.items():
            if aid.endswith(suf):
                for alt in vocab:
                    if alt == val:
                        continue
                    res = _post({"op": "submit", "challenge": cid, "answers": {aid: alt}})
                    if str(res.get("result", "")).lower() in ("correct", "accepted"):
                        fixed[aid] = alt
                        break
    out["fixed"] = fixed
    # keep this variant's bytes for offline analysis
    keep = HW / ".run" / "variants" / str(body.get("attempt_id", "x"))
    keep.mkdir(parents=True, exist_ok=True)
    for f in adir.glob("*"):
        (keep / f.name).write_bytes(f.read_bytes())
    (keep / "answers.json").write_text(json.dumps({**answers, **fixed}))
    (keep / "unfixed.json").write_text(json.dumps([a for a, _ in out["wrong"] if a not in fixed]))
    out["missing"] = [a for a in ids if a not in answers]
    out["elapsed"] = round(time.time() - t0, 2)
    print(json.dumps(out))


if __name__ == "__main__":
    main()
