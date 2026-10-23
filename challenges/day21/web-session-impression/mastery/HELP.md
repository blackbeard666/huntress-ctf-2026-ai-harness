# HELP (duel2 generalize worker)

Blocked only by the stop gate, not by the solver.

- `solve.py` (.run/duel2-gen-day21/web-session-impression/solver) answers 3/3 on `variant-mastery-ff8db5ea` in ~4s;
  `single_solve`, `auto-time_trial-7935346d` and both `compound-live-*` cases pass.
- `variant-mastery-ff8db5ea` reports `ok:false, unverified:true`: hctf/solvers.py requires a non-empty `expected.json`
  (`ok = ... and bool(expected)`), and the variant's is `{}` (the GM never verified it). It is still replayed because its
  target is live. I may not submit (task rule) and must not hand-edit `expected.json`, so it cannot turn green here.
- Needed from the orchestrator: submit the solver's 3 answers (`hctf submit <id> --from-solver`) so the GM-accepted values
  land in expected.json, or treat an unverified-but-fully-answered live variant as passing.
- Derived proofs are in solver/NOTES.md (not GM-verified). VARIANT AXIS line is there too.
