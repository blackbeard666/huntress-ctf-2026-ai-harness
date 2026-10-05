#!/usr/bin/env bash
# hctf day launcher: pre-flight -> warm Homebase -> run the full parallel sweep, logging cleanly.
# Replaces the fragile inline `nohup hctf run ... &`. Writes .run/dayNN.log; prints the tail command.
#
# Usage:
#   bash bin/day.sh [DAY] [--scout N] [--local N] [--fg]
#     DAY        day number (default: inferred from today's date vs CTF day-1).
#     --scout N  TT scouting rounds (label-spelling insurance for hard lanes; default 0 / off).
#     --local N  local worker slots (default 5).
#     --fg       run in the foreground (default: background via setsid, survives this shell).
#
# Examples:
#   bash bin/day.sh                 # today's day, background
#   bash bin/day.sh 6 --scout 3     # day 6 with 3 scouting rounds
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/.." && pwd)"
cd "$ROOT" || exit 1
# shellcheck disable=SC1091
source bin/env.sh 2>/dev/null || true

CTF_DAY1="2026-10-03"
DAY=""; SCOUT=0; LOCAL=5; FG=0
while [ $# -gt 0 ]; do
  case "$1" in
    --scout) SCOUT="${2:-0}"; shift 2;;
    --local) LOCAL="${2:-5}"; shift 2;;
    --fg)    FG=1; shift;;
    *[0-9]*) DAY="$1"; shift;;
    *) echo "unknown arg: $1" >&2; shift;;
  esac
done
if [ -z "$DAY" ]; then
  DAY=$(( ( $(date +%s) - $(date -d "$CTF_DAY1" +%s) ) / 86400 + 1 ))
fi
printf -v DAYTAG 'day%02d' "$DAY"
LOG=".run/${DAYTAG}.log"
mkdir -p .run

echo "=== hctf $DAYTAG launcher ($(date '+%F %H:%M:%S %Z')) ==="

# 1) Pre-flight: abort only on a hard FAIL (GM/token). Warnings (Homebase/VPN) are non-blocking.
if ! bash bin/preflight.sh; then
  echo "ABORT: pre-flight reported a FAIL. Fix it, then re-run." >&2
  exit 1
fi

# 2) Warm the Homebase SSH ControlMaster so a tight timed window never pays a cold reconnect (~25s seen).
if ip route get 10.1.50.243 2>/dev/null | grep -q tun0; then
  timeout 30 hctf hb exec -- true >/dev/null 2>&1 && echo "[warm] Homebase SSH control channel established." \
    || echo "[warm] Homebase not reachable; run stays local-first (fine)."
fi

# 3) Launch the sweep.
RUN_ARGS=(run --day "$DAY" --local "$LOCAL")
[ "$SCOUT" -gt 0 ] && RUN_ARGS+=(--scout "$SCOUT") && echo "[scout] $SCOUT TT scouting round(s) enabled."

echo "[run] hctf ${RUN_ARGS[*]}  ->  $LOG"
# Post-run: ATT&CK generalization gate (coverage vs the confirmed role/scenario tables + reference).
POST="python3 -m lib.refs.coverage $DAY 2>&1 | sed 's/^/[attack-coverage] /'"
if [ "$FG" -eq 1 ]; then
  hctf "${RUN_ARGS[@]}" 2>&1 | tee "$LOG"
  rc=${PIPESTATUS[0]}
  echo "[done] run exited rc=$rc"; echo "=== ATT&CK coverage ($DAYTAG) ==="; eval "$POST" | tee -a "$LOG"
  exit "$rc"
else
  # setsid detaches into its own session so it survives the launching shell cleanly (nohup+& was fragile).
  setsid bash -c "cd '$ROOT' && source bin/env.sh && hctf ${RUN_ARGS[*]} > '$LOG' 2>&1; { echo; echo '=== ATT&CK coverage ($DAYTAG) ==='; $POST; } >> '$LOG' 2>&1" >/dev/null 2>&1 &
  echo "[run] launched in background (pid $!)."
  echo "      watch:  tail -f $LOG     board:  hctf dash | grep $DAYTAG     health:  hctf why <id>"
  echo "      the ATT&CK generalization report (python3 -m lib.refs.coverage $DAY) appends to $LOG when the run finishes."
fi
