# HELP: generalize gate cannot pass on unverified variant-* cases (solver fix is done)

The solver fix is in place and every GM-verified case passes. The generalize stop gate still blocks because
`hctf/solvers.py:test_solver` sets `ok = not err and not diff and bool(expected)`, which can never be true for a case
whose `expected.json` is empty. All four `variant-mastery-*` cases have an empty `expected.json`, and workers must not
fill it (GM-verified only, and the harness restores edits).

State of the 4 variant cases on the fixed solver:
- variant-mastery-664b2505 / d271467d / f9ac3fc4: byte-identical artifacts (same sha256) to `auto-mastery-<id>` and
  `mastery-<id>`, which are fully GM-verified (103/113/83 fields) and pass with `ok=true`.
- variant-mastery-0b1ae1d0 (25 lines, new day-25 `U+XXXX` line): 123/123 answered, 0 of the 123 GM-rejected values
  produced again. Every slug is a valid `adj-noun-noun-NN` that ends with its own line-25 code-point decode. I
  re-derived sets 1-3 independently (day codec per line + code points): `hearty-meadow-maple-52`,
  `droll-blanket-copper-77`, `cozy-meadow-ripple-57`, and the solver matches.

Fix (solve.py): Mastery line 25 is no longer pre-decoded by `_uplus_lines`. `uplus` is registered as the day-25
free codec, so `decode._positional` decodes it. The old pre-decode made `_unknown_line_cands` re-"decode" the plain
`le-52` into the wrong digits. See solver/NOTES.md.

Needed from the orchestrator: count `unverified` cases with `rejected_hits == 0` and `answered == total` as passing
(as `orchestrate.py:2593/7299` already do), or retry Mastery so the GM can verify a fresh variant.
