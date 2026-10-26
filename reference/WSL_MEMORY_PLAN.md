# WSL memory headroom — deferred plan (D26 post-mortem, not applied)

Status: **deferred by the user (10-26)**. Apply only if CPU and memory contention is still a factor after the
D26 software fixes (parallel live answer, niced single-duel racers, background baseline replays).

## Evidence (Day 26)
- Host: Windows, 15.7 GB RAM, 12 logical CPUs. WSL gets the default 50 % = **7.8 GB** (there's no `.wslconfig`).
- `bin/day.sh:158`: `MAXMB = MemTotal − 600 MB`, `HIGHMB = MAXMB − 700` → unit MemoryHigh **6.5 GB**, MemoryMax 7.2 GB.
- Day 26 run unit: MemoryPeak **6.81 GB** (≥ MemoryHigh). `[res]` high_events went from +111 to **+4076**
  (reclaim throttling of every process in the unit) between T+1:43 and the end. psi_mem some stayed ≤ 2 %, so most
  of the reclaim was page cache (358 MB binary Mastery download, case corpora). psi_cpu peaked at 72 % with load 28.
- Windows itself needs ~4-5 GB with the browser profile open.

## Proposal
1. Create `C:\Users\cavila\.wslconfig`:
   ```ini
   [wsl2]
   memory=11GB
   processors=12
   swap=4GB
   ```
   11 GB leaves ~4.7 GB for Windows. If Windows pages under the browser, drop to 10 GB.
2. Apply at a quiet time (not within 2 h of a drop, no day run / prebuild / rehearsal run active):
   `wsl --shutdown` from Windows. This kills every WSL process: Claude sessions, the hctf-vpn OpenVPN service
   (tun0), Homebase SSH masters, systemd user units.
3. After restart:
   - `sudo systemctl start hctf-vpn` (or let it auto-start) and check tun0.
   - Re-apply `sudo ip link set tun0 mtu 1200` if needed (see the homebase-mtu-pmtud memory).
   - Run `bash bin/preflight.sh`.
   - `free -m` should show ~11 GB; day.sh then derives MemoryHigh ≈ 9.7 GB automatically, so no code change is needed.
4. Optional: once Day 27/28 `[res]` lines show high_events ≈ 0, consider `HCTF_DUEL_EXTRA_MIN_AVAIL_GB` /
   `HCTF_ANSWER_FIRST_MIN_AVAIL_GB` unchanged. They gate on MemAvailable, which simply grows.

## Rollback
Delete `.wslconfig` (or set `memory=8GB`) and `wsl --shutdown`.

## Measure
Compare `[res]` high_events, psi_cpu, and per-lane go-text latency ("go text ready at +X s") for the day before and the
day after.
