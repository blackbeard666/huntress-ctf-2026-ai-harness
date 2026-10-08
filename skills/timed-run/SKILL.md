---
name: timed-run
description: Fixing a solver after a Time Trial or Mastery variant beat it (offline, between attempts -- no clock is running while you work). Covers reading the failed variant (variant-*/auto-*/mutation-* cases), diffing it against the passing cases, fixing the construct family generally, and verifying with hctf solver-test / solver-run.
---

# A timed variant beat the solver -- fix it offline
No LLM runs inside the clock: the window ran `solve.py`, submitted what it could (the answered subset too when it was
incomplete) and localized wrong fields. You are the generalize worker between attempts. **Do not submit or start
attempts**: the orchestrator retries with a fresh variant the moment the failing case passes.

Time Trial / Mastery are NEW, dynamic mutations of the task (organizer: "new unseen effects"), so fix the family, not
the sample:
1. Open the newest `solver/cases/variant-*` / `auto-*` / `mutation-*` case: `contract.json` (sets, questions, artifact
   names) and its artifacts. Compare with a passing case. Usual differences:
   - new file names, an archive wrapper, more nesting, a delivery named `delivery N: <name>` per Mastery set
   - more or fewer encoding layers, a different codec / key / alphabet / radix, another container (ELF<->PE)
   - extra Mastery sets, or an ESCALATED field set carrying earlier days' questions (`dNN-...` ids): the verdict names
     the earlier day's solver of this lane -- adapt (import or port) its parsing; answers still come from today's bytes
   - `mutation-*`: same answers, answer-invariant change (renamed delivery, reordered/subset/extra questions, two sets)
2. Patch `solver/solve.py` with the smallest GENERAL change (no answer literals, no special case for this variant);
   every field fails independently, unknown questions are skipped, a cheap fallback runs only on a miss.
3. `timeout 20 hctf solver-test <base id>` -- every case passes -- and `hctf solver-run <mode id>` outputs every
   answer_id. Then stop.
