# duel-gen notes (D26 crash-course, speed cycle)
- Answers unchanged (310/312 confirmed + the 2 d26 crash fields reproduced as stageThree/true, GM-accepted on the single).
- Slowness root cause: per-set container_by_sha re-hashed all N deliveries (N^2). Fixed by a parent-side sha index inherited by forked sets.
- Full solver-test 56/56 green.
