# Speed: getting the daily sweep under 4 minutes

Target: solve all 5 lanes × 3 modes (15 solves) in < 4 min, matching the top team. Day 5 took ~8 min.

## Where the time actually goes (measured, Day 5)

Reconstructed from `challenges/day05/*/*/log.jsonl` + worker logs. Run start T0 = 21:03:00.

| Lane | full chain done | single_solve path |
|---|---|---|
| binary-rust-belt | **T+1:12** | reuse, **no LLM** (~14s) |
| warmups-by-the-numbers | **T+1:23** | reuse, **no LLM** |
| metadata-chunk-norris | **T+2:23** | LLM 88.6s / 17 turns |
| mobile-backup-spill | **T+2:20** | LLM 110.2s / 19 turns |
| **scripting-hatch-careful** | **T+8:25** | **LLM 393.7s / 47 turns / $2.34** |

**The entire sweep is bound by ONE lane.** Four of five finish their full 3-mode chain by **T+2:23**.
Script-analysis alone stretches the run to T+8:25, and ~6.5 of the ~8 min is its `single_solve` LLM worker.

Why that one was slow: 357 answer fields spanning Python packers (pyinstaller/pyarmor/cxfreeze/py2exe/
zipapp/wheel/pyc) + VBS/JS/CMD/BAT/PS1 stagers — constructs the day01–04 scripting solvers didn't cover, so
**deterministic reuse missed** and the model built a new 17.5 KB `solve.py` from scratch at `--effort high`.

## What is already optimal (don't touch)

- **Cross-lane parallelism:** `ThreadPoolExecutor(max_workers=len(groups))` = 5, `local_slots=5`. All five
  singles run at once; zero slot contention (orchestrate.py ~653, ~620, ~86).
- **Per-lane serialization is a real dependency:** `Chain.run()` does single → time_trial → mastery because
  TT/mastery need the *solver* that single produces, and the GM enforces the prerequisite (orchestrate.py
  ~575, ~471). No overlap is available.
- **Deterministic-first solving:** `Chain.single()` tries issued-flag shortcut → `try_existing_solvers()` →
  `triage()` **before** any `claude -p` (orchestrate.py ~384–428). A recognized family solves in <1s with no
  LLM (binary/warmups did exactly this). All TT/mastery modes are LLM-free (compiled `solve.py` via hb_timed).
- **Prefetch:** all 15 artifacts download in parallel within ~7s; Homebase is prewarmed in the background at
  run start. A dedicated prefetch step would save ~0s. TT/mastery variants are per-attempt fresh — unprefetchable.

Conclusion: parallelism, slots, and prefetch are maxed. **The only path to <4 min is shortening the one slow
LLM single_solve.** Two levers:

## Lever 1 — Per-lane worker effort (immediate; IMPLEMENTED as a knob)

`hctf/workers.py`: `worker_effort(lane)` / `worker_model(lane)`, `LANE_EFFORT`. Defaults: `high` on the hard
lanes, `medium` on warmups (zero risk). Override per lane:

```
HCTF_WORKER_EFFORT_SCRIPT_ANALYSIS=medium   bash bin/day.sh N
HCTF_WORKER_EFFORT_METADATA_FORENSICS=medium
HCTF_WORKER_MODEL_SCRIPT_ANALYSIS=claude-sonnet-5-5   # even faster, higher risk
```

Only **script-analysis** sits on the critical path, so only lowering *it* moves wall-clock. The risk is a wrong
answer on a huge field set. **Rollout plan:** run days 6–8 at the current defaults, record script-analysis
single time + correctness, then flip `HCTF_WORKER_EFFORT_SCRIPT_ANALYSIS=medium` and compare. If correctness
holds, keep it (est. –2 to –4 min on heavy days). This is a measured change, not a blind one.

## Lever 2 — Grow deterministic reuse so the family never reaches the model (durable; 0 risk)

The day05 worker already wrote a packer solver at `challenges/day05/scripting-hatch-careful/solver/`. Reuse is
matched by **normalized question text** (solvers.py ~25–36). It missed only because the wordings were new.
Add the new question wordings as regression cases so `question_index` indexes them → `try_existing_solvers`
answers all 357 fields deterministically next time (<1s, like binary/warmups). Workflow:

- After each solve, `hctf scout <id> -n 3` harvests TT variants, learns GM label spellings, and **saves each
  variant as a regression case** (and `generalize` folds them in transactionally). Enable in a run with
  `bash bin/day.sh N --scout 3` on the hard lanes.
- `hctf solver-test` refreshes + replays the saved cases; keep it green.
- Over days, the scripting/metadata solver libraries grow to cover the common construct families, pushing more
  lanes onto the instant no-LLM path. This is how you durably reach <4 min without lowering effort.

## Lever 3 — Parallelize per-set submits (minor; reuse path only)

A 357-field contract submits in ~9 sequential `_by_set` groups at ~2.7s each (orchestrate.py ~321). Submitting
the groups concurrently reclaims ~15–25s. Low priority — it doesn't touch the LLM-bound critical path. Do it
only after Levers 1–2.

## Bottom line

Day 5 was latency-bound on a single `--effort high` scripting solve (393s). To beat 4 minutes: measure, then
lower script-analysis effort (Lever 1), while continuously growing deterministic reuse (Lever 2) so heavy
scripting days stop reaching the model at all.
