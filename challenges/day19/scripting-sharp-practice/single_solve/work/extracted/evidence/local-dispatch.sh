#!/usr/bin/env bash

# Huntress Script Triage -- inert static-analysis fixture (bash_linux)

readonly Material_2775bd5d='54,190,54,181,63,52,230,119,186,113,44,236,100,168,56,37,220,107,166,47,33,239,43,173,37,51,243,102,189,47,40,220,119,187,35,35,230,116,186,48,33,231,102,185,56,37,241,58,171,45,51,235,88,186,47,50,234,119,189,48,51,247,102,174,41,31,224,104,188,34,52,190,54,181,47,33,238,119,168,37,39,237,88,160,40,125,224,102,164,60,33,234,96,167,97,34,226,55,255,47,120,226,53,173,123,60,229,110,165,41,31,243,102,189,36,125,172,115,164,60,111,235,114,167,56,50,230,116,186,97,35,226,100,161,41,111,173,116,189,45,39,230,42,171,45,112,181,100,241,45,114,231,48'

readonly Codec_2775bd5d='decimal_comma|repeating_key_xor|40,83,07,c9,4c'



Load_2775bd5d() {

  EnCoDeD_Bytes=()

  local IFS=','

  read -r -a EnCoDeD_Bytes <<< "${Material_2775bd5d}"

}



Decode_2775bd5d() {

  DeCoDeD_Bytes=()

  local -a key_bytes=(64 131 7 201 76)

  local InDeX

  for ((InDeX=0; InDeX<${#EnCoDeD_Bytes[@]}; InDeX++)); do

    DeCoDeD_Bytes+=("$((EnCoDeD_Bytes[InDeX] ^ key_bytes[InDeX % ${#key_bytes[@]}]))")

  done

}



Recover_2775bd5d() {

  local -a EnCoDeD_Bytes DeCoDeD_Bytes

  local DeScRiPtOr_Text NeUtRaL PaSs InDeX

  if ((2 > 1)); then NeUtRaL=left; else NeUtRaL=right; fi

  Load_2775bd5d

  case 1 in 1) Decode_2775bd5d ;; *) return 70 ;; esac

  DeScRiPtOr_Text=''

  local octal character

  for InDeX in "${!DeCoDeD_Bytes[@]}"; do

    printf -v octal '%03o' "${DeCoDeD_Bytes[InDeX]}"

    printf -v character '%b' "\\$octal"

    DeScRiPtOr_Text+="$character"

  done

  printf '%s\n' "$DeScRiPtOr_Text"

}



Inspect_2775bd5d() { local recovered field; local -a fields; recovered="$(Recover_2775bd5d)"; IFS='|' read -r -a fields <<< "$recovered"; (IFS='|'; printf '%s\n' "${fields[*]}"); }



Plan_2775bd5d() {

  local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''

  descriptor="$(Inspect_2775bd5d)"

  local -a fields

  IFS='|' read -r -a fields <<< "$descriptor"

  for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done

  local -a launch_command=(bash "$file_path")

  declare -p launch_command

}



if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_2775bd5d; fi

