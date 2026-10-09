"""Cost of one Claude Code stream-json run (runs ON Homebase: `python3 hbcost.py <log>` -> {"usd", "turns", "final"}).
The result line's total_cost_usd when the run finished; otherwise (killed mid-run) the per-message usage priced at Opus
4.x Bedrock list rates -- the same arithmetic the result line uses (verified on a smoke run: $0.2186575 both ways)."""
import json
import sys

PRICE = {"in": 5e-6, "out": 25e-6, "cw": 6.25e-6, "cr": 0.5e-6}   # $/token, Opus 4.5-4.7 list


def cost(path):
    usd, turns, seen = 0.0, 0, set()
    try:
        lines = open(path, errors="replace").read().splitlines()
    except OSError:
        return {"usd": 0.0, "turns": 0, "final": False}
    for line in reversed(lines):
        if line.startswith("{") and '"type":"result"' in line.replace(" ", ""):
            try:
                d = json.loads(line)
                return {"usd": float(d.get("total_cost_usd") or 0), "turns": d.get("num_turns"), "final": True}
            except ValueError:
                break
    for line in lines:
        if not line.startswith("{"):
            continue
        try:
            d = json.loads(line)
        except ValueError:
            continue
        m = d.get("message") or {}
        if d.get("type") != "assistant" or not m.get("usage") or m.get("id") in seen:
            continue
        seen.add(m.get("id"))
        u = m["usage"]
        turns += 1
        usd += (u.get("input_tokens", 0) * PRICE["in"] + u.get("output_tokens", 0) * PRICE["out"]
                + u.get("cache_creation_input_tokens", 0) * PRICE["cw"] + u.get("cache_read_input_tokens", 0) * PRICE["cr"])
    return {"usd": round(usd, 4), "turns": turns, "final": False}


if __name__ == "__main__":
    print(json.dumps(cost(sys.argv[1])))
