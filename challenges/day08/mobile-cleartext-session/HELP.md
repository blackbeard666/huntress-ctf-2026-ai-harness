# HELP: time_trial "solver did not produce all answers" is an infrastructure failure, not a solver bug

- `time_trial/log.jsonl`: `start` returned HTTP 503 `{"error": "training_rotation_invalid"}` after 4 retries
  (`last_timed.json`: result training_rotation_invalid, attempt_id null). The following `artifact` call returned
  409 `start_required`.
- So no variant APK was downloaded and no `variant-*`/`auto-*` case exists; the solver had no bytes to answer from.
- `hctf solver-test mobile-android-day-08-cleartext-session` passes (single_solve, 0.13 s).
- `hctf solver-run .../time_trial` cannot run: "no contract/artifacts for this mode yet (it has not been started)".
- Needed: the orchestrator should retry `start` for time_trial once the GM training rotation is valid again; the
  existing solver should then be run on the real variant. Solver left unchanged (no evidence of a wrong field).

## Update (second generalize, 2026-10-08T13:03Z)
- Same again: `time_trial/log.jsonl` shows a second `start` at 13:03:28Z -> 503 `training_rotation_invalid` (4 retries),
  then `artifact` -> 409 `start_required`. Still no variant bytes or `auto-*`/`variant-*` case. The GM verdict's
  rejected-field list is empty (`[]`), which matches "nothing was ever submitted".
- `hctf solver-test` still passes (single_solve, 0.17 s). The solver already handles the TT artifact name and the
  Mastery `delivery N:` sets by sha256 pairing. Solver left unchanged.
- Blocker: the GM training rotation for this challenge. A third generalize cycle won't help until `start` succeeds.
