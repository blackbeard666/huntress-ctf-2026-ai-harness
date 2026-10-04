# HELP: Expansion Pack — 2 of 159 fields blocked by the per-field wrong cap

157/159 confirmed. Remaining: `batch-launcher-control` (local-dispatch.bat) and `batch-relay-control` (relay-handoff.cmd).

**The concept is known.** Both files have the same generator-inserted control block (LF-only lines):
`set "HUNTRESS_READY=1"`, then `if defined HUNTRESS_READY <first join statement>`. Only the GM's spelling is unknown.

GM vocabulary confirmed for the other 7 files: `direct`, `errorlevel_guard`, `goto_dispatch`, `call_subroutine`.

Rejected by the GM for this form (both fields are now at the harness 6-wrong cap):
if_defined, "if defined", defined_guard, if_defined_guard, flag_guard, defined_flag, variable_guard,
environment_probe, direct, for_loop.

Next candidates, in ranked order (also in `lib/knowledge.py` BATCH_DEFINED_GUARD_CANDIDATES):
environment_guard, env_guard, ready_flag, ready_guard, sentinel_guard, opaque_predicate, defined_check, flag_check,
conditional_guard.

The solver emits `environment_guard` (`solver/batchplan.py` DEFINED_GUARD_FORM). The timed per-field probe on a fresh
attempt will test it. When one is accepted, set DEFINED_GUARD_FORM and move it into BATCH_CONTROL_VOCAB.
To unblock the single solve, someone needs to raise HCTF_MAX_WRONG for these two ids (operator decision).
