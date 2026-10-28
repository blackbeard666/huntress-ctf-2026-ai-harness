# D28 post-mortem plan — whole board sub-2:00

## Context
Day 28: 21/21 GM-CORRECT but the board finished at **T+5:50**; 1st/2nd place finished in 2–3 min. **Target: the
ENTIRE board (every lane incl. web, every mode) GM-CORRECT by T+2:00, on known AND unknown variants** (standing rule,
memory `sub2min-whole-board-goal`). Four lanes were done by T+2:06; the misses are binary (single 3:39 → TT 4:40 →
Mastery 5:50), the two web chains (4:47 / 5:12) and script (2:06).

Fixing tonight's bugs alone (Part A) gets ≈T+3:00. Sub-2 additionally needs the structural items in Part B: the
remaining time is **bytes over our ~1.7–5 MB/s home link** and **LLM work on the critical path**.

Constraint: implement only after ALL post-run activity (prebuild `hctf-prebuild-day28-220036`) has finished; work on
branch `d22-web-critical-path` (prebuild `restore()` reverts lib/hctf/tests edits while it runs).

## Sub-2:00 budget (T0 = drop; tonight's actuals → target)
| lane | single | TT | Mastery | where tonight's time went |
|---|---|---|---|---|
| binary | 3:39 → ≤0:40 | 4:40 → ≤0:50 | 5:50 → ≤1:35 | 35.9 MB dl @1.7 MB/s; 31 residual fields → LLM 151 s; TT live 48 s; 60 s accept block; 203 MB Mastery dl |
| web ×2 | 2:12 / 1:22 → ≤0:55 | 2:39 / 2:35 → ≤1:15 | 4:47 / 5:12 → ≤1:50 | new-class LLM single; TT provisioning on path; proof-4 unroutable + 45 s retries |
| script | 1:08 → ≤0:45 | 1:25 → ≤1:00 | 2:06 → ≤1:40 | 40 s harness in single (pre-triage contention); 10 MB Mastery status/dl |
| metadata/mobile/warmups | ≤0:33 | ≤1:01 | ≤1:20 | already inside budget |

---

## Part A — tonight's bugs (≈ −2:50 on the board)

### Binary
1. **Answer-first on the residual, sharded.** `answer_first_eligible(lane, len(af.ids))` (`hctf/orchestrate.py:718`,
   :4716/:966) counts all 392 fields; the dry run knew the 31-field residual at go time. Compute eligibility on the
   residual, narrow the field list + `.live_fields.json` (reuse `LiveAnswer.narrow()`/`_live_fields`, fa16eb6f), and
   shard by `dNN_` family into 2–3 parallel live workers when the residual is above ~12 fields.
2. **Go at the download mark (+24 s, not +50.6 s)**; triage/prior-note follow by inbox (`_go_pending`/`_deliver_note`).
   Add sub-marks to the 21.4 s pre-triage window (orchestrate.py:4505→4553).
3. **In-network race runs**: `_solver_sig` (`hctf/workers.py:1712`) prunes `cases/` during the walk; `hb_race_prepare`
   (:2030) sat 29 s and stood down.
4. **Cross-format check before TT**: run the solver over every prior-case member of each touched family (PE vs ELF etc.)
   and flag fields that come back empty → pre-TT harden. (TT missed `d10_section_count`: ELF-only handler, PE member.)
5. **Mode advance doesn't wait for the post-live accept**: `_accept_after_live` → `_gen_baseline_join()` blocked 60 s
   (57-case baseline 78.7 s + 27 s replay; orchestrate.py:3668/3693/3719/3722). Run the accept in the background.
6. **No off-path load during timed downloads**: defer baseline replays and duel generalizes while a timed mode
   downloads (psi_mem full 0.87 tonight); A/B the hard-coded `_TPE(max_workers=8)` (orchestrate.py:5505).

### Web
7. **Clue-less day-04 LFI class routes in the first pass**: day-20 `solve.py:281` `lfi()` always tries
   `/run/huntress/objective.txt` (depth 5..9); `lib/web/handlers/__init__.py:105-108` `_routes` keeps `?param=` links;
   clue-less fingerprint → `known=True` instead of the 12 s `UNKNOWN_KEY_BUDGET`.
8. **MISS-RETRY only for not-ready targets** (`lib/web/__init__.py:222-265`): ~45 s wasted per miss tonight.
9. **WEB_PREPROVISION doesn't consume the once-per-chain TT kick on `prerequisite_required`** (orchestrate.py:819-826,
   5385, 5883, 7270).
10. **Hot-reload plugins between timed-runner retries** (`handlers/__init__.py:433` loads once at import).
11. Lane-aware baseline case timeout (web ≥20 s; `HCTF_BASELINE_CASE_TIMEOUT`, orchestrate.py:1071).

