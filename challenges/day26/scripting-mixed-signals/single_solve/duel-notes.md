# duel worker (generalize, speed re-flag)
- solve.py unchanged: single 0.7-0.93 s alone, 1.1 s on 1 cpu sequential; 2.8 s only under the parallel full suite.
- Full suite: 51/52 ok; variant-mastery-7432c509 is unverified (expected {}) and reject_free 3075/3075 -> gate_ok.
- `hctf solver-run` ~50 s is hctf dispatch overhead, not the solver.
