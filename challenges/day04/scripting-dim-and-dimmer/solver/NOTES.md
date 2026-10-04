# Dim and Dimmer solver notes

Concept: the Day 3 "Expansion Pack" bundle (PowerShell samples, JScript plans, Batch plans — handled by the vendored
day03 code: solve.py/powerplay.py/batchplan.py/jsdecode.js, unchanged) plus inert **VBScript** fixtures (`vbsplan.py`).

## VBScript (vbsplan.py)
- `Const Material_<id>` holds the plan as text bytes; `Load_<id>()` parses it (decimal/hex, separator, maybe reversed),
  `Decode_<id>()` undoes the byte transform; `Recover_<id>()` wraps the Decode call in a control construct.
- Load and Decode are **executed by a small VBScript-subset transpiler** (Dim/ReDim/For/If/assignments; Split, Mid, Len,
  UBound, CInt("&H.."), Array, Chr, Xor/Mod...), with `eval` restricted to translated tokens and no builtins. So a new
  separator/transform in a variant decodes from its own code. If the interpreter hits an unsupported statement, a
  `Codec_`-driven decoder (`codec_decode`) is the fallback.
- representation / transform = fields 1/2 of `Const Codec_<id> = "rep|transform|key"` (GM-confirmed). Without the const,
  they're inferred from the Load/Decode code (`infer_representation` / `infer_transform`, which agree on all 9 files).
- control = the innermost construct around the Decode call (GM vocab `direct`/`select_case`/`do_once`/`while_once`). An outer
  `If True Then` block and single-line `If (2 > 1) Then ..` junk are noise. do_loop/do_exit/while_wend/while_loop were rejected.
  Plus two UNCONFIRMED forms (see the axes below): `On Error Resume Next` mode -> `error_guard` (on_error_resume and direct
  GM-rejected), `For p = 0 To 0` -> `for_once`.
- role from plan `steps` (shared `role_of`); ATT&CK: launcher/staged_chain = T1059.005, others as JS/Batch.

## Cases
- `single_solve` (GM-confirmed), `day03-*` (Day 3 regression cases for the reused PS/JS/Batch code),
- `synthetic-mastery-vbs`: set1 = real bytes, set2 = re-encoded host-context plan (new key/values), CRLF + mangled keyword
  case, a direct->while_once and a do_once->direct control swap. Checks the VBS path generalizes.

## Variant axis: Base64 material (Time Trial 3fd867ae)
- `base64_literal`: `Load_<id> = Base64_<id>(Material_<id>)`, a hand-rolled Base64 decoder Function (Replace/InStr/`\`/`^`,
  `ReDim Preserve`, `Err.Raise` on a bad char). `base64_chunks`: Load_ first re-joins 4 `Mid()` slices of the Material.
- New transforms: `reverse_then_xor` (`result(UBound(s) - i) = s(i) Xor k`) and `identity` (`result(i) = s(i)`); also `hex_dash`.
- The interpreter gained Replace/InStr/Trim, vbCr/vbLf/vbCrLf/vbTab/vbBinaryCompare, `ReDim Preserve` that keeps the
  contents, `Err.Raise` (raises -> Codec fallback), user Function calls from Load (already worked), and a compile cache.
- `codec_decode` handles base64_* / reverse_then_xor / identity; `infer_representation` / `infer_transform` recognise them.
  Interpreter, Codec fallback and inference agree on all 9 files of the variant (case `variant-time_trial-3fd867ae`, whose
  expected.json holds the VBS fields, cross-checked with an independent Python decode).
- The live failure was `solver_incomplete` (6 missing plan fields for the two Base64 files); the attack/role of those files
  also depended on the plan (relay-handoff role is staged_chain, not the benign_utility fallback).

## Variant axis: On Error / For-once control wrappers (Time Trial 0663ae04)
- `host-context.vbs` wrapped the Decode call as `On Error Resume Next` / `x = Decode_..` / `e = Err.Number` /
  `On Error GoTo 0` / `If e <> 0 Then Err.Raise ..`. The solver said `direct` -> **GM-rejected**. `control_form` now treats
  `On Error Resume Next` as a mode (on until `On Error GoTo 0`, not a block) and returns `lib.knowledge.VBS_CONTROL_ON_ERROR`
  (= first of `VBS_CONTROL_ON_ERROR_CANDIDATES`: on_error_resume, on_error_resume_next, on_error, error_resume, resume_next,
  error_guard, ...). **The spelling is not GM-confirmed yet**; if the GM rejects it, `hctf labels` seeds the rest of the list
  in order (playbook `_vbs_control_derive`). Once it's confirmed, set it first in knowledge.py and update both expected.json files.
- `memory-stage.vbs` wrapped it in `For decodePass = 0 To 0 .. Next` (old output `direct`, not judged) -> `for_once`
  (`VBS_CONTROL_FOR_ONCE`, named like do_once/while_once; also unconfirmed). Only a For loop whose bounds are equal
  constants counts.
- The same On Error construct was in TT 3fd867ae (impact/uploader). Its expected.json said `direct`, but that value was never
  GM-judged, so both are now `on_error_resume`.
- Case `auto-time_trial-0663ae04`: non-VBS fields + 13 VBS fields GM-accepted; the other VBS fields were filled from the
  solver after an independent Codec_-driven Python decode matched every plan (rep/transform/adapter/campaign/url/path).
  The unconfirmed labels in it: vbscript-benign-control (on_error_resume) and vbscript-stager-control (for_once).

## Label axis: On Error wrapper is NOT `on_error_resume` (Time Trial d60a2262)
- Same `On Error Resume Next` / Decode_ / `Err.Number` / `On Error GoTo 0` / `If e <> 0 Then Err.Raise` wrapper, this time in
  host-context (benign), memory-stage (stager) and relay-handoff (relay). The GM localized `vbscript-benign-control` =
  `on_error_resume` as INCORRECT (the only wrong field it pinned; the rest of the localization was incomplete).
- Rejected so far for this construct: `direct` (0663ae04), `on_error_resume` (d60a2262) -> `lib.knowledge.VBS_CONTROL_ON_ERROR_REJECTED`.
- Now emitted: `error_guard` (head of the re-ranked `VBS_CONTROL_ON_ERROR_CANDIDATES`). Why: the generator spells labels as
  `<short keyword>_<role>` (do_once, while_once, if_guard, errorlevel_guard, goto_dispatch) and rejected every
  spelled-out statement (do_exit, while_wend, if_defined, on_error_resume). This wrapper checks Err after the call and
  bails out, the VBS twin of Batch `errorlevel_guard`. **Still unconfirmed.** Next in line if it is rejected:
  on_error_guard, err_guard, on_error_resume_next, on_error, resume_next, ... (`hctf labels` seeds them in that order and
  skips the rejected ones). Once one is confirmed, put it first in knowledge.py and update the expected.json files of
  0663ae04 (benign) and 3fd867ae (uploader/impact). Those currently hold `error_guard`, which is not GM-judged.
- Case `auto-time_trial-d60a2262` expected.json holds only GM-accepted values (no control fields). On its bytes the solver
  emits all 231 ids: benign/stager/relay = error_guard, dropper/uploader (`For p = 0 To 0`) = for_once, impact =
  select_case (under an `If True Then` wrapper), launcher = do_once, downloader/chain = direct.
