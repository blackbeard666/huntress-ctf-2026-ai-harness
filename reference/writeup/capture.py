"""Phase 0 of the retrospective: snapshot perishable data (GM full list, Hall of Fame speed board).

Read-only GETs only. Output: reference/writeup/data/*.json
"""
import json
import os
import sys
import time
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
OUT = os.path.join(ROOT, "reference", "writeup", "data")
os.makedirs(OUT, exist_ok=True)

from hctf.cli import call  # noqa: E402  (same helper `hctf list` uses)

SB = "https://2026.huntress.ctf.games/api/speed-scoreboard"


def dump(name, obj):
    with open(os.path.join(OUT, name), "w") as f:
        json.dump(obj, f, indent=1)
    print(f"wrote {name}", file=sys.stderr)


def gm_list():
    days = {}
    for d in range(1, 32):
        env = call(None, "list", "--day", str(d))
        days[d] = env.get("body")
        n = len((env.get("body") or {}).get("challenges", []))
        print(f"day {d}: {n} entries", file=sys.stderr)
        time.sleep(0.3)
    env = call(None, "list", "--all")
    dump("gm_list_by_day.json", days)
    dump("gm_list_all.json", env.get("body"))


def scoreboard():
    for mode in ("time_trial", "mastery"):
        for view in ("rankings", "leaders"):
            rows, off, cap = [], 0, None
            while True:
                url = f"{SB}?mode={mode}&view={view}&limit=1000&offset={off}&sort=elapsed_ms&direction=asc"
                with urllib.request.urlopen(url, timeout=60) as r:
                    body = json.load(r)
                cap = body.get("captured_at", cap)
                page = body.get("rows", [])
                rows += page
                if len(page) < 1000:
                    break
                off += 1000
            dump(f"hof_{mode}_{view}.json", {"captured_at": cap, "rows": rows})
            print(f"{mode}/{view}: {len(rows)} rows", file=sys.stderr)


if __name__ == "__main__":
    what = sys.argv[1:] or ["gm", "hof"]
    if "hof" in what:
        scoreboard()
    if "gm" in what:
        gm_list()
