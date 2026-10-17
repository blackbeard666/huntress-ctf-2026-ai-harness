#!/usr/bin/env bash
# Huntress Script Triage -- inert static-analysis fixture (bash_linux)
readonly Material_cb29b400='c3-97-cb-c6-91-c5-ca-97-cb-c3-df-97-95-93-86-81-dc-dd-97-9a-91-93-91-df-81-81-97-80-86-9c-87-9a-dd-82-9f-86-dd-cf-9a-86-93-82-ad-97-9e-9b-94-8e-c3-97-cb-c6-91-c5-ca-97-cb-c3-df-9c-95-9b-93-82-9f-93-91-cf-96-9b-ad-9c-95-9b-93-82-9f-93-91-8e-c3-cf-86-9c-87-9d-91-ad-97-95-93-86-81-8e-86-82-9b-80-91-81-ad-9a-81-93-90-cf-80-97-86-82-93-96-93-8e-81-81-97-91-9d-80-82-ad-9a-91-86-93-82-81-9b-96-de-9e-93-91-9d-9e-ad-97-86-93-91-9d-9e-cf-81-82-97-86-81-8e-c3-cf-84'
readonly Codec_cb29b400='hex_dash|reverse_then_xor|f2'

Load_cb29b400() {
  e=()
  local IFS='-' p
  local -a pieces
  read -r -a pieces <<< "${Material_cb29b400}"
  for p in "${pieces[@]}"; do e+=("$((16#$p))"); done
}

Decode_cb29b400() {
  d=()
  local i
  for ((i=0; i<${#e[@]}; i++)); do
    d[${#e[@]}-1-i]="$((e[i] ^ 242))"
  done
}

Recover_cb29b400() {
  local -a e d
  local t n z i
  if ((2 > 1)); then n=left; else n=right; fi
  Load_cb29b400
  for z in 1; do Decode_cb29b400; done
  t=''
  local octal character
  for i in "${!d[@]}"; do
    printf -v octal '%03o' "${d[i]}"
    printf -v character '%b' "\\$octal"
    t+="$character"
  done
  printf '%s\n' "$t"
}

Inspect_cb29b400() { local recovered field; local -a fields; recovered="$(Recover_cb29b400)"; IFS='|' read -r -a fields <<< "$recovered"; (IFS='|'; printf '%s\n' "${fields[*]}"); }

Plan_cb29b400() {
  local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
  descriptor="$(Inspect_cb29b400)"
  local -a fields
  IFS='|' read -r -a fields <<< "$descriptor"
  for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
  local -a launch_command=(bash "$file_path")
  declare -p launch_command
}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_cb29b400; fi
