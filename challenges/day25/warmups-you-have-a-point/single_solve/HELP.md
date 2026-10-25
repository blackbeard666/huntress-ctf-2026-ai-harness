# HELP: generalize gate can't pass because of stale empty-expected variant cases

The solver is correct and fast. No `solve.py` change can make the stop gate pass:

- `hctf/solvers.py` `test_solver.one()` sets `ok = not err and not diff and bool(expected)`. A case whose
  `expected.json` is `{}` is therefore never ok, whatever the solver outputs.
- `variant-mastery-{0b1ae1d0,664b2505,d271467d,f9ac3fc4}` have `expected.json == {}`. Each one has the same artifact sha256
  and the same questions as `auto-mastery-<id>`, whose expected.json is fully GM-verified (123/103/113/83 fields).
- solve.py on the variant bytes: matches 100% of the auto-mastery verified values, 0 gm_feedback rejected hits, all
  fields answered, 0.3-0.9 s per case. Single Solve takes 0.10 s and outputs `brave-beacon-wizard-34` (confirmed).
- Full `hctf solver-test warmups-day-25`: every case passes except these 4 (unverified, error=None). Slowest case 0.98 s.

Fix (harness-side, not allowed for a worker): drop the 4 `variant-mastery-*` cases, now superseded by
`auto-mastery-*`, or fill their expected.json from the matching auto case. The orchestrator code
(orchestrate.py:2593, 7299) already ignores unverified cases. Only the stop gate's `all(r["ok"])` in
`ensure_case_and_test` counts them.
