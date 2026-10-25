"""Verify a web class plugin draft against a live target and promote it into lib/web/handlers/ atomically.

    .venv/bin/python -m lib.web.plugin $TMPDIR/day25_web_<slug>.py <target url>          # verify + promote
    .venv/bin/python -m lib.web.plugin $TMPDIR/day25_web_<slug>.py <target url> --no-promote

D25 post-mortem (Track D2): the web single's proof was found by hand and a separate codify worker wrote the plugin
84-159 s later -- always too late for the Time Trial, and one runner imported a plugin file mid-edit (it imported fine,
but its exploit was half written). Now the single's worker writes the plugin as a DRAFT (its own $TMPDIR, never the
handlers dir), runs it here, submits the proof this prints, and the draft is promoted only after it produced a proof
on a live target: os.replace of a complete file, so the timed runners (fresh solve.py processes that glob
lib/web/handlers/*.py at import) see the old plugin or the new one, never half of one, and never an unverified one.

Checks, in order (exit code):
  2  the draft is not a plugin: stem `dayNN_web_<slug>`, imports, KEY_MAP [(regex, stem)] + HANDLERS {stem: callable}
  3  no KEY_MAP pattern matches a KEY of the target's /api/clues (the generic solver would never dispatch to it)
  1  the handler returned no proof_<hex> within --timeout s
  0  proof printed (`PROOF proof_...`) and, unless --no-promote, the draft promoted (`PROMOTED <path>`)
The last stdout line is a JSON summary. Plumbing only (load, dispatch check, timed call, atomic copy): the exploit
itself is the worker's code.
"""
import importlib.util
import json
import os
import re
import shutil
import sys
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from lib import websolve  # noqa: E402

STEM_RE = re.compile(r"^day\d\d_web_[a-z0-9_]+$")
HANDLERS_DIR = Path(os.environ.get("HCTF_WEB_PLUGIN_DIR") or (Path(__file__).resolve().parent / "handlers"))
BACKUP_DIR = ROOT / ".run" / "web_plugins"


