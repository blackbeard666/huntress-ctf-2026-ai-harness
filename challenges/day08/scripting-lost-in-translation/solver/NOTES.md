# Day 7 — Node by Node (script-analysis, node operation graphs)

Concept: one evidence.zip with 61 members (PowerShell samples, JScript/Batch/VBScript/Python/Bash/Node operation
graphs); each graph decodes to a plan (steps/adapter/campaign/indicator) and is sorted into a role.

VARIANT AXIS: none in the bytes. TT attempt 26b7da83 failed because its download was the GM body `{"error":"rate_limited"}` (24 B saved as evidence.zip, sha != contract sha256), so every field came out None/default. The harvested variants 49b73141 + 7d6f8d53 were already answered 469/469 by the current solver (spot-checked against the raw bytes; their expected.json is solver-derived, not GM-verified). Parse rule: if every artifact is a small `{"error": ...}` JSON, exit non-zero (solve.py now does) instead of guessing roles. The bytes-less case was removed from cases/ (still kept under time_trial/attempts/26b7da83).

VARIANT AXIS: none (Day 8 TT). The start returned 503 `training_rotation_invalid` with no attempt and no artifact, so there were no variant bytes. The solver answers the TT contract's 615 ids 615/615 on the single's bytes. Rule: a start error is an orchestrator retry, not a solver change.

VARIANT AXIS: none in the bytes (D8 Mastery 7432c509). Same 5-set bundle shape (outer zip holding evidence-01..05.zip) as the GM-verified auto-mastery cases; the solver answered 3075/3075 but the attempt EXPIRED (submit RemoteDisconnected after 5.42 s solve on Homebase). expected.json = solver output, spot-checked against the raw bytes (PS base64 record, VBS Codec_ field, While/if-errorlevel control). Speed fix: sets solve in forked processes (group_by_set + ProcessPoolExecutor, sequential fallback); the nested-zip index no longer decrypts every script leaf just to sniff for PK (375 PBKDF2s -> only the members asked, per set, in parallel); powerplay.xor is one big-int XOR.

## Proposed lib additions
- `lib.common.gm_error_body(artdir) -> bytes|None`: detect a GM error JSON (`rate_limited`, ...) saved in place of an
  artifact, so every solver fails loudly. Better still: the harness download step (hctf/hb_timed.py) should retry on
  `{"error":"rate_limited"}` and never save it as the artifact. That would have saved this timed attempt.
- `lib.common.iter_entries(root, leaf_ext=...)`: don't load a member just to sniff for a nested zip when its name has a script/text extension (.js/.ps1/.py/.vbs/.cmd/.bat/.sh/.mjs/.php/...). Today it decrypts every AES member of a Mastery bundle up front (375 PBKDF2 = ~0.2 s locally, many times that on Homebase), and each forked set repeats it. See `_iter_entries` in this solve.py.
