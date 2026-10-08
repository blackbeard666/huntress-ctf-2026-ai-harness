# Speed: getting the daily sweep under 4 minutes

Target: solve all 5 lanes × 3 modes (15 solves) in < 4 min, matching the top team. Day 5 took ~8 min.

## Timed-submit latency — FIXED (the biggest per-attempt win)

Symptom: our timed submits took >2s while top teams submit in ~1s. Cause: timed attempts ran **local**
against the *public* GM (5–8s/call, highly variable) instead of on **Homebase** against the *inside* proxy.
On Day 5 they fell back to local because `_homebase_ready()` went through the browser-based `power()` check,
which on a cold ControlMaster reconnect timed out, hit the (WSL-dead) Windows browser, raised, and latched
`_hb["failed"]=True` for the whole run.

Fixes (2026-10-05):
- `workers._homebase_ready()`: readiness is now pure **SSH reachability** (no browser), tolerates a cold
  reconnect, and doesn't latch-fail on a provisioning hiccup.
- `remote.ssh()` / `_rsync()`: retry up to `HCTF_SSH_RETRIES=3` with backoff to ride through transient
  UDP-VPN drops; `run_hb_timed` returns `exec_error` (never raises) so a kickoff failure falls back to local.
- `remote.gm()`: the `ssh` transport falls back to the public GM (token) on any Homebase failure.
- VPN root cause (CORRECTED Day 6): the ~4-min `--ping-restart` cycle was NOT idling. The Windows OpenVPN GUI was
  connected with the SAME profile; CourseStack keeps one session per profile, so the two clients evicted each other
  every ~4 min (~60s dead each). Fix: no Windows client at all -- our VPN is command-line only (`hctf-vpn` systemd unit in WSL); the GUI
  was removed from Windows startup. `bin/preflight.sh` FAILs on any Windows openvpn.exe on our profile; `--fix` taskkills it. The unit's `--ping 10 --ping-restart 60` is still fine to keep. The local→Homebase link is ~230ms RTT; the in-window GM calls are HB→inside-proxy (off the VPN),
  so they stay fast and stable once an attempt is kicked off.

Measured on the Day 5 script-analysis Time Trial (7s window):

| phase | local (public GM) | Homebase (inside proxy) |
|---|---|---|
| submit | 2.76s | **0.55s** |
| download | 1.78s | 0.24s |
| in-window total | 4.98s | **1.4s** |
| total elapsed | 7.79s | 3.38s |

Timed attempts now auto-route to Homebase when it's reachable (prewarmed at run start; `bin/day.sh` warms the
control socket first). `HCTF_GM_TRANSPORT=ssh` forces *all* GM calls (incl. untimed single_solve) through the
inside proxy — a further win for the many submits on a big single_solve, but left opt-in for now since the
untimed artifact path (download-on-HB then rsync-back) is less battle-tested than local.

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

