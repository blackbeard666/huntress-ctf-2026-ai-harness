# Day 22 post-mortem (main live + rehearsal validation) and the whole-board sub-2-min plan

Goal ([[sub2min-whole-board-goal]]): every lane **incl. web** GM-CORRECT within 2:00 of the drop. Top team did the
whole board in ~1:00 on D22.

| run | standard 15/15 | web 6/6 | live-answer passes | cost | conditions |
|---|---|---|---|---|---|
| main live (21:00) | **T+1:35** (KPI) | T+8:00 | 2 | $8.65 | clean host, slow HB VM (x8.7) |
| rehearsal validation (22:58) | T+14:02 | T+7:29 | 7 | $19.36 | **host shared with main's prebuild**, branch harness, alt knowledge |

Both 21/21. Neither met the goal. All numbers below are from `.run/day22.log` (main), the per-attempt table
(`python3 .run/timed_table.py <log> <t0>`) and `hctf timeline --log`.

---

## 1. What went wrong — root causes, with evidence

### A. The validation environment was invalid (self-inflicted)
- **A1. Two harness copies shared one 12-core host.** Main's `prebuild --parallel` (LLM workers of 300–756 s each +
  solver regression gates) ran through the whole rehearsal run. Binary's coordinator hint: *"timeouts came from machine load
  (avg 37-50), not from solve.py"*. Prebuild's own gates failed from the same load (`find_codecs took 2.26s (> 2 s)`).
  `bin/day.sh` step 0 and `preflight.sh` only guard **their own copy's** prebuild; preflight checks memory, not CPU load
  or other copies. Alt preflight's "GM slow 10.3 s" was likely partly local contention.
- **A2. I validated with a 4-file sync instead of `bin/fair_run.sh <day> <pre> [overlays]`.** The rehearsal copy's seed/solver state
  was not main's pre-drop state, so standard-lane differences mix harness and knowledge. fair_run supports overlays
  (the branch `hctf/` comes from main HEAD; `skills/web/SKILL.md` can be overlaid) — it was the right tool.

### B. The harness still runs clock-era machinery in a no-clock regime
Every D22 TT/Mastery contract (both runs) has `deadline=None, run_for_time=False`; every attempt reported
`window=None`. Spot checks show the same on D15/D16/D17/D19 TTs.
- **B1. Pre-TT single speed gate fires with no clock.** `SINGLE_SPEED_BUDGET=2.5 s` → "speed generalize before the
  first timed attempt". Alt script: single 3.1 s → TT at **T+4:00** (main T+1:03). Alt binary: 6.4 s "re-timed alone"
  (on a loaded host) → **7 min speed generalize** → TT at **T+10:32** (main T+1:23), 542 s on the critical path.
  With no clock a 3–6 s solver costs nothing.
