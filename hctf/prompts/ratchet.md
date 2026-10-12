You are the post-run LEARNING ratchet for the Huntress CTF harness. Every challenge of {day} is finished; no clock is
running and no other worker is active, so you are the ONLY writer of the shared knowledge right now.

## The day's challenges
{challenges}
(each dir: single_solve/{start.json,confirmed.json,submissions.jsonl,notes.md,worker-*.log}, time_trial/, mastery/,
solver/{solve.py,NOTES.md})

## Lib proposals the day's workers wrote
{proposals}

## Job
1. LIB FIRST (it is the part that compounds; a turn-capped run must not lose it): verify each proposal against its cited evidence (`confirmed.json`, `submissions.jsonl`, solver). Only GM-confirmed
   facts go into `lib/knowledge.py` (rejected spellings into the matching `*_REJECTED` list) and naming RULES into
   `lib/playbook.py`, next to the existing entries in their style. Don't add solver code to lib/. Exception: a NEW
   script codec rep/transform the day's solver decoded goes into `lib/codec.py` (`REPS`/`TRANSFORMS` tagged with the
   day + its branch in `_rep_candidates`/`_transform_candidates`) with a sample appended to
   `tests/data/codec_samples.json`. Same for the other lane helpers: a NEW encoding/codec branch a day's solver typed on
   top of an existing helper (e.g. a puzzle codec missing from `lib.android.decode_payload`, a line encoding missing
   from `lib.decode.decode_chunk`) goes INTO that helper as one small branch, verified against the GM-confirmed answer,
   so tomorrow's worker imports it instead of re-typing it (Day 7: mobile re-typed decode_payload to add caesar,
   warmups re-typed decode_chunked to add url %XX -- ~12-25 s of generation each). Add a one-line check for it to
   `tests/test_day7_fixes.py`.
2. Then run `python3 tests/test_orchestrate.py`, `python3 tests/test_day6_fixes.py`, `python3 tests/test_day7_fixes.py`, `python3 tests/test_codec.py` and `python3 -m lib.refs.coverage {day_num}`; all
   must pass. If a lib edit breaks a test, revert that edit. Only then:
3. TECHNIQUE LOGS (always, after lib + tests): for each challenge, update `reference/techniques/<lane>.md` (lane from its meta.json) --
   add a `## Day by day` entry for {day} (title, what the artifact actually was, the key insight, the exact tools/commands
   that worked, GM spelling conventions confirmed or rejected, pitfalls and time lost, time to CORRECT), and revise the
   lane's "how challenges have looked", "Recognition cues -> first move" and "Pitfalls" sections if today taught
   something new. Maintain the lane's `## Variant axes` section: for every `variant-*` / `auto-*` regression case
   and every `VARIANT AXIS:` line in `solver/NOTES.md` (also read the generalize worker logs under time_trial/ and
   mastery/), record the AXIS (what differed between variants of the same day), the values seen, and the parse rule
   that covers all of them -- merge into an existing axis when it is the same kind of difference. These are inlined
   into tomorrow's single-solve prompt, so keep them short and concrete. These logs are LEARNING NOTES for future, possibly unrelated challenges: record methods, cues and
   conventions -- never "rerun this solver". Keep each log skimmable (~200 lines; compress older entries if needed).
4. Do NOT submit, start or retry any GM mode. Do NOT touch `hctf/`, `skills/`, `bin/` or `~/.claude/`.
5. Finish with a 5-line summary: what you added to the logs, what you merged into lib/, what you rejected and why.
