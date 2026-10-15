"""Prebuild fixtures for the mobile and script lanes (hctf/prebuild.py gate). Offline, no GM.

tests/data/android_fixtures/<name>.json + <name>.apk (or .zip):
    {"entry": "extract_answer" | "puzzle_candidates" | "raw_entry_scan" | "dex_strings", "expected": "ANS-<16 hex>" | null,
     "decoy": bool, "generator_cmd": "...", "oracle_cmd": "..."}
  The named lib.android function runs on the fixture; `expected` must be its answer (extract_answer) or among its hits;
  a decoy (expected null) must yield no ANS token. In-window entries (all but extract_answer) must finish in < 2 s.
tests/data/script_fixtures/<name>.json (+ optional <name>.txt holding the script source):
    {"text" | file sibling, "expected_plain": "...", "decoy": bool, "generator_cmd", "oracle_cmd"}  -> one of
      lib.codec.find_codecs(text)'s `plain` readings equals expected_plain (decoy: none does / expected_plain null), or
    {"material", "rep", "transform", "key", "expected"}                                         -> lib.codec.decode(...)
Every lane needs provenance (generator_cmd / oracle_cmd) and >= 1 decoy once it has >= 2 fixtures.

Run:  source bin/env.sh && python3 tests/test_lane_fixtures.py      (exit 0 = all pass)
"""
import json
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from lib import android, codec  # noqa: E402

ANS = re.compile(r"ANS-[0-9A-Fa-f]{16}")
probs = []


def need_provenance(lane, fx_list):
    for name, fx in fx_list:
        if not (fx.get("generator_cmd") and fx.get("oracle_cmd")):
            probs.append(f"{lane}/{name}: needs generator_cmd + oracle_cmd provenance")
        elif re.search(r"lib[./](android|codec)", str(fx.get("oracle_cmd"))):
            probs.append(f"{lane}/{name}: the oracle must be an independent reader, not lib.{lane}")
    if len(fx_list) >= 2 and not any(fx.get("decoy") for _, fx in fx_list):
        probs.append(f"{lane}: fixtures need at least one decoy (\"decoy\": true)")


# --- mobile ----------------------------------------------------------------------------------------------------------
adir = ROOT / "tests" / "data" / "android_fixtures"
mob = []
for fj in sorted(adir.glob("*.json")):
    if fj.name == "TARGETS.json":
        continue
    fx = json.loads(fj.read_text())
    mob.append((fj.stem, fx))
    apk = next((p for p in (fj.with_suffix(".apk"), fj.with_suffix(".zip")) if p.exists()), None)
    entry = fx.get("entry") or "extract_answer"
    fn = getattr(android, entry, None)
    if apk is None or fn is None:
        probs.append(f"android/{fj.name}: needs a sibling .apk/.zip and a lib.android entry (got {entry!r})")
        continue
    t0 = time.time()
    try:
        got = fn(str(apk))
    except Exception as e:  # noqa: BLE001
        probs.append(f"android/{fj.name}: {entry} raised {e!r}")
        continue
    dt = time.time() - t0
    if entry != "extract_answer" and dt > 2.0:
        probs.append(f"android/{fj.name}: {entry} took {dt:.2f}s (> 2 s in-window)")
    hits = [got] if isinstance(got, str) else [str(x) for x in (got or [])]
    tokens = {m.group(0).upper() for h in hits for m in ANS.finditer(h)}
    exp = fx.get("expected")
    if exp is None or fx.get("decoy"):
        if tokens:
            probs.append(f"android/{fj.name}: decoy yielded {sorted(tokens)[:3]}")
    elif str(exp).upper() not in tokens:
        probs.append(f"android/{fj.name}: {entry} -> {sorted(tokens)[:3] or hits[:2]}, expected {exp}")
need_provenance("android", mob)

# --- script ----------------------------------------------------------------------------------------------------------
sdir = ROOT / "tests" / "data" / "script_fixtures"
scr = []
for fj in sorted(sdir.glob("*.json")):
    if fj.name == "TARGETS.json":
        continue
    fx = json.loads(fj.read_text())
    scr.append((fj.stem, fx))
    try:
        if "material" in fx:
            got = codec.decode(fx["material"], fx.get("rep"), fx.get("transform"), fx.get("key"))
            exp = fx.get("expected")
            if fx.get("decoy") or exp is None:
                if got:
                    probs.append(f"script/{fj.name}: decoy decoded to {str(got)[:60]!r}")
            elif got != exp:
                probs.append(f"script/{fj.name}: decode -> {str(got)[:80]!r}, expected {str(exp)[:80]!r}")
            continue
        src = fx.get("text")
        if src is None:
            side = next((p for p in sorted(sdir.glob(fj.stem + ".*")) if p.suffix != ".json"), None)
            src = side.read_bytes().decode("utf-8", "replace") if side else None
        if src is None:
            probs.append(f"script/{fj.name}: needs `text`, a sibling source file, or material/rep/transform")
            continue
        t0 = time.time()
        plains = [c.get("plain") for c in codec.find_codecs(src) if c.get("plain")]
        if time.time() - t0 > 2.0:
            probs.append(f"script/{fj.name}: find_codecs took {time.time() - t0:.2f}s (> 2 s)")
        exp = fx.get("expected_plain")
        if fx.get("decoy") or exp is None:
            if exp is not None and exp in plains:
                probs.append(f"script/{fj.name}: decoy produced the expected plain")
        elif exp not in plains:
            probs.append(f"script/{fj.name}: find_codecs plains {[p[:40] for p in plains][:3]}, expected {exp[:60]!r}")
    except Exception as e:  # noqa: BLE001
        probs.append(f"script/{fj.name}: raised {e!r}")
need_provenance("script", scr)

if probs:
    print("\n".join(probs))
    raise SystemExit(1)
print(f"ok  lane fixtures: android {len(mob)}, script {len(scr)} (decoys + provenance checked)")
