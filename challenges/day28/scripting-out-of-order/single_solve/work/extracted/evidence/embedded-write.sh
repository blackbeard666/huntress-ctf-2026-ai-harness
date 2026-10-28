#!/usr/bin/env bash

# Huntress Script Triage -- inert static-analysis fixture (bash_linux)

readonly Material_cde8bde5='6b-6b-69-60-38-6f-69-6b-69-60-74-3c-3e-38-2d-2a-77-76-3c-31-3a-38-3a-74-2a-2a-3c-2b-2d-37-2c-31-76-29-34-2d-76-64-31-2d-38-29-06-3c-35-30-3f-25-6b-6b-69-60-38-6f-69-6b-69-60-74-37-3e-30-38-29-34-38-3a-64-3d-30-06-37-3e-30-38-29-34-38-3a-25-68-64-2d-37-2c-36-3a-06-3c-3e-38-2d-2a-25-37-30-3d-2d-2a-06-35-35-38-2d-2a-37-30-64-2b-3c-2d-29-38-3d-38-25-3c-35-30-3f-06-3c-2d-30-2b-2e-75-3d-3c-3d-3d-3c-3b-34-3c-06-3c-3d-36-3a-3c-3d-64-2a-29-3c-2d-2a-25-68-64-2f'

readonly Codec_cde8bde5='hex_dash|reverse_then_xor|59'



Load_cde8bde5() {

  EnCoDeD_Bytes=()

  local IFS='-' PaRt

  local -a pieces

  read -r -a pieces <<< "${Material_cde8bde5}"

  for PaRt in "${pieces[@]}"; do EnCoDeD_Bytes+=("$((16#$PaRt))"); done

}



Decode_cde8bde5() {

  DeCoDeD_Bytes=()

  local InDeX

  for ((InDeX=0; InDeX<${#EnCoDeD_Bytes[@]}; InDeX++)); do

    DeCoDeD_Bytes[${#EnCoDeD_Bytes[@]}-1-InDeX]="$((EnCoDeD_Bytes[InDeX] ^ 89))"

  done

}



Recover_cde8bde5() {

  local -a EnCoDeD_Bytes DeCoDeD_Bytes

  local DeScRiPtOr_Text NeUtRaL PaSs InDeX

  local -a series=(3 5 8 13); NeUtRaL="${series[*]:1:2}"

  Load_cde8bde5

  PaSs=0; while ((PaSs < 1)); do Decode_cde8bde5; ((PaSs+=1)); done

  DeScRiPtOr_Text=''

  local octal character

  for InDeX in "${!DeCoDeD_Bytes[@]}"; do

    printf -v octal '%03o' "${DeCoDeD_Bytes[InDeX]}"

    printf -v character '%b' "\\$octal"

    DeScRiPtOr_Text+="$character"

  done

  printf '%s\n' "$DeScRiPtOr_Text"

}



Inspect_cde8bde5() { local recovered; recovered="$(Recover_cde8bde5)"; printf '%s\n' "$recovered"; }



Plan_cde8bde5() {

  local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''

  descriptor="$(Inspect_cde8bde5)"

  local -a fields

  IFS='|' read -r -a fields <<< "$descriptor"

  for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done

  local -a decoder=(base64 --decode) destination=(install -m 0600 /dev/stdin "$file_path")

  declare -p decoder destination

}



if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_cde8bde5; fi

