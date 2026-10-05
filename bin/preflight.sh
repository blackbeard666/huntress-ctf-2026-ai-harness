#!/usr/bin/env bash
# hctf pre-flight: one command, run it before every daily drop.
# Checks (in order of how badly they bite): pairing-token validity + days-to-expiry, GM reachability,
# VPN tunnel, Homebase SSH + credits. Prints a PASS/WARN/FAIL line each and a final verdict.
# Exit 0 = go (no FAILs), 1 = a FAIL that will block solving.
#
# Run: cd ~/huntress-2026 && source bin/env.sh && preflight.sh   (or: bash bin/preflight.sh)
set -uo pipefail

# --- config you may need to update ---------------------------------------------------------------
TOKEN_EXPIRY="2026-11-01"   # UPDATE THIS after re-pairing (secrets/gm_pairing_token). See reference/RUNBOOK.md.
CTF_DAY1="2026-10-03"       # day 01 release date; daily cadence -> day 31 = CTF_DAY1 + 30 days.
CTF_LASTDAY=31
HB_HOST="10.1.50.243"
# -------------------------------------------------------------------------------------------------

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/.." && pwd)"
cd "$ROOT" || exit 1
# shellcheck disable=SC1091
source bin/env.sh 2>/dev/null || true

fails=0; warns=0
ok()   { printf '  [ OK ]  %s\n' "$*"; }
warn() { printf '  [WARN]  %s\n' "$*"; warns=$((warns+1)); }
fail() { printf '  [FAIL]  %s\n' "$*"; fails=$((fails+1)); }
hdr()  { printf '\n== %s ==\n' "$*"; }

today="$(date +%F)"
printf '=== hctf pre-flight  (%s %s) ===\n' "$today" "$(date +%Z)"

# 1) Pairing token --------------------------------------------------------------------------------
hdr "Pairing token (GM auth)"
if [ ! -s secrets/gm_pairing_token ]; then
  fail "secrets/gm_pairing_token missing or empty — GM access impossible. Re-pair (reference/RUNBOOK.md)."
else
  exp_epoch="$(date -d "$TOKEN_EXPIRY" +%s 2>/dev/null)"
  now_epoch="$(date +%s)"
  days_left=$(( (exp_epoch - now_epoch) / 86400 ))
  # projected final CTF day
  last_epoch="$(date -d "$CTF_DAY1 +$((CTF_LASTDAY-1)) days" +%s 2>/dev/null)"
  last_date="$(date -d "@$last_epoch" +%F 2>/dev/null)"
  if   [ "$days_left" -lt 0 ]; then fail "token EXPIRED ($TOKEN_EXPIRY). Re-pair now."
  elif [ "$exp_epoch" -lt "$last_epoch" ]; then
       warn "token expires $TOKEN_EXPIRY ($days_left d) — BEFORE the CTF's last day ($last_date). Re-pair before then or days 30-31 will fail."
  elif [ "$days_left" -le 5 ]; then warn "token expires in $days_left d ($TOKEN_EXPIRY) — re-pair soon."
  else ok "token present, expires $TOKEN_EXPIRY ($days_left days left; CTF ends ~$last_date)."
  fi
fi

# 2) GM reachability ------------------------------------------------------------------------------
hdr "Game Master (public GM via token)"
gm_out="$(timeout 40 hctf list 2>&1)"; gm_rc=$?
if [ "$gm_rc" -eq 0 ] && ! grep -qiE "traceback|unreachable|error" <<<"$gm_out"; then
  n="$(grep -cE '^D[0-9]' <<<"$gm_out" || true)"
  ok "GM reachable (hctf list rc=0; $n released challenge-modes listed)."
else
  fail "GM not reachable (rc=$gm_rc). First lines: $(head -2 <<<"$gm_out" | tr '\n' ' ')"
fi

# 3) VPN tunnel -----------------------------------------------------------------------------------
hdr "CTF VPN (for Homebase; GM does not need it)"
if ip -brief addr show tun0 >/dev/null 2>&1; then
  tun_ip="$(ip -brief addr show tun0 | awk '{print $3}')"
  if ip route get "$HB_HOST" 2>/dev/null | grep -q tun0; then
    ok "tun0 up ($tun_ip); route to $HB_HOST via tun0."
  else
    warn "tun0 up ($tun_ip) but no route to $HB_HOST via it. Restart: sudo systemctl restart hctf-vpn"
  fi
else
  svc="$(systemctl is-active hctf-vpn 2>/dev/null)"
  warn "tun0 DOWN (hctf-vpn service: ${svc:-unknown}). Homebase unreachable until up: sudo systemctl start hctf-vpn"
fi

# 4) Homebase SSH + credits -----------------------------------------------------------------------
hdr "Homebase (optional low-latency compute for tight timed windows)"
hb_out="$(timeout 35 hctf hb exec -- 'echo hb-ok' 2>&1)"
if grep -q hb-ok <<<"$hb_out"; then
  st="$(timeout 20 hctf hb status 2>&1 | tr -d ' \n')"
  ok "Homebase SSH works. status: ${st:0:120}"
else
  warn "Homebase SSH not answering (VM off, cold boot, or VPN down). Runs still work local-first; timed lanes lose the latency edge. Detail: $(head -1 <<<"$hb_out")"
fi

# verdict -----------------------------------------------------------------------------------------
printf '\n=== verdict: %d FAIL, %d WARN ===\n' "$fails" "$warns"
if [ "$fails" -gt 0 ]; then
  echo "NOT READY — resolve FAILs above before the drop."
  exit 1
fi
[ "$warns" -gt 0 ] && echo "READY (with warnings) — GM works; warnings above are non-blocking (Homebase/VPN are optional)."
[ "$warns" -eq 0 ] && echo "ALL GREEN — go."
exit 0