## Part B — structural, required for sub-2:00
12. **MEASURED 10-28 23:55 — premise wrong, Homebase download NOT faster.** Same 35.9 MB binary evidence:
    Homebase inside proxy 22.5 s (1.6 MB/s) vs local public GM 5.0 s (7.3 MB/s) off-peak; at the drop local was
    20.8 s (1.7 MB/s). So the drop-time slowness is load (GM-side and/or our own 7 lanes downloading concurrently),
    not our link. Replacement: at the drop, order downloads by critical-path need (binary single first, defer
    non-critical prefetches/status polls during the first 30 s), cap our concurrent download streams, and log
    per-download MB/s so D29 shows whether it's GM-side. Original (superseded) idea kept for reference:
    **In-network bytes for big deliveries.** Tonight: binary single 35.9 MB at 1.7 MB/s (20.8 s),
    binary Mastery 203 MB at ~5 MB/s (41 s, 3.9 MB start reply 9.7 s), script Mastery 10 MB. Plan: a **Homebase-resident
    timed run for modes whose contract or deliveries exceed a threshold**. Homebase does start → download → solve →
    submit, and only the result (KB) crosses our link. The rule "big start replies never on the HB daemon" stays;
    this path never returns the big body. Same for the single's evidence download, which goes into the in-network race
    (item 3) instead of local. **Measure first**: HB↔GM throughput and Homebase RAM/disk headroom for 203 MB
    (t3.small, 2 GB, credits 60/day). If HB can't hold it, fall back to streaming download plus per-delivery solve
    overlap.
13. **Zero-residual binary: field-matrix breadth.** 24 of tonight's 31 residual fields were new questions on
    earlier-day families: section/symbol/class counts, `cli_runtime`, `has_*_runtime`, sha of ordered sets, packing
    keys, overlay size. Have prebuild generate and offline-test the generic field set across every family × format
    (ELF/PE/Mach-O, .symtab vs .dynsym rules), so an unseen field on a known family is answered without an LLM.
    Gate it with a mutation suite of "known family, new field" variants (`hctf scout` variants plus synthetic).
    Today's 7 d28 fields remain the only LLM work and are covered by item 1's sharded workers.
14. **Web new-class single ≤55 s with targets pre-provisioned**: with item 9 fixed, TT and Mastery targets start
    provisioning the moment the single is CORRECT. Codify must land before the TT runner starts (breach did this,
    fail-open's codify landed 55 s late). Have the TT wait ≤10 s for a pending codify instead of racing without it.
    Pre-drop compounding check: one regression case per earlier web class, including clue-less ones (lane-day 04, 05,
    13, 16 never exercised) → first-pass Mastery is guaranteed for known classes.
15. **Orchestrator contention at the drop**: `[res]` sampler gaps of 14–15 s at T+0:17–0:46 inflated pre-triage by about
    20 s on binary and script. Move dry runs, reuse races and zip extraction to subprocesses (procgov), and keep
    ≤N heavy jobs per lane during the first 60 s.
16. **Web start latency**: breach `start el=18.46` + ~15 s before the start request; TT `t_env 13.87 s`
    (`workers.py:1083-1085`); relay ch0 died at 21:00:25. Instrument, then fix the routing or warm-up.

## Ops
17. Technique-log turn cap `hctf/workers.py:44` 34 → 40. Re-run binary's technique log alone (`ratchet_digest('day28')`
    filtered → `_ratchet_logs`, `HCTF_MAX_TURNS_RATCHET_LOG=50`), and review the mobile/metadata files for truncation.
18. Homebase route survives reconnects: `setup/hctf-vpn.service` ExecStart
    `--script-security 2 --route-up "/sbin/ip route replace 10.1.50.243/32 dev tun0"` + ExecStartPost. Reinstall with
    sudo. Fix the `bin/preflight.sh:124` hint and have `--fix` add the /32. (Both tunnels are in 10.200.0.0/16 → the
    pushed 10.1/16 binds to tun1.)
19. Corrupted hardlinked case: restore `challenges/day27/scripting-from-whence-it-came/solver/cases/single_solve/
    artifacts/evidence.zip` from `…/single_solve/artifacts/latest/` (sha 58ac2b36…). Check warmups' compound-d27 miss.
    Break every main↔alt shared inode. Drop `rsync --link-dest` for `challenges/` in `.run/sync_alt_*.sh`.
20. Relay hygiene (`hctf/gmroute.py`): no relay hedge for known-big `status`; per-channel slow demotion in `_chan`.
21. Warm-up ≥15 min before 21:00, so preflight's fault-replay suite runs (`bin/preflight.sh:304-306`).

## Verification (sub-2 gate)
- `tests/test_d28_speed.py` (pattern of `tests/test_d27_web.py`) covers items 1, 4, 5, 7–11, 14. Replay the saved web
  case `auto-mastery-d08c1077` and breach's: proof-4 must come in the first pass, under 15 s.
- Item 12 measured before building: HB download MB/s vs local, and a 203 MB fit test on the VM.
- Item 13: offline field-matrix suite over all binary cases plus synthetic new-field variants. Every field must be
  answered, with 0 empties.
- `bash bin/preflight.sh` full, including `tests/test_fault_replay.py`, green.
- **Gate:** run a full Day 28 replay on a rehearsal copy (`hctf/replay_gm.py`) and record `hctf kpi`. Done only when the board is
  21/21 ≤ T+2:00 and every lane is within the budget table. Otherwise iterate on the lane that is over budget.
- Homebase: with tun1 up, `systemctl restart hctf-vpn` → `ip route get 10.1.50.243` = tun0.
- `hctf train` for script/warmups → 732/732 after the case fix.
