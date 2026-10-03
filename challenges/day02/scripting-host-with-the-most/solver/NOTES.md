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

Time Trial (2026-10-03, 25 unverified variants): the clock is 5 s from `started_at`, and every failed attempt was
`expired`/never submitted, not wrong. Every variant only re-rolls the same axes: file names, layer kind/order
(reverse+XOR array, custom base64 + byte shift, ...), helper/variable casing, and the call/property/function styles. Step graphs
and roles match the single solve exactly. All 25 were re-derived independently (native-eval node run of the
inspect function + separate style regexes + the PS literals checked against the decoded bytes); expected.json is filled in from that.
Speed axis: `jsdecode.js` now takes N paths and decodes every JScript member in ONE node process (each file in its own vm
context); the solver went from ~0.31 s to ~0.13 s. The remaining latency is in the harness start/download round trip.

Variant d6c34027 (2026-10-04 hardening pass): no new axis. It has the same evidence.zip (sha256 6b8e6166...) and the same
contract as 4019a438. The attempt logged `start` + `download` and then nothing: it expired before submit (deadline =
started_at + 5 s), it was not a wrong answer. All 87 answers were re-derived independently (base64 PS literals; native
node `vm` run of each `inspect_*`; styles read by hand off the inspect bodies) and they equal the solver output, which is
now stored in expected.json. The solver runs in ~0.12 s, so the gap is in the orchestrator's start→download→submit
latency, not in solve.py.
