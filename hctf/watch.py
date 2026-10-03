"""Live views over the running harness, built from chain.json + each worker's stream-json log.

hctf watch        - full-screen board: every challenge x mode, stage, elapsed, and the agent's current action.
hctf tail <chal>  - follow one agent's reasoning and tool calls as they stream.
"""
import glob
import json
import os
import time
from pathlib import Path

from . import paths

C = {"dim": "\033[2m", "b": "\033[1m", "grn": "\033[32m", "yel": "\033[33m", "red": "\033[31m",
     "cyn": "\033[36m", "mag": "\033[35m", "rst": "\033[0m", "clr": "\033[2J\033[H"}


def _latest_worker_log(chal_root):
    logs = glob.glob(str(chal_root / "*" / "worker-*.log"))
    return max(logs, key=os.path.getmtime) if logs else None


def _last_action(log, tail_bytes=20000):
    """The most recent meaningful event from a stream-json worker log: tool call or assistant text."""
    try:
        with open(log, "rb") as f:
            f.seek(max(0, os.path.getsize(log) - tail_bytes))
            lines = f.read().decode("utf-8", "replace").splitlines()
    except OSError:
        return ""
    for line in reversed(lines):
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            o = json.loads(line)
        except ValueError:
            continue
        if o.get("type") == "result":
            return f"done: {str(o.get('result', ''))[:80]}"
        if o.get("type") == "assistant":
            for blk in reversed(o.get("message", {}).get("content", [])):
                if blk.get("type") == "tool_use":
                    inp = json.dumps(blk.get("input", {}))[:90]
                    return f"{blk.get('name')} {inp}"
                if blk.get("type") == "text" and blk.get("text", "").strip():
                    return "think: " + blk["text"].strip().replace("\n", " ")[:90]
    return ""


def _rows():
    rows = []
    for p in sorted(paths.CHALLENGES.glob("day*/*/chain.json")):
        s = json.loads(p.read_text())
        root = p.parent
        stage = s.get("stage", "")
        action = ""
        upd = s.get("updated", "")
        if s.get("worker"):
            log = _latest_worker_log(root)
            if log:
                action = _last_action(log)
        rows.append({"chal": str(root.relative_to(paths.CHALLENGES)), "lane": s.get("lane", ""),
                     "stage": stage, "worker": s.get("worker") or "", "tt": s.get("time_trial_result", ""),
                     "mast": s.get("mastery_result", ""), "action": action, "updated": upd})
    return rows


def _color_stage(stage):
    if stage == "done":
        return C["grn"] + stage + C["rst"]
    if "blocked" in stage or "help" in stage or "crashed" in stage:
        return C["red"] + stage + C["rst"]
    if stage:
        return C["yel"] + stage + C["rst"]
    return stage


def watch(interval=2.0):
    try:
        while True:
            rows = _rows()
            out = [C["clr"], f"{C['b']}Huntress harness — live{C['rst']}  {time.strftime('%H:%M:%S')}   "
                   f"(done {sum(r['stage']=='done' for r in rows)}/{len(rows)})", ""]
            out.append(f"{C['dim']}{'challenge':<40}{'stage':<22}{'tt':<9}{'mast':<9}{'current action'}{C['rst']}")
            for r in sorted(rows, key=lambda r: r["chal"]):
                chal = (r["chal"][:37] + "…") if len(r["chal"]) > 38 else r["chal"]
                act = r["action"]
                if act.startswith("think:"):
                    act = C["cyn"] + act + C["rst"]
                elif act.startswith("done:"):
                    act = C["grn"] + act + C["rst"]
                elif act:
                    act = C["mag"] + act + C["rst"]
                stage = _color_stage(r["stage"])
                pad = 22 + (len(stage) - len(r["stage"]))
                out.append(f"{chal:<40}{stage:<{pad}}{r['tt']:<9}{r['mast']:<9}{act}")
            out.append("")
            out.append(f"{C['dim']}refresh {interval}s · Ctrl-C to exit · `hctf tail <challenge>` for one agent's full stream{C['rst']}")
            print("\n".join(out), flush=True)
            time.sleep(interval)
    except KeyboardInterrupt:
        print()


def tail(cid):
    """Follow the newest worker log for a challenge, pretty-printing thinking + tool calls live."""
    root = paths.challenge_root(cid)
    log = None
    for _ in range(60):
        log = _latest_worker_log(root)
        if log:
            break
        time.sleep(1)
    if not log:
        print(f"no worker log yet for {cid}")
        return
    print(f"{C['b']}tail {Path(log).relative_to(paths.ROOT)}{C['rst']}  (Ctrl-C to exit)\n")
    try:
        with open(log, "r", encoding="utf-8", errors="replace") as f:
            while True:
                line = f.readline()
                if not line:
                    time.sleep(0.4)
                    continue
                line = line.strip()
                if not line.startswith("{"):
                    continue
                try:
                    o = json.loads(line)
                except ValueError:
                    continue
                t = o.get("type")
                if t == "assistant":
                    for blk in o.get("message", {}).get("content", []):
                        if blk.get("type") == "text" and blk.get("text", "").strip():
                            print(f"{C['cyn']}🧠 {blk['text'].strip()}{C['rst']}")
                        elif blk.get("type") == "tool_use":
                            print(f"{C['mag']}⚙ {blk.get('name')}{C['rst']} {json.dumps(blk.get('input', {}))[:200]}")
                elif t == "user":
                    for blk in o.get("message", {}).get("content", []):
                        if isinstance(blk, dict) and blk.get("type") == "tool_result":
                            c = blk.get("content")
                            txt = c if isinstance(c, str) else json.dumps(c)
                            print(f"{C['dim']}  → {txt[:200].strip()}{C['rst']}")
                elif t == "result":
                    print(f"{C['grn']}✔ {str(o.get('result',''))[:300]}{C['rst']}")
    except KeyboardInterrupt:
        print()
