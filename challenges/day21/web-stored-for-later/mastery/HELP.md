# Live attempt 82740ce5 -- already CORRECT (nothing left to do; gate bookkeeping gap)

- `hctf status web-exploitation-day-07-stored-xss/mastery` -> `result: CORRECT`, `accepted_ids: [proof-1, proof-2]`,
  solved at 2026-10-21T13:07:19.325Z, flag `8b4ed02e412efd8e51befd766ff39367`.
- proof-2 = `proof_72f79da7342c4acf8b87971d90b22f8b`, read from Target 2's board: the solver's stored payload
  (fetch `/staff-ba832ab0` -> POST `/api/postcards/{id}/receipt-30f87c`) had fired in the moderator browser after the
  solver's 12 s poll window ended; the receipt appeared on messages 1-3.
- Why the stop gate didn't release: the first submit returned HTTP 503 `temporarily_unavailable` (kind `error`) even
  though the GM registered the solve; the retry returned `already_solved`. `stop_gate.py` (live stage) only counts
  `accepted`/`correct` rows in `submissions.jsonl`, so it never saw the solve.

## Proposed lib additions
- stop_gate / `hctf submit`: treat `already_solved` for the owed attempt as done (or confirm it with `op=status`), and
  after a 503 on submit, check status before retrying.
- solver: lengthen the moderator-receipt poll for untimed attempts, or re-read the board at the end of the run (the
  receipt landed just after the 12 s window).
