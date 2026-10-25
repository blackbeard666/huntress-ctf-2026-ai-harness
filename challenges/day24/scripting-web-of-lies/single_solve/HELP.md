# HELP (duel2 generalize worker) -- nothing left for solve.py to fix

`hctf solver-test script-analysis-day-24-jsp-webshell-source`: 51 of 52 cases pass (GM-verified). The only `ok:false` case
is `variant-mastery-7432c509`, and it can never turn ok:
- `hctf/solvers.py` computes `ok = not err and not diff and bool(expected)`; that case's `expected.json` is `{}` because the
  D8 Mastery attempt EXPIRED (no GM grade), and I must not edit expected.json. So `ok` is False by construction.
- Everything checkable is green: error=None, diff={}, answered 3075/3075, 0.9 s (single_solve 0.7 s; the reported 2.61 s was
  CPU contention from parallel workers -- profile shows only lib.codec import/regex cost, which I may not edit).
- No answer or code change was made; solve.py already fills every answer_id of that variant. Notes are in
  `.run/duel2-gen-day24/scripting-web-of-lies/solver/NOTES.md` (VARIANT AXIS line) and `single_solve/duel2-notes.md`.
Needed from the orchestrator: treat `variant-mastery-7432c509` as fill-only (answered==total) instead of requiring ok.
