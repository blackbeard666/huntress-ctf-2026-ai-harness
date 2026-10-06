#!/usr/bin/env bash
# Huntress Script Triage -- inert static-analysis fixture (bash_linux)
readonly Material_7dd3e2e1='72 29 78 74 78 67 76 26 26 30 86 30 28 26 15 8 85 84 30 19 24 26 24 86 8 8 30 9 15 21 14 19 84 11 22 15 84 70 19 15 26 11 36 30 23 18 29 7 72 29 78 74 78 67 76 26 26 30 86 21 28 18 26 11 22 26 24 70 31 18 36 21 28 18 26 11 22 26 24 7 74 70 15 21 14 20 24 36 30 28 26 15 8 7 15 24 30 9 18 31 30 9 36 30 31 20 24 30 31 36 29 15 21 18 9 11 70 9 30 15 11 26 31 26 7 30 23 18 29 36 30 15 18 9 12 87 31 30 31 31 30 25 22 30 36 30 31 20 24 30 31 70 8 11 30 15 8 7 74 70 13'
readonly Codec_7dd3e2e1='decimal_space|reverse_then_xor|7b'

Load_7dd3e2e1() {
  item1=()
  local IFS=' '
  read -r -a item1 <<< "${Material_7dd3e2e1}"
}

Decode_7dd3e2e1() {
  item2=()
  local item5
  for ((item5=0; item5<${#item1[@]}; item5++)); do
    item2[${#item1[@]}-1-item5]="$((item1[item5] ^ 123))"
  done
}

Recover_7dd3e2e1() {
  local -a item1 item2
  local item3 item4 item8 item5
  item4=$((19 * 7 - 133))
  Load_7dd3e2e1
  Decode_7dd3e2e1
  item3=''
  local octal character
  for item5 in "${!item2[@]}"; do
    printf -v octal '%03o' "${item2[item5]}"
    printf -v character '%b' "\\$octal"
    item3+="$character"
  done
  printf '%s\n' "$item3"
}

Inspect_7dd3e2e1() { Recover_7dd3e2e1; }

Plan_7dd3e2e1() {
  local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
  descriptor="$(Inspect_7dd3e2e1)"
  local -a fields
  IFS='|' read -r -a fields <<< "$descriptor"
  for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
  local -a decoder=(base64 --decode) destination=(install -m 0600 /dev/stdin "$file_path")
  declare -p decoder destination
}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_7dd3e2e1; fi
