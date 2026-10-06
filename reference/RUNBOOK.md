# Huntress harness — operator runbook

Repo: WSL `~/huntress-2026`. Always `source bin/env.sh` first (puts the project toolbox + venv on PATH).
Flowchart of the whole workflow: https://claude.ai/artifact/BqcfWXz9pFBqmdZyHpktPo

## Prerequisites each session (WSL-native — current setup)
Claude Code now runs **natively inside WSL** (not from Windows via `wsl -d Ubuntu`). GM access is direct over the
public GM with the pairing token — no Windows, no browser, no VPN needed just to solve. Homebase (optional
low-latency compute for tight timed windows) needs the VPN + the VM powered on.

1. **One command does the pre-flight checks:** `source bin/env.sh && preflight.sh`
   It verifies token validity + **days-to-expiry**, GM reachability, the VPN tunnel, and Homebase SSH, and prints
   PASS/WARN/FAIL. Exit 0 = go. Run it before every drop.
2. **VPN:** auto-starts on boot via the systemd unit `hctf-vpn.service` (OpenVPN, `secrets/*.ovpn`, with
   `--pull-filter ignore redirect-gateway` so worker API traffic stays off the tunnel). Manage with
   `sudo systemctl {status,start,restart} hctf-vpn`. It only gates Homebase, not the GM.
3. **Homebase VM power:** `remote.power()` drives the Windows CourseStack browser, which is NOT wired up in
   native WSL. The VM must be powered on out-of-band — either start it from the CourseStack web console, or (legacy)
   run `python.exe \\wsl.localhost\Ubuntu\home\testpwn\huntress-2026\browser\launch.py` from Windows PowerShell.
   Once it's up and the VPN is connected, `power("status")` short-circuits to "running" over SSH (patched in
   `hctf/remote.py`) so prewarm/timed routing work without the browser. Runs never power it OFF unless they
   powered it on themselves. (TODO: a WSL-native power path would remove the only remaining Windows dependency.)

## Daily play (one command)
```
source bin/env.sh
bash bin/day.sh                        # today's day (inferred); pre-flight -> warm Homebase -> background run
bash bin/day.sh 6 --scout 3           # a specific day, with TT label-scouting on hard lanes
# low-level (what day.sh wraps):
hctf run --day N --local 5
```
`day.sh` logs to `.run/dayNN.log`; watch with `tail -f`, `hctf dash | grep dayNN`, `hctf why <id>`.

### Speed tuning (worker effort is the main wall-clock lever)
A heavy day is bound by one slow `single_solve` LLM worker (deterministic reuse/triage runs first and is instant).
Effort defaults to `high` on every lane (warmups included); `bash bin/day.sh N --effort xhigh` raises all lanes. Override per lane with
`HCTF_WORKER_EFFORT_<LANE>` / `HCTF_WORKER_MODEL_<LANE>` (LANE = index lane upper-cased, `-`→`_`), e.g.
`HCTF_WORKER_EFFORT_SCRIPT_ANALYSIS=medium`. See `hctf/workers.py` (LANE_EFFORT) and reference/SPEED.md.
`hctf run` syncs challenges, then runs each as an independent parallel chain
(Single Solve → solver → Time Trial → Mastery). It auto-powers Homebase, provisions its solver deps,
and self-heals timed variants offline. Workers submit the instant they have an answer; nothing waits.

## Watch it live
```
hctf watch                 # board: every challenge x mode, stage, each agent's current action
hctf tail <challenge-id>   # follow one agent's reasoning + tool calls as they stream
hctf dash                  # one-shot status table
```

## Manual / debugging commands
```
hctf list [--day N] [--all]           hctf status <id>
hctf start <id>                       hctf artifact <id>        # download, sha256-checked
hctf triage <id>                      # deterministic no-LLM analysis -> triage.md
hctf solver-run <id>                  hctf solver-test <base-id>
hctf submit <id> '{"<answer_id>":"<value>"}'
hctf timed <id>                       # run one time_trial/mastery end to end
hctf hb status|on|off|ensure|deploy|setup
hctf hb exec -- <cmd>                 # run a command on Homebase (inside the CTF network)
```

## Credits (important)
- Homebase burns ~2 credits/hr while running; the Game Master is only reachable through it.
- Credits **refill daily at 9:00 AM ET** with the new challenge release.
- The credit governor keeps a reserve (soft 4 / hard 1.5): below hard it powers the VM off so the GM stays
  reachable when needed. Check with `hctf hb status`.

## Tuning (env vars)
- `HCTF_MAX_WRONG` (6) — per-field wrong-answer probe budget for non-flag vocabulary. Flags hard-capped at 3.
- `HCTF_SINGLE_TIMEOUT` (1500) / `HCTF_GENERALIZE_TIMEOUT` (720) — worker wall-clocks (seconds).
- `HCTF_MAX_TURNS_SINGLE|GENERALIZE|FIX` — per-stage turn caps (ilio-style cost bound).
- `HCTF_SPECULATIVE_TIMED` (1) — early handoff: once the Single Solve is CORRECT and a snapshot of the still-running
  worker's solver (`.run/spec-dayNN/<chal>/solver`, files stable `HCTF_SPEC_STABLE`=20s) reproduces its answers, run ONE
  Time Trial -> Mastery pass from it. Pre-pass failures are free; the normal timed stage takes over after the worker.
- `HCTF_CHAIN_CRASH_RETRIES` (1) — a crashed chain is re-run (solved modes skip) before it is marked `crashed`.
- Offline self-tests: `python3 tests/test_orchestrate.py` (orchestrator paths) and `python3 tests/test_hardening.py`.

## How it solves (short)
- **Single Solve:** triage grounds the agent; it tries the existing solver library first (0 model time), else a
  `claude -p` worker analyzes the bytes, writes a variant-proof `solver/solve.py`, and submits.
- **Time Trial / Mastery (~6s windows):** `hctf/hb_timed.py` runs start→download→solve→submit ON Homebase
  (sub-ms GM latency), submitting per set. A failed attempt → offline `generalize` worker re-derives the
  variant's answers and fixes the solver → retry on a fresh clock. All autonomous.
- **Library:** `lib/` (common/decode/elf/scripts/knowledge) + per-challenge solvers accumulate across days;
  `lib/knowledge.py` stores GM-confirmed vocabulary so later days don't re-probe.

## State on disk (all inside the project)
- `challenges/dayNN/<lane>-<title>/{single_solve,time_trial,mastery,solver}/` — per-mode contracts, artifacts,
  submissions, confirmed answers, worker logs; `chain.json` is the chain's live status.
- `.run/` runtime (ssh socket, locks, tmp, caches, logs) · `secrets/` (.ovpn + ssh key) · `tools/`+`bin/` toolbox.

## After a Homebase factory reset
`hctf hb setup` reinstalls solver deps; `hctf run` re-syncs hctf/lib/solvers automatically. The SSH key in
`secrets/huntress_homebase` must be re-authorized (re-run the key-install step) since a reset wipes authorized_keys.
