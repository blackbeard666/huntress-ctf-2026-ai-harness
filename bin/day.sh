#!/usr/bin/env bash
# hctf day launcher: pre-flight -> warm Homebase -> run the full parallel sweep, logging cleanly.
# Replaces the fragile inline `nohup hctf run ... &`. Writes .run/dayNN.log; prints the tail command.
#
# Usage:
#   bash bin/day.sh [DAY] [--wait] [--preflight] [--scout N] [--local N] [--effort LEVEL] [--fg]
#     DAY        day number (default: inferred from today's date vs CTF day-1).
#     --wait     arm-and-fire: do all prep NOW (pre-flight if stale, Homebase warm), then poll the GM every
#                ${HCTF_WAIT_POLL:-1}s and launch the INSTANT the day is listed -- nothing else runs at drop time.
#     --preflight force the pre-flight even if a passing one is fresh (default: skip when .run/preflight.ok is
#                younger than HCTF_PREFLIGHT_MAX_AGE s, default 6h -- never re-check at drop time).
#     --scout N  TT scouting rounds (label-spelling insurance for hard lanes; default 0 / off).
#     --local N  local worker slots (default 5).
#     --effort L global worker effort: low|medium|high|xhigh|max (default: $HCTF_WORKER_EFFORT or high).
#                Per-lane floors in hctf/workers.py LANE_EFFORT still raise script/binary to xhigh.
#     --fg       run in the foreground (default: background via setsid, survives this shell).
#
# Examples:
#   bash bin/day.sh 7 --wait        # T-2min: prep now, fire at the drop (the normal daily launch)
#   bash bin/day.sh                 # today's day, background
#   bash bin/day.sh 6 --scout 3     # day 6 with 3 scouting rounds
#   bash bin/day.sh 6 --effort xhigh  # day 6 with every worker at xhigh effort
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/.." && pwd)"
cd "$ROOT" || exit 1
# shellcheck disable=SC1091
source bin/env.sh 2>/dev/null || true

CTF_DAY1="2026-10-03"
DAY=""; SCOUT=0; LOCAL=5; FG=0; WAIT=0; FORCE_PF=0; EFFORT="${HCTF_WORKER_EFFORT:-high}"
while [ $# -gt 0 ]; do
  case "$1" in
    --scout) SCOUT="${2:-0}"; shift 2;;
    --local) LOCAL="${2:-5}"; shift 2;;
    --effort) EFFORT="${2:-high}"; shift 2;;
    --fg)    FG=1; shift;;
    --wait)  WAIT=1; shift;;
    --preflight) FORCE_PF=1; shift;;
    *[0-9]*) DAY="$1"; shift;;
    *) echo "unknown arg: $1" >&2; shift;;
  esac
done
if [ -z "$DAY" ]; then
  DAY=$(( ( $(date +%s) - $(date -d "$CTF_DAY1" +%s) ) / 86400 + 1 ))
fi
case "$EFFORT" in low|medium|high|xhigh|max) ;; *) echo "bad --effort: $EFFORT" >&2; exit 2;; esac
export HCTF_WORKER_EFFORT="$EFFORT"
printf -v DAYTAG 'day%02d' "$DAY"
LOG=".run/${DAYTAG}.log"
mkdir -p .run

echo "=== hctf $DAYTAG launcher ($(date '+%F %H:%M:%S %Z')) ==="

# 1) Pre-flight: abort only on a hard FAIL. SKIPPED when a passing pre-flight is fresh -- the checks belong at
#    warm-up time, never between the drop and the launch (Day 6 lost ~75s re-running them at 21:00).
pf_age=$(( $(date +%s) - $(cat .run/preflight.ok 2>/dev/null || echo 0) ))
if [ "$FORCE_PF" -eq 0 ] && [ "$pf_age" -lt "${HCTF_PREFLIGHT_MAX_AGE:-21600}" ]; then
  echo "[preflight] passed $((pf_age/60)) min ago -- skipping (force with --preflight)."
elif ! bash bin/preflight.sh; then
  echo "ABORT: pre-flight reported a FAIL. Fix it, then re-run." >&2
  exit 1
fi

