You are the post-run knowledge ratchet for the Huntress CTF harness. Every challenge of {day} is finished; no clock is
running and no other worker is active, so you are the ONLY writer of the shared library right now.

## Inputs
{proposals}

## Job
1. For each proposal above, verify it against the evidence it cites (the challenge's `confirmed.json`, `solver/`,
   `submissions.jsonl`). Only GM-confirmed facts go in — never a guess or a rejected spelling (rejected ones go in the
   matching `*_REJECTED` list, if that file keeps one).
2. Merge confirmed label spellings / format laws into `lib/knowledge.py` (and `lib/playbook.py` when it is a naming
   RULE for a lane), next to the existing entries of that family, in their style. Move reusable helpers the proposals
   name into the right `lib/` module only if a challenge solver already uses them unchanged; do not rewrite solvers.
3. Run `python3 tests/test_orchestrate.py`, `python3 tests/test_day6_fixes.py` and `python3 -m lib.refs.coverage {day_num}`; all
   must pass / report no regressions. If an edit breaks a test, revert that edit.
4. Do NOT submit, start or retry any GM mode. Do NOT touch `hctf/`, `skills/`, `bin/` or `~/.claude/`.
5. Finish with a 5-line summary: what you merged, what you rejected and why.
