# Host With the Most (script-analysis day 02) solver

Concept: `evidence*.zip` (AES, `infected`) = 3 inert PowerShell fixtures (Day 1 "Power Play" format; that solver's
`analyse`/`find_member` are imported as-is) + 9 inert WSH JScript fixtures.

JScript: each file hides a JSON plan `{steps, adapter, values{campaign_id,url,file_path,host_id,next_stage,extension,
note_name,...}, stageCount}` behind custom base64 / XOR key arrays / reverse / byte-XOR layers; an `inspect_*` function
evals it. `jsdecode.js` runs the file in an empty node `vm` context (no require/ActiveXObject), swaps `eval` for a
capture, calls every top-level function and keeps the first parsed object with `steps`, so new layers decode untouched.
- role from steps: handoff -> staged_chain (confirmed for .js next stage too, never "relay"); upload -> uploader;
  transform/recovery_note -> impact; acquire_remote+memory -> stager; acquire_remote+write -> downloader;
  embedded+write -> dropper; dispatch -> launcher; else benign_utility.
- function-style: `function inspect_x(` declaration / `x = function(` anonymous_expression / `x = function name(` named_expression.
- invocation-style: the first call in the inspect body to another top-level function: `.call(` / `.apply(` / direct.
- property-style: accesses on the eval'd descriptor var: `d.k` only = dot, `d["k"]` only = bracket_literal, both = mixed.
- Questions are routed by the answer-id suffix (`jscript-<role>-<field>`), the artifact picks the file, so file names and
  roles are decoupled.

ATT&CK (all GM-confirmed, role-based): benign=none, downloader=T1105, stager=T1105, impact=T1486, dropper=T1140,
launcher=T1059.007, staged_chain/relay=T1059.007, uploader=T1041. Rejected: launcher T1218.010, stager T1059.007/T1620,
dropper T1105/T1027.009.
Synthetic check: renamed recover/inspect functions and swapped call/property styles still classify correctly.
