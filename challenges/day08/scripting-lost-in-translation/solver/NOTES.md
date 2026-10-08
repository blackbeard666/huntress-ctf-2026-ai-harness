# Day 7 — Node by Node (script-analysis, node operation graphs)

Concept: one evidence.zip with 61 members (PowerShell samples, JScript/Batch/VBScript/Python/Bash/Node operation
graphs); each graph decodes to a plan (steps/adapter/campaign/indicator) and is sorted into a role.

VARIANT AXIS: none in the bytes. TT attempt 26b7da83 failed because its download was the GM body `{"error":"rate_limited"}` (24 B saved as evidence.zip, sha != contract sha256), so every field came out None/default. The harvested variants 49b73141 + 7d6f8d53 were already answered 469/469 by the current solver (spot-checked against the raw bytes; their expected.json is solver-derived, not GM-verified). Parse rule: if every artifact is a small `{"error": ...}` JSON, exit non-zero (solve.py now does) instead of guessing roles. The bytes-less case was removed from cases/ (still kept under time_trial/attempts/26b7da83).

VARIANT AXIS: none (Day 8 TT). The start returned 503 `training_rotation_invalid` with no attempt and no artifact, so there were no variant bytes. The solver answers the TT contract's 615 ids 615/615 on the single's bytes. Rule: a start error is an orchestrator retry, not a solver change.

## Proposed lib additions
- `lib.common.gm_error_body(artdir) -> bytes|None`: detect a GM error JSON (`rate_limited`, ...) saved in place of an
  artifact, so every solver fails loudly. Better still: the harness download step (hctf/hb_timed.py) should retry on
  `{"error":"rate_limited"}` and never save it as the artifact. That would have saved this timed attempt.
