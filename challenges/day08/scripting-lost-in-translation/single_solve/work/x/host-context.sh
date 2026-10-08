#!/usr/bin/env bash
# Huntress Script Triage -- inert static-analysis fixture (bash_linux)
readonly Material_6a2ba9ec='8c:53:47:92:89:8a:7b:86:89:53:7a:7b:79:85:7a:7b:75:79:85:84:7c:7f:7d:8b:88:77:8a:7f:85:84:42:88:7b:8a:8b:88:84:75:79:85:84:7c:7f:7d:8b:88:77:8a:7f:85:84:92:77:7a:77:86:8a:7b:88:53:88:7b:77:7a:85:84:82:8f:75:79:85:84:7c:7f:7d:8b:88:77:8a:7f:85:84:92:89:8a:77:7d:7b:75:79:85:8b:84:8a:53:47:92:79:77:83:86:77:7f:7d:84:75:7f:7a:53:79:77:83:86:77:7f:7d:84:43:4b:4b:48:4c:49:7a:4e:49:4b:4f:92:7e:85:89:8a:75:7f:7a:53:7e:85:89:8a:43:4b:4b:48:4c:49:7a:4e:49:4b:4f'
readonly Codec_6a2ba9ec='hex_colon|add_modulo_256|16'

Load_6a2ba9ec() {
  EnCoDeD_Bytes=()
  local IFS=':' PaRt
  local -a pieces
  read -r -a pieces <<< "${Material_6a2ba9ec}"
  for PaRt in "${pieces[@]}"; do EnCoDeD_Bytes+=("$((16#$PaRt))"); done
}

Decode_6a2ba9ec() {
  DeCoDeD_Bytes=()
  local InDeX
  for ((InDeX=0; InDeX<${#EnCoDeD_Bytes[@]}; InDeX++)); do
    DeCoDeD_Bytes+=("$(((EnCoDeD_Bytes[InDeX] - 22 + 256) % 256))")
  done
}

Recover_6a2ba9ec() {
  local -a EnCoDeD_Bytes DeCoDeD_Bytes
  local DeScRiPtOr_Text NeUtRaL PaSs InDeX
  local -a compass=(north south); NeUtRaL="$(IFS=:; printf '%s' "${compass[*]}")"
  Load_6a2ba9ec
  PaSs=0; while ((PaSs < 1)); do Decode_6a2ba9ec; ((PaSs+=1)); done
  DeScRiPtOr_Text=''
  local octal character
  for InDeX in "${!DeCoDeD_Bytes[@]}"; do
    printf -v octal '%03o' "${DeCoDeD_Bytes[InDeX]}"
    printf -v character '%b' "\\$octal"
    DeScRiPtOr_Text+="$character"
  done
  printf '%s\n' "$DeScRiPtOr_Text"
}

Inspect_6a2ba9ec() { local recovered field; local -a fields; recovered="$(Recover_6a2ba9ec)"; IFS='|' read -r -a fields <<< "$recovered"; (IFS='|'; printf '%s\n' "${fields[*]}"); }

Plan_6a2ba9ec() {
  local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
  descriptor="$(Inspect_6a2ba9ec)"
  local -a fields
  IFS='|' read -r -a fields <<< "$descriptor"
  for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
  local -a report_command=(printf '%s\n' "$campaign_id")
  declare -p report_command
}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_6a2ba9ec; fi