- **B2. First-attempt routing sends heavy no-clock Masteries to the slow VM.** "Window unknown" → Homebase-first unless
  `homebase_cheaper()` says otherwise, and before any measurement the estimate (from the single's tiny solve stamp)
  badly under-counts a multi-set Mastery. Alt warmups Mastery: **63.9 s solve on the VM** vs **2.75 s locally**; main's
  warmups Mastery: 15.9 s solve + 11.8 s submit on the VM (~6 s locally). The retry then logs the right rule
  ("VM x7.51 slower and the window is unknown/untimed: running locally") — only after the miss.
- **B3. VM budget exhaustion is misread as an incomplete solver.** The 63.9 s run returned `solver_incomplete` with
  108/108 fields empty. `_slow_vm_no_clock()` requires `solver_too_slow`, so instead of re-running the live attempt
  locally it started a **4-min generalize on a solver that was fine** → warmups Mastery at **T+8:15** (main T+1:23).

### C. Generalize start-up latency
Decision → worker spawn took **1:23 (warmups), 1:43 (binary), 2:24 (script)**. Before spawning, `generalize()` runs
`_baseline_results()` — a parallel replay of every regression case (CPU-bound; it exploded under A1) — plus pool
acquisition. The transactional gate needs the baseline only at accept time.

### D. Reuse-race seeds are verified against the single only
Alt metadata single: **reuse race WON at +16.8 s** ("seed verified → the ready-watcher hands it to the timed modes").
TT/Mastery then asked the D21 carry-over field `d21-apk-001-apk-package-name` the seed lacks → both blocked →
live-answer: TT T+1:31 (main 1:00), Mastery T+3:08 (main 1:35). The timed contracts are prefetched at chain start
(the "MASTERY COMPOUNDS … carried over" line), so coverage could be checked at the race win — it isn't. Alt binary's
Mastery miss (`set5.d14_analysis_hcfg_storage`) is the same family (carry-over field on one set).

### E. Web: every new class is discovered three times
Mastery = 3 live targets ("Recover the proof from Target N"): today's class + 2 earlier classes, **shuffled**.
- **E1. A doomed 40 s race.** `lib.web.solve_target(budget=40)` races clue-keyed handlers + every earlier day's
  `answer()` + a `default` ladder. For a never-seen class only the ladder applies, and it failed every time on D22:
  4/4 TT attempts burned 40.7–42.9 s, Masteries 53–59 s, then blocked. (Race winners go to stderr — the ladder's real
  hit rate is unmeasured.)
- **E2. The hot single worker is killed at CORRECT** (`exit -15`), although for web "solver verified" means
  "handed over without a replay" (the target is 410 after CORRECT). The exploit never becomes a clue-keyed handler
  during the run.
- **E3. The winning method is thrown away.** `_live_methods` is fed only by live-answer workers; the answer-first /
  single method goes to the single worker's inbox. So each chain's first live-answer (the TT) starts **cold**:
  32/56 s on main, 71/66 s on a rehearsal copy.
- **E4. Fixes aren't target-agnostic.** The rehearsal copy's TT-time generalize was accepted, but on Mastery today's class sat on
  Target 3: *"the day-22 solver is just the generic web dispatcher, and it has no file-upload handler"* → proof-3
  empty → another live-answer (133/122 s under load).
- **E5. Banking is one day late.** The ratchet folded `upload` + `csrf` (today's classes) into
  `lib/web/handlers/__init__.py` at 21:13 — after the run. The rehearsal copy's handlers file still has only `session_fixation`.
- **E6. Pole B (skill mandate) can't fire as designed:** answer-first/duel usually submits first and the single worker
  is then killed (E2). Worse, "verify solve.py before submitting the single" can *delay* the single. Needs E2's fix.
- **Pole #3 measurement:** web single post-triage is **100 % prompt-build** — `[retrieval 0.0s, timed-prefetch 0.0s,
  prompt-build 9.2s / 13.9s]` (mastery_delta / compound / carry-over notes).

---

## 2. What went right — keep, and optimize

- **Pole #1 is a real win** (I first called it a wash by comparing end-to-end T+ across very different load; the
  per-phase numbers say otherwise). TT CORRECT → Mastery CORRECT:

  | chain | main (4–5 min pre-Mastery harden) | alt (pole #1, live-answers ~2x slower) |
  |---|---|---|
  | uploading-expectations | 5:20 | **3:29** |
  | forged-with-care | 4:00 | **3:32** |

  At main-like live-answer speed the rehearsal copy phase would be ~1:45 → a ~2–3.5 min win per web chain.
- **Reuse race** won 5 standard singles in 17–31 s; TT pre-start at the single's CORRECT and Mastery pre-start at the
  TT's CORRECT both work; Homebase TTs with tiny solves are ~1 s attempts.
- **Recovery is robust:** 7 live-answer passes on a rehearsal copy, 0 untimed fallbacks, 0 `!!!` alerts, 0 rejected generalizes.
- **Compounding works one day late:** web-harden re-solves web days 1–8 CORRECT; tonight's ratchet banked D22's classes.

**Where main's 1:35–1:45 standard board goes** (`hctf timeline`, T+ from the drop):

| chain | single | TT | Mastery | single→TT | TT→Mastery |
|---|---|---|---|---|---|
| mobile | 22 | 43 | 53 | 21 s | 10 s |
| warmups | 25 | 40 | 83 | 15 s | 43 s (VM attempt 28 s) |
| metadata | 43 | 60 | 95 | 17 s | 35 s |
| binary | 62 | 83 | 103 | 21 s | 20 s |
| script | 47 | 63 | 105 | 16 s | 42 s |

The attempts themselves are 2–18 s. The rest: **Mastery pre-start downloads at drop load 20–25 s** (metadata 24.7,
script 22.2, binary 20.3 — TTs 4–6 s), a **resume `start` after the pre-start** (2–7 s, the runner reuses the bytes
but still calls start), submit 1–7 s, and the reuse race itself (script: +27.6 s).

---

## 3. Plan

Owner: orchestrator. Every item ships with a test in the existing suites and a flag to revert.

### P0 — before the next run (cheap, high certainty)
| # | change | fixes | expected |
|---|---|---|---|
| 1 | **Host exclusivity.** `preflight.sh` FAILs (and `day.sh` stops with a clear message) when ANY other harness copy's prebuild or run is live on the host; `fair_run.sh`/rehearsal runs refuse to start beside main's prebuild. | A1 | valid measurements; no false speed gates |
| 2 | **No clock ⇒ no pre-attempt speed gates.** When the next mode's contract has `deadline=None and run_for_time is False`, skip `_note_single_speed` (pre-TT), `_mastery_speed_gate` and `_web_speed_gate`; at most a background copy-generalize (`_start_bg_gen` style), never on the critical path. Generalizes pole #1 to all lanes. | B1 | alt-like loads: script TT −3 min, binary TT −9 min; clean: guards future regressions |
| 3 | **No clock + slow VM ⇒ local on the first attempt** for multi-set modes; Homebase only once a measurement says it is cheaper. | B2 | main warmups Mastery ~−20 s |
| 4 | **Slow-VM budget exhaustion = too slow.** Homebase-routed, no clock, solve ≥ budget and ≥ 90 % fields empty ⇒ mark `solver_too_slow` ⇒ the existing local re-run of the live attempt. | B3 | removes the rehearsal copy 6-min warmups detour |
| 5 | **Revise the pole-B skill text** to "never delay the single's submission; codify after" until #8 keeps the worker alive. | E6 | no single slowdown |

### P1 — web critical path (the long pole)
| # | change | fixes | expected |
|---|---|---|---|
| 6 | **Propagate the winning method.** At the single's CORRECT push the answer-first result / single worker's final notes into `_live_methods`, so the TT live-answer starts hot (and Mastery's after it). | E3 | TT live-answer 32–56 s → ~15–25 s |
| 7 | **Skip the doomed race, precisely.** First log race winners into the timed result (stderr today). Then: if no clue-keyed handler or earlier `answer()` matches a target's key, cap that target's ladder (~8 s) so the attempt blocks fast. Replaces pole #2's blunt first-attempt cap (keep pole #2 off). | E1 | −30 s per web TT and Mastery |
| 8 | **Codify at CORRECT for web.** Don't kill the web single worker at CORRECT: give it a bounded window (≤45 s, overlapping the TT target provisioning) to write today's exploit as a **clue-keyed handler** in its solver (dispatch on the `/api/clues` key, never on target number); the TT attempt runs it; live-answer stays the fallback. | E2, E4, E6 | TT/Mastery first-try ~10–15 s each |
| 9 | **Bank handlers in-run.** When a web TT passes, fold its clue-keyed handler into the chain solver before Mastery starts (not only at the post-run ratchet). | E4, E5 | Mastery's shuffled targets hit today's class first-try |
| 10 | **Pole #3:** move prompt-build notes (mastery_delta / compound / carry-over) off the web go-text via the inbox, like the prior-solver dry run. | measured | web single −9–14 s |

Web budget if P1 lands: single ~1:05 + TT ~0:20 + Mastery ~0:25 ≈ **1:50** (vs 8:00 today). The single's LLM exploit
(~45–60 s for a never-seen class) is then the floor.

### P2 — standard good path (1:35 → ~1:15 and below)
| # | change | fixes | expected |
|---|---|---|---|
| 11 | **Coverage check at reuse-race win:** dry-check the seed against the prefetched TT/Mastery field shapes; if carry-over shapes are missing keep the single worker on them / start a background generalize, instead of handing an incomplete seed to the timed modes. | D | avoids D's +1–1.5 min |
| 12 | **Generalize starts first:** spawn the worker immediately and run `_baseline_results()` beside it (needed at accept time only). | C | −1 to −2 min per generalize under load |
| 13 | **No resume after pre-start:** when the pre-start body's `attempt_id` matches, the runner uses it without a second `start`. | §2 | −2–7 s per mode |
| 14 | **Measure, then attack, drop-time GM I/O:** log Mastery artifact sizes + download throughput; try parallel ranges for Mastery bytes; profile the reuse race (script +27.6 s). | §2 | the remaining 20–40 s per chain |

### P3 — validation procedure (so the next run proves something)
1. Stop main's prebuild (P0 #1 enforces it), then on a rehearsal copy: `bash bin/fair_run.sh <day> <pre-drop commit> skills/web/SKILL.md`.
2. Alt has now solved D22 (web would be sticky) → validate on **rehearsal D23**, fresh, after main's live D23.
3. Score **per phase** (single → TT CORRECT → Mastery CORRECT per chain), not only end-to-end T+, and record
   `hctf kpi --label`. A run on a contended host is not a speed result.

### Implementation status (10-23, branch `d22-web-critical-path`)
Tests: `tests/test_d22_postmortem.py` (74 checks) + `tests/test_hostguard.py` (68); pinned `test_day7_fixes` #26 and
`test_web_lane` #13 to the clocked regime they test. Every change has a flag.

| # | shipped | flag (default) | note |
|---|---|---|---|
| 1 | `hctf/hostguard.py`; preflight FAIL on another copy's run/prebuild + 5-min load WARN; `day.sh` stops other copies' prebuilds, only WARNs on their runs (its own preflight runs with `HCTF_SHARED_HOST=1`); `fair_run.sh` refuses (exit 2); `prebuild.py` `_worker_pids` scoped to this copy, chain-shell match covers `bash -lc 'cd ROOT && …; python -m hctf.cli prebuild'` | `HCTF_SHARED_HOST` (0) | |
| 2 | no clock ⇒ pre-TT single speed gate only above 20 s; Mastery estimate gate off; untimed non-web pre-Mastery harden only when the TT-derived Mastery estimate exceeds 0.8 × the solver budget | `HCTF_NO_CLOCK_SPEED` (1), `HCTF_NO_CLOCK_SINGLE_SPEED` (20) | `_expect_untimed()` |
| 3 | `workers.no_clock_local`: untimed + slow VM + multi-set + unmeasured ⇒ local first attempt | `HCTF_NO_CLOCK_MULTISET_LOCAL` (1) | single-set TTs keep Homebase |
| 4 | `vm_budget_exhausted`: `solver_incomplete` with ≥90 % fields empty after ≥90 % of the untimed budget on the VM ⇒ local re-run | — | broadens `_slow_vm_no_clock` |
| 5 | web skill: submit first, the class becomes a plugin | — | replaces "verify before submit" |
| 6 | `single_method_text` → `_live_methods` at the single's CORRECT; proof-* shapes interchangeable on live lanes | — | |
| 7 | `class_known` (handler or earlier solver names a concept clue key); unknown ⇒ race capped; every target race logged to `.run/web_race.jsonl` (winner, elapsed, known, budget) | `HCTF_WEB_UNKNOWN_KEY_BUDGET` (12) | prior solvers now loaded once per process |
| 8 | `WebCodify` background worker at a web single's CORRECT → `lib/web/handlers/<dayNN>_<chal>.py` (KEY_MAP + HANDLERS), auto-loaded by `lib.web.handlers` (one file per challenge: no lost update between two web chains); prompt `hctf/prompts/codify.md` | `HCTF_WEB_CODIFY` (1), `HCTF_WEB_CODIFY_TIMEOUT` (300), `HCTF_WEB_CODIFY_HOLD` (0) | the TT is not held by default |
| 9 | web generalize + seed notes point at the same per-challenge plugin | — | "adopt a green bg-gen before Mastery" superseded: plugins need no adoption (web cases aren't replayable) |
| 10 | **real root cause found**: `lane_known_shapes` under the global `_SHAPE_LOCK`, built AT the drop — web's `mastery_delta` is the one that asks for it. Now memoized per (lane, day) and warmed before the release wait; the MASTERY COMPOUNDS log moved after the go text; prompt-build sub-marks | `HCTF_SHAPE_WARM` (1) | the planned "defer notes via inbox" was the wrong fix |
| 11 | reuse-race handoff: each carry-over shape checked on the newest earlier GM-verified case asking it (`carry_cases`), started in the background at the race snapshot; gaps ⇒ worker told + hold (as the new-id hold) | `HCTF_CARRY_CHECK` (1) | conclusive, unlike substituting the single's bytes |
| 12 | **measurement only**: `generalize prep Xs: case-check, baseline replay, evidence/prompt, snapshot` | — | overlap NOT shipped: the baseline must reflect the PRE-worker code (accept gate); a safe overlap needs the replay on the snapshot copy + watcher/duel/accept re-plumbing. #1/#2 removed the triggers seen on a rehearsal copy — decide from the next run's numbers |
| 13 | `hb_timed._prestarted_body`: a fresh, untimed, complete pre-start is used once instead of a second `start` | `HCTF_PRESTART_REUSE` (1), `HCTF_PRESTART_TRUST_S` (300) | |
| 14 | pre-start lines split `[start, download, MB, MB/s]`; reuse-race WON line `[rank, solver runs, submits, seed verify]` | — | attack after data |
| P3 | `hctf timeline --t0 HH:MM:SS` (default: the release line) + `->TT` / `->M` phase columns | — | |

Superseded: pole #2's blunt first-attempt budget cap (`HCTF_WEB_TIMED_LIVE_FIRST`) stays OFF — #7 caps only never-seen
classes and #8 makes the class dispatchable. Pre-existing red test found (not from this work): `tests/test_day14_s3.py`
§9 (lane seed staging vs `upgrade_solver_main`), already failing at f90a60b6.

### Replay measurement (10-23 09:24, alt, KPI row `D22 replay-pm23c`)
Setup: the branch harness; knowledge = main's lib as of 10-22 09:50 (`.run/replay-wb21b/kbackup`: D21 ratchet in,
nothing D22 taught — web handlers know only `session_fixation`) + this work's lib code (`.run/build_pin_d22.sh`,
directory pin); `HCTF_REROLL_CORRECT=1` so every TT/Mastery is a REAL fresh variant on the real GM (now forwarded to
Homebase too — the first two replays short-circuited as "already passed" and were discarded); standard lanes only (a D22
web replay can't work: a replayed single is a dead 410 target, a non-replayed one is already solved).

| chain | replay single / TT / M (->TT, ->M) | main live D22 (from the drop) |
|---|---|---|
| mobile | 11 / 29 / 45 (18, 16) | 22 / 43 / 53 (21, 10) |
| warmups | 24 / 38 / 50 (14, **12**) | 25 / 40 / 83 (15, **43**) |
| metadata | 18 / 46 / 67 (28, 21) | 43 / 60 / 95 (17, 35) |
| script | 21 / 44 / 77 (23, 33) | 47 / 63 / 105 (16, 42) |
| binary | 47 / 59 / 89 (**12**, 30) | 62 / 83 / 103 (21, 20) |

**Board 1:29 vs 1:45**, 10/10 timed first-try, 0 generalizes. Attributable: warmups Mastery 43 s → 12 s (#3: the
108-set attempt solved locally in 1.76 s vs 15.9 s + 11.8 s submit on the VM live; 63.9 s on the shared VM); binary TT 12 s
after a 9.8 s single solver that the old 2.5 s gate would have speed-generalized (#2 — alt live: 567 s); `[shapes]`
warmed in 0.7 s before the singles (#10). NOT attributable: single times (judged by the local replay GM, no drop load).
Not exercised: #6/#8 (no web), #12 (no generalize), #13 (the pre-start skips already-passed modes), #4/#11 (no VM
cut-off, no carry gap — and no false holds). Regression found and fixed: #3 on a small fan-out (mobile's 6-set Mastery
8.5 s locally vs 1.25 s on Homebase's warm daemon) → local only from 12 sets.

Next leads (from the #14 breakdowns): (1) the reuse race's `seed verify` re-runs the seed the plan already ran —
1-10 s, 10.0 s on binary, the last single; reuse the plan's output. (2) warmups' race: one submit took 17.7 s (live D22
too: WON at +17.6 s) — find out why. (3) Mastery `start` for big artifacts (script: 12.4 s incl. the re-roll) — the
pre-start hides it on a fresh day; confirm on D23.

### Main for Day 23
Run D23 from branch `d22-web-critical-path` (everything above is on it, behind flags). Warm-up: `bash bin/preflight.sh`
(new: the host-exclusivity section must be OK) then `bash bin/day.sh 23 --wait`. What to read in `.run/day23.log`:
`[shapes] … warmed` before the drop; web go-text `prompt-build` ≤ ~1 s; `web codify:` lines and a `lib/web/handlers/
day23_*.py` plugin; web Mastery first-try; `generalize prep` breakdowns; `pre-started … [start, download, MB/s]`; then
`hctf timeline --day 23 --t0 21:00:00`. Then validate on rehearsal D23 (fresh) with `bin/fair_run.sh` (main's prebuild stopped
— the guard enforces it). Edit `hctf/` only with main's prebuild stopped or in a worktree ([[prebuild-reverts-code-edits]]).
