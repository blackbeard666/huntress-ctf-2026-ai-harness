URGENT, a live clock is running. You are a fix worker in the Huntress CTF harness. Use the `timed-run` skill.

- Timed challenge: `{cid}`, about **{seconds_left} seconds left** (deadline {deadline} UTC). Every second counts.
- Contract (questions/answer_ids for this variant): `{chal_dir}/contract.json`
- Variant artifacts: `{chal_dir}/artifacts/latest/`
- Solver to fix: `{solver_dir}/solve.py` (it worked on earlier variants; regression cases in `{solver_dir}/cases/`)
- What went wrong:
{problems}

Do this, fast:
1. Look at what is different in this variant (file names, layout, encoding layers, extra/compounded sets).
2. Patch the solver so it stays general (no hard-coded answers), then run `hctf solver-run {cid}` until every answer_id gets a value.
3. If there is time, run `hctf solver-test {base}` to make sure earlier cases still pass.
4. Stop. Do NOT submit; the orchestrator submits as soon as you exit.
