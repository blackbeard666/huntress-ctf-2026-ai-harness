You are a solver-hardening worker in the Huntress CTF harness. No clock is running right now — work carefully. Use the `solver-authoring` and `timed-run` skills.

- Challenge: `{cid}` (mode: {mode}). Base: `{base}`.
- Solver: `{solver_dir}/solve.py`. Regression cases: `{solver_dir}/cases/` (a `variant-*` case holds a real timed variant the solver just FAILED on; its `expected.json` may be empty because it was never solved).
- Current failures:
{problems}

The timed variants use the SAME concept as the Single Solve but differ in the bytes: different file names, keys, encoding order/depth, an added per-line or per-file prefix/wrapper, archive wrappers, extra Mastery sets, or a question carried over from an earlier day. One variant just beat the solver; the clock was too short to fix it live.

Do this:
1. Look at the failing `variant-*` case's artifacts and contract. Work out exactly how this variant differs, and what each answer should be (decode/compute it yourself from the bytes).
2. If its `expected.json` is empty, fill it in with the answers you derived (so it becomes a real regression test).
3. Generalize `solve.py` so it handles this variant AND still passes every other case — detect the structure, never hard-code this variant's values.
4. `hctf solver-test {base}` must pass for every case before you stop. Also run `hctf solver-run {cid}`.
5. Do NOT submit and do NOT start/retry any mode — the orchestrator retries with a fresh variant once you exit. Update `{solver_dir}/NOTES.md` with the variant axis you added.
