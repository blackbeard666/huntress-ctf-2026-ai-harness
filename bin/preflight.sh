#!/usr/bin/env bash
# hctf pre-flight: one command, run it before every daily drop.
# Checks (in order of how badly they bite): pairing-token validity + days-to-expiry, GM reachability,
# VPN tunnel, Homebase SSH + credits. Prints a PASS/WARN/FAIL line each and a final verdict.
# Exit 0 = go (no FAILs), 1 = a FAIL that will block solving.
#
# Run: cd ~/huntress-2026 && source bin/env.sh && preflight.sh   (or: bash bin/preflight.sh)
#   --fix   also kill (taskkill) any Windows openvpn.exe connected with our VPN profile (see check 3b).
# A passing run writes .run/preflight.ok (epoch); bin/day.sh skips its own pre-flight while that is fresh, so the
# drop-time launch never re-runs these checks.
set -uo pipefail
FIX=0; [ "${1:-}" = "--fix" ] && FIX=1

# --- config you may need to update ---------------------------------------------------------------
TOKEN_EXPIRY="2026-11-01"   # UPDATE THIS after re-pairing (secrets/gm_pairing_token). See reference/RUNBOOK.md.
CTF_DAY1="2026-10-03"       # day 01 release date; daily cadence -> day 31 = CTF_DAY1 + 30 days.
CTF_LASTDAY=31
HB_HOST="${HCTF_HB_HOST:-10.1.50.243}"; VPN_DEV="${HCTF_VPN_DEV:-tun0}"
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
if ip -brief addr show $VPN_DEV >/dev/null 2>&1; then
  tun_ip="$(ip -brief addr show $VPN_DEV | awk '{print $3}')"
  if ip route get "$HB_HOST" 2>/dev/null | grep -q $VPN_DEV; then
    ok "$VPN_DEV up ($tun_ip); route to $HB_HOST via $VPN_DEV."
  else
    warn "$VPN_DEV up ($tun_ip) but no route to $HB_HOST via it. Restart: sudo systemctl restart hctf-vpn"
  fi
else
  svc="$(systemctl is-active hctf-vpn 2>/dev/null)"
  warn "$VPN_DEV DOWN (hctf-vpn service: ${svc:-unknown}). Homebase unreachable until up: sudo systemctl start hctf-vpn"
fi