def load_draft(path):
    """(module, problems[]) for a draft file, imported under a private name (never lib.web.handlers.<stem>, so the
    dispatcher's own module cache is untouched)."""
    path = Path(path)
    probs = []
    if not STEM_RE.match(path.stem):
        probs.append(f"file name {path.name!r}: must be dayNN_web_<slug>.py (the harness's plugin name for the chain)")
    try:
        spec = importlib.util.spec_from_file_location(f"_webplugin_draft_{path.stem}_{os.getpid()}", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
    except Exception as e:  # noqa: BLE001 - any import failure is the finding
        return None, probs + [f"import failed: {e!r}"[:400]]
    km = list(getattr(mod, "KEY_MAP", None) or [])
    hs = dict(getattr(mod, "HANDLERS", None) or {})
    if not callable(hs.get(path.stem)):
        probs.append(f"HANDLERS must map {path.stem!r} to the exploit function")
    mine = [e for e in km if isinstance(e, (tuple, list)) and len(e) == 2 and e[1] == path.stem]
    if not mine:
        probs.append(f"KEY_MAP needs at least one (r\"<clue KEY regex>\", {path.stem!r}) entry")
    for e in mine:
        try:
            re.compile(e[0])
        except (re.error, TypeError) as x:
            probs.append(f"KEY_MAP regex {e[0]!r}: {x}")
    return mod, probs


def key_hits(mod, stem, clues):
    """(concept keys, furniture keys) of the target's /api/clues that the draft's KEY_MAP maps to `stem` -- the same
    rule as lib.web.handlers.for_key (KEY_COMPANIONS honoured: a gated pattern needs its companion key present)."""
    keys = [k for k in (clues if isinstance(clues, dict) else {})]
    comp = dict(getattr(mod, "KEY_COMPANIONS", None) or {})
    concept, furn = [], []
    for pat, name in [e for e in (getattr(mod, "KEY_MAP", None) or []) if len(e) == 2]:
        if name != stem:
            continue
        need = comp.get(pat)
        if need and not any(re.search(need, k, re.I) for k in keys):
            continue
        for k in keys:
            if re.search(pat, k, re.I):
                (furn if k in websolve.COMMON_KEYS else concept).append(k)
    return sorted(set(concept)), sorted(set(furn))


def run_handler(fn, base, clues, timeout):
    """fn(base, clues) bounded by `timeout` s (HCTF_SOLVE_DEADLINE caps every websolve.fetch inside it). -> (value,
    error string or None, seconds)."""
    out = {}
    old = os.environ.get("HCTF_SOLVE_DEADLINE")
    os.environ["HCTF_SOLVE_DEADLINE"] = str(time.time() + timeout)

    def go():
        try:
            out["v"] = fn(base, clues)
        except Exception as e:  # noqa: BLE001
            out["e"] = repr(e)[:400]
    t0 = time.time()
    th = threading.Thread(target=go, daemon=True)
    th.start()
    th.join(timeout + 1.0)
    if old is None:
        os.environ.pop("HCTF_SOLVE_DEADLINE", None)
    else:
        os.environ["HCTF_SOLVE_DEADLINE"] = old
    if th.is_alive():
        return None, f"no result within {timeout:g}s", round(time.time() - t0, 2)
    return out.get("v"), out.get("e"), round(time.time() - t0, 2)


def promote(draft, dest_dir=None):
    """Copy a verified draft over lib/web/handlers/<stem>.py atomically (tmp file in the same dir + os.replace); the
    plugin it replaces is kept under .run/web_plugins/. Stale bytecode of that name is dropped. -> the final path."""
    draft = Path(draft)
    dest_dir = Path(dest_dir or HANDLERS_DIR)
    final = dest_dir / f"{draft.stem}.py"
    if final.exists():
        try:
            if final.read_bytes() == draft.read_bytes():
                return final
            BACKUP_DIR.mkdir(parents=True, exist_ok=True)
            shutil.copy2(final, BACKUP_DIR / f"{draft.stem}.{time.strftime('%Y%m%dT%H%M%S')}.py")
        except OSError:
            pass
    tmp = dest_dir / f".{draft.stem}.{os.getpid()}.tmp"
    tmp.write_bytes(draft.read_bytes())
    os.replace(tmp, final)
    for pyc in (dest_dir / "__pycache__").glob(f"{draft.stem}.*.pyc"):
        try:
            pyc.unlink()
        except OSError:
            pass
    return final


def verify(draft, base, timeout=30.0, do_promote=True, dest_dir=None, clues=None):
    """The whole check (see the module docstring). -> summary dict with `rc`."""
    draft = Path(draft)
    rep = {"draft": str(draft), "plugin": draft.stem, "target": base, "rc": 2, "problems": []}
    mod, probs = load_draft(draft)
    if probs:
        rep["problems"] = probs
        return rep
    base = base if base.endswith("/") else base + "/"
    if not isinstance(clues, dict):
        clues, _key = websolve.clues(base)
    rep["clue_keys"] = sorted(clues)
    concept, furn = key_hits(mod, draft.stem, clues)
    rep.update(concept_keys=concept, furniture_keys=furn)
    if not (concept or furn):
        rep.update(rc=3, problems=[f"KEY_MAP matches none of the target's /api/clues keys {sorted(clues)}: the "
                                   "solver would never dispatch to it (key on a concept KEY of this class)"])
        return rep
    if not concept:
        rep["problems"].append("KEY_MAP matches only kit furniture keys (framework / feature_route / current_role "
                               "...): prefer the class's concept key")
    v, err, secs = run_handler(mod.HANDLERS[draft.stem], base, clues, timeout)
    rep["seconds"] = secs
    p = websolve.PROOF_RE.fullmatch(str(v).strip()) if v else None
    if not p:
        rep.update(rc=1, problems=rep["problems"] + [err or f"handler returned {str(v)[:120]!r}, not a proof_<hex>"])
        return rep
    rep.update(rc=0, proof=p.group())
    if do_promote:
        rep["promoted"] = str(promote(draft, dest_dir))
    return rep


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("draft", help="the draft plugin file (dayNN_web_<slug>.py, in your $TMPDIR)")
    ap.add_argument("target", help="a live target URL (contract targets[].url) of this class")
    ap.add_argument("--no-promote", action="store_true", help="verify only")
    ap.add_argument("--timeout", type=float, default=30.0)
    a = ap.parse_args(argv)
    rep = verify(a.draft, a.target, timeout=a.timeout, do_promote=not a.no_promote)
    for pr in rep.get("problems") or []:
        print(f"PROBLEM {pr}")
    if rep.get("proof"):
        print(f"PROOF {rep['proof']}")
    if rep.get("promoted"):
        print(f"PROMOTED {rep['promoted']} (the timed modes' solver dispatches to it on every fresh target)")
    print(json.dumps(rep))
    return rep["rc"]


if __name__ == "__main__":
    sys.exit(main())
