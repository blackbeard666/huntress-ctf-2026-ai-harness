---
name: solver-authoring
description: How to turn a solved Single Solve into a deterministic solver (challenges/<day>/<lane>-<title>/solver/solve.py) that also beats the Time Trial and Mastery variants. Covers the --contract/--artifacts interface, reading questions/answer_ids/sets from the contract, generalizing across variants, regression cases and hctf solver-test / solver-run. Use right after a Single Solve is confirmed, and whenever a solver fails on a new variant.
---

# Solver contract
```
python solve.py --contract <contract.json> --artifacts <dir>   ->  stdout (last line): {"<answer_id>": "<value>", ...}
```
- Iterate `zip(contract["answer_ids"], contract["questions"])`. Each question names its own `artifact` (file name inside
  `--artifacts`, or inside an archive there). **Mastery** = several sets: `set1.x`, `set2.x`, ... each with its own
  artifact (`blob-01.txt`, ...). It may also mix questions from earlier days. Answer every id you recognize and skip the rest
  (the dispatcher sends other questions to other solvers).
- Route by the question *text*, not its position: dispatch on keywords from `q["question"]` and the answer-id suffix
  (`id.split(".")[-1]`).
- Apply `normalization` (`trim`, lowercase, ...) yourself.
- Diagnostics go to stderr; only the JSON line goes to stdout. **Degrade per field, never per run:** an unexpected
  structure or an unknown question leaves THAT answer_id out (stderr says why) and every other field is still printed.
  One exception for the whole run = nothing submitted for any field in the timed window.
- Use only the project venv (`.venv`) plus stdlib/installed tools; subprocess calls need a `timeout`.
- Speed matters (timed modes): no network, no heavy whole-program analysis unless it is truly needed; cache nothing between runs.

# Reuse the shared library (import, don't re-derive)
The repo root is on PYTHONPATH, so `import lib.<x>` works from any solver. Prefer these over re-writing:
- `lib.common` — `load_contract`, `find_artifact` (handles `container.zip -> member`, nested zips, odd names,
  CTF passwords), `normalize`, `set_prefix` (`set1.`/`slot0_` -> unit index), `printable`.
- `lib.decode.peel(data, accept)` — BFS layered decoder (base/hex/xor/rot/compression/zip/url/reverse) for warmups.
- `lib.elf` — ELF `fields()`/`section_string()`/`exported_symbol()` emitting the GM's confirmed vocabulary.
- `lib.scripts` — `deobfuscate()`, `iocs()`, `attack_for(scenario)`, `role_attack(role, language)`
  (confirmed role->ATT&CK, e.g. `('stager','python')`->`T1105`; cmd=.003/vbs=.005/py=.006/js=.007),
  `attack_candidates(behavior)` (reference-backed candidates for a NOVEL role). Resolve every `*-attack`
  field from these — never hand-type a T-code. The submit guard refuses an id ATT&CK doesn't know.
- `lib.refs.attack` — authoritative MITRE ATT&CK reference: `is_valid(id)`, `name(id)`, `tactics(id)`,
  `id_for_name(name)`, `search(behavior)`. Use it to VALIDATE any attack value and to generate candidates
  for an unseen role/scenario; the GM still judges correctness on submit.
- `lib.knowledge` — the central store of GM-confirmed spellings (ELF endianness=`little`, machine=`x86-64`,
  scenario->ATT&CK, booleans). **When the GM confirms a new spelling, add it here**, not just in one solver.
If you discover a genuinely reusable helper, keep it in your `solver/` and list it under `## Proposed lib additions` in
`solver/NOTES.md` (target module + function); the post-run ratchet moves it into `lib/` so later days inherit it.
Never edit `lib/` during a run: other workers import it concurrently.

# Write it general the first time (no extra pass after CORRECT)
Apply this checklist WHILE writing — a Single Solve worker is ended as soon as it is CORRECT and the solver reproduces
the answers, so there is no "hardening pass" afterwards. Assume the variants differ in: file names, keys/XOR bytes, number of encoding layers and their order, field positions,
archive passwords given in the prompt, embedded strings, the extra Mastery sets, and the order of the questions.
The organizers say Time Trial / Mastery hand out "new, dynamic variations/mutations" and reward solvers that work
against "new unseen effects": also expect a different codec/container than the single's, a delivery wrapped in one
more zip, and ESCALATED field sets that add earlier days' questions (`dNN-...` ids; D7 metadata TT went 1 -> 11 fields).
Checklist:
- [ ] every constant is *derived* from the artifact or the contract (no answer literals, no hard-coded keys or offsets)
- [ ] layered decoding loops until a stop condition instead of assuming N layers
- [ ] parsers search for structure (magic bytes, regexes) instead of fixed offsets
- [ ] handles both a single file and an archive containing it
- [ ] works when the question order changes, and when only a subset of questions is passed in
- [ ] an extra question it has never seen doesn't stop the known ones (skip it, answer the rest)
- [ ] when the direct parse finds nothing, a cheap generic fallback runs (the lane lib's name-agnostic decoder /
      `find_artifact`, then a match against the field's `answer_format`) -- only on a miss, so the happy path stays fast
The harness checks the last four itself before the first timed attempt (`hctf/mutate.py`: renamed delivery, reordered /
subset / extra questions, two Mastery sets) and generalizes on any break -- so get them right while writing.

# Prove it
- Single Solve worker: `hctf solver-run <mode-id>` once (runs the solver on the current contract + files, no submit),
  then `hctf submit <id> --from-solver`. That's all — no `solver-test`, no synthetic cases.
- Generalize worker (a real variant failed): `hctf solver-test <single-solve-id>` replays every case in `solver/cases/`
  (Time Trial / Mastery variants are added automatically); it must pass before you stop.
- `solver/NOTES.md`: a few lines — the concept; `## Technique` (recognition cue, tools/commands that worked, dead
  ends) for the lane's technique log; the variant axes handled; and `## Proposed lib additions`.
