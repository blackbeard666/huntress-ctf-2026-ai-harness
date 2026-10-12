# Homebase: inventory, how we use it, and the 60-credit/day plan (2026-10-09)

> **2026-10-09 16:41 -- alt ran OUT of credits** ~30 min after power-on, having spent only ~0.5 VM-h (~1 credit) and
> ~$1.4 list of Bedrock test runs (smoke $0.22, mechanics $0.19, realistic rehearsal ~2 min). Unless the balance was
> already low, Bedrock is far more expensive per credit than the 1.0/$ guess (if it started at 60: ~40 credits per $).
> Shadows are therefore **opt-in** (`HCTF_HB_SHADOW=1`) until the rate is calibrated; alt env is Homebase OFF.

## What the VM actually is (enumerated on the the VM 10.1.54.179)
- AWS EC2, Ubuntu 24.04, **2 vCPU** (Xeon Platinum 8259CL), **3.8 GB RAM, no swap**, 38 GB disk (25 GB free after
  ~/hbtools). No passwordless sudo (rehearsal); player is not in the `docker` group. Fast internet egress (GitHub, Adoptium).
- **Inside the CTF network:** the inside GM proxy `http://10.0.0.219/huntress-ctf-proxy` answers in ~0.1 s (public GM
  from WSL: 0.2-8 s). Identity = the VM's owner (no token).
- **Bedrock through the instance role** `assumed-role/EC2BedrockInvoke` (us-east-1). Claude Code 2.1.286
  (`/usr/bin/claude`) with `CLAUDE_CODE_USE_BEDROCK=1` runs **Opus 4.7** (`global.anthropic.claude-opus-4-7`), also Opus
  4.6 / Sonnet 4.5 / Haiku 4.5 (per /opt/huntress-ai-arena/bedrock-agent-engine-proof.json). **Sonnet 4.6 is denied**
  (403 on InvokeModelWithResponseStream). codex-cli 0.159.3 -> `global.openai.gpt-6-luna` (default of the organizer's
  web app). Smoke test: a 2-turn tool-using Opus 4.7 run = $0.22 list, 10.7 s.
