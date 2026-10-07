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
