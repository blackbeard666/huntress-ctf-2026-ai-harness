# ELF Aware solver
Concept: read ELF header/sections/symbols (pyelftools) + disassemble one tiny function (capstone).
Variant axes handled: zip or bare ELF, any member name, Mastery `setN.*` with `delivery N: <zip>` artifacts,
PIE/EXEC/stripped (dynsym fallback for the designated symbol), x86/x86-64/ARM/AArch64 return constants,
missing .huntress -> `none`, question order/subsets.
GM vocabulary: elf_class readelf-style (`ELF64`), elf_type constant-style (`ET_EXEC`).
UNCONFIRMED: endianness (`little endian`) and machine (`x86-64`); `EM_X86_64` was rejected. See single_solve/HELP.md.

Variant axis (time_trial 0ed75a94, `section-beacon.elf`): designated function renamed (`inspect_section`, returns 0x801)
but the question still says "constant returned by recover_code" and its answer_format changed integer -> exact_text
("use the literal none only when the requested field is absent"). Submitting `2049` (inspect_section's value) was
judged incorrect (all other fields match the confirmed single-solve vocabulary), so the solver now answers `none` when
the named function is absent from every symbol table and the format isn't `integer`; with an `integer` format it still
falls back to the designated symbol. `none` here is derived, NOT yet GM-confirmed.

Variant axis (time_trial ee1ec04b, multi-member "slot" bundle): evidence.zip holds `slot-0.elf`..`slot-3.elf`; the
contract has 9 shared questions (ids `marker`, ...) but 36 answer_ids `slotN_<qid>`. The solver now pairs each
answer_id with its question by exact id -> id suffix -> position (`pair_ids`), takes the prefix (`slot0`) as a slot
label and picks the archive member whose name matches `<label>[-_]N` (fallback: number alone, then position; 0- or
1-based inferred from the ids). Slots 0-2 = symbol-orientation profile; slot 3 = stripped profile
(`BR01-STRIPPED-PROFILE`, no .symtab, dynsym only libc). For slot 3, exported_symbol=`none` and recover_code=`none`
(named function absent from every symbol table; same rule as 0ed75a94, an unnamed function at 0x401120 still returns
0x1003=4099). Only slot0_recover_code=1337 is GM-confirmed; slot3 `none` values are derived, NOT confirmed. If the GM
rejects them, the alternative is to answer recover_code from the unnamed `mov eax, imm; ret` stub (4099 here).
Harness: hctf/solvers.py dispatch/sub_contract also zipped answer_ids with questions (slot0 only); fixed with
`paired_questions` (exact id -> suffix -> position, backward compatible).

Variant axis (time_trial a5693ce5, slot bundle with a non-stripped odd member): same 4-slot / 36-answer_id layout as
ee1ec04b, but slots 0-2 are byte-identical symbol-orientation builds (slot0 GM-confirmed) and slot 3 is an
"immediate-recovery" profile: `.huntress`=`BR01-IMMEDIATE-RECOVERY`, .symtab kept, recover_code = `mov eax,0x1ca3; ret`
= 7331. No solve.py change needed; the live run only submitted slot0 because the orchestrator process still had the
pre-fix hctf/solvers.py loaded (old `zip(answer_ids, questions)` dispatch -> 9 of 36). With the current
solvers.py, the timed path (`solve_contract(sub_contract(c, todo))`) answers all 36, and the 27 remaining after slot0.
expected.json now holds all 36 (slots 1-3 derived from the bytes, not yet GM-confirmed).
Restart the orchestrator after editing hctf/*.py, otherwise it keeps running the old module.

Variant axis (time_trial 79a5230e, slot bundle mixing profiles): same 4-slot / 36-answer_id layout; slots 0,1,3 are
byte-identical symbol-orientation builds (slot0 GM-confirmed), slot 2 is the section-beacon build from 0ed75a94
(`BR01-SECTION-BEACON`, exported `inspect_section` = mov eax,0x801; ret, no `recover_code` -> `none`). No solve.py
change needed: the solver already answers all 36 (and the 27 left after slot0) through the current solvers.py path.
The live failure was again a stale orchestrator: `hctf run` (started 23:42:41) predates the solvers.py
`paired_questions` fix (23:45:19), so its old `zip(answer_ids, questions)` dispatch only sent slot0's 9 ids.
expected.json now holds all 36 (slots 1-3 derived from the bytes; slot2 recover_code=`none` still unconfirmed).

Variant axis (time_trial 3faca1a1, slot bundle, 2+2 profiles): same 4-slot / 36-answer_id layout; slots 0-1 are
byte-identical symbol-orientation builds (slot0 GM-confirmed), slots 2-3 are byte-identical section-beacon builds
(`BR01-SECTION-BEACON`, `inspect_section` = mov eax,0x801; ret, no `recover_code` -> `none`). No new axis and no solve.py
change: solve.py and `hctf solver-run .../time_trial` both answer all 36. The "did not produce all answers" failure
was the same stale orchestrator for the 4th time (pid 6963, `hctf run` started 23:42:41, before the solvers.py
`paired_questions` fix at 23:45:19), so it submitted only slot0's 9 ids. Fresh variants keep failing this way until the
orchestrator is restarted. expected.json now holds all 36 (slots 1-3 derived and readelf-verified, not GM-confirmed).

Variant axis (time_trial 2ceb1dd9, slot bundle, 3 profiles): same 4-slot / 36-answer_id layout; slots 0-1 are
byte-identical symbol-orientation builds (slot0 GM-confirmed), slot 2 = section-beacon (`inspect_section` = 0x801,
recover_code `none`), slot 3 = stripped profile (`BR01-STRIPPED-PROFILE`, has_symtab false, exported_symbol/recover_code
`none`). No new axis and no solve.py change: solve.py and `hctf solver-run` answer all 36. The failure was the stale
orchestrator for the 5th time (pid 6963, started 23:42:41, before the solvers.py fix at 23:45:19), which again
submitted only slot0 (accepted, remaining 27). It must be restarted to load the current hctf/solvers.py.
expected.json now holds all 36 (slots 1-3 derived and readelf/objdump-verified, not GM-confirmed).

Variant axis (time_trial 61e92157, slot bundle, 3 profiles): same 4-slot / 36-answer_id layout; slots 0-1 are
byte-identical symbol-orientation builds (slot0 GM-confirmed), slot 2 = section-beacon (`inspect_section` = 0x801,
recover_code `none`), slot 3 = immediate-recovery (`BR01-IMMEDIATE-RECOVERY`, recover_code = mov eax,0x1ca3 = 7331).
No new axis and no solve.py change: solve.py and `hctf solver-run` answer all 36. Stale orchestrator for the 6th time
(`hctf run` pid 6942/child, started 23:42, predates the solvers.py fix at 23:45:19); it submitted only slot0
(accepted). The fix is to restart the orchestrator, not to change the solver. expected.json now holds all 36 (slots 1-3
derived and objdump/readelf-verified, not GM-confirmed).
