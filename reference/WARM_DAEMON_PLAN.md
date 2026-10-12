# Warm solver daemon on Homebase: plan (2026-10-12)

## Context
The Hall of Fame (reference/gm-api.md "Hall of Fame") ranks every team by the GM-measured time of its fastest timed
attempt per challenge. On Day 9 the leaders take 0.26-1.5 s and we rank #16-#33 (warmups TT: #1 258 ms, ours 566 ms).
Our gap is per-attempt overhead, not solving. Each timed attempt today does this:
`ssh` exec -> fresh `python3 hb_timed.py` (imports + 32-connection pool) -> start -> download -> **fresh `python3
solve.py`** -> submit, everything through the inside proxy.

Measured on the main Homebase VM (2 vCPU) on 2026-10-12 (`.run/hb_forkbench.py`, `.run/hb_latency.py`):

| | today | warm alternative |
|---|---|---|
| solver start, small lanes (warmups/mobile/metadata) | 150-230 ms fresh process | 15-51 ms forked from a pre-loaded parent |
| script solver (spawns node itself) | 575-670 ms | 464-532 ms |
| GM request, kept-alive | 232 ms inside proxy | 170 ms public GM over HTTPS with bearer token |
| before the clock, per mode | ssh exec + interpreter + pool warm, ~0.6-1.0 s | one JSON line on an open channel |

Expected: about 250-350 ms less inside the clock per attempt (warmups TT ~566 -> ~250-300 ms, close to the leaders),
and about 0.6-1 s less chain time per timed mode. Answers are byte-identical to the subprocess run on all 4 lanes
tested.

## Design
1. **`hctf/hb_daemon.py` (runs on Homebase)**: a long-lived process started by the orchestrator over ONE persistent
   ssh channel (`ssh ... python3 ~/hw/hctf/hb_daemon.py --stdio`). It speaks JSON lines (request id, op), with one
   thread per request so all 5 chains can run in parallel.
   - The first line carries the pairing token. It is kept **in memory only**: never on the VM disk, in argv, or in
     logs (redacted). GM traffic goes to the public GM with the bearer (170 ms), falling back to the inside proxy.
   - `ops`: `ping`, `warm {solver}`, `attempt {cid, solver, op, expect_bytes, env}`, `shutdown`.
2. **Zygotes: one per solver dir** (`hctf/hb_zygote.py`): a separate, single-threaded process. This avoids
   fork-in-a-threaded-process deadlocks and module-name clashes between lanes and days (e.g. `bashplan.py`).
   - It puts the solver dir on `sys.path` and runs `runpy.run_path(solve.py, run_name="hctf_warm")` once, which loads
     the solver's imports and definitions; the `__main__` guard (present in every solver and in the skeleton) stops
     `main` from running.
   - Each solve: `os.fork()` -> the child sets `sys.argv`, runs `runpy.run_path(..., run_name="__main__")`, and returns
     stdout over a pipe. The daemon enforces the solve budget (kills the child).
   - Solver globals mutated in a solve never leak, because each solve runs in its own fork. Solvers' own per-set fork
     pools keep working.
   - A zygote is re-warmed when the solver's signature changes (`workers._solver_sig`), e.g. after a fix-up worker.
   - Memory: about 100-200 MB per zygote x 5 on 3.8 GB. Idle zygotes for finished chains are reaped.
3. **One timed-attempt code path:** refactor `hb_timed.main()` into `run_attempt(args, solve_fn, http)`.
   - `solve_fn` is either the subprocess (CLI, local fallback) or the zygote (daemon). The pipeline's per-set solves
     use the same `solve_fn`, so they become cheap forks too.
   - The CLI and every GM rule (HoF pool, re-roll, partial submit, localize, no double POST) stay in one place, unchanged.
   - Artifacts go to `/dev/shm/hctf/<slug>` (tmpfs); the result and bytes are still mirrored to `.run/tmp-timed`, so
     the current pull/capture flow keeps working.
4. **Orchestrator side (`hctf/workers.py`)**: an `HbDaemon` client.
   - It starts lazily in the Homebase prewarm, with a health ping in the existing 5 s health thread and a restart on
     failure.
   - `prepush_solver()` sends `warm` right after the tar push, so the zygote is ready before the TT kickoff.
   - `run_hb_timed()` uses `daemon.attempt()` when the daemon is healthy, otherwise the current ssh+`hb_timed.py` path.
   - If the daemon dies mid-attempt -> exec_error -> the existing fallback. Its `start` reconnects to the same attempt
     (start is idempotent), so no variant is spent twice.
   - Flag: `HCTF_HB_DAEMON` (default on after the rehearsal); `HCTF_HB_PUBLIC_GM` to keep the inside proxy.
   - The rehearsal copy sends the shared token: with the public GM, identity is the bearer, not the VM.
5. **Out of scope** (logged as follow-up): solver-internal tool cold starts (the script solver's node, ~450 ms) need
   a solver-side convention (keep a warm helper / decode in-process). Not a harness change.

## Files
- new: `hctf/hb_daemon.py`, `hctf/hb_zygote.py`, `tests/test_hb_daemon.py`
- refactor: `hctf/hb_timed.py` (`run_attempt` + pluggable `solve_fn`/transport; CLI unchanged)
- `hctf/workers.py`: `HbDaemon` client, `run_hb_timed`/`prepush_solver` integration, health; `sync_homebase_base` ships the new files
- docs: `reference/HOMEBASE.md`, `reference/SPEED.md`; memory note

## Verification
1. **Offline:**
   - Zygote answers == subprocess answers for every saved case of every day01-09 solver (all lanes), run locally.
   - Protocol, concurrency (5 parallel attempts), solve timeout kill, re-warm on signature change, token never on
     disk/argv/log.
   - Daemon crash -> fallback path. Plus the existing 14 suites.
2. **Homebase, no GM:** the fork bench through the daemon (warm/solve timings), and 5 zygotes' memory.
3. **Live:** timed attempts on older days (Day 7/8 TT + Mastery; their pools have ~27-29 attempts left; Day 9 is
   spent on main, and its script Mastery is GM-broken). Compare our `elapsed` and the HoF `elapsed_ms` before and
   after. Any attempt can only improve our HoF time.
4. **Then a blind full-day rehearsal** when a fresh day is available.