# 2) Warm the Homebase SSH ControlMaster in the BACKGROUND (never blocks the launch; the run re-probes Homebase
#    itself before each tight window).
if [ "${HCTF_AUTO_HOMEBASE:-1}" != 0 ] && ip route get "${HCTF_HB_HOST:-10.1.50.243}" 2>/dev/null | grep -q "${HCTF_VPN_DEV:-tun0}"; then
  # Also provision + full code sync NOW (a freshly booted VM took ~25s of first sync inside the run, during which the
  # first timed attempts fell back to local -- main replay 2026-10-07); the run's own sync is then incremental.
  ( timeout 30 hctf hb exec -- true >/dev/null 2>&1 && echo "[warm] Homebase SSH control channel established." \
      && timeout 600 python3 -c "from hctf import workers; workers._provision(lambda m: print(m, flush=True))" \
      && echo "[warm] Homebase provisioned + code synced (run starts warm)." \
      || echo "[warm] Homebase not reachable yet; the run's health thread re-probes it every ${HCTF_HB_HEALTH_S:-5}s." ) &
fi

# 2b) --wait: everything above is done; now just poll for the drop and fire the instant it is listed.
if [ "$WAIT" -eq 1 ]; then
  echo "[wait] polling the GM every ${HCTF_WAIT_POLL:-1}s for day $DAY ..."
  until out="$(timeout 20 hctf list --day "$DAY" 2>&1)" && [ -n "$out" ] && ! grep -q "No released challenges" <<<"$out" \
        && grep -qE '^D[0-9]' <<<"$out"; do
    sleep "${HCTF_WAIT_POLL:-1}"
  done
  echo "[wait] day $DAY released at $(date '+%H:%M:%S') -- launching"
fi
if pgrep -f "hctf.cli run --day $DAY( |$)|hctf run --day $DAY( |$)" >/dev/null; then
  echo "[run] a day $DAY run is already in progress -- not launching a second one." >&2
  exit 0
fi

# 3) Launch the sweep.
RUN_ARGS=(run --day "$DAY" --local "$LOCAL")
[ "$SCOUT" -gt 0 ] && RUN_ARGS+=(--scout "$SCOUT") && echo "[scout] $SCOUT TT scouting round(s) enabled."

echo "[run] hctf ${RUN_ARGS[*]}  ->  $LOG"
EFFORT_LINE="[effort] global=$HCTF_WORKER_EFFORT; per lane: $(python3 -c 'import hctf.workers as w; print(" ".join(f"{l}={w.worker_effort(l)}" for l in ("warmups","metadata-forensics","script-analysis","binary-reverse-engineering","mobile-android")))' 2>/dev/null)"
echo "$EFFORT_LINE"
# Post-run: ATT&CK generalization gate (coverage vs the confirmed role/scenario tables + reference).
# + toolchain gap review: every preferred tool triage found missing (installed at runtime / no recipe -> add one).
POST="python3 -m lib.refs.coverage $DAY 2>&1 | sed 's/^/[attack-coverage] /'; python3 -m hctf.toolchain report --day $DAY 2>&1 | sed 's/^/[tool-gaps] /'"
if [ "$FG" -eq 1 ]; then
  echo "$EFFORT_LINE" > "$LOG"
  hctf "${RUN_ARGS[@]}" 2>&1 | tee -a "$LOG"
  rc=${PIPESTATUS[0]}
  echo "[done] run exited rc=$rc"; echo "=== ATT&CK coverage ($DAYTAG) ==="; eval "$POST" | tee -a "$LOG"
  exit "$rc"
else
  # setsid detaches into its own session so it survives the launching shell cleanly (nohup+& was fragile).
  setsid bash -c "cd '$ROOT' && source bin/env.sh && echo '$EFFORT_LINE' > '$LOG'; hctf ${RUN_ARGS[*]} >> '$LOG' 2>&1; { echo; echo '=== ATT&CK coverage ($DAYTAG) ==='; $POST; } >> '$LOG' 2>&1" >/dev/null 2>&1 &
  echo "[run] launched in background (pid $!)."
  echo "      watch:  tail -f $LOG     board:  hctf dash | grep $DAYTAG     health:  hctf why <id>"
  echo "      the ATT&CK generalization report (python3 -m lib.refs.coverage $DAY) appends to $LOG when the run finishes."
fi
