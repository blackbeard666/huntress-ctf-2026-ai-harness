# Solver: Day 01 mobile-android — Exported Trust

## Concept
The APK exports a deep-link Activity (`.ChallengeActivity`, scheme
`huntressNN://<host>/unlock`) that, when invoked with `answer` + `case_id`, attaches an
embedded `client_secret` and the `answer` as `proof` to a backend
`http://127.0.0.1:19090/mobile/attempt/<token>/evidence` call. The `proof` the app
sends is the value stored in `assets/huntress_puzzle.json`, and the backend's returned
evidence code equals that value (`ANS-` + 16 uppercase hex). The backend is the app's
on-device loopback and is not reachable from Homebase, so the challenge is solved
statically: the evidence code = the decoded puzzle `data`.

## What the solver does
1. For each question (routed by "evidence"/"exported" keywords), locate the APK via
   `lib.common.find_artifact` (handles the Mastery `delivery N: ...apk` names and sets).
2. Read `assets/huntress_puzzle.json` straight from the APK zip (no decompile — fast).
3. Decode `data` per the declared `codec` (plain/base64/base32/hex/rot13/reverse),
   extract the `ANS-<16hex>` pattern, uppercase, normalize.

## Variant axes handled
- package suffix, case reference, APK filename — never read; derived or irrelevant.
- Mastery multi-set (`set1.answer`..`setN.answer`), each with its own delivery APK.
- puzzle `codec` other than plain (proven by `cases/synthetic-base64`).

## Proof
- `hctf solver-test` → single_solve + synthetic-base64 both ok.
- `hctf solver-run .../time_trial` and `.../mastery` → all answers, no missing/problems.
