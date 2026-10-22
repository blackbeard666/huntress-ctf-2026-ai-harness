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
3. **Single prep overhead ~11.5s post-triage (OPEN, daytime).** `GO_EARLY=1` already keeps the prior-solver dry-run off
   the critical path, so the 11.5s is something else (prior-solver copy / compound-contract read / mastery_delta).
   Pin it (compare web's 11.5s vs script's 4.4s post-triage) and trim for web. Modest (~11s).

## Pole B (SCOPE — daytime, highest remaining value): re-author the web solver to re-exploit the live target
**Why:** if the web single's `solve.py` performed the exploit *parametrically* (recon → exploit → read `proof` from the
live target by URL), TT and Mastery would solve **first-try** with NO live-answer at all — removing the whole ~40s
solver-then-live-answer per timed mode (and making "A" unnecessary). This is the real path to web under 2 min.
**What to change:** the web single solver-authoring prompt / `solver-authoring` + `web` skills so the deliverable
`solve.py` (a) takes the target URL/base from the contract's `targets`, (b) performs the exploit against *that* URL at
run time (not cached answers), (c) extracts each `proof-*` from the live response. Today's solvers answer static fields
only and defer `proof-*` to the single worker.
**Risk:** solver-quality/variance across unseen web challenges; a live-exploiting solver can be fragile. Keep live-answer
as the backstop (it already works). Validate on the rehearsal replay; measure first-try TT/Mastery rate.
**Open question:** is the exploit deterministic enough per fresh target that one authored `solve.py` re-exploits every
variant? If the proof is e.g. a per-target random flag obtained by a fixed exploit, yes; if it needs per-variant recon,
the solver must recon too.

## Validation plan (web is NOT in offline replays — `replay_main_self.sh` sets `web-*` aside)
1. **Blind rehearsal replay** of a web day with the branch harness + flags:
   - Baseline: flags off (current main behavior) — expect web ~T+7:50-shape.
   - Pole #1 only (default): expect web Mastery ~T+2:30-3:30.
   - Pole #1 + "A" (`HCTF_WEB_TIMED_LIVE_FIRST=1`): expect web TT/Mastery each ~35s faster.
   - Tune `HCTF_WEB_LIVE_FIRST_BUDGET` (5s start) so the first attempt reliably returns `solver_incomplete` with
     `missing` populated (NOT `solver_error` — a live-answer needs the field list).
2. Record a KPI row per config; compare web finish T+ per mode (never rank on total — [[incomplete-runs-not-best]]).
3. Merge `d22-web-critical-path` to master once the rehearsal replay confirms web improves with no regressions; sync alt.

## Flags (all reversible)
- `HCTF_WEB_PRE_MASTERY_HARDEN=1` — restore the old blocking pre-Mastery harden (pole #1 off).
- `HCTF_WEB_TIMED_LIVE_FIRST=1` — enable live-answer-first (pole #2 "A"); `HCTF_WEB_LIVE_FIRST_BUDGET` tunes the cap (5s).
