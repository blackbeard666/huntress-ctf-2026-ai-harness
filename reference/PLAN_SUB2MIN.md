# Plan: consistent sub-2-minute (then sub-1-minute) days, with a loop that still improves

Written 2026-10-17 (before Day 17) from `.run/day09..16.log`, `hctf timeline`, `hctf cost`, SPEED.md and the memory log.

## 1. Premise, restated

The organizers' framing: a deterministic, general-purpose solver on autopilot for a month, moving at machine speed and
coping with unseen variation. Our standing goals (north-star list): autonomy, robustness, speed, transfer,
determinism ratchet, knowing the breaking point. The user's rules that bound the design: LLM-first with standard
tools (no hand-built parsers ahead of the model), worker effort high on every lane (duels medium), HoF is not a
goal, incomplete runs are never "best", report N/15 first.

Since Day 15 every TT/Mastery attempt comes from the GM's UNTIMED regular pool. There is no in-window clock on our
critical path any more: the day's T+ is purely our own wall time, and a failed attempt can be completed in-attempt
(the GM accepts partial submits and pins each confirmed id). This changes what "speed" means: the clock we fight is
LLM turns + GM round trips + our own harness, not a 6 s window.

## 2. Where the time went (Days 9-16, main real runs)

| Day | 15/15 at | 14/15 at | Tail (what alone set the day's T+) | Best fair/blind replay |
|---|---|---|---|---|
| 9  | 1:59 | ~1:00 | binary single LLM 91 s (new field) | r9b 1:00 |
| 10 | 1:37 | ~0:55 | metadata single LLM 86 s | alt 1:24 |
| 11 | 1:09 | ~0:52 | script single LLM 58 s | alt 1:03 |
| 12 | 7:12 | 1:16 | warmups Mastery: solver fallback with no deadline + harness bundle bug (2 generalizes) | alt 1:06 |
| 13 | 3:38 | ~1:30 | warmups Mastery 4 attempts + generalize 107 s; binary generalize 104 s | alt 1:31 |
| 14 | 2:20 | 0:49 | warmups Mastery compounding: 2 generalizes 104 s + untimed fallback | alt 5:34 (its own tail) |
| 15 | 6:43 | 2:26 | script Mastery: one GM reply cut off killed in-attempt localize -> 181 s generalize + duel | - |
| 16 | ~15:44 (manual) | 4:52 | script single: 55 sequential GM probes = 4 min of a 66 s model solve; script Mastery: fixed 120 s runner cap vs 5475 ids; WSL OOM | alt 7:02 |

Three facts fall out of this table.

1. **The fast path already exists and is ~50-70 s.** On D9-D11 and on every rehearsal fair run, four lanes finish their
   whole chain by T+40-70. The floor is the slowest LLM single_solve: 4-8 turns at ~10 s/turn = 40-90 s, plus
   drop->GM start 3-5 s, download+triage 8-15 s, handoffs 1-5 s per mode, TT+Mastery solve+GM ~6-12 s.
2. **Every day over 2 minutes was ONE lane with a generalize on the critical path or a harness bug new to that
   day** (never both the LLM being slow and the answer being hard). A generalize costs 41-182 s (7-31 turns) and
   each day has had 1-2 of them. The harness bugs were each different: no solve deadline in a fallback (D12),
   bundle-case trimming (D12), single-attempt pool (D14), IncompleteRead escaping `_post` (D15), fixed untimed
   budget + sequential bisect + process fan-out OOM (D16).
3. **The improvement loop works but lags by one day.** The rehearsal fair run after each day's fixes is 2-6x faster than
   the real run (D12 66 s vs 432 s, D13 91 vs 218, D16 422 vs 944). Fixes land; they just land after the day
   that needed them. The next day then finds a new class.

Reuse-race (no-LLM single) hit rate D12-D16, the determinism we actually have per lane:

| lane | race won | typical LLM single when lost |
|---|---|---|
| mobile | 5/5 (+2.6..+5.7 s) | - |
| script | 3/5 (+7.8..+24.7 s) | 13-19 s (D13-15), 271 s (D16, bisect) |
| binary | 2/5 (+8.3..+10.5 s) | 18-93 s |
| warmups | 2/5 (+3.9..+4.6 s) | 34-75 s |
| metadata | 0/5 | 42-86 s + duel |

Metadata is a new container format every day, so text-matched reuse never fires; it is the lane whose single is
always LLM-bound, and the one whose single most often sets the 14/15 time.

Cost of the loop today: ratchet 5-23 min / $2-8 per day, ratchet_log workers up to 23 min / $7.7 (D16), speed-harden
~4 min, train ~1 min, prebuild hours (off-peak), total $8-15 per day on top of $2-6 of live workers.

## 3. Target

- **SLO-A: 15/15 by T+2:00 on at least 4 of 5 days. SLO-B: 14/15 by T+1:00 median.** Then push SLO-A to 1:00.
- **SLO (from D25, supersedes SLO-A as the headline): board N/N incl. web by T+2:00 from the drop** -- every mode of
  every lane, the web chains included (user 10-21: the whole board is the target, web is a regular lane), T0 = 21:00
  (the launch only when the run was not armed before the drop). Scored by `hctf kpi --day N --record` -> the "Board v2" /
  "Lanes v2" tables in reference/KPI.md (D20-D24 backfilled: 15:01, 17:38, 8:00, 29:08, 3:35 -- web set the board
  on four of five days).
- Zero manual interventions (D16 needed one).
- Determinism ratio (answer ids confirmed without an LLM turn / total ids) reported per day; today roughly
  mobile 100%, script ~94%, binary ~94%, warmups ~90%, metadata 0%.

## 4. The plan, in priority order

Each item names the mechanism, the measured gain it targets, and the gate that proves it.

### P0. Never generalize on the critical path (the 2-7 min item)

The pool is untimed, so an attempt that is 95% right can always be finished IN the attempt. Make that the only
path during the run; generalize is a background activity whose output is adopted if it arrives in time.

- **Fix-in-attempt first, always.** On any `incorrect`/`accepted`, the runner localizes with the parallel group
  bisect (grouptest, 12 in flight, already shipped D16) and resubmits; the orchestrator calls generalize only when
  localize reports it cannot resolve a field (empty ids with no candidate). D15's 181 s and D16's 12 min would have
  been ~1 min each. Gate: a replay of D15 and D16 with the real GM verdicts ends both Masteries without a generalize.
- **Candidate ranking before the model.** For a wrong closed-vocab field, try `label_hints.json` + `lib/vocab.json`
  + the lane's playbook grammar as the probe candidate list (deterministic, ~5 s on Homebase), then the model.
  D15's `delayed -> percent` was a 28-turn duel for one spelling. Gate: `hctf labels` resolves every D9-D16 wrong
  field from hints alone in the replay.
- **Carry TT verdicts into Mastery deterministically.** The TT's in-window fixed map (field -> accepted value) is
  overlaid per field, not per value (D15 showed a value remap can be wrong). Already partly there (bank overlay,
  label_hints); make it the default and test it.
- **Generalize budget.** When a generalize is unavoidable: duel at medium (shipped), max 20 turns, 90 s wall, and
  it never blocks the next mode on an untimed pool (background generalize exists since bfd2dcd; make the
  foreground wait path unreachable when `_expect_untimed()`).

### P1. Make the harness bug of the day a replay failure the night before (the robustness item)

Four of the last five tails were harness faults, each one new. Build a **fault-injection replay** on top of
`hctf/replay_gm.py` and run it in the post-run gate every night:

- Faults: IncompleteRead / short body mid-submit, 429 bursts, 5 s GM latency, the 500-answer submit cap, a 5475-id
  contract, a 1-attempt pool, `prerequisite_required` 409, a finished-CORRECT body on start, a slow VM, a download
  stall, a solver that never prints (deadline), a worker that dies on auth.
- Invariants asserted: every mode ends CORRECT per GM truth with no manual step; no runner killed before its
  scaled budget; no re-roll of a CORRECT attempt; every subprocess group reaped; peak RSS under the unit's
  MemoryHigh.
- Budgets scale with the contract everywhere (`untimed_plan` does this for the runner; audit the single's submit
  loop, the harvest, localize, prefetch and probes for any flat constant).

Gate: the fault suite is green before `day.sh` is armed; a red suite is a FAIL in preflight, not a WARN.

### P2. Shrink the LLM single floor from 40-90 s to ~25 s (the 1-minute item)

- **One-shot "live answer" worker on every LLM-bound single**, in parallel with the solver-building worker: it gets
  triage + the standard-tool dumps (exiftool, readelf, jadx/aapt summaries, decoded text) + the contract and must
  answer in <=2 turns, submitting whatever it is confident in; the solver worker then only has the empty/wrong ids
  to chase. This is the D16 metadata `live` path generalized to the single. Target: 14/15 by T+40.
- **Pre-drop warm workers.** `WarmWorker` is READY in 3 s but is launched at chain start; launch at T-30 s off the
  clock-aware drop wait so handoff happens at T+1 instead of T+7-8 (SPEED.md: "only a pre-drop launch could help").
- **Triage that ends the first turn.** Metadata/binary workers spend 2-3 turns re-discovering what triage could
  have printed (format facts, strings, section/manifest summaries). Measure turns-to-first-submit per lane each
  day (`hctf cost` has turns; add first-submit time) and push the standard-tool output the worker asked for in
  turn 1 into triage. Keep effort at high (user rule): the lever is turns, not effort.
- **Metadata reuse that matches on format, not text.** The race keys on normalized question text; metadata questions
  are per-format and never repeat. Key the race on the triage-detected container (regf/ole/ooxml/pdf/eml/lnk/png...)
  -> prebuilt `lib/meta` extractor, so a known format answers deterministically and only a genuinely new format
  reaches the model. Gate: `hctf train` metadata cumulative = 100% and the race wins the replay single on D10-D16.

### P3. Keep Homebase for probe throughput, not window fit

With untimed pools the VM's job is the 12-way bisect/localize probes and start/submit round trips (0.5 s vs 2-5 s
public). Route by `route_costs` (shipped) and treat a slow VM (t3.small after the reset) as "local". If main's VM
stays slow, ask for the reset to be undone or budget credits for a bigger instance; do not spend engineering on
in-window latency any more.

