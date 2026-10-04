# Solver: Day 03 mobile-android — Intent Injection
Copied from Day 02 (Deep Link Drift): identical app shape. Exported `.ChallengeActivity` on
`huntress03://intent-injection/unlock` relays nested-Intent extras (`answer`, `case_id`) to a loopback `.../evidence`
URL with `client_secret` + `proof`. Answer == decoded `assets/huntress_puzzle.json` `data` (codec base64 on single_solve).
CORRECT on single_solve. cases/synthetic-mastery: 2 sets built from the real APK with base64/reverse puzzle codecs,
literal and plain 'delivery N:' filenames. Time Trial / Mastery contracts name intent_injection_{time_trial,mastery_0N}.apk.
