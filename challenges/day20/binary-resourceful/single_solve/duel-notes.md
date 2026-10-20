# duel (generalize, speed cycle)
- No code change. The solver is not slow: 0.7-1.1 s isolated on the single (240/240 verified), 0.70 s pinned to 2 CPUs. The 5.28 s was a contention measurement (load avg ~5).
- The full solver-test passes all 43 cases (worst Mastery 2.5 s with the whole suite running in parallel).
- The open GM field d20_analysis_hcfg_resource_size: the solver outputs 380, which matches the single's expected.json.
