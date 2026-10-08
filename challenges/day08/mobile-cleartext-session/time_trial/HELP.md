# HELP: time_trial blocked by GM, not by the solver

- All 3 `start` calls for `mobile-android-day-08-cleartext-session/time_trial` (log.jsonl, 13:01Z-13:04Z) returned
  HTTP 503 `{"error": "training_rotation_invalid"}` (after 4 retries / 40 s); every `artifact` call -> 409 `start_required`.
- So no variant was ever handed out. There is no `variant-*`/`auto-*` case and no GM verdict, and
  `hctf solver-run .../time_trial` exits 4 ("has not been started"). The success condition can't be met offline.
- Solver status: `hctf solver-test` passes (single_solve 0.13 s). Running solve.py on the TT contract with the single's
  APK renamed to `cleartext_session_time_trial.apk` returns `{"answer": "ANS-..."}` for the only answer_id.
- Needed: the orchestrator should stop treating `training_rotation_invalid` as a solver failure (it has now started
  3 generalize cycles in a row). Retry `start` later or escalate it to the organizers as a GM-side rotation error.
