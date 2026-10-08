# HELP — day08 metadata-whats-in-the-box / time_trial

There's nothing to fix in the solver. The timed start returned `training_rotation_invalid` (see `time_trial/last_timed.json`: attempt_id null, no window), so no variant artifact was downloaded. `hctf solver-run .../time_trial` therefore reports "no contract/artifacts for this mode yet", which caused the "solver did not produce all answers" failure.

Verified offline:
- `hctf solver-test metadata-forensics-day-08-whats-in-the-box`: ok, 12/12.
- solve.py run with the TT contract on the single's bytes: all 12 answer_ids answered and equal to the GM-confirmed single answers.
- solve.py run on all 9 Day-07 cases (the same field families, real TT/Mastery variants with 2 sets and nested drops): every answer_id answered, 0 diffs.

Action for the orchestrator: retry the time_trial start (the `training_rotation_invalid` error is on the GM/rotation side, not in the solver).

## Generalize cycle 2 (2026-10-08 21:0x)
Same situation again: `time_trial/last_timed.json` still shows `training_rotation_invalid`, attempt_id null, and there's no `variant-*`/`auto-*` case. `hctf solver-run .../time_trial` prints "no contract/artifacts for this mode yet (it has not been started)", so the "did not produce all answers" failure comes from the start being refused, not from the solver.
Re-verified: `hctf solver-test` ok 12/12 (0.15 s). The 5-set Mastery contract (`setN.` prefixes, `metadata-day-08-evidence-0N.zip`) gives 60/60 answers when run on per-set copies of the single's bytes.
The orchestrator needs to get a real timed attempt started (the rotation/start error is on the GM side). Another generalize pass without variant bytes can't change anything.
