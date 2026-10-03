---
name: timed-run
description: Fixing a solver while a Time Trial or Mastery clock is running. Covers reading the live variant (contract.json + artifacts/latest), diffing it against the solver's regression cases, patching fast while staying general, and verifying with hctf solver-run. Use when the prompt says a live deadline is running.
---

# You are racing a server-side deadline
The orchestrator already started the attempt, downloaded the variant and ran the solver library. Something failed.
**Do not submit**: the orchestrator submits the moment you exit, and every second you spend counts.

1. `cat <mode dir>/contract.json | python3 -m json.tool | head -80`: count the sets and questions, and note the artifact names.
2. Compare with `solver/cases/*/contract.json` (what the solver already handles). Usual differences:
   - new file names or an archive wrapper
   - more or fewer encoding layers, a different key or alphabet
   - extra Mastery sets, or a question from an *earlier day* that belongs to another challenge's solver. The dispatcher matches by
     question text, so if one is unmatched, reuse that other solver's logic: import it, don't copy it.
3. Patch `solver/solve.py` with the smallest general change (no answer literals).
4. `hctf solver-run <mode id>` until `missing` is empty and `problems` is empty. Then stop.
5. If time allows: `hctf solver-test <base id>` so the old cases still pass.

If you can't finish before the deadline, still stop when about 20 s are left. The run expires, the variant is kept as a
regression case, and the orchestrator retries with the improved solver.
