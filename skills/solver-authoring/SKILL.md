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
- Diagnostics go to stderr; only the JSON line goes to stdout. Exit non-zero with a clear message if the structure is unexpected.
- Use only the project venv (`.venv`) plus stdlib/installed tools; subprocess calls need a `timeout`.
- Speed matters (timed modes): no network, no heavy whole-program analysis unless it is truly needed; cache nothing between runs.

# Reuse the shared library (import, don't re-derive)
The repo root is on PYTHONPATH, so `import lib.<x>` works from any solver. Prefer these over re-writing:
- `lib.common` — `load_contract`, `find_artifact` (handles `container.zip -> member`, nested zips, odd names,
  CTF passwords), `normalize`, `set_prefix` (`set1.`/`slot0_` -> unit index), `printable`.
- `lib.decode.peel(data, accept)` — BFS layered decoder (base/hex/xor/rot/compression/zip/url/reverse) for warmups.
- `lib.elf` — ELF `fields()`/`section_string()`/`exported_symbol()` emitting the GM's confirmed vocabulary.
- `lib.scripts` — `deobfuscate()`, `iocs()`, `attack_for(scenario)` (confirmed ATT&CK ids).
- `lib.knowledge` — the central store of GM-confirmed spellings (ELF endianness=`little`, machine=`x86-64`,
  scenario->ATT&CK, booleans). **When the GM confirms a new spelling, add it here**, not just in one solver.
If you discover a genuinely reusable helper, add it to the right `lib/` module so later days inherit it.

# Generalize before you finish
Assume the variants differ in: file names, keys/XOR bytes, number of encoding layers and their order, field positions,
archive passwords given in the prompt, embedded strings, the extra Mastery sets, and the order of the questions.
Checklist:
- [ ] every constant is *derived* from the artifact or the contract (no answer literals, no hard-coded keys or offsets)
- [ ] layered decoding loops until a stop condition instead of assuming N layers
- [ ] parsers search for structure (magic bytes, regexes) instead of fixed offsets
- [ ] handles both a single file and an archive containing it
- [ ] works when the question order changes, and when only a subset of questions is passed in

# Prove it
- `hctf solver-test <single-solve-id>`: rebuilds case `single_solve` from the GM-confirmed answers and replays every case
  in `solver/cases/` (Time Trial and Mastery variants are added automatically once they are confirmed).
- `hctf solver-run <mode-id>`: runs the solver library on any mode's current contract and files, without submitting.
- Optional: hand-make a mutated variant (change key/filename/layers) under `solver/cases/synthetic-*` with `expected.json`
  to check that the solver really generalizes.
- Keep `solver/NOTES.md`: what the concept is and which variant axes you handled.
