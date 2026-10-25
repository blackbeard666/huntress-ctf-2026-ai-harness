#!/usr/bin/env bash

# Huntress Script Triage -- inert static-analysis fixture (bash_linux)

readonly Material_cebdd5ef='105:48:36:111:102:103:88:99:102:48:87:88:86:98:87:88:82:86:98:97:89:92:90:104:101:84:103:92:98:97:31:101:88:103:104:101:97:82:86:98:97:89:92:90:104:101:84:103:92:98:97:111:84:87:84:99:103:88:101:48:99:101:92:97:103:89:82:101:88:99:98:101:103:111:102:103:84:90:88:82:86:98:104:97:103:48:36:111:86:84:96:99:84:92:90:97:82:92:87:48:86:84:96:99:84:92:90:97:32:40:38:35:38:37:36:41:41:84:43:111:91:98:102:103:82:92:87:48:91:98:102:103:32:40:38:35:38:37:36:41:41:84:43'

readonly Codec_cebdd5ef='decimal_colon|subtract_modulo_256|0d'



Load_cebdd5ef() {

  stored_bytes=()

  local IFS=':'

  read -r -a stored_bytes <<< "${Material_cebdd5ef}"

}



Decode_cebdd5ef() {

  recovered_bytes=()

  local byte_index

  for ((byte_index=0; byte_index<${#stored_bytes[@]}; byte_index++)); do

    recovered_bytes+=("$(((stored_bytes[byte_index] + 13) % 256))")

  done

}



Recover_cebdd5ef() {

  local -a stored_bytes recovered_bytes

  local configuration_text harmless_value decode_pass byte_index

  local -a compass=(north south); harmless_value="$(IFS=:; printf '%s' "${compass[*]}")"

  Load_cebdd5ef

  if ! Decode_cebdd5ef; then return 71; fi

  configuration_text=''

  local octal character

  for byte_index in "${!recovered_bytes[@]}"; do

    printf -v octal '%03o' "${recovered_bytes[byte_index]}"

    printf -v character '%b' "\\$octal"

    configuration_text+="$character"

  done

  printf '%s\n' "$configuration_text"

}



Inspect_cebdd5ef() { Recover_cebdd5ef; }



Plan_cebdd5ef() {

  local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''

  descriptor="$(Inspect_cebdd5ef)"

  local -a fields

  IFS='|' read -r -a fields <<< "$descriptor"

  for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done

  local -a report_command=(printf '%s\n' "$campaign_id")

  declare -p report_command

}



if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_cebdd5ef; fi