- Organizer services: `huntress-ai-arena-app` (web UI on 127.0.0.1:18080, "T3 Code") + a CourseStack readiness proxy on
  :8080; `/usr/local/bin/huntress-claude` (wrapper that appends the organizer AGENTS.md -- we call `/usr/bin/claude`
  directly, our own CLAUDE.md applies). sshd forbids -L/-D forwarding (organizer control; don't work around it).
- **Credits:** 60/day (user, 2026-10-09). The VM costs 2 credits/h (gbPerRuntime=2) and **Bedrock AI usage draws from
  the same pool**. The balance is only readable through the CourseStack browser session (main: `hctf/hbpower.py`; alt:
  none), so `hctf/hbbudget.py` keeps our own ledger. Conversion credits-per-list-$ is NOT measured yet
  (`HCTF_HB_CREDITS_PER_USD`, default 1.0) -- calibrate: note the UI balance, run one metered shadow, note it again.

## How we used it before today
Only for clock-critical timed attempts (`hb_timed`: TT/Mastery solver next to the GM, Homebase-first routing) and the
Single Solve submit hop. Everything else (all LLM work, triage, generalize, ratchet) ran locally. Unused:
1. **Bedrock Claude** (the biggest resource): the `--homebase N` pool existed but drove codex and was never enabled.
2. **Toolchain:** `~/hw/bin` links point at /home/testpwn/... and dangle on the VM; no Java, jadx, apktool, Ghidra,
   rizin, upx, exiftool, ilspycmd. Any solver/worker shelling out to them failed on Homebase (env-mismatch fallback).
3. **Uptime:** the VM was powered on by hand at warm-up and idle-stopped; nothing metered what it cost.

## What is implemented (all gated, all default ON where safe)
| Piece | Where | Knobs |
|---|---|---|
| Credit ledger: VM uptime per boot (btime -> last seen) x 2/h + every Homebase LLM run's list cost | `hctf/hbbudget.py`, `.run/hb_ledger.jsonl` | `HCTF_HB_DAILY_CREDITS`=60, `HCTF_HB_VM_RESERVE`=6, `HCTF_HB_CREDITS_PER_USD`=1.0, `HCTF_HB_RESET_UTC_HOUR`=13 |
| VM metering: the run's health thread books uptime each minute; `hctf hb keepalive` does it while armed | `workers.meter_vm`, `bin/day.sh --wait` | `HCTF_HB_METER_S`=60, `HCTF_KEEPALIVE_S`=14400 |
| **Bedrock shadow Single Solve worker** on the slow lanes, racing the local worker (OPT-IN) | `hctf/hbshadow.py`, `Chain._maybe_start_shadow` | `HCTF_HB_SHADOW`=0 (set 1 to enable), `HCTF_HB_SHADOW_LANES`=script-analysis,binary-reverse-engineering,binary, `HCTF_HB_SHADOW_MAX`=2, `HCTF_HB_SHADOW_USD`=8, `HCTF_HB_MODEL` |
| VM toolchain (no root, ~/hbtools, 2.7 GB): JDK 21, jadx 1.5.6, apktool, dex2jar, Ghidra 12.1.4 (1.5 GB heap), rizin 0.9.1, upx, GoReSym, exiftool, .NET 10 + ilspycmd 11.1 | `setup/homebase_tools.sh`, `hctf hb tools` | on PATH for hb_timed + Homebase workers |
| `--homebase N` pool now drives Claude on Bedrock (codex kept as `HCTF_HB_ENGINE=codex`) | `workers.run_homebase` | `HCTF_HB_ENGINE` |
| Preflight: Bedrock role + claude, ~/hbtools completeness, today's credit line | `bin/preflight.sh` | |
| CLI: `hctf hb budget`, `hctf hb keepalive --timeout S`, `hctf hb tools` | `hctf/cli.py` | |

### Shadow worker flow
1. At the Single Solve launch (n==0, eligible lane, real GM, budget OK, < 2 live) a thread waits <= 45 s for the
   prewarmed VM, pushes the chal state (no timed dirs, files <= 4 MB), the prior solver, the prompt, and the artifact
   (<= 6 MB over the VPN; bigger ones are fetched on the VM through the inside GM), then starts
   `setsid nice -n 10 timeout 1500 claude -p ... --max-budget-usd <cap>` detached (Opus 4.7, same effort/tools/
   max-turns as local, same prompt + a "you are the shadow" note). nice keeps hb_timed's solver runs first on the CPU.
2. Every 5 s one SSH round-trip: alive?, the VM's confirmed.json, a CORRECT count, the solver's newest mtime.
   Confirmations merge into local `confirmed.json`/`submissions.jsonl` (via `record_remote_result`, under `chal_lock`)
   so the local worker, `_watch_ready` and the stop gate see them.
3. Once the single is CORRECT, the shadow's solver is pulled to `.run/shadow-dayNN/<chal>/solver` and verified locally
   (reproduces every confirmed answer). If the local worker isn't ready yet, `ready` is set under a shared lock with
   `_watch_ready`; the local worker ends (STOPPED_RC) and the timed modes start from the shadow's solver. If the local
   worker ends without a passing solver but the shadow has a verified one, it's adopted.
4. When the chain leaves the Single Solve the process group is killed, the cost (result line or per-message usage at
   Opus list price, `hctf/hbcost.py`) goes to the ledger, and the transcript lands in the mode dir as
   `worker-single-hbshadow-<tag>.log`.
Never in replays (the VM can only reach the real GM); never when `HCTF_AUTO_HOMEBASE=0`.

## Budget plan (60 credits/day, VM + AI share it)
| Item | Est. credits/day |
|---|---|
| VM armed at warm-up (~T-30 min) -> run -> ratchet (~T+45 min), keepalive + health metering | 2.5-3 |
| One rehearsal/replay window on Homebase (~1.5 h) | 3 |
| Shadow singles, script + binary (Opus 4.7, ~$1.5-4 each at list, cap $8) | 4-8 |
| Headroom: shadow relaunches, `--homebase` pool generalizes, calibration | ~45 |
VM_RESERVE (6) is always kept back so AI spend can't starve the VM's own uptime. The VM is NOT kept on 24/7 (48 credits
would leave 12 for AI); it idle-stops after the run, as before.

## Next levers (not built yet)
- Shadow **generalize** for timed failures on the slow lanes (transactional: run on the VM, adopt only if every case
  passes locally) -- the biggest remaining tail after the single.
- Shadow for **all lanes on a relaunch** (n>=1: the local worker already failed once; diversity is cheap insurance).
- Measure `HCTF_HB_CREDITS_PER_USD` (one UI read before/after); if credits are cheap per $, raise SHADOW_MAX/lanes.
- Post-run ratchet / speed-harden on Bedrock to keep local Claude limits for drop time.

## Warm timed-attempt daemon (2026-10-12, bcf3509)
Timed attempts on Homebase run in `hctf/hb_daemon.py` (one process per run, started at provisioning over one
persistent ssh stdio channel) instead of an ssh exec of `hb_timed.py` per attempt. Each solver dir gets a zygote
(`hctf/hb_zygote.py`) that ran the solver's top level once; every solve is a fork of it (12-51 ms vs 150-230 ms).
GM traffic from the daemon goes to the PUBLIC GM with this copy's bearer (sent over the ssh channel, kept in memory
only; 170 ms/call vs 232 ms via the inside proxy). The prepush warms the zygote before the first clock; hot-pushed
daemon code restarts it. Off switches: `HCTF_HB_DAEMON=0` (per-attempt ssh exec, as before), `HCTF_HB_PUBLIC_GM=0`
(inside proxy). Logs: `~/hw/.run/hb_daemon.log` (+ `.err`). Live 2026-10-12 on Day 8 (6/6 correct): solve phase 0.02 s
(was 0.13-0.18), HoF warmups TT 627 -> 411 ms (#26 -> #12), metadata TT 752 -> 409 ms (#41 -> #7), warmups M 685 -> 557 ms.
