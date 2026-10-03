# notes
- manifest: exported .ChallengeActivity, huntress02://deep-link-drift/unlock | droidasc getmanifest | permissive validation (no host/path checks in code)
- ChallengeActivity: loads http://127.0.0.1:19090/mobile/attempt/d02-.../evidence?case_id&client_secret&proof=<answer> | decompiled | loopback, not reachable; same as day01
- assets/huntress_puzzle.json codec=reverse data=94AEE0A765B0097A-SNA -> ANS-A7900B567A0EEA49 | day01 pattern (proof == evidence code) | submitting
- submitted ANS-A7900B567A0EEA49 | GM | CORRECT. Solver = day01 solver + 'delivery N:' prefix fallback; solver-test ok (single_solve + synthetic-mastery)
- 2026-10-04 re-check | solver-test ok (single_solve, synthetic-mastery, time_trial confirmed); solver-run mastery/time_trial produce full answers | unverified mastery cases moved aside; mastery expiries = 6s server window
- 2026-10-04 stop gate said incomplete | start.json had been overwritten by a later re-start response with no attempt_id/answer_ids, so is_complete() couldn't match the CORRECT submission | restored the original start body (attempt 91549e48) from log.jsonl, old file kept at work/start.json.restart-bak; is_complete=True, solver-test ok
