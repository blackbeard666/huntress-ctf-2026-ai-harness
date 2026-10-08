# HELP — day08 scripting-lost-in-translation / time_trial

There's nothing to fix in the solver. The timed start returned HTTP 503 `{"error":"training_rotation_invalid"}`. It failed after 4 retries (see `time_trial/log.jsonl` op=start and `time_trial/last_timed.json`: attempt_id null, no window). No variant artifact was ever downloaded. `time_trial/contract.json` is only the 409 `start_required` status body. So `hctf solver-run .../time_trial` reports "no contract/artifacts for this mode yet", and that produced the "solver did not produce all answers" failure. The same error hit metadata-whats-in-the-box and mobile-cleartext-session today.

Verified offline:
- `hctf solver-test script-analysis-day-08-cross-language-iocs`: ok for all 6 cases. That covers the Day 8 single (615/615, GM-verified) and five Day 7 TT/Mastery variants (469 or 938 fields each), with 0 diffs.
- I ran solve.py with the TT contract's 615 questions against the single's bytes: 615/615 answered, all equal to the GM-verified single answers, in about 1.3 s.

Action for the orchestrator: retry the time_trial start. The `training_rotation_invalid` error comes from the GM/rotation side, not from the solver.
