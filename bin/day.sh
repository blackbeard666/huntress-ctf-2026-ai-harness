#!/usr/bin/env bash
# hctf day launcher: pre-flight -> warm Homebase -> run the full parallel sweep, logging cleanly.
# Replaces the fragile inline `nohup hctf run ... &`. Writes .run/dayNN.log; prints the tail command.
#
# Usage:
#   bash bin/day.sh [DAY] [--wait] [--preflight] [--scout N] [--local N] [--effort LEVEL] [--fg]
#     DAY        day number (default: today's US-Eastern date vs CTF day-1 = 2026-10-01, i.e. day N = October N ET).
#     --wait     arm-and-fire: do all prep NOW (pre-flight if stale, Homebase warm), then start the run, which polls
#                the GM in-process (`hctf run --wait-release`) and launches the INSTANT the day is listed.
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

# Day N is released on October N at 09:00 ET (verified D20 = 10-20, D21 = 10-21; the old 10-03 was 2 days stale and a
# bare `day.sh --wait` armed the WRONG day). The default is counted on the US-Eastern calendar, so an evening (Manila)
# arm before the drop and an after-midnight Manila relaunch both name the day the GM is (about to be) serving.
CTF_DAY1="2026-10-01"
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
  et_today="$(TZ=America/New_York date +%F)"
  DAY=$(( ( $(date -u -d "$et_today" +%s) - $(date -u -d "$CTF_DAY1" +%s) ) / 86400 + 1 ))
  echo "[day] no day given: day $DAY (US-Eastern date $et_today; day 1 = $CTF_DAY1)"
fi
case "$EFFORT" in low|medium|high|xhigh|max) ;; *) echo "bad --effort: $EFFORT" >&2; exit 2;; esac
export HCTF_WORKER_EFFORT="$EFFORT"
printf -v DAYTAG 'day%02d' "$DAY"
LOG=".run/${DAYTAG}.log"
mkdir -p .run
# A relaunch of the same day keeps the previous run's log (D23 alt: run 3 overwrote run 2's -- its timeline had to be
# rebuilt from submissions.jsonl): .run/dayNN.log -> .run/dayNN-<its mtime>.log, the new run writes a fresh one.
if [ -s "$LOG" ]; then
  KEEP=".run/${DAYTAG}-$(date -r "$LOG" +%Y%m%d-%H%M%S).log"
  mv "$LOG" "$KEEP" && echo "[log] previous $LOG kept as $KEEP"
fi

echo "=== hctf $DAYTAG launcher ($(date '+%F %H:%M:%S %Z')) ==="

# 0) An off-peak `hctf prebuild` batch (launched after the last run's ratchet; deadline 30 min before the drop) must
#    never share the box with a run: stop it and restore its lib/ snapshot. Offline + instant when none is running.
if [ "${HCTF_PREBUILD_STOP:-1}" != 0 ] && { [ -e .run/prebuild.lock ] || [ -d .run/prebuild-snapshot ] \
     || pgrep -f "hctf.cli prebuild|hctf prebuild" >/dev/null; }; then
  timeout 60 python3 -m hctf.cli prebuild --stop 2>&1 | sed 's/^/[prebuild] /'
fi
# 0b) ...and ANOTHER harness copy on this box (alt / a worktree / a replay copy) must not share the CPU either (10-22:
#     an rehearsal validation run beside main's `prebuild --parallel` hit load 37-50; every timing invalid). The `prebuild
#     --stop` above only reaches THIS copy (it keeps processes whose cwd is this root): stop the other copies' prebuilds
#     inside THEIR roots (prebuild is always preemptible). Another copy's RUN is never stopped from here and never
#     blocks a live launch: a loud WARNING only (and the pre-flight below runs with HCTF_SHARED_HOST=1 -> WARN, not FAIL).
if [ -f "$ROOT/hctf/hostguard.py" ]; then
  if [ "${HCTF_PREBUILD_STOP:-1}" != 0 ]; then
    timeout 300 python3 -m hctf.hostguard stop-other-prebuilds --root "$ROOT" 2>&1 | sed 's/^/[hostguard] /'
  fi
  while IFS= read -r hg_line; do
    echo "WARNING: another harness copy is busy on this host -- timings are invalid while two copies share the CPU: ${hg_line#OTHER }" >&2
  done < <(timeout 30 python3 -m hctf.hostguard check --root "$ROOT" 2>/dev/null | grep '^OTHER ' || true)
fi

# 1) Pre-flight: abort only on a hard FAIL. SKIPPED when a passing pre-flight is fresh -- the checks belong at
#    warm-up time, never between the drop and the launch (Day 6 lost ~75s re-running them at 21:00).
pf_age=$(( $(date +%s) - $(cat .run/preflight.ok 2>/dev/null || echo 0) ))
if [ "$FORCE_PF" -eq 0 ] && [ "$pf_age" -lt "${HCTF_PREFLIGHT_MAX_AGE:-21600}" ]; then
  echo "[preflight] passed $((pf_age/60)) min ago -- skipping (force with --preflight)."
elif ! HCTF_SHARED_HOST=1 bash bin/preflight.sh; then   # another copy busy = WARN here (0b warned): never block a launch
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

