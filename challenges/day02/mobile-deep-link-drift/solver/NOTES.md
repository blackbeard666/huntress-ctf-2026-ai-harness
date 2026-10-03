# Solver: Day 02 mobile-android — Deep Link Drift
Same structure as Day 01 (Exported Trust): exported `.ChallengeActivity` on `huntress02://deep-link-drift/unlock`
(permissive validation) loads loopback `.../evidence?case_id=..&client_secret=..&proof=<answer>`. The backend
answer code == decoded `assets/huntress_puzzle.json` `data` (codec `reverse` here). Confirmed CORRECT on single_solve.
Solver reads the asset from each APK (Mastery `delivery N: ...apk` handled by lib.common.find_artifact) and decodes per codec.
Variant proof: cases/synthetic-mastery (2 sets, base64+reverse codecs, literal and plain 'delivery N:' filenames).
