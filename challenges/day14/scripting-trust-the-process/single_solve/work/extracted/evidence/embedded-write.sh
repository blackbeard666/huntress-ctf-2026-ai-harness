#!/usr/bin/env bash
# Huntress Script Triage -- inert static-analysis fixture (bash_linux)
readonly Material_883e8831='124,67,55,130,121,122,107,118,121,67,106,107,105,117,106,107,101,107,115,104,107,106,106,107,106,50,125,120,111,122,107,101,108,111,114,107,130,103,106,103,118,122,107,120,67,111,116,121,122,103,114,114,101,121,122,106,111,116,130,121,122,103,109,107,101,105,117,123,116,122,67,55,130,105,103,115,118,103,111,109,116,101,111,106,67,105,103,115,118,103,111,109,116,51,55,55,107,56,104,58,60,56,54,58,130,108,111,114,107,101,118,103,122,110,67,53,122,115,118,53,110,123,116,122,120,107,121,121,51,105,103,105,110,107,53,52,121,122,103,109,107,51,55,55,107,56,104,58,60,56,54,58'
readonly Codec_883e8831='decimal_comma|add_modulo_256|06'

Load_883e8831() {
  EnCoDeD_Bytes=()
  local IFS=','
  read -r -a EnCoDeD_Bytes <<< "${Material_883e8831}"
}

Decode_883e8831() {
  DeCoDeD_Bytes=()
  local InDeX
  for ((InDeX=0; InDeX<${#EnCoDeD_Bytes[@]}; InDeX++)); do
    DeCoDeD_Bytes+=("$(((EnCoDeD_Bytes[InDeX] - 6 + 256) % 256))")
  done
}

Recover_883e8831() {
  local -a EnCoDeD_Bytes DeCoDeD_Bytes
  local DeScRiPtOr_Text NeUtRaL PaSs InDeX
  NeUtRaL=$((19 * 7 - 133))
  Load_883e8831
  local decode_target=Decode_883e8831; "$decode_target"
  DeScRiPtOr_Text=''
  local octal character
  for InDeX in "${!DeCoDeD_Bytes[@]}"; do
    printf -v octal '%03o' "${DeCoDeD_Bytes[InDeX]}"
    printf -v character '%b' "\\$octal"
    DeScRiPtOr_Text+="$character"
  done
  printf '%s\n' "$DeScRiPtOr_Text"
}

Inspect_883e8831() { local recovered; recovered="$(Recover_883e8831)"; printf '%s\n' "$recovered"; }

Plan_883e8831() {
  local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
  descriptor="$(Inspect_883e8831)"
  local -a fields
  IFS='|' read -r -a fields <<< "$descriptor"
  for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
  local -a decoder=(base64 --decode) destination=(install -m 0600 /dev/stdin "$file_path")
  declare -p decoder destination
}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_883e8831; fi