# 2a) Homebase while armed: the heavy toolchain for the Bedrock shadow workers (only when they are on) + the credit line.
if [ "${HCTF_AUTO_HOMEBASE:-1}" != 0 ] && ip route get "${HCTF_HB_HOST:-10.1.50.243}" 2>/dev/null | grep -q "${HCTF_VPN_DEV:-tun0}"; then
  # Only when shadows are on: a cold install (JDK/Ghidra) loads the 2-vCPU VM for minutes -- during the run's first
  # Homebase-routed timed windows -- and nothing but the shadow workers uses ~/hbtools.
  if [ "${HCTF_HB_SHADOW:-0}" = 1 ]; then
    ( timeout 1800 hctf hb tools >/dev/null 2>&1 && echo "[warm] Homebase toolchain (~/hbtools) ready." \
        || echo "[warm] Homebase toolchain incomplete (shadow workers fall back to python libs): hctf hb tools" ) &
  fi
  # informational only: in the BACKGROUND (it is an SSH round trip, up to 30 s on a flapping VPN, before the run starts)
  ( echo "[credits] $(timeout 30 hctf hb budget 2>/dev/null | tail -1)" ) &
fi

# 2b) --wait: the run starts NOW and waits for the drop itself (`hctf run --wait-release`: in-process GM polling over
#     warm connections, the poll's list feeds the launch). Its Homebase health probe (every ${HCTF_HB_HEALTH_S:-5}s)
#     keeps the VM active + metered while armed -- the separate `hctf hb keepalive` died silently while armed on D9.
#     D9 with the shell loop: drop seen 21:00:03, first GM start stamped 3-5 s later (python start + a second list).
if [ "$WAIT" -eq 1 ]; then
  echo "[wait] armed: the run polls the GM in-process for day $DAY (every ${HCTF_RELEASE_POLL:-0.3}s + call time)"
fi
if pgrep -f "hctf.cli run --day $DAY( |$)|hctf run --day $DAY( |$)" >/dev/null \
   || { [ -f "$ROOT/.run/$DAYTAG.unit" ] && systemctl --user is-active --quiet "$(cat "$ROOT/.run/$DAYTAG.unit")" 2>/dev/null; }; then
  echo "[run] a day $DAY run is already in progress -- not launching a second one." >&2
  exit 0
fi

# 3) Launch the sweep.
RUN_ARGS=(run --day "$DAY" --local "$LOCAL")
[ "$WAIT" -eq 1 ] && RUN_ARGS+=(--wait-release)
[ "$SCOUT" -gt 0 ] && RUN_ARGS+=(--scout "$SCOUT") && echo "[scout] $SCOUT TT scouting round(s) enabled."

echo "[run] hctf ${RUN_ARGS[*]}  ->  $LOG"
EFFORT_LINE="[effort] global=$HCTF_WORKER_EFFORT; per lane: $(python3 -c 'import hctf.workers as w; print(" ".join(f"{l}={w.worker_effort(l)}" for l in ("warmups","metadata-forensics","script-analysis","binary-reverse-engineering","mobile-android","web")))' 2>/dev/null)"
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
  PIDF="$ROOT/.run/$DAYTAG.pid"
  SCRIPT="cd '$ROOT' && source bin/env.sh && echo \$\$ > '$PIDF' && echo '$EFFORT_LINE' > '$LOG'; hctf ${RUN_ARGS[*]} >> '$LOG' 2>&1; { echo; echo \"\$(date +%H:%M:%S) [postrun] coverage start\"; echo '=== ATT&CK coverage ($DAYTAG) ==='; $POST; echo \"\$(date +%H:%M:%S) post-run finished\"; } >> '$LOG' 2>&1"
  if command -v systemd-run >/dev/null && systemctl --user is-system-running 2>/dev/null | grep -qE 'running|degraded' \
     && [ "${HCTF_RUN_SYSTEMD:-1}" != "0" ]; then
    # A transient USER unit (linger on: preflight): outside this terminal / Claude session, and memory-capped so a
    # runaway fan-out is OOM-killed INSIDE the unit (solver forks first: oom_score_adj 300/800) -- D16: the kernel
    # OOM killer took WSL's init with it and the post-run never finished.
    MEMKB=$(awk '/^MemTotal/{print $2}' /proc/meminfo)
    MAXMB=$(( MEMKB / 1024 - ${HCTF_RUN_MEM_RESERVE_MB:-600} )); HIGHMB=$(( MAXMB - 700 ))
    UNIT="hctf-$DAYTAG-$(date +%H%M%S)"
    # a user unit does NOT inherit this shell's environment: carry every HCTF_* / HUNTRESS_* override over explicitly
    SETENV=()
    while IFS= read -r kv; do SETENV+=(--setenv="$kv"); done < <(env | grep -E '^(HCTF_|HUNTRESS_)[A-Za-z0-9_]*=' || true)
    # the script goes to a FILE: systemd expands `$` in a unit's command line ($$ -> $, $(date) mangled)
    printf '%s\n' "$SCRIPT" > "$ROOT/.run/$DAYTAG.unit.sh"
    systemd-run --user --collect --unit "$UNIT" --working-directory "$ROOT" -p MemoryHigh="${HIGHMB}M" \
      -p MemoryMax="${MAXMB}M" "${SETENV[@]}" bash -l "$ROOT/.run/$DAYTAG.unit.sh" >/dev/null 2>&1
    echo "$UNIT" > "$ROOT/.run/$DAYTAG.unit"
    echo "[run] launched as systemd user unit $UNIT (MemoryHigh ${HIGHMB}M, MemoryMax ${MAXMB}M; pid in $PIDF)."
    echo "      status:  systemctl --user status $UNIT"
  else
    # setsid detaches into its own session so it survives the launching shell cleanly (nohup+& was fragile).
    setsid bash -c "$SCRIPT" >/dev/null 2>&1 &
    echo "[run] launched in background (pid $!; no user systemd -- not memory-capped)."
  fi
  echo "      watch:  hctf feed --day $DAY (follows the post-run too)     board:  hctf dash | grep $DAYTAG"
  echo "      the ATT&CK generalization report (python3 -m lib.refs.coverage $DAY) appends to $LOG when the run finishes."
fi
