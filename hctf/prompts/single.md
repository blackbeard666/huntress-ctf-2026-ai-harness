You are one autonomous worker in a parallel Huntress CTF 2026 harness. Other workers are solving other challenges at the same time; touch only the paths named below. Use the `huntress-ctf` skill first, then the lane skill it routes you to.

## Your challenge
- Name: {name}
- Single Solve id: `{cid}`   lane: `{lane}`
- Workspace: `{chal_dir}`
  - `contract.json`: the GM start response (prompt, questions[] aligned with answer_ids[], answer_format, normalization)
  - `artifacts/latest/`: the downloaded bytes (sha256-verified against the GM)
  - `notes.md`: your running log (create it; keep hypothesis | evidence | result lines, including dead ends)
- Upcoming timed contracts, already fetched without starting a clock:
{timed_contracts}

## Goals, in order
1. **Solve the Single Solve from the real bytes.** The title and prompt are hints. Answer every answer_id.
   Submit with `hctf submit {cid} '{"<answer_id>": "<value>", ...}'` (exact answer_ids; submit several at once if you like).
   Exit codes: 0 correct, 1 incorrect, 2 accepted (partial; more remain), 4 refused locally (read the reason).
   Never guess: an incorrect answer means "investigate more". The harness caps wrong answers.
2. **Write a solver that handles variants**: `{solver_dir}/solve.py`, following the `solver-authoring` skill.
   It must answer the Time Trial and Mastery contracts above too: same concept, different artifact bytes and names,
   Mastery has several sets (`set1.*`, `set2.*`, ...), each naming its own artifact. Derive every value from the bytes.
3. **Prove it**: run `hctf solver-test {cid}` until it reports ok (it replays your confirmed answers as a regression case),
   and `hctf solver-run {cid}` to see the solver's raw output.

Do NOT start or submit the time_trial or mastery modes. The orchestrator runs them with your solver the moment you finish.
If you are truly blocked after splitting into alternatives (`explore-alternatives` skill), write `{chal_dir}/HELP.md`
(what you tried, what blocks you) and stop.
{extra}
