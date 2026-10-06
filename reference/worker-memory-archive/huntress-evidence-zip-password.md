---
name: huntress-evidence-zip-password
description: Huntress CTF script-analysis evidence zips are AES-encrypted with password "infected", which the contract never states
metadata:
  type: project
---
Day01 script-analysis "Power Play" evidence.zip is AES-256 (compress_type 99, so python zipfile can't read it) with password `infected`, and the contract does not mention it. Extract with `7z x -pinfected ... </dev/null`; without -p and stdin, 7z hangs on a prompt and reports "Break signaled".
The synthetic_collection ATT&CK id is not T1005, T1560 or T1119 (all rejected 2026-10-03). Leading unsubmitted candidate: T1074 Data Staged (descriptor names a stage-*.zip); then T1555.003, T1539, T1041.

**Why:** cost a detour, and three wrong answers used up the local cap.
**How to apply:** try `infected` first on encrypted sample zips; for the collection technique see HELP.md in challenges/day01/scripting-power-play.
