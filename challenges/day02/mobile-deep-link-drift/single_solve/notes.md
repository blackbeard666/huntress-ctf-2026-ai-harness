# notes
- manifest: exported .ChallengeActivity, huntress02://deep-link-drift/unlock | droidasc getmanifest | permissive validation (no host/path checks in code)
- ChallengeActivity: loads http://127.0.0.1:19090/mobile/attempt/d02-.../evidence?case_id&client_secret&proof=<answer> | decompiled | loopback, not reachable; same as day01
- assets/huntress_puzzle.json codec=reverse data=94AEE0A765B0097A-SNA -> ANS-A7900B567A0EEA49 | day01 pattern (proof == evidence code) | submitting
- submitted ANS-A7900B567A0EEA49 | GM | CORRECT. Solver = day01 solver + 'delivery N:' prefix fallback; solver-test ok (single_solve + synthetic-mastery)
