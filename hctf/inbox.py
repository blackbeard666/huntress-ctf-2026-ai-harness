"""Mid-run messages from the harness to a running Single Solve worker (stdlib only: the hook imports it on every tool call).

The WarmWorker's stream-json stdin closes after "go", so anything the harness learns LATER (the reuse race banked 119/120
fields, the prior-solver dry run finished, a spelling convention) lands here, in `<chal dir>/inbox.jsonl`, and
.claude/hooks/nudge.py hands unread entries to the worker as PostToolUse `additionalContext` on its next tool call
("HARNESS UPDATE (GM facts): ..."). The orchestrator resets the inbox at every worker launch.
"""
import json
import os
import time
from pathlib import Path

NAME = "inbox.jsonl"


def post(chal_dir, text, key=""):
    """Append one message (one line of JSON; appends of a short line are atomic enough for one writer + one reader)."""
    if not text:
        return
    p = Path(chal_dir) / NAME
    with open(p, "a") as f:
        f.write(json.dumps({"key": key, "ts": time.time(), "text": text}, ensure_ascii=False) + "\n")


def texts(chal_dir):
    """Every message posted so far (all readers), oldest first."""
    try:
        lines = (Path(chal_dir) / NAME).read_text().splitlines()
    except OSError:
        return []
    out = []
    for line in lines:
        try:
            out.append(json.loads(line).get("text") or "")
        except ValueError:
            continue
    return [t for t in out if t]


def reset(chal_dir):
    """Drop everything (a new worker launch starts with an empty inbox; its go text carries what was known)."""
    for p in [Path(chal_dir) / NAME, *Path(chal_dir).glob(".inbox-*")]:
        try:
            p.unlink()
        except OSError:
            pass


def unread(chal_dir, reader):
    """Entries not yet delivered to `reader` (a per-worker cursor file holds the byte offset already read)."""
    p = Path(chal_dir) / NAME
    cur = Path(chal_dir) / f".inbox-{reader}"
    try:
        data = p.read_bytes()
    except OSError:
        return []
    try:
        off = int(cur.read_text() or 0)
    except (OSError, ValueError):
        off = 0
    if off >= len(data):
        return []
    end = data.rfind(b"\n") + 1            # only whole lines (a writer may be mid-append)
    if end <= off:
        return []
    out = []
    for line in data[off:end].splitlines():
        try:
            out.append(json.loads(line))
        except ValueError:
            continue
    tmp = cur.with_name(cur.name + f".{os.getpid()}")
    tmp.write_text(str(end))
    os.replace(tmp, cur)
    return out