`hctf/workers.py`: `worker_effort(lane)` / `worker_model(lane)`, `LANE_EFFORT`. Default: `high` on EVERY lane
(owner's rule — warmups included). `bash bin/day.sh N --effort xhigh` raises all lanes (Day 6 experiment). Override per lane:

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

## Early handoff + one-request reuse (2026-10-06)

rehearsal copy Day 5 re-run (T+7:09 vs main's T+8:25): script-analysis had every answer CORRECT at **T+3:10**, but its
worker kept hardening the solver until T+6:25 before Time Trial could start. `orchestrate.Chain._speculate` now runs
ONE Time Trial -> Mastery pass from a verified snapshot as soon as the single is CORRECT (worker keeps going; a
pre-pass failure costs nothing and its variant is adopted as a regression case after the worker). Expected ~2-3 min
off the critical lane. The reuse path now submits all answers in one request (per-set, forced, only to localize).

## Day 6 fixes: expired timed attempts (2026-10-06)

Day 6 had 4 expired/failed timed attempts though every solver was correct. Causes and fixes:
- **Homebase latched off for the whole run.** The prewarm SSH landed in a VPN gap, `_homebase_ready()` set
  `failed=True`, and every timed attempt ran local (public GM start ~5s alone on a 7s window). Now a failure only
  cools down `HCTF_HB_RETRY_S` (20s) and is re-probed; recovery is logged.
- **Early handoff parked a clock expiry until the worker exited** (scripting TT idled ~6 min). `_speculate` now
  retries a clock expiry (solver answered everything) immediately, up to `HCTF_SPEC_TIMING_RETRIES` (2).
- **Drop-time launch re-ran pre-flight + a blocking 30s Homebase warm** (~75s lost at 21:00). `bin/day.sh N --wait`
  now does all prep up front, skips a pre-flight that passed within 6h, warms Homebase in the background, then polls
  every 3s and launches the instant the day is listed.
- **Orchestrator log went silent**: `contextlib.redirect_stdout` is process-global; overlapping calls from parallel
  chains stranded `sys.stdout` on a StringIO. Replaced with thread-local `cli.quiet()`.
- `last_timed.json` now keeps `detail` (exec_error cause) and `routed` is set on local attempts too.

## Day 6 adversarial review -> Day 7 changes (2026-10-06)

4 read-only review agents (scratch in `.run/review/`). Root cause of 12m13s vs the top team's 1m45s: 60% of worker
time came AFTER the first CORRECT (mandated hardening), reuse threw away prior solvers that already had the answers,
and the timed handoff serialized behind locks and waits. Changes:
- **Merged reuse** (`solvers.reuse_plan`, `Chain.try_existing_solvers`): every same-lane solver runs on the FULL
  contract in parallel; per-field merge (confident = the solver's own GM-verified cases contain that answer_id).
  Confident fields are submitted at once and bisected on a failure (probe-tagged submits, budget 20), with other
  solvers' alternate values tried for a judged-wrong field; speculative fields only when they would finish the
  challenge. The best solver seeds `solver/`; the worker gets ONLY the remaining answer_ids. Offline replay with only
  prior solvers: confident fields 813/814 right across Days 4-6; Day 6 mobile solved, script 357/399, binary 40/48.
- **Stop at CORRECT** (`Chain._watch_ready`, `workers.run_local(stop=)`): once the single is CORRECT and the solver
  (stable 2s, *.py only, 1s poll) reproduces every confirmed answer, the worker is ended, the verified snapshot is
  restored and the timed modes start. Prompts/skills now say: answers go INTO solve.py, `hctf submit <id>
  --from-solver`, stop; no solver-test/synthetic cases/hardening in the single.
- **Timed robustness:** `exec_error` -> `error:exec` = retry after waiting for Homebase health, never a generalize;
  clock-expiry retry sleep 8s -> 2s; prerequisite wait 20s -> 3s.
- **Homebase:** background health thread (`workers.start_homebase_health`, single 5s-connect probe every 5s);
  `_homebase_ready()` is a non-blocking read; provisioning (2s import check, full setup only if missing) runs in that
  thread, never under a lock; solver push is one round-trip without `cases/`; on a pass the evidence pull + regression
  capture run in the background. SSH keepalive 5s x 3.
- **Isolation:** workers run with `--strict-mcp-config` (23 claude.ai MCP servers were loading per worker) and
  auto-memory off; they never edit `lib/` mid-run -- `## Proposed lib additions` in solver/NOTES.md are merged by ONE
  post-run `ratchet` worker (`orchestrate.ratchet`, `HCTF_RATCHET=0` to skip).
- Effort: all lanes back to high (xhigh made each turn ~50% slower for no wall-clock gain).
- Fixed latent crash: duplicate `Chain._snapshot_solver` (any generalize would raise TypeError); guard test.
Not done yet: one Homebase process chaining TT -> Mastery, pre-launching workers before the drop.

## Replay-driven fixes (2026-10-06/07, from-scratch Day 6 replays on a rehearsal copy)

`hctf/replay_gm.py` + alt `.run/replay_full.sh` re-run a solved day from scratch (local single judge, real GM timed).
Fixes from runs 1-3 + a read-only analysis of their logs:
- Timed failures are diagnosed on THE FAILED VARIANT (its pulled bytes; kept in `<mode>/attempts/<id>/`), never on a
  fresh probe attempt: two "environment" verdicts were real solver gaps (bash comma keys; lib PE_MACHINE lacked 0x8664).
  A probe attempt that itself passes the mode now ends the stage; label resolution skips fields the solver left empty.
- hb_timed reports a solver timeout as JSON (attempt_id, solver_too_slow) so the variant is pulled; no local fallback
  for a too-slow solver; the speed generalize works on that variant.
- Generalize: one 8s parallel baseline (was a 120s/case run + a second baseline: 141s before the worker); a
  stop-when-green watcher ends the worker once the failing cases pass with no regressions.
- Solver skeleton (`hctf/templates/solve_skeleton.py`) seeded when reuse finds nothing: per-set loop + sha256-paired
  `artifact_bytes()` incl. Mastery's `delivery N: x.apk`. `hctf submit --from-solver` runs a Mastery dry run on the
  Mastery contract's artifact names and warns if a set comes back empty.
- Parallel artifact downloads (8); background evidence pulls on their own SSH connection; skip the per-mode GM status
  call when single() just saw the mode start_required; sandbox re-binds project symlink targets (alt .venv/tools).

## Lane solvers: deterministic first (2026-10-07)

Analysis of the full from-scratch replay (warmups 28/33/116, mobile 55/60/66, script 408/510/738 vs the top team's
1-7s / 2-6s / 87-94s): the time was all LLM work on lanes whose fields are 100% mechanical. `lib/lanes/<lane>/solve.py`
are day-independent, stdlib(+pyzipper) solvers run FIRST by merged reuse (`solvers.reuse_plan`), confident when every
field is answered in its answer_format; a winning lane solver is seeded as a thin `solver/solve.py` wrapper so TT/Mastery
run the same code. Validated offline on every saved case of days 1-6:
- warmups (`lib/lanes/warmups`): 49/49 cases, 184/184 fields (layered/radix/cipher search guided by the answer regex +
  the fixed warmup sentence, numbered mixed-encoding chunks); <= 0.16 s for a 28-set Mastery.
- mobile-android (`lib/lanes/mobile`): 27/27 cases (huntress_puzzle.json, every codec tried, Mastery `delivery N:`).
- script-analysis (`lib/lanes/script`): 12218/12218 fields on main's 80 cases (19134/19134 incl. alt), 0 wrong; one codec
  engine (carriers x transforms x key forms incl. comma keys) + name-convention extraction (`Material_`/`Codec_`) + one
  plan parser; with a language disabled it still answers ~90% of that language (new-language fallback).
Through reuse_plan with ONLY the lane solvers: warmups/mobile days 2-6 and script days 2-6 all fields confident + right,
~0.2-0.35 s. After reuse, enum fields still open are probed with the options their question names (role of a new graph).
Note: a Day-6 replay can no longer measure these fairly (they were validated on Day 6); Day 7 is the real test.

## Analysis -> action latency (2026-10-07, 46 worker transcripts, `.run/review4/`)

Verdict: neither over- nor under-analysis. The answer is visible early (median 2 s metadata, ~7 s warmups/binary,
27 s mobile); all 6 wrong submits in 34 singles were GM label SPELLINGS, never wrong decodes; rework <= 2%. 79-97% of
wall-clock is model generation between tool calls (~4-6 s per turn) -> fewer turns is the lever. Fixes:
- triage.md: `## STATUS` (answers already accepted by reuse + the exact REMAINING ids) and `## Extracted` (every
  archive, incl. password-protected and nested, pre-unpacked into work/extracted/ in ~0.05 s).
- single.md: no up-front skill loading, batch independent reads, subagents only for >1 new family (max 2, one message,
  one blocking wait), "a decoded value matching answer_format IS the answer -- don't reproduce the backend".
- `hctf labels`: the solver's own value is tried FIRST unless already rejected (cold binary submitted `jar_jvm` first).
- gm.py: GET 15 s timeout + one retry, POST 30 s (a hung call stalled a worker 65.7 s).
- preflight: worker-sandbox check (venv + solver deps importable inside bwrap).
- binary-reverse-engineering (`lib/lanes/binary`, 2026-10-07): 2494/2494 GM-confirmed values on every saved case of
  days 1-6, 0 wrong, <= 0.27 s; per-container analyzers (pyelftools/pefile/capstone, pure-Python JAR constant pool) +
  a CRC-validated HCFG hunter across raw/zip/gzip/base64/hex/UTF-16/constant-pool. New-day test: Day 6 with JAR code off
  544/550 (all real GM cases correct), Day 5 without Rust/Go 160/160; arbitrary labels (Day 3 `pe_cli`) stay residual.
- metadata-forensics (`lib/lanes/metadata`, 2026-10-07): 58/58 (26 cases), 0 wrong, ~0.1 s; registry of confirmed
  families + a GENERIC tier (pure-Python parsers for ~20 formats, confirmed formatting rules, impostor -> none). With
  each day's registry entry disabled the generic tier still answers all 58; fuzzed future families 49/50 emitted correct,
  0 wrong (unconfirmed spellings are held back, not guessed).
All five lanes now have lane solvers; through reuse_plan alone every lane's single of days 1-6 is fully confident + right.

## REVERSED 2026-10-07: no hand-built lane solvers, no deterministic-solver-first
The owner's direction: don't reinvent the wheel and don't bet on yesterday's shapes -- each day's challenges are
unknown. The `lib/lanes/*` solvers (hand-written ELF/JAR/PE/metadata parsers etc.) and the lane-first reuse step were
REMOVED; enum pre-probing is off by default (HCTF_ENUM_PROBE_BUDGET=0). The goal is an LLM that identifies the
goal/target fast and solves it with the standard tools (readelf/rizin/Ghidra headless, jadx/apktool, exiftool, 7z,
box-js...), loaded via its lane skill on the first call. Kept: harness latency work (triage STATUS + pre-extracted
archives, skeleton, submit --from-solver, stop-at-correct, Homebase/window/sandbox fixes). The lane-solver numbers
above are historical.
- Earlier days = LEARNING NOTES (owner, 2026-10-07): merged reuse of old solvers is OFF (`HCTF_REUSE_OLD_SOLVERS=0`).
  `reference/techniques/<lane>.md` (patterns, recognition cues -> first tool, day-by-day techniques, GM conventions,
  pitfalls) is referenced in the worker prompt; the post-run ratchet updates it after every day from that day's notes,
  transcripts and confirmed answers. Accumulated GM-confirmed knowledge (lib/knowledge.py, vocab.json, playbook) stays.

## Day 7 (2026-10-07): real run T+6:16 -> replays T+2:07, and single-worker trims
Real Day 7: 15/15 by T+6:16. Critical path = script TT, two generalize cycles (4:10): new Node/bash codec names
(TT #1) and a GM 429 body saved as evidence.zip (TT #2). Also: bundle-zip `find_artifact` bug (warmups Mastery set1),
clock-expiry retry bug (blocked after 1 expiry), 116 s of `javap` over a fat Kotlin jar's stdlib in binary triage.
Fixes (61e8ea3, 8abd11f, fe99c70, 252951e, fa62eac, 51eff69, b7611bb):
- timed: GM 429/error body never becomes evidence (exec_error + backoff, no generalize); Homebase for EVERY timed
  window when healthy (`HCTF_TIGHT_WINDOW` default inf); harvest yields to other chains' live clocks; `start` on a
  passed mode re-rolls a fresh clock (op retry); `no_answer_ids` -> retry; `rotation_exhausted` -> terminal.
- lib.codec name-agnostic fallback (336/336 real D7 codecs with renamed reps vs 203 names-only).
- startup: no gm_solved status call on a fresh mode, timed contracts prefetched beside start/triage, recon in a
  thread pool, JVM stdlib classes skipped in binary recon.
- single workers: lane skill + triage + generated lane-helper index inlined in the prompt; import helpers, write +
  `submit --from-solver` in one Bash call; binary/script told to copy the latest same-lane solver (cumulative
  contracts; harness reuse stays OFF); submits via the Homebase inside proxy when the ControlMaster is up (0.98 s vs
  1.72 s median warm; single-shot ssh with an exec marker -> never a double POST); gm.py logs 429 retries per call.

Replays (main account, singles judged locally, lib already holds Day 7 knowledge -> optimistic for singles):
| replay | metadata | mobile | warmups | binary | script | notes |
|---|---|---|---|---|---|---|
| d7fix1 (after timed fixes) | 0:35 | 0:40 | 0:58 | 1:01 | 2:07 | 15/15, all TT/Mastery first try on Homebase |
| d7fix3 (after single-worker trims) | single 21 s (TT: GM rotation_exhausted) | 0:44 | **0:35** | 1:42 | 3:01 | warmups single 18 s; script 1 generalize |
Single-worker turns (launch -> CORRECT) d7fix1 -> d7fix2: metadata 7 -> 4, mobile 6 -> 4, warmups 11 -> 4, script
29 -> 18, no Skill calls. Wall time per clean lane barely moved in replays (they already skip the public-GM submit);
the real-drop gain is the submit path + fewer turns. Measure at Day 8 via log.jsonl `elapsed`/`retries`.
GOTCHA: each main-account replay burns real TT/Mastery variants; after the real run + 3 replays the GM answered
`rotation_exhausted` for metadata TT. Max ~2 replays of a day on main; use alt for more.

## Rehearsal Day 7 fair run (2026-10-07 22:39) -> fixes -> script-lane replay
Fair run = the rehearsal copy's FIRST Day 7 solve with main's harness at 0cd4aa6 but knowledge pinned to 97b3694 (pre-Day-7 lib,
technique logs, skills, codec tests; Day 7 solvers/transcripts masked). 15/15 GM-verified by **T+5:01** (main real:
6:16). `hctf timeline --log ~/huntress-2026-rehearsal/.run/day07.log`:
| chain | single | TT | Mastery | generalizes | notes |
|---|---|---|---|---|---|
| metadata / mobile / warmups | 25 / 26 / 34 | 32 / 33 / 39 | 35 / 35 / 43 | 0 | 2-3 tool calls each; caesar + %XX written by the workers |
| binary | 69 | 78 | 84 | 0 | copied the D6 solver (sanctioned) |
| script | 87 | 197 | 301 | 2 (77 s + 68 s) | TT `xor_hex|cd`, Mastery `reversed_base64|`: one codec family, two cycles |
Script critical path: LLM 224 s, harness 69 s (13+6+14+9+7+20 between steps). Found:
- harvest never ran: `start` after the failed attempt's deadline resumes it (`{"result": "expired"}`) -> "start
  refused" -> 0 variants (fixed 1b0024f: re-roll with op retry). GM guidance: only `retry` spends one of
  `unique_attempts_remaining` (~32 per timed mode per day).
- the harvest note was appended to gm_wrong AFTER render (never reached a worker); the generalize prompt now inlines
  the failing bytes + a passing counterpart and always says "fix the construct family" (e9fe849).
- accept re-ran the 36-case suite the watcher had just verified; suite parallel 4 -> min(8, nproc) (7236296).
- re-attempts go straight to op retry (bce45a8); `hctf timeline` (7537579); `bin/fair_run.sh` (a33d45e).
Replay fix1 (alt, script lane only, same fair pin, KEEP_PRIOR=1, Homebase): single 76, TT 252, **Mastery 258 first
try** (2 TT generalizes 64 s + 68 s, harvest 3 + 2 variants, 1 green->accept in 1 s, blocked->worker 2-3 s vs 6-7 s).
The second TT cycle was a codec the 4 first-cycle variants never drew (`xor_hex|e8`; harvest drew reversed_base64 x3):
sampling can't cover a ~10-member family. Main is covered regardless: main's lib.codec name-agnostic fallback (8abd11f,
excluded from the fair pin) decodes all 128 codec declarations of these variants with Day<=6 names only, and main's
Day 7 solver answers all 11 replay variants/auto cases with 0 empty / 0 wrong (0.4-0.8 s each).

### Follow-up: why the replay still needed 2 TT generalizes, and what changed (2026-10-08)
Root cause: the worker fixed exactly the codecs its cases showed (green only checks those) and stopped; the next
variant drew another member of the same ~10-member codec family. Changes:
- Name-agnostic decoders everywhere a name table used to fail silently (97cece0): lib.android.decode_payload ->
  decode_any() BFS over the primitives with the ANS shape as oracle; lib.decode.decode_chunk -> reversed/escaped/HTML/
  Morse/base58/QP/b85 line encodings; rot-N scoring by English bigrams (old unigram scorer picked the wrong shift on
  ~27% of GM warmups answers; now 98%). 21/21 mobile + 45/45 warmups regression cases unchanged.
- GM fact (alt test): retry/start on a LIVE attempt resume it (same id, no attempt spent) -> no parallel harvest;
  harvest now retries 0.5 s after the deadline and polls on "same id" (f06fa2e, ~4 s per variant).
- Generalize evidence (41bd075): codec census over the newest 24 cases (shapes the failing file used across them) +
  handler pointer (densest solver function for the construct; bashplan.codec_decode first on the replay).
- Codec-family probe (5ed8487): lib.codec.encode() + hctf/family.py re-encode the failing language's fixtures under
  other known rep x transform (format copied from real materials, round-trip verified), run the solver, report misses
  in the evidence. NOT a green gate: emulating solvers (vbsplan) legitimately disagree with recoded materials. Main D7
  solver: bash 16/16, Node 16/16; the rehearsal copy's table-based D7 solver: bash 14/16 (2 real gaps). Starts beside the baseline
  replay (off the critical path). `HCTF_FAMILY_PROBE=0` disables.
A fair Day-7 replay can't measure the probe (pre-7 lib.codec lacks xor_hex and the fallback); Day 8 is the test --
check `hctf timeline` for TT generalize count and the probe line in any generalize worker's prompt.

### Blind Day 7 replay `blind1` (alt, 2026-10-08 00:38, all 5 lanes, workflow 5e72c22, Day-7 vocabulary stripped)
Setup: `bin/fair_run.sh 7 97b3694 lib/common.py lib/android.py lib/decode.py lib/codec.py` + alt `.run/sanitize_d7.py`
(caesar/percent branches, D7 REPS and D7 comments removed; generic fallbacks kept) + alt `.run/blind_d7.sh start|stop`
(masks every .run entry except tmp/locks/known_hosts/ssh socket; stashes old worker scratch). 56 tool calls, 0 flagged.
`hctf timeline`: metadata 23/45/48, warmups 34/46/49, mobile 32/47/51, **script 86/169/174 (1 generalize 53 s, Mastery
first try; fair run 301, fix1 258)**, binary 61/389/394 -> 15/15 by T+394, binary the new critical path:
- single solver 5.9 s on its own case (jar_hcfg over all ~18.7k classes of the Kotlin fat jars) -> TT exec_error
  "too slow" (attempt + ~30 s); speed generalize fixed it to 0.3 s by call 7 (~60 s) but ran 284 s: no early stop for a
  speed-only generalize (all cases passed slowly -> watcher never started), plus a `7z x` hung 120 s on stdin.
Fixes: 6c9ba41 (speed_watch_sets early stop + single-time speed gate HCTF_SINGLE_SPEED_BUDGET=2.5 s -> one speed
generalize before the first timed attempt), c500c83 (bin/7z: -y, default -pinfected, stdin closed), c8a9748
(lib.binary.jar_app_classes / class_utf8: 3121 -> 5 classes in 12 ms; binary skill + helper index).
Expected with these: binary ~T+100, day bound by script (~T+175).

### Blind Day 7 replay `blind2` (alt, 2026-10-08 07:59, workflow 0b7ac72 + the Homebase with static 7-Zip)
`hctf timeline`: mobile 30/37/42, warmups 41/47/51, metadata 31/117/169 (2 generalizes: ESCALATED variants -- TT 11
fields / Mastery 22 with d04-d06 carry-overs + an evidence-note file, vs 1/2 fields in every earlier run: the GM rotates
later attempts into harder variants), script 106/**116 (TT first try -- first time ever)**/252 (1 Mastery generalize
50 s, then 68 s to the retry), binary 67/**170**/- (Mastery `rotation_exhausted`: the rehearsal copy's binary Mastery pool for Day 7
is used up). 75 calls, 0 worker flags (ratchet tried masked test_day7_fixes.py after the run).
Verified live: speed gate (binary single solver 12.7 s -> speed generalize BEFORE any attempt), speed early stop (green
in 85 s vs 284 s), TT passed first try after it. The slow solver was the copied Day-6 base (fair pin); main's Day-7
binary solver already skips kotlin/ (1.8 s single, 3.2 s Mastery), which is what Day 8 copies.
Found: (1) a non-pass result with no new variant (rotation_exhausted) still did the synchronous Homebase pull of the
mode's tmp-timed dir -- 13 MB of stale Mastery evidence at ~130 KB/s over the VPN, ~100 s; (2) background capture pulls
(6.6 MB binary TT pass) share that link with the next attempt's solver push (script Mastery: 68 s green -> result).
Homebase tools: the VM now has 7z (static 7-Zip in ~/.local/bin via `hctf hb setup`); still absent by design: java/jadx/
apktool/exiftool/binwalk/upx/rizin/zip (in-window solvers are pure Python; analysis runs locally).

### Blind Day 7 replay `blind3` (alt, 2026-10-08 08:09, workflow f9dc82e)
`hctf timeline`: mobile 23/29/33, warmups 36/41/44, metadata 47/127/133 (1 generalize, escalated 11-field TT),
binary 111/133/- (no speed gate needed; Mastery pool exhausted -> rotation_exhausted 2 s after the TT pass, no pull --
was ~100 s), script 81/141/224 (TT: first attempt answered everything in 0.9 s but the GM took 40.7 s to answer the
submit -> clock expiry -> retried, passed, no generalize; Mastery: 1 generalize 49 s, green -> result 11 s, was 68 s).
14/15 by T+224 (binary Mastery unavailable). 56 calls, 0 flags. Background captures all landed after the attempts.
Remaining: (1) hb_timed waits on a hung GM submit long after the window closed (40 s); (2) the codec-family probe only
runs inside a generalize -- when the TT passes clean, Mastery still meets the next codec (bash-advanced-tokens, every
run); (3) a harvest GM call that hangs holds the generalize's accept ~15 s after the worker exits.

### Blind Day 7 replay on MAIN `mainblind1` (2026-10-08 08:31, workflow 52b6016; alt had no Homebase credits)
`.run/blind_main.sh start|stop` (main-side twin of the rehearsal copy tooling: lanes aside, lib/skills/techniques pinned to 97b3694
+ scrubbed generic overlays, worker scratch stashed, 195 paths masked; restore = git + stash, main left git-clean).
`hctf timeline`: mobile 24/30/33, warmups 35/40/43, metadata 17/151/153 (escalated 11-field TT, 1 generalize 121 s,
Mastery first try), binary 66/153/- (speed gate 12.7 s -> pre-attempt speed generalize 69 s, TT first try; Mastery pool
exhausted on main too), **script 91/163/168: pre-attempt codec-family probe (calibration: vbs = noise) found 2 bash misses
9 s after the single -> family-* adopted, one 51 s generalize -> Time Trial AND Mastery first try** (no failed attempt,
no escalated variant). 14/15 by T+168 (fair rehearsal run 301, blind1 394, blind2 252, blind3 224). 63 calls, 0 flagged.
Main Homebase now has static 7-Zip too (`hctf hb setup`; main VM has no passwordless sudo either).
Next bottleneck: metadata on escalated variants (TT generalize 121 s); the hung-harvest-call fix is still open.

### Blind Day 7 replay on MAIN `mainblind2` (2026-10-08 08:41, workflow 81f61b7)
`hctf timeline`: mobile 27/32/35, warmups 41/45/48, metadata 42/47/50 (escalated 11/22-field variants, first try -- the
single worker happened to write a generic solver; the new metadata skill guidance was pinned out of this run), binary
83/91/- (fast solver, no speed gate; Mastery exhausted), **script 76/134/139 (pre-attempt family probe: 2 bash misses,
38 s generalize, TT + Mastery first try)**. All 9 timed modes that could run passed FIRST TRY. 38 calls, 0 flagged.
INCOMPLETE: 14/15 -- binary Mastery never ran (pool exhausted on both copies), so T+139 is NOT comparable with the
15/15 runs (fair rehearsal run T+301, blind1 T+394); blind2/blind3/mainblind1/mainblind2 are all 14/15 for the same reason.
Compare per mode instead. Offline only (not GM-judged): this run's binary solver, with the run's own pre-Day-7 lib,
reproduces 112/112 and 96/96 GM-verified answers of the two saved Day 7 binary Mastery variants (1.5 s / 0.5 s).
The harvest re-roll fix (81f61b7) wasn't exercised: no timed attempt failed.

## Day 8 (2026-10-08): real run 15/15 at T+20:22 -- three timed-path failures, one triage regression
Per lane T+ single / TT / Mastery (s): warmups 69/76/79, metadata 65/297/303, mobile 60/343/348, script 123/289/493,
binary 518/534/1222. Without the incidents the run was ~T+9 (binary single T+8:38 was the next bottleneck).
- **Binary Mastery (~650 s, the critical path):** submit reused a keep-alive socket the GM proxy closed during the 8 s
  solve -> `RemoteDisconnected` (no verdict) twice; each failure then pulled 5 x 31 MB of evidence over the ~140 KB/s VPN
  *synchronously* before the retry (442 s + 186 s). Fix: fresh socket for no-resend calls + idle > 3 s never reused;
  transport drop with clock left -> one resend; failed-attempt pull only when the next step needs the bytes
  (`workers.needs_bytes`).
- **Script Mastery (~176 s):** same socket bug, then `start` resumed the dying attempt (4 s left) -> 2 s solver budget
  -> misread as "solver too slow" -> 143 s generalize. Fix: wait a nearly-spent attempt out and `retry`
  (`orchestrate._resume_need`, hb_timed `--min-left` backstop); a starved solve is `expired`/`clock_short`.
- **GM dual-pool change (~640 s lane time, 6 useless generalize workers):** regular pool refused TT starts
  (`training_rotation_invalid`). Fix: always request the Hall of Fame pool (`run_for_time`), start refusals ->
  `error:start` (back off, never generalize), no 503 backoff on deterministic refusals.
- **bin/7z regression (c500c83):** wrapper appended a second `-y` -> every triage pre-extraction failed (script decoded
  payloads 0/0, no binary recon). Fixed.
- **Binary single 510 s:** 120 s Bash hang (D7 solver brute force on a 67 MB Swift ELF), 66 s profile, bisect killed by
  one hung GM POST, `hb ensure` crash in the sandbox, elf_class `kind: integer` = `64`. Fixes: 60 s default Bash cap
  for workers, robust bisect (retry a hung probe, infer the clean-sibling half / last family), kind-aware label law.
- **Single submits never went via Homebase** (ssh refused ssh_config inside bwrap): warmups waited 30 s of 429 backoff.
  Fix: `SSH_OPTS` starts with `-F /dev/null`.

### Day 9 prep (2026-10-08 22:3x): failed-variant pull, warm workers, probe overlap, compounding probe
- **Failed-variant pull, scoped:** only the deliveries covering the failing field families (`workers.deliveries_for`),
  fetched as 10 parallel byte ranges over separate SSH connections (`remote.fetch_file`; the VPN caps each TCP flow),
  sha256-checked. Binary D8 Mastery d7c5e016: 157 MB full pull 10-20 min -> delivery 1 only, **37.9 s** (6 streams
  61 s, 12 streams 42 s, 16 streams trip sshd MaxStartups). Subset cases get a trimmed contract
  (`timed.trim_to_present`); a localized `incorrect` now also builds the `variant-*` case (green watcher target).
- **Warm Single workers:** launched at chain start on stream-json input (`workers.WarmWorker`): static prompt +
  "reply READY", triage + go on handoff; stop gate allows the warm-up turn (flag file). Live: READY in 3.0 s, no tools.
  Expected ~5 s/lane off the first tool call (D8: T+13-16 s). `HCTF_WARM_WORKERS=0` = cold.
- **Probe overlap:** mutation + compounding probes run beside the first TT and are awaited before Mastery (or merged
  into a TT-failure generalize); the codec-family probe stays blocking (script).
- **Worker tools:** `--tools Bash,Read,Write,Edit,Skill,Task` (26 at init before). **GM backoff:** 2,4,4,... s cap,
  8 retries (~30 s). **Mastery speed gate:** mutation probe's 2-set run -> estimate vs 2x the TT window.
- **Pass captures** wait `HCTF_CAPTURE_GRACE` (6 s) so the next mode's kickoff starts first, then `wait_idle()`.

### Blind Day 8 replay on MAIN `d8warm1` (2026-10-08 22:40, workflow 6b29f3b + estimate fix, knowledge pinned 672753b)
**15/15 at T+631 s** (real Day 8: T+1222). Per lane single/TT/Mastery: mobile 32/37/41, metadata 36/41/44,
warmups 38/43/45, script 117/132/145 (TT+Mastery first try), binary 368/468/631 (TT: 2 empty `d02_*_has_cpp_*` fields
on a mutated Day 2 binary -> generalize green in 41 s; Mastery: the stripped-d01 trap again -- the pre-Day-8 Day 7
solver still guesses -- -> generalize green in 60 s).
- Scoped failed-variant pulls live: TT 31 MB in 31.2 s, Mastery delivery 1 in 38.2 s (Day 8: 442 + 186 s blocking).
  The localized-incorrect path built `variant-mastery-9c4e39de` (trimmed to set 1), the green watcher ended the worker.
- Warm workers: all 5 READY with no tools, handoff T+7-8 s, first tool done T+13.1-17.0 s -- **no gain vs Day 8**
  (T+13-16): the warm-up finishes about when triage does, and the ~5 s after handoff is the model reading the triage
  (first Bash has no cold-start: measured 1.1 s with or without a Bash pre-warm). Only a pre-drop launch could help.
- Caveat: replay Singles are judged by the local replay GM (no public-GM 429s), so the faster singles (32-38 s vs
  60-65 s) are NOT evidence for the submit-via-Homebase fix.
- Speed-gate estimate double-counted python startup per set (warmups 5.7 s for a ~0.2 s solve) -> now marginal
  per-set cost (2-set run - base run) + one startup.
- Main's real Day 8 binary solver (e6f556c) passes every new replay variant (TT d02 cpp, stripped-d01 Mastery);
  13 new GM-verified replay cases adopted into the Day 8 solvers.

### Blind Day 8 replay on MAIN `d8tc1` (2026-10-08 23:11, workflow 3bf828b, knowledge pinned 672753b)
**15/15 at T+256 s, every timed mode first try** (d8warm1 T+631, real Day 8 T+1222). Single/TT/Mastery: warmups
33/39/41, metadata 35/40/43, mobile 38/43/47, script 104/117/133, binary 210/225/256 (single 368 -> 210: triage now
extracts -- the 7z fix -- so the worker had readelf/Go/Rust/.NET/JVM recon from the start).
- **Toolchain check missed Swift:** the scan took the first 400 extracted paths and the Day 7 Kotlin jar's 3k+ .class
  files sorted ahead of `d08--variant-000.elf` (#3146). Fixed (`toolchain.scan_order`: shallow first, classes last;
  regression test). swift-demangle had been removed for the test; installed by hand mid-run (26 s).
- **Near-miss:** binary Mastery in-window 25.87 s of 27 (download 10.1 + solve 15.1; this replay's solver came from the
  Day 7 base -- the real D8 solver solves in ~8 s). Speed gate estimate was accurate (13.96 s) but compares solve only
  with 2x the TT window (20 s); it ignores download. Not changed: counting download would have flagged a pass.
- 8 new GM-verified cases adopted (binary pass captures were still copying when the run exited).
