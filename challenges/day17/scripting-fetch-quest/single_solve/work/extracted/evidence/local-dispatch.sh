#!/usr/bin/env bash

# Huntress Script Triage -- inert static-analysis fixture (bash_linux)

readonly Material_3754a747='86:d4:d1:d1:80:8d:d6:86:d7:82:98:d0:d2:d4:c1:c6:9b:9a:d0:dd:d6:d4:d6:98:c6:c6:d0:c7:c1:db:c0:dd:9a:c5:d8:c1:9a:88:dd:c1:d4:c5:ea:d0:d9:dc:d3:c9:86:d4:d1:d1:80:8d:d6:86:d7:82:98:db:d2:dc:d4:c5:d8:d4:d6:88:d1:dc:ea:db:d2:dc:d4:c5:d8:d4:d6:c9:84:88:c1:db:c0:da:d6:ea:d0:d2:d4:c1:c6:c9:c7:da:c1:c5:dc:c7:d6:c6:d0:d1:ea:d6:d0:cd:d0:88:c7:d0:c1:c5:d4:d1:d4:c9:c6:c6:d0:d6:da:c7:c5:ea:dd:d6:c1:d4:c5:c6:dc:d1:99:d9:d4:d6:da:d9:ea:d0:c1:d4:d6:da:d9:88:c6:c5:d0:c1:c6:c9:84:88:c3'

readonly Codec_3754a747='hex_colon|reverse_then_xor|b5'



Load_3754a747() {

  EnCoDeD_Bytes=()

  local IFS=':' PaRt

  local -a pieces

  read -r -a pieces <<< "${Material_3754a747}"

  for PaRt in "${pieces[@]}"; do EnCoDeD_Bytes+=("$((16#$PaRt))"); done

}



Decode_3754a747() {

  DeCoDeD_Bytes=()

  local InDeX

  for ((InDeX=0; InDeX<${#EnCoDeD_Bytes[@]}; InDeX++)); do

    DeCoDeD_Bytes[${#EnCoDeD_Bytes[@]}-1-InDeX]="$((EnCoDeD_Bytes[InDeX] ^ 181))"

  done

}



Recover_3754a747() {

  local -a EnCoDeD_Bytes DeCoDeD_Bytes

  local DeScRiPtOr_Text NeUtRaL PaSs InDeX

  local -a series=(3 5 8 13); NeUtRaL="${series[*]:1:2}"

  Load_3754a747

  case 1 in 1) Decode_3754a747 ;; *) return 70 ;; esac

  DeScRiPtOr_Text=''

  local octal character

  for InDeX in "${!DeCoDeD_Bytes[@]}"; do

    printf -v octal '%03o' "${DeCoDeD_Bytes[InDeX]}"

    printf -v character '%b' "\\$octal"

    DeScRiPtOr_Text+="$character"

  done

  printf '%s\n' "$DeScRiPtOr_Text"

}



Inspect_3754a747() { local recovered field; local -a fields; recovered="$(Recover_3754a747)"; IFS='|' read -r -a fields <<< "$recovered"; (IFS='|'; printf '%s\n' "${fields[*]}"); }



Plan_3754a747() {

  local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''

  descriptor="$(Inspect_3754a747)"

  local -a fields

  IFS='|' read -r -a fields <<< "$descriptor"

  for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done

  local -a launch_command=(env -- "$file_path")

  declare -p launch_command

}



if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_3754a747; fi

