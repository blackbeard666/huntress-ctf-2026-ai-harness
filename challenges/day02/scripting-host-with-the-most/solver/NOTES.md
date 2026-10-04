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

Mastery (attempt 71804192, 2026-10-04; case variant-mastery-71804192): new axis = **outer bundle zip**. The download is
`script-analysis-day-02-encoded-intent-mastery.zip` holding `evidence-01.zip` (set1) and `evidence-02.zip` (set2), each
AES/`infected` with the same 3 PS + 9 JScript members (174 answer_ids, 87 per set). Day 1's `find_member` only looks one zip
deep, so every lookup raised FileNotFoundError ("solver did not produce all answers"). Fix: `solve.find_member` falls back
to `lib.common.find_artifact`, which walks nested zips and prefers the member whose parent is the named set zip, so set1 and set2
never cross. No new content axes: same step graphs/roles, values and styles per set re-rolled (e.g. set2 relay uses `.apply`
with dot access, set2 local-dispatch.js is byte-identical to set1's). All 174 answers were re-derived independently (PS base64
decoded by hand; native node vm run of each `inspect_*`; styles read by hand off the bodies) and match the solver; run time ~0.4 s.

Mastery (attempt bd7c8549, 2026-10-04; case variant-mastery-bd7c8549): new delivery axis = **one download per set, all
named `evidence.zip`** (contract `artifacts[]` = 2 entries with filename `evidence.zip` + sha256), while the questions still say
`evidence-01.zip -> ...` / `evidence-02.zip -> ...`. The live attempt expired (probe fetched only download #1 at deadline+1 s),
and the case was first written with the STALE 71804192 bundle; it now holds the real bytes (re-fetched by capability, hashes
equal the contract). Fix: `lib.common.container_by_sha(root, contract, container)` pairs the unique question container names with
`artifacts[]` by order and returns the saved file with that sha256; `solve.find_member` uses it whenever no file carries the
container's name, so set N can never silently read set 1's member (the Day 1 name heuristic did exactly that: 42/174 wrong in
`cases/synthetic-same-name-sets`, which stores both sets as `a/evidence.zip`, `b/evidence.zip`). No new content axes: same
roles/steps/styles; all 174 answers re-derived independently (PS base64; native node vm run of each inspect_*; styles by
eye — note `var x = function x_body(` is named_expression, not declaration) and match the solver. ~0.17 s.

Mastery (attempt 5c64a3d8, 2026-10-04; case variant-mastery-5c64a3d8): **no new axis, no solver change.** Same delivery as
bd7c8549 (two downloads, both `evidence.zip`, set by sha256). The case was again first written with the STALE 71804192 bundle
(hence "unverified"). It now holds the real bytes (4ae798b1... / b1980239..., fetched by capability, hashes equal the contract).
The live attempt failed upstream of solve.py: the log shows `start` -> `artifact {}` (the no-capability fallback op) and NO
`download` ops before the deadline, so the solver never saw the bytes. That is a timed-runner fetch problem (hctf/timed.py /
hb_timed.py download step), not a solver one. All 174 answers re-derived independently (PS base64; native node vm run of each
inspect_*, 54 value fields compared by script; styles by hand) and equal the solver output. ~0.2 s.

Mastery (attempt 7a6c43ab, 2026-10-04; case variant-mastery-7a6c43ab): **no new content axis; new delivery axis = partial
delivery.** Same shape as bd7c8549/5c64a3d8 (two downloads, both `evidence.zip`, 174 ids). The case was again first written
with STALE bytes (5c64a3d8's 4ae798b1/b1980239); it now holds the real 197f12d0... / c260b5d7... (delivery 2 re-fetched by
capability). Live run: `start` -> `artifact` op at +3 s saved only `hctf/dl/probe/evidence.zip` (delivery 1); i.e. `cli.c_artifact`
again took its no-plan fallback, though `_planned_downloads(start.json)` yields both files now (likely start.json not yet
saved when it ran; orchestrator issue). On bytes, the solver was already right: all 174 re-derived independently (PS base64;
node vm per inspect_*, 54 value fields 0 diffs; 54 styles by hand) and equal its output. Set1's PS extension really is the
short `.locked-d1e6a`. **Solver bug found + fixed:** with only delivery 1 present, the name fallback answered all 87 set-2 ids
from set 1's same-named members (confidently wrong). New `lib.common.delivery_missing(root, contract, container)`: when the
contract pairs containers 1:1 with hashed deliveries and no file is named/hashes to this container, `find_member` raises, so
that set is left unanswered instead of borrowed. Regression: `cases/synthetic-partial-delivery` (only `evidence.zip` = delivery
1; set-2 ids expected null = absent). ~0.18 s.

Mastery (attempt 73a1bfcb, 2026-10-04; case variant-mastery-73a1bfcb): **no new axis, no solver change.** Same 174-id,
two-`evidence.zip` shape. Deadline was start+6 s; only delivery 1 (0800fdb4..., `hctf/dl/probe/evidence.zip`) was fetched,
delivery 2 (19f4279d...) never was, and the attempt was not submitted (orchestrator log: repeated `expired`, 10-13 s elapsed).
The case was again written with STALE bytes (5c64a3d8's 4ae798b1/b1980239): the running orchestrator predates the
`timed.artifacts_for` attempt-manifest guard (hctf/timed.py edited 10:48, after the orchestrator started). Delivery 2 is
unrecoverable offline, so the case now holds only the real delivery 1 as `evidence-01.zip`, and its contract is trimmed to the 87
set1 ids. All 87 re-derived independently (PS base64; node vm per inspect_*; styles by hand). New content values seen and
handled: uploader adapter `ConfigSecurityPolicy.exe` (LOLBin), dropper/benign adapter `Scripting.FileSystemObject`, a short
PS impact extension `.locked-ae479`. 0 diffs vs solver. ~0.13 s. The real fix is time-to-bytes in the timed runner, not solve.py.

Mastery (attempt 7a66d146, 2026-10-04; case variant-mastery-7a66d146): **no new axis, no solver change.** Same 174-id,
two-`evidence.zip` shape (deadline start+6 s). The case was AGAIN written with STALE bytes (5c64a3d8's 4ae798b1/b1980239), so
"unverified, diff={}" meant only that expected.json was empty. Live log: `start`, then one `artifact` op at +3 s that saved only
delivery 1 (`hctf/dl/probe/evidence.zip`, d7efdb06...); no submit. Case now holds the real d7efdb06... (from the probe copy) and
211c4be0... (delivery 2 re-fetched by capability via `remote.gm('download', cap, ...)`), both hashes equal the contract. All 174
re-derived independently (PS base64 decoded with `base64 -d`, every reconstruct block is identity; own node vm script runs each
inspect_*: 0 value diffs; 54 styles by hand) and equal the solver output. Values seen: set2 uploader adapter again
`ConfigSecurityPolicy.exe`, set2 local-dispatch.js again byte-identical to set1's. ~0.2 s. Root cause remains the timed
runner (stale case bytes + only delivery 1 fetched before the deadline), not solve.py.

Mastery (attempt d27dddc9, 2026-10-04; case variant-mastery-d27dddc9): **no new axis, no solver change.** Same 174-id,
two-`evidence.zip` shape (deadline start+6 s). This time the case bytes are real (f888b8c2... / dde3311c..., equal to the
contract and the attempt manifest): both `download` ops finished by +3 s. Then nothing was logged: no submit, so the attempt
expired. No answer was rejected. All 174 re-derived independently (PS base64, identity reconstruct; own node vm run of each inspect_*,
54 value fields 0 diffs; 54 styles by hand, 0 diffs). They equal the solver output (~0.18 s), and expected.json is filled in. Values
seen: set2 local-dispatch.js again byte-identical to set1's (both campaign-3f8e0c467a, which is real and not a set mix-up); short PS
impact extensions `.locked-64704`/`.locked-9e7f8`; uploader adapters `ConfigSecurityPolicy.exe` / `MSXML2.ServerXMLHTTP.6.0`.
The bottleneck is still download→solve→submit inside the orchestrator's 6 s window, not solve.py.

Mastery (attempt f266b8e1, 2026-10-04; case variant-mastery-f266b8e1): **no new axis, no solver change.** Same 174-id,
two-`evidence.zip` shape (deadline start+6 s). The case bytes are real (e93ec920... / 7d5fbc55..., equal to the contract): both
downloads finished by +4 s. All 174 answers re-derived independently: PS base64 decoded directly, with every reconstruct block
an identity; my own node vm harness called each `inspect_*` with native eval, and 72 value fields showed 0 diffs; 54 styles were
read by hand with 0 diffs. They equal the solver output (~0.17 s), and expected.json is filled in. **Why these attempts fail:**
`.run/logs/day2-mastery-2.log` shows the last two attempts (555be4b7, 0f36f5c6) ended
`per_set: set1 accepted (remaining 87), set2 expired` at 10.6-11.7 s elapsed. Set 1's answers were taken. Set 2's submit came
after the 6 s deadline because the runner submits sets one after another and each GM round trip takes seconds. So the fix
belongs in the timed runner (submit all sets in one call, or in parallel, right after solve), not in solve.py. Values seen:
set2 local-dispatch.js again byte-identical to set1's (campaign-3f8e0c467a); uploader adapters `CertReq.exe` /
`ConfigSecurityPolicy.exe`; set2 chain adapter `Microsoft.XMLHTTP`; short PS impact extensions `.locked-3fa17`/`.locked-740d8`.

Mastery (attempt d7196e63, 2026-10-04; case variant-mastery-d7196e63): **no new axis, no solver change.** Same 174-id,
two-`evidence.zip` shape (deadline start+6 s). The case bytes are real (cba5420b... / 6f456fd3..., equal to the contract).
The log shows `start`, then `download` ops at +2 s and +4 s, then nothing: no submit, so the attempt expired, and no answer
was rejected. All 174 answers re-derived independently: PS base64 decoded directly (every reconstruct block is an identity);
a separate node vm harness (`eval` capture) ran each `inspect_*`; 54 styles read by hand. 0 diffs vs the solver (~0.19 s), and
expected.json is filled in. Values seen: set2 local-dispatch.js again byte-identical to set1's (campaign-3f8e0c467a); uploader
adapters `WinHttp.WinHttpRequest.5.1` / `CertReq.exe`; short PS impact extensions `.locked-3b992`/`.locked-335e4`.
Same root cause as f266b8e1: downloads alone eat ~4 of the 6 s, and sets are submitted
one after another. This needs a timed-runner fix, not a solve.py change.

Mastery (attempt bbc61a78, 2026-10-04; case variant-mastery-bbc61a78): **no new axis, no solver change.** Same 174-id,
two-`evidence.zip` shape (deadline start+6 s). The case bytes are real (e920976d... / d3c63a0a..., equal to the contract): both
`download` ops finished by +3 s (03:24:52/53). After that the attempt log has no entries, so there was no submit, the attempt
expired, and no answer was rejected. All 174 answers re-derived independently: 6 PS base64 blobs decoded directly (every
reconstruct block is an identity); a separate node vm harness (native eval) called each `inspect_*`, and 54 value fields had
0 diffs; 54 styles were read by hand off the inspect bodies, with 0 diffs. They equal the solver output (~0.17 s), and
expected.json is filled in. Values seen: set2 local-dispatch.js again byte-identical to set1's (campaign-3f8e0c467a);
benign adapter `Scripting.Dictionary` (new, read straight from the plan); uploader adapters `CertReq.exe` /
`MSXML2.ServerXMLHTTP.6.0`; short PS impact extensions `.locked-8dce0`/`.locked-fa703`; set2 relay uses `var x = function
x_body(` + bare `recover_x()` + bracket-only access (named_expression / direct / bracket_literal). Same root cause as
f266b8e1/d7196e63: the timed runner does not submit within the 6 s window. This needs a runner fix, not a solve.py change.

Mastery (attempt 6d6d679a, 2026-10-04; case variant-mastery-6d6d679a): **no new axis, no solver change.** Same 174-id,
two-`evidence.zip` shape; contract questions are identical to bbc61a78. The case bytes are real (b68beac3... / 056fa40d...,
equal to the contract). Live log: `start` 03:27:14, `download` at +3 s and +5 s, then nothing, so there was no submit and
the attempt expired. No answer was rejected. All 174 answers were re-derived independently: 6 PS base64 blobs decoded directly
(every reconstruct block is an identity); a separate node vm harness called each `inspect_*`, with 54 value fields and 0 diffs;
54 styles were read by hand off the inspect bodies, with 0 diffs. They equal the solver output (~0.17 s), and expected.json is
filled in. Values seen: set2 local-dispatch.js again byte-identical to set1's (campaign-3f8e0c467a); uploader adapters
`ConfigSecurityPolicy.exe` / `MSXML2.ServerXMLHTTP.6.0`; set1 impact adapter `ADODB.Stream`; set2 downloader adapter
`MSXML2.XMLHTTP.6.0`; set2 collection URL without the `cdn-` prefix (`https://7c12c3a939.example.invalid/...dat`), read straight
from the literal; short PS impact extensions `.locked-807f7`/`.locked-5568d`. Same root cause as f266b8e1/d7196e63/bbc61a78:
downloads finish at +5 s of a 6 s window, so the timed runner cannot submit in time. This needs a runner fix, not a solve.py change.

Mastery (attempt 45e7bbd8, 2026-10-04; case variant-mastery-45e7bbd8): **no new axis, no solver change.** Same 174-id,
two-`evidence.zip` shape with the same questions as 6d6d679a. The case bytes are real (57ad9f5e... / 02bd38e8..., equal to the
contract). Live log: `start` 03:29:34, `download` at +1 s and +4 s, then nothing, so there was no submit and the attempt
expired. No answer was rejected. All 174 answers were re-derived independently: 6 PS base64 blobs decoded with `base64 -d`
(every reconstruct block is an identity); a separate node vm harness ran each `inspect_*` with native eval, and a field-wise
script found 0 diffs across 72 value answers; 54 styles were read by hand (decl line + recover call form + a per-descriptor
`.k`/`["k"]` access count), with 0 diffs. They equal the solver output (~0.17 s), and expected.json is filled in. Values seen: set2
local-dispatch.js again byte-identical to set1's (campaign-3f8e0c467a); uploader adapters `CertReq.exe` /
`ConfigSecurityPolicy.exe`; short PS impact extensions `.locked-d4d72`/`.locked-5b73e`; set2 impact PS URL without `cdn-`.
Same root cause as f266b8e1/d7196e63/bbc61a78/6d6d679a: the timed runner does not submit within the 6 s window.
