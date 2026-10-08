# Day 08 metadata — What's in the Box? — solver notes

VARIANT AXIS: none observed. The "failed" TT attempt never started (`last_timed.json`: `training_rotation_invalid`, attempt_id null), so no variant bytes exist. The TT contract has the same 12 answer_ids as the single (evidence-note-* + d04..d07 carry-overs + `d07-zip-NNN-zip-central-directory-member-names`). solve.py answers all 12 on the single's bytes. It also answers every Day-07 timed case (TT 11-field, Mastery 22-field 2-set, nested drops 001-004) with zero diffs. CD names are walked raw from the EOCD's cd_offset in CD order, keeping `room-NN/` directory context (UTF-8 flag 0x800, else cp437).
VARIANT AXIS: still none (cycle 2) -- TT start refused again with `training_rotation_invalid`, so no variant bytes; the solver answers 12/12 TT ids and 60/60 for the 5-set Mastery contract (`setN.` prefix, `-0N.zip` per-set containers paired by sha256).

## Proposed lib additions
- `zip_cd_names(data)` (raw central-directory walk from the EOCD, compact JSON list) -> lib.common, shared by D7/D8 metadata solvers.
