# mobile-cleartext-session solver notes

- Answer = `ANS-<16 hex>` from `assets/huntress_puzzle.json` (single: codec `reverse`), decoded via
  `lib.android.decode_payload` (declared codec -> `decode_any`), `parts`/`order` reassembly, then a literal
  `ANS-` scan of every APK member as fallback.

VARIANT AXIS: none observed -- all three TT "failures" (2026-10-08T13:01Z, 13:03Z, 13:04Z) were GM `start` -> 503 `training_rotation_invalid` (server-side rotation error, not a solver failure), so no variant contract/bytes were ever downloaded; solver unchanged. Checked against the TT contract with the artifact renamed to `cleartext_session_time_trial.apk`: answers `answer` correctly (puzzle codec read from `huntress_puzzle.json`, decode_any + literal-ANS fallback cover the re-rolled codec/key axis).

## Proposed lib additions
- (none)
