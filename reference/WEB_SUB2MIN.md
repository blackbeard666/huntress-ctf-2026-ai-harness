# Web critical path → sub-2-min (whole board)

**Goal** ([[sub2min-whole-board-goal]]): the ENTIRE board, web included, GM-CORRECT within 2 min of the drop. Day 22
standard board was T+1:35 but **web finished T+7:50** — the whole-board miss. This doc is the diagnosis + the fix work.

## Day 22 web timeline (per chain; from .run/day22.log)
- Single CORRECT: T+1:20 / T+1:38 (LLM exploit of the live target; ~46s solve + ~18s prep)
- TT CORRECT (live-answer): T+2:40 / T+3:27 — first attempt blocked (`solver_incomplete`, missing `proof-1`, solve 40s)
- **Mastery live target ready in 4.5s** (GM not slow); **pre-Mastery speed-harden ran ~4.5 min**; Mastery solved in 14s
  with `window: null` (no clock). → T+7:17 / T+7:50.

## Poles and status
1. **Mastery pre-Mastery speed-harden gate — ~4.5 min (DONE, default on).** `_web_speed_gate` ran a BLOCKING generalize
   before the first Mastery attempt. On a live web lane the target is ready in ~5s and Mastery has no clock, so it was
   pure serial delay. Fix (commit a26b98d8, branch `d22-web-critical-path`): skip the blocking harden for live web lanes
   (`is_live_lane`); first attempt runs now, blocked-path live-answer recovers a slow one, post-run speed-harden still
   banks the fast solver. Revert: `HCTF_WEB_PRE_MASTERY_HARDEN=1`. Untimed non-web keeps the blocking harden.
2. **TT/Mastery first attempt wastes ~40s then blocks → live-answer (DONE as "A", flag default OFF).** The web solver
   has no handler for the live-exploit `proof` field, so it runs its full ~40s and still blocks. Fix "A" (commit
   ee561bbb): cap the FIRST web timed attempt's solver seconds (`HCTF_WEB_LIVE_FIRST_BUDGET`, 5s) so it blocks fast and
   the proven blocked-path live-answer takes the open attempt at once (serial — no concurrent double-submit). Retries
   clear the cap. **Enable with `HCTF_WEB_TIMED_LIVE_FIRST=1`.** Est. web TT ~72s → ~39s. NOT YET VALIDATED (web is
   excluded from offline replays — validate on the rehearsal replay).
3. **Single prep overhead ~11.5s post-triage (INSTRUMENTED, trim after the rehearsal run).** `GO_EARLY=1` already keeps the
   prior-solver dry-run off the critical path, and web is NOT a cumulative lane (`prior_solver_dir` returns None for web;
   it seeds from `lib.web`, staged pre-triage) — so the 11.5s is post-triage: retrieval, the upcoming-timed-contract
   prefetch wait (`tfuts` status calls — may be slow for web), or prompt-build (`mastery_delta`/`lane_known_shapes`).
   Couldn't pin by inspection, so the post-triage timer is now split in the go-text line:
   `post-triage Ws [retrieval As, timed-prefetch Bs, prompt-build Cs]` (orchestrate `_prelude_split`). The rehearsal run names
   the culprit; then defer it off the go (the timed-contract list / compound note can follow via the inbox like the dry
   run does). Modest (~11s).

## Pole B (DONE — prompt change in `skills/web/SKILL.md`, validate live): web solver must re-exploit
**Why:** if the web single's `solve.py` performs the exploit *parametrically* (recon → exploit → read `proof` from the
live target by URL), TT and Mastery solve **first-try** with NO live-answer — removing the whole ~40s
solver-then-live-answer per timed mode. This is the real path to web under 2 min.
**Root cause (not a missing instruction):** the web skill already said "fetch from the live target," but the single
worker gets the proof by hand, writes a `solve.py` that only handles static fields, and the single's target dies (HTTP
410) at CORRECT, so nothing catches the gap before TT hits a FRESH target.
**Change (committed):** `skills/web/SKILL.md` adds a mandatory section "proof-* fields: solve.py MUST re-exploit":
`exploit(base_url)->answer` re-runs end to end against `contract["targets"]`; and **before submitting the single, RUN
solve.py against the still-live single target and confirm it reproduces EVERY field incl. proof** (the one lane where
self-verifying against the live service is REQUIRED — it overrides single.md's generic "don't reach a backend to confirm"
rule, which exists because the target is about to 410 and TT/Mastery get a fresh one).
**Risk:** solver-quality/variance; keep live-answer + pole #2 "A" as the backstop. Measure first-try TT/Mastery rate on
the rehearsal run. **Open question:** is the exploit replayable on a fresh target (fixed exploit → per-target flag = yes; needs
per-variant recon = solver must recon too). The skill tells the worker to assume replayable until the live run disproves.

## Validation plan — ALT IS FRESH ON DAY 22, so web runs for real
The "web excluded from replays" caveat only applies to a SELF-replay of an already-solved day (the solved web single is
sticky-accepted, not freshly exploited; `replay_main_self.sh` sets `web-*` aside for that reason). **Alt has NOT solved
Day 22**, so the validation is a plain LIVE run of Day 22 on a rehearsal copy against the real GM — web runs naturally with FRESH
targets (single + TT + Mastery all genuinely exploited). No replay-GM/local-serve needed; no web-aside.
1. Sync the branch harness (`hctf/`, `skills/web`) onto the rehearsal copy; run `hctf run --day 22 --local 5` on a rehearsal copy with:
   - **Pole #1** on by default (`HCTF_WEB_PRE_MASTERY_HARDEN` unset) — expect web Mastery ~T+2:30-3:30 (was 7:50).
   - **Pole #2 "A"**: `HCTF_WEB_TIMED_LIVE_FIRST=1` — expect web TT/Mastery each ~35s faster; watch the `routed`
     line show `live-first Ns` and the first attempt return `solver_incomplete` with `missing` populated (NOT
     `solver_error` — a live-answer needs the field list; tune `HCTF_WEB_LIVE_FIRST_BUDGET`, 5s start).
   - **Pole B**: watch whether TT/Mastery now solve FIRST-TRY (solver produced proof, no live-answer) — the win that
     makes "A" unnecessary. Read a web worker's go-text line for the pole #3 `[retrieval/timed-prefetch/prompt-build]`
     split to name the single's ~11.5s.
2. Record a KPI row; compare web finish T+ per mode (never rank on total — [[incomplete-runs-not-best]]).
3. Merge `d22-web-critical-path` to master once alt confirms web improves with no regressions; sync both copies.

## Flags (all reversible)
- `HCTF_WEB_PRE_MASTERY_HARDEN=1` — restore the old blocking pre-Mastery harden (pole #1 off).
- `HCTF_WEB_TIMED_LIVE_FIRST=1` — enable live-answer-first (pole #2 "A"); `HCTF_WEB_LIVE_FIRST_BUDGET` tunes the cap (5s).
