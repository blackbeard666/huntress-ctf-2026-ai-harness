#!/usr/bin/env python3
"""Generic web-exploitation solver -- the web LANE SEED (B2). Dispatches on GET /api/clues and solves any challenge of
the known kit with NO per-day code, so a web day needs no drop-time generalize. One solver serves single / time_trial /
every Mastery target.

    solve.py --contract <contract.json> --artifacts <dir>   ->  {answer_id: proof} JSON on the last line

Do NOT rewrite this. For a brand-new clue KEY (a vuln class never seen), add a handler in lib/web/handlers/ and map
its key there; the `default` ladder already makes a real attempt meanwhile. The post-run ratchet folds a verified new
handler back in. Exploit logic lives in lib/web (dispatch) + lib/web/handlers (per-class) -- standard HTTP, LLM-first."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from lib import web  # noqa: E402

if __name__ == "__main__":
    web.main()