### P4. Make the improvement loop pay for itself (the "still improving" requirement)

The loop must be judged by tomorrow's T+, not by whether a ratchet merged.

- **Nightly blind replay of today on the post-ratchet harness** (replay_gm, knowledge pinned to pre-day). Record
  T+ 14/15 and 15/15 and the determinism ratio. A ratchet that does not improve the replay (or breaks any earlier
  day in `hctf train`) is kept out, as the baseline-aware gate already does for tests.
- **One ratchet process, bounded.** Ratchet + ratchet_log cost up to 23 min / $10 (D16) and once ran out of turns
  mid-binary (D14). Split by lane with a 40-turn cap each, run in parallel under procgov, and make them write
  technique notes first (the part that ran out on D14).
- **Prebuild aimed by misses.** Prebuild modules are only worth it if they later win a race. Feed it the atlas gaps
  ranked by (a) lanes whose race lost this week and (b) formats/toolchains the organizers have escalated to
  (today-probe + mastery_delta). Report prebuild hit rate: modules that answered a live field / modules built.
- **Scoreboard in one place.** `hctf timeline` + `hctf cost` + race wins + generalizes-on-critical-path + manual
  steps -> a per-day row appended to `reference/SPEED.md` (or a `hctf kpi --day N`), so the trend is visible and
  the user never has to ask whether a change helped.

