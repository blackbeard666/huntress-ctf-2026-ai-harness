# Huntress CTF 2026 "AI Arena" harness (`hctf`)

An automated harness that plays the **Huntress CTF 2026 AI Arena**: every day it retrieves the new challenges from the
organizers' Game Master (GM) API and solves all of them in parallel (every lane, every mode) with LLM worker agents
(`claude -p`). The output of each solve is a reusable solver, its regression cases and GM-confirmed knowledge that carries
over to later days.

- **Lanes:** warmups, metadata-forensics, script-analysis, binary-reverse-engineering, mobile-android, plus web (from
  Day 19).
- **Modes per lane:** `single_solve` (untimed), `time_trial` (one fresh variant on a clock) and `mastery` (multi-set
  variant on a longer clock).
- **The GM never reveals expected values.** It only validates submissions, and synthetic labels must be spelled exactly,
  so a large part of the harness is about learning label spellings and keeping solvers robust to unseen variants.

For the design and how the harness got here, read [`ARCHITECTURE.md`](ARCHITECTURE.md). Day-to-day operation is in
[`reference/RUNBOOK.md`](reference/RUNBOOK.md).

## How it works

1. **Drop.** `bin/day.sh N --wait` polls the GM and launches `hctf run` the moment the day is released.
2. **One chain per challenge, in parallel.** Each chain runs single -> time_trial -> mastery
   (`hctf/orchestrate.py`).
3. **Single solve.** Triage runs first, without an LLM (`hctf/triage.py`, `hctf/toolchain.py`). A reuse race submits
   prior solvers' answers while a sandboxed LLM worker writes `solver/solve.py`. The worker is stopped once the GM says
   CORRECT and the solver is verified.
4. **Timed modes.** The solver runs inside the clock, on the organizers' Homebase VM when it's available (persistent
   daemon + forked warm solver) and locally otherwise. A failure captures the variant as a case and triggers a
   *transactional generalize*: the worker's edit is kept only if no previously passing case breaks.
5. **After the run.** A ratchet worker merges each solver's proposed knowledge into `lib/` (test-gated), and `hctf
   prebuild` writes speculative extractors and codecs for likely next concepts.

Core principles: LLM-first with standard tools (readelf, Ghidra, jadx, exiftool, ...) rather than hand-built parsers;
every solve leaves a solver plus regression cases; only GM-confirmed knowledge is ratcheted forward.

## Repository layout

| Path | What's there |
|---|---|
| `hctf/` | The harness: CLI (`cli.py`), orchestrator, workers, timed path, Homebase daemon/zygote, label probing, probes, post-run ratchet/prebuild, GM client. |
| `hctf/prompts/` | Worker role prompts (single, generalize, fix, ratchet). |
| `lib/` | Knowledge layer shared by solvers: `playbook.py` (GM label grammar / naming laws), `knowledge.py` (confirmed values + rejected spellings), `vocab.json` (confirmed label cache), codecs/decoders, metadata extractors, binary/Android/web helpers, ATT&CK references. |
| `skills/` | Agent skills: the solve loop (`huntress-ctf`) and one skill per lane. |
| `challenges/dayNN/<lane>-<title>/` | Per-challenge state: `chain.json`, per-mode contracts/logs/submissions, and `solver/` (`solve.py`, `NOTES.md`, `cases/`). `_lane/` holds cumulative lane solvers. |
| `reference/` | GM API notes, runbook, plans and post-mortems, KPI log, per-lane technique logs and coverage atlas, solutions index. |
| `tests/` | Regression and fault-injection suites (including the offline fault replay run by pre-flight). |
| `bin/` | `hctf` launcher, `env.sh`, `preflight.sh`, `day.sh`, replay helpers. Tool launchers are installed here but not tracked. |
| `setup/` | Toolbox installers (`install.sh`, `install_tools.sh`), Homebase provisioning, the VPN systemd unit. |
| `.claude/` | Worker hooks (stop gate, nudge, no-block) and settings. |
| `CLAUDE.md`, `AGENTS.md` | What every worker agent is told. |

## Setup

Runs on Linux (developed in WSL2 Ubuntu). Everything installs under the project directory; nothing goes system-wide
except the apt packages listed in `setup/install_tools.sh`.

```bash
bash setup/install.sh          # uv, project-local Python 3.12 venv, Node, Ghidra, jadx, analysis libraries
bash setup/install_tools.sh    # more lane tools: GoReSym, ilspycmd, rustfilt, ... (apt list in its header)
source bin/env.sh              # puts hctf and the toolbox on PATH
```

You also need:

- a logged-in Claude Code CLI (`claude auth login`) and `bwrap` (workers run sandboxed);
- a GM pairing token in `secrets/gm_pairing_token`;
- optionally, the CTF OpenVPN profile and Homebase SSH key in `secrets/` for the low-latency timed path.

`secrets/` is gitignored and must never be committed.

## Daily use

```bash
cd ~/huntress-2026 && source bin/env.sh
bash bin/preflight.sh            # at warm-up, before the drop (--fix kills a duplicate Windows OpenVPN client)
bash bin/day.sh N --wait         # waits for the release and launches the whole day
hctf feed --day N                # one line per milestone, until all chains finish
```

Useful commands:

| Command | Purpose |
|---|---|
| `hctf list --day N` | The day's challenges. |
| `hctf dash` / `hctf watch` | Chain status table / live board. |
| `hctf why <id>` | Is a lane converging or stuck? Block reason, wrong fields, attempts, last worker result. |
| `hctf tail <id>` | One worker's reasoning. |
| `hctf status <id>` / `hctf reconcile --day N` | GM's authoritative result / rewrite local state from the GM. |
| `hctf cost --day N` | Worker LLM cost and turns per chain and stage, plus non-ok worker exits. |
| `hctf kpi --day N --record` | Append the day's KPI row to `reference/KPI.md`. |
| `hctf labels <id> <answer_id> --term ...` | Resolve a GM synthetic-label spelling by probing. |
| `hctf hb status\|on\|off` | Homebase VM control. |
| `hctf solutions` | Regenerate `reference/SOLUTIONS.md`. |

Each test suite is a standalone script, for example `python3 tests/test_fault_replay.py` (run from the repo root with
`bin/env.sh` sourced).

## Results

Wall clock from release to the last GM-confirmed CORRECT, main account, real runs. Full history in
[`reference/KPI.md`](reference/KPI.md).

| Day | 5 standard lanes | Web lane |
|---|---|---|
| D09 | 15/15 in 1:58 | - |
| D11 | 15/15 in 1:06 | - |
| D14 | 15/15 in 2:20 (14/15 in 0:49) | - |
| D18 | 15/15 in 1:43 | - |
| D20 | 15/15 in 1:12 | 6/6 in 14:52 |
| D22 | 15/15 in 1:35 | 6/6 in 7:50 |
| D23 | 15/15 in 28:55 (14/15 in 16:10) | 9/9 in 7:21 |
| D24 | 15/15 in 2:09 | 6/6 in 3:32 |

Worker LLM cost runs about $3-15 per day.

## Branches

`d22-web-critical-path` is the current line (default branch). `master` and the `dNN-*` branches are earlier milestones
and fix branches kept for history.

## Note

This repository contains working solutions to an ongoing competition. Keep it private until the CTF ends (2026-10-31).