# 3b) Duplicate VPN client ------------------------------------------------------------------------
# The CourseStack server keeps ONE session per profile. If a Windows openvpn.exe (GUI-launched or command-line) is
# connected with the same profile, it and our WSL tunnel evict each other every ~4 min (~60s dead each: "[server]
# Inactivity timeout"), and timed attempts that land in a gap fall back to slow local and EXPIRE (Day 6). Blocking.
# Our VPN is command-line only (the hctf-vpn systemd unit in WSL); a Windows client is never needed.
OVPN="${HCTF_OVPN:-$(ls secrets/*.ovpn 2>/dev/null | head -1)}"   # this copy's profile (main: huntress-ctf-2026-ai-arena, alt: alt)
WIN_TASKLIST=/mnt/c/Windows/System32/tasklist.exe
WIN_TASKKILL=/mnt/c/Windows/System32/taskkill.exe
WIN_PS=/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe
if [ -x "$WIN_TASKLIST" ] && timeout 10 "$WIN_TASKLIST" 2>/dev/null | grep -qi '^openvpn\.exe'; then
  ours="$(md5sum "$OVPN" 2>/dev/null | cut -d' ' -f1)"
  # "<pid>|<commandline>" per Windows openvpn.exe
  procs="$(timeout 20 "$WIN_PS" -NoProfile -Command "Get-CimInstance Win32_Process -Filter \"name='openvpn.exe'\" | ForEach-Object { '' + \$_.ProcessId + '|' + \$_.CommandLine }" 2>/dev/null | tr -d '\r')"
  dup_pids=""
  while IFS='|' read -r pid cmd; do
    [ -z "$pid" ] && continue
    c="$(grep -oE -- '--config +"?[^"]+\.ovpn' <<<"$cmd" | sed -E 's/--config +"?//' | head -1)"
    [ -z "$c" ] && continue
    cands=()
    if [[ "$c" =~ ^[A-Za-z]: ]]; then cands=("$(wslpath -u "$c" 2>/dev/null)")   # absolute Windows path
    else for d in /mnt/c/Users/*/OpenVPN/config "/mnt/c/Program Files/OpenVPN/config"; do cands+=("$d/$c" "$d/${c%.ovpn}/$c"); done
    fi
    for f in "${cands[@]}"; do
      [ -f "$f" ] && [ "$(md5sum "$f" | cut -d' ' -f1)" = "$ours" ] && { dup_pids="$dup_pids $pid"; break; }
    done
  done <<<"$procs"
  dup_pids="${dup_pids# }"
  if [ -n "$dup_pids" ]; then
    if [ "$FIX" -eq 1 ]; then
      for pid in $dup_pids; do timeout 10 "$WIN_TASKKILL" /PID "$pid" /T /F >/dev/null 2>&1; done
      sleep 1
      left=""
      for pid in $dup_pids; do timeout 10 "$WIN_TASKLIST" /FI "PID eq $pid" 2>/dev/null | grep -qi openvpn && left="$left $pid"; done
      if [ -n "$left" ]; then
        fail "Windows openvpn.exe on OUR profile still running after --fix (PID$left). Kill it: taskkill.exe /PID <pid> /F"
      else
        ok "Windows openvpn.exe on our profile (PID $dup_pids) killed (--fix); WSL owns the session now."
      fi
    else
      fail "Windows openvpn.exe (PID $dup_pids) is connected with OUR profile: it evicts $VPN_DEV every ~4 min. Fix: bash bin/preflight.sh --fix"
    fi
  else
    ok "Windows openvpn.exe is running but not on our profile (no session fight)."
  fi
else
  ok "no Windows openvpn.exe on our profile."
fi
# Flap detector (catches a duplicate on ANOTHER machine too): >=2 inactivity restarts in 15 min.
flaps="$(journalctl -u "${HCTF_VPN_UNIT:-hctf-vpn}" --since '-15 min' --no-pager 2>/dev/null | grep -c 'Inactivity timeout' || true)"
if [ "${flaps:-0}" -ge 2 ]; then
  warn "${HCTF_VPN_UNIT:-hctf-vpn} restarted $flaps times in 15 min (session fight? another client on this profile, e.g. a 2nd machine)."
fi

# 3c) Worker sandbox: the venv + solver deps must be usable INSIDE the bwrap sandbox (rehearsal replays silently lost
# pyzipper/rizin when .venv was a symlink into a masked tree -- 25-30 s per worker, and AES zips decoded to nothing).
hdr "Worker sandbox"
sb_out="$(timeout 30 python3 -c "
import subprocess, sys; sys.path.insert(0, '.')
from hctf import workers
cmd = workers.sandboxed(['$ROOT/.venv/bin/python', '-c', 'import pyzipper, elftools, pefile, capstone; print(\"sandbox-ok\")'])
r = subprocess.run(cmd, capture_output=True, text=True, timeout=25); print(r.stdout.strip() or r.stderr.strip()[-200:])
" 2>&1)"
if grep -q sandbox-ok <<<"$sb_out"; then ok "workers' sandbox has the venv + solver deps (pyzipper, pyelftools, pefile, capstone)."
else fail "worker sandbox can't import solver deps: $(tail -1 <<<"$sb_out")"; fi

# 3c2) Claude auth for workers: Day 1, six single workers died within 50 s on "OAuth session expired and could not be
# refreshed" and nothing flagged it. Check the refresh token's expiry against the CTF's last day, then one live turn
# (haiku, ~1 s, fractions of a cent) proves the refresh works. HCTF_PREFLIGHT_NO_LLM=1 skips the live turn.
hdr "Claude worker auth"
ca_out="$(python3 - "$CTF_DAY1" "$CTF_LASTDAY" <<'PY' 2>&1
import datetime, json, sys, time
from pathlib import Path
day1, last = sys.argv[1], int(sys.argv[2])
end = datetime.datetime.fromisoformat(day1) + datetime.timedelta(days=last)
try:
    o = json.load(open(Path.home() / ".claude/.credentials.json"))["claudeAiOauth"]
except Exception as e:
    print(f"WARN no OAuth credentials file ({e.__class__.__name__}); workers may use an API key"); sys.exit()
r = (o.get("refreshTokenExpiresAt") or 0) / 1000
if not r:
    print("WARN credentials have no refreshTokenExpiresAt; expiry unknown"); sys.exit()
left = (r - time.time()) / 86400
when = datetime.datetime.fromtimestamp(r).strftime("%Y-%m-%d %H:%M")
if left <= 0:
    print(f"FAIL Claude login EXPIRED ({when}): run `claude auth login`")
elif r < end.timestamp():
    print(f"WARN Claude login expires {when} ({left:.1f} d) -- BEFORE the CTF's last day; `claude auth login` again before then")
else:
    print(f"OK Claude login valid until {when} ({left:.0f} d)")
PY
)"
case "$ca_out" in OK*) ok "${ca_out#OK }";; WARN*) warn "${ca_out#WARN }";; *) fail "${ca_out#FAIL }";; esac
if [ "${HCTF_PREFLIGHT_NO_LLM:-0}" != 1 ]; then
  smoke="$(timeout 90 claude -p "Reply with exactly: OK" --max-turns 1 --model claude-haiku-5-5 --strict-mcp-config \
           --output-format json 2>&1)"
  if python3 -c 'import json,sys; d=json.loads(sys.argv[1]); sys.exit(0 if not d.get("is_error") else 1)' "$smoke" 2>/dev/null; then
    ok "live worker-auth turn succeeded (claude -p)."
  else
    fail "claude -p failed -- workers can't start: $(tail -c 220 <<<"$smoke" | tr '\n' ' ')  (fix: claude auth login)"
  fi
fi

# 3d) Lane analysis tools (workers call these via their lane skills; missing ones push them into hand-rolled Python).
hdr "Lane tools"
miss=""
for t in file xxd strings binwalk 7z readelf objdump nm c++filt rizin rabin2 analyzeHeadless upx ilspycmd GoReSym rustfilt \
         javap jadx apktool aapt apksigner d2j-dex2jar exiftool pdfinfo qpdf mutool pdf-parser pdfid pngcheck zsteg steghide \
         binwalk foremost mediainfo sqlite3 yara box-js js-beautify webcrack node pwsh; do
  command -v "$t" >/dev/null 2>&1 || miss="$miss $t"
done
if [ -z "$miss" ]; then ok "all lane tools on PATH (binary, metadata, mobile, script, warmups)."
else warn "missing lane tools:$miss  (install: setup/install_tools.sh + apt list at its top)"; fi
# Toolchain tools (setup/tools/<tool>.sh recipes; triage installs a missing one at runtime) + unresolved gaps from
# earlier runs (`hctf tool-gaps`): a gap with no recipe means a weaker fallback on the next drop -- add the recipe.
tc_miss=""
for r in setup/tools/*.sh; do t=$(basename "$r" .sh); [ "$t" = _lib ] && continue; PATH="$ROOT/bin:$ROOT/.venv/bin:$PATH" command -v "$t" >/dev/null || tc_miss="$tc_miss $t"; done
if [ -z "$tc_miss" ]; then ok "toolchain tools from setup/tools/ recipes all installed."
else warn "toolchain tools not installed yet:$tc_miss (triage installs them at runtime; or now: bash setup/tools/<tool>.sh)"; fi
gaps=$(python3 -m hctf.toolchain report 2>/dev/null | grep -c -- '-> ' || true)
if [ "${gaps:-0}" -gt 0 ]; then warn "$gaps unresolved toolchain gap(s) from earlier runs: hctf tool-gaps"; else ok "no unresolved toolchain gaps (hctf tool-gaps)."; fi
if python3 -c "import chepy, lib.codec" >/dev/null 2>&1; then ok "triage decoders: chepy + lib.codec importable."
else warn "triage decoders missing (chepy or lib.codec): run setup/install_tools.sh -- script triage won't decode literals"; fi

# 4) Homebase SSH + credits -----------------------------------------------------------------------
hdr "Homebase (optional low-latency compute for tight timed windows)"
if [ "${HCTF_AUTO_HOMEBASE:-1}" = 0 ]; then
  ok "Homebase disabled (HCTF_AUTO_HOMEBASE=0): timed attempts run locally; skipping the SSH check."
  hb_out=skip
else
  hb_out="$(timeout 35 hctf hb exec -- 'echo hb-ok' 2>&1)"
fi
if [ "$hb_out" = skip ]; then :
elif grep -q hb-ok <<<"$hb_out"; then
  st="$(timeout 20 hctf hb status 2>&1 | tr -d ' \n')"
  ok "Homebase SSH works. status: ${st:0:120}"
  # Bedrock shadow workers (hctf/hbshadow.py): the VM's instance role (free STS call, no model tokens) + the
  # heavy toolchain in ~/hbtools (setup/homebase_tools.sh) + today's credit ledger.
  hbx="$(timeout 40 hctf hb exec -- 'timeout 20 aws sts get-caller-identity --query Arn --output text 2>&1 | grep -o "assumed-role/[A-Za-z0-9]*"; command -v claude >/dev/null && echo claude-ok; for t in java jadx apktool analyzeHeadless rizin ilspycmd exiftool; do [ -x ~/hbtools/bin/$t ] || echo "nohbtool:$t"; done' 2>&1)"
  if grep -q 'assumed-role/EC2BedrockInvoke' <<<"$hbx" && grep -q claude-ok <<<"$hbx"; then
    ok "Homebase Bedrock role + Claude Code present (shadow workers: lanes ${HCTF_HB_SHADOW_LANES:-script-analysis,binary-reverse-engineering}; HCTF_HB_SHADOW=${HCTF_HB_SHADOW:-0} (opt-in))"
  else
    warn "Homebase Bedrock role/Claude Code not confirmed (shadow workers will fail to launch; local workers unaffected): $(head -2 <<<"$hbx" | tr '\n' ' ')"
  fi
  hbmiss="$(grep -o 'nohbtool:[A-Za-z]*' <<<"$hbx" | cut -d: -f2 | tr '\n' ' ')"
  if [ -z "$hbmiss" ]; then ok "Homebase toolchain (~/hbtools) complete."
  else warn "Homebase toolchain missing: $hbmiss -> hctf hb tools   (shadow workers fall back to python libs)"; fi
  bud="$(timeout 30 hctf hb budget 2>&1 | tail -1)"
  left="$(grep -o '[0-9.]* left' <<<"$bud" | cut -d' ' -f1)"
  if [ -n "$left" ] && awk "BEGIN{exit !($left < 15)}"; then warn "$bud (shadows stop when the day's budget runs low)"
  else ok "${bud:-credit ledger unreadable}"; fi
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
mkdir -p .run && date +%s > .run/preflight.ok
exit 0
