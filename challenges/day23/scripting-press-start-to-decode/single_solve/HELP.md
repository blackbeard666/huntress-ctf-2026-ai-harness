# HELP (duel2 generalize worker) -- gate unsatisfiable, solver is done

`hctf solver-test` cannot pass for case `variant-mastery-7432c509`: hctf/solvers.py test_solver computes
`ok = not err and not diff and bool(expected)`, and that case's expected.json is empty (the variant was never
GM-solved), so it is always `ok:false, unverified:true`.

State of the solver (.run/duel2-gen-day23/scripting-press-start-to-decode/solver/solve.py, unchanged):
- variant-mastery-7432c509: answers 3075/3075 ids in ~1.0 s, no skip / no value / failed log lines.
- every GM-verified case: ok, diff {} (last full run). single_solve runs in 0.72-0.81 s wall locally
  (1.85 s under cProfile); the 2-3.5 s case times in the gate output come from parallel workers loading the box.
- Remaining cost is lib.codec regex compilation + AES member reads (lib/ is off limits); decode-once, the
  nested-zip index and fork-per-set are already in place.

No answers, expected.json files or cases were edited. Orchestrator: retry with a fresh variant.