### P5. Governance that stops a bad day becoming a lost day

- Preflight FAILs (not WARNs) on: fault-replay red, MemAvailable < 6 GB, linger off, VM slow when Homebase is
  expected, token < 3 days.
- Feed `⚠` on: runner killed by budget, exec_error twice on one mode, generalize > 90 s, any sequential GM loop
  > 20 calls, load > cores.
- A day that is 14/15 at T+2 with one mode in a generalize loop auto-switches that mode to the untimed fallback +
  resume path rather than retrying generalize (D16's loop ran 11 minutes).

## 5. Sequencing before the next drops

- **Tonight / Day 17 warm-up (no lib edits during prebuild):** P0 fix-in-attempt default + budget audit; P5 preflight
  FAILs; P1 fault suite with the D15/D16 faults first (IncompleteRead, 5475 ids, sequential bisect). Validate on an
  rehearsal fair replay of D16: expect script Mastery < 2 min, 15/15 < 3 min.
- **Day 18-19:** P2 live-answer single on metadata + binary, pre-drop warm workers, triage turn-1 audit. Validate:
  rehearsal fair D17 14/15 <= 1:00.
- **Day 20+:** P4 nightly replay KPI, lane-split ratchet, prebuild hit rate; P2 format-keyed metadata race.

What would have to be true for a sub-1-minute 15/15: every single either race-won (<10 s) or live-answered in two
turns (<30 s), no generalize anywhere, GM round trips on Homebase, and the harness fault suite green. Nothing in
that list is new capability; it is the existing pieces (race, live answer, grouptest, bank overlay, background
generalize, replay GM, warm workers) made the default path and gated nightly.

## 6. Implemented 2026-10-17 (before Day 17)

- **Release detection (new finding, not in the plan above):** D15/D16 saw the release 13-14 s after the drop because a
  `list --day N` for a populated day takes 2-13 s. `wait_for_release` now probes `status warmups-day-NN` (0.5-2 s,
  404 until the drop) every poll in the hot window and then races per-lane lists against the full list
  (`_list_race`; the GM's `binary` lane filter matches nothing, so a lane that answers [] falls back to `--search`;
  the union counts only when every lane answered and it is at least yesterday's size). Knobs:
  HCTF_RELEASE_FAST_PROBE, HCTF_RELEASE_HOT_AFTER, HCTF_RELEASE_LIST_EVERY.
- **P1 fault-injection replay:** `hctf/replay_gm.py --timed <cid>=<case dir>,...` serves Time Trial / Mastery locally
  with the real GM's untimed regular-pool semantics (reconnect, retry = next variant, pool, prerequisite, finished
  CORRECT body, accepted_ids/remaining, already_solved, practice) plus faults `--fault-cut/-latency/-429/-start-503/
  -prereq-flap/-dl-stall`, `--pool N`, and a `{"op":"_fault"}` control. `tests/test_fault_replay.py` = 26 checks over
  11 scenarios (D8 503, D14 one-variant pool, D15 cut reply, D16 slow GM + big contract + runner deadline/resume,
  alt-D16 prerequisite flap, r9b finished body, 429s, stalled download, release detection). Green in ~2 min.
  `bin/preflight.sh` runs it (FAIL when red; skipped inside the last 12 min or with HCTF_PREFLIGHT_NO_FAULT=1).
- **P5 preflight gates:** host memory (FAIL < 2.5 GB available, WARN < 4 GB), pairing token and Claude login FAIL at
  <= 2 days, the fault suite above.
- **P4 KPI:** `hctf kpi --day N [--record]` / `--all` -> T+ 14/15 and 15/15 from the release line, release lag, race
  wins, timed first-try count, generalizes (count / s / on the critical chain), live-answer / in-attempt / untimed
  passes, `!!!` count, live vs post-run worker cost; rows in `reference/KPI.md`.
- **P0 knobs:** HCTF_LIVE_MAX_FIELDS 40 -> 80 (D12's 58 empty slug fields now go to a live worker on the open attempt
  instead of a generalize); last_timed.json keeps already_passed / bank_overlay / resumed_banked / unjudged_resends /
  localize_error / localize_waves / resubmit_fixed for `hctf why`; HCTF_REPLAY_REROLL=0 keeps the real GM's
  no-re-roll rule against a local stand-in.
- The rest of P0 (fix-in-attempt, label hints, resume, live answer racing the generalize, background generalize) was
  already in place; the suite now proves the runner half of it offline.

- **P2 answer-first single (shipped later the same evening):** when the reuse race does not win a single of <= 80
  fields, a second `live`-stage worker (medium effort, 3 concurrent, memory-gated) derives and SUBMITS the fields from
  the bytes in a few tool calls while the chain's worker builds the solver; confirmed values go to the solver worker's
  inbox; ended at CORRECT. Smoke vs a stand-in GM serving the D16 metadata single: CORRECT in 8.0 s / 2 tool calls
  (real D16: 74 s single + 49 s duel). Knobs: HCTF_ANSWER_FIRST(=1), _MAX_FIELDS, _LANES, _EFFORT, _MAX, _RACE_WAIT.
  The chain still waits for a solver that reproduces the confirmed answers before TT/Mastery (the solver worker now
  gets the truth early instead of probing the GM for it).
- **P2 metadata format-keyed race:** already present -- `solvers.reuse_plan` includes `paths.lane_solver_dirs` (the
  lib/meta lane solver), so a known container answers in the race; what metadata lacks is breadth (prebuild), not
  dispatch.
- **P5 feed:** ⚠ once a generalize runs past 90 s (HCTF_FEED_GEN_WARN_S), naming `hctf why <base>`.

Still open (next): P2 pre-drop warm workers (design: the warm worker's env/prompt carry the challenge id and dirs,
which exist only after the list -- needs a per-lane placeholder dir + a redirect the hooks honour; validate on an alt
fair replay before a live day); P2 triage turn-1 audit (turns-to-first-submit per single worker into `hctf kpi`);
P4 nightly blind-replay KPI + lane-split ratchet + prebuild hit rate; P5 feed warning for sequential GM loops.

## 7. Implemented 2026-10-21 (before Day 21)
D20 measured: the 15 regular modes were CORRECT on the GM by T+1:12; the feed/KPI said T+1:29.
- **Measure at the GM's CORRECT:** timeline/kpi/feed count a timed mode at its `timed: {"result": "correct"}` line
  (`result: correct` came 16-24 s later). D20 KPI row now 15/15 at T+1:12.
- **TT -> Mastery handover:** `labels.record_values` re-parsed start.json per confirmed field (O(n^2): ~20 s on script's
  6645-answer Mastery, 4 s on its TT, between the GM's CORRECT and the next mode) -> one question map, 0.05 s.
  Mastery pre-start at the TT's CORRECT (`_prefetch_mastery_start`, HCTF_PREFETCH_MASTERY; untimed pools, not web):
  start + download overlap the pre-Mastery block.
- **P2 pre-drop warm workers: measured, not built.** Every lane's warm worker is READY ~3 s after chain start, but no
  lane's go text came before +8 s (metadata +8, mobile +9, warmups +10, script +16, binary +25): the go text, not the
  worker, is the floor, so a T-30 launch saves nothing. The prior-solver dry run already never holds the go
  (GO_EARLY). Binary's go = start+download ~7 s + triage; triage's own parts sum to 5-7 s, the rest is unaccounted ->
  the go text line now carries `start+download / pre-triage / triage / post-triage` seconds (D21 will say where).
- **P4 nightly blind replay:** `bin/replay_rehearsal_day.sh start|stop <tag> <day> <pre>` (promoted from .run) records the
  replay's KPI row in reference/KPI.md as `D<N> replay-<tag>` (`hctf kpi --day N --log <run.log> --label <tag>
  --record`). Needs alt to have played the day for real (it serves the rehearsal copy's own singles); not scheduled automatically
  (each replay costs LLM credit + ranked attempts).
- **Web (see web-team-limit notes):** parallel web chains, preparing kicks + web_trace, live pre-Mastery compounding
  check.


## 8. Implemented 2026-10-26 (D25 post-mortem, before Day 26)
D25: 24/24 GM-CORRECT, but board T+6:02 (regular 15/15 T+5:51, web 9/9 T+3:56). The tails were two compounding Masteries
wrong on the first try plus a slow failure path. No Hall of Fame work (TT/Mastery stay on the untimed regular pool).
Merged as `d25-A` (`bd1b5c4b`) + follow-ups `5b07aed4`, `6a7a7976`.
- **First-try correctness (A):** binary solvers d08-d25 keyed caches on `id(bytes)` -> a freed-and-reused address on
  Homebase's 2-proc pool gave a later set an earlier set's facts (46 wrong fields). Caches now hold the object and
  check identity; `lib/solverrt.max_procs()` / `HCTF_SOLVER_MAX_PROCS`; case replays run on 2 procs
  (`HCTF_CASE_MAX_PROCS`); `tests/test_no_id_cache.py` lint + a stop-gate block. A TT -> Mastery pool rehearsal
  (8 synthetic sets on 2 vs 1 procs, background at TT CORRECT) catches the next one. Warmups: `_unknown_line_cands`
  puts the verbatim line first (rot18 `le-07` beat `le-52` -> 123/123 wrong); a last line that fails its own day
  codec (pre-decoded by a solver) reads as unknown. today-probe ignored dotfiles (dead since D22).
- **Routing + transport (B):** no-clock timed modes run local when there is untimed evidence (Homebase kickoff cost
  25-30 s/mode; `HCTF_NO_CLOCK_LOCAL=0` reverts); hedged idempotent `start`, sized from today's contract; ranged
  parallel download with a self-probe (`HCTF_GM_RANGE_STREAMS`); sha-matching pulls kept; atomic `challenges/index.json`.
- **Failure path (C):** generalize baseline async (-70 s); case dedupe by sha; reject-free unverified cases pass the
  stop gate + green watcher + duel (~-130 s); live cap lifted for uniform shapes (`HCTF_LIVE_UNIFORM_MAX`); no-LLM lib
  racer (`hctf/libracer.py`); early live on per-set verdicts; no label-retry bisection on free-text fields.
- **Web (D):** the single's worker writes and verifies the plugin (`lib/web/plugin.py`), Mastery re-runs it, the
  Mastery target is requested at TT CORRECT; feed/kpi count live-answer TT passes (`timeline.TIMED_PASSED`; D25 KPI
  re-recorded 24/24, web 9/9); `KEY_COMPANIONS` gate shared concept keys; answer-first cap scales with chains; opt-in
  web prebuild lane (`HCTF_PREBUILD_WEB=1`, offline fixture gate).
- **In-network race (B3b, built 10-26, `73740ebc` + `272807ae`):** a lane whose last single was >= 10 MB (binary only,
  32-35 MB D20-D25) also races on Homebase: once the local `start` lands, the VM reconnects to that attempt over the
  in-network proxy (no bearer; refused on a bearer channel), downloads in-network, runs the newest same-lane solvers on
  warm zygotes and returns answers only; the client merges + submits through the shared race path (first plan per
  attempt claims it). A win before the local bytes land hands the timed modes over at once. Solvers pushed + warmed
  while armed. Live on a rehearsal copy (D25 binary TT variant): VM start 1.1 s, 35.8 MB in-network 7.1 s, answers identical to the
  local runs, submit CORRECT. Off-peak the public download is as fast (5 s); the win is at the drop (D25: 68.6 s).
- **GM Range: NOT honoured** (alt probe 10-26: `Range: bytes=...` -> 200 + full body, no Content-Range/Accept-Ranges).
  gm.py's ranged path costs nothing (one request, used whole) but cannot speed the drop download up.
- **Rehearsal fair D25 (10-26; workflow = these fixes, knowledge = 1cb31043, Day 25 masked):** 24/24; regular 15/15 T+1:36,
  board T+2:26 from launch (main D25: T+5:51 / T+6:02); 0 generalizes (main: 2, 241 s); 0 timed modes on Homebase;
  timed first try 15/16; warmups Mastery T+0:47 and binary Mastery T+1:38 first try; live $6.41 (main $9.73). Web: the
  single's worker promoted the plugin on 2/3 chains and their TT/Mastery dispatched to it with no live worker. Found +
  fixed: the race gave up when no relay channel was up yet; the codify hardening prompt crashed on a Path; the
  answer-first worker was ended mid-plugin at the single's CORRECT (now a 45 s promote grace,
  HCTF_WEB_AF_PLUGIN_GRACE). Remaining board tail = web: an LLM single (47-56 s) + GM Mastery target provisioning (~57 s).
- **Verify on D26:** the in-network race line + its win time on binary at the drop; web plugin at every single's
  CORRECT (grace line); board N/N by T+2:00.
