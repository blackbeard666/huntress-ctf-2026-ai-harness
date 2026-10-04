# Huntress harness — operator runbook

Repo: WSL `~/huntress-2026`. Always `source bin/env.sh` first (puts the project toolbox + venv on PATH).
Flowchart of the whole workflow: https://claude.ai/artifact/BqcfWXz9pFBqmdZyHpktPo

## Prerequisites each session
1. **Browser (for VM power + credits):** launch the CourseStack browser with the Windows Python, from PowerShell
   (not Git Bash, which mangles the `\\wsl` path):
   `python.exe \\wsl.localhost\Ubuntu\home\testpwn\huntress-2026\browser\launch.py`
   It reuses the logged-in profile (CDP on 127.0.0.1:9222). `hctf hb` talks to it.
2. **VPN:** the OpenVPN GUI profile `huntress-ctf-2026` must be connected (reaches Homebase SSH).
3. That's it — `hctf hb ensure` powers the VM on and provisioning happens automatically on `hctf run`.

## Daily play (one command)
```
source bin/env.sh
hctf run --day N --local 5            # all of day N, 5 parallel local workers
# or everything released:
hctf run --local 5
```
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
