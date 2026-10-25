# HELP: generalize gate cannot pass (unverifiable case), solver work is done

- Fix made: the speed failure. In `.run/duel-gen-day25/scripting-ashes-to-assets/solver/solve.py`, ~180 per-member
  `log(member, json.dumps(...))` stderr dumps (0.43 s of `print` on the harness pipe) now run only with
  HCTF_SOLVER_DEBUG=1. Single solve: about 0.6 s wall (0.71 s on 1 CPU, was 2.59 s). Answers are byte-identical.
- Full `hctf solver-test`: 51/52 cases pass with no diff and every field filled; `hctf solver-run`: missing [], problems [].
- Blocker: `cases/variant-mastery-7432c509/expected.json` is `{}` because the D8 attempt expired ungraded.
  `hctf/solvers.py` test_solver sets `ok = not err and not diff and bool(expected)`, so this case is ok=false for ANY
  solver. The solver fills 3075/3075 fields. The fix has to come from the orchestrator: treat `unverified` cases as
  non-blocking in the stop gate (ensure_case_and_test), or retire this case. Workers may not edit expected.json or hctf/.
