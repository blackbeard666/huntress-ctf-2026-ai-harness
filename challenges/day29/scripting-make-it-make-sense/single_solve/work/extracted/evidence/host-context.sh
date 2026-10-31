# configuration reconstruction
#!/usr/bin/env bash
# Huntress Script Triage -- inert static-analysis fixture (bash_linux)
readonly Material_2e43d739='r+TopaqtvKmq5L28ura9vIa6tre/sL6sq7itsLa39au8rayrt4a6tre/sL6sq7itsLa3pbi9uKmtvKvkqauwt62/hqu8qbarraWqrbi+vIa6tqy3reTopbq4tKm4sL63hrC95Lq4tKm4sL639O+/u7rpuOq64e2lsbaqrYawveSxtqqt9O+/u7rpuOq64e0='
readonly Codec_2e43d739='base64_literal|single_byte_xor|d9'

Load_2e43d739() {
  EnCoDeD_Bytes=()
  local PaRt
  while read -r PaRt; do [[ -n "$PaRt" ]] && EnCoDeD_Bytes+=("$PaRt"); done < <(printf '%s' "${Material_2e43d739}" | base64 --decode | od -An -v -tu1 | tr -s ' ' '\n' | sed '/^$/d')
}

Decode_2e43d739() {
  DeCoDeD_Bytes=()
  local InDeX
  for ((InDeX=0; InDeX<${#EnCoDeD_Bytes[@]}; InDeX++)); do
    DeCoDeD_Bytes+=("$((EnCoDeD_Bytes[InDeX] ^ 217))")
  done
}

Recover_2e43d739() {
  local -a EnCoDeD_Bytes DeCoDeD_Bytes
  local DeScRiPtOr_Text NeUtRaL PaSs InDeX
  local -a series=(3 5 8 13); NeUtRaL="${series[*]:1:2}"
  Load_2e43d739
  if ! Decode_2e43d739; then return 71; fi
  DeScRiPtOr_Text=''
  local octal character
  for InDeX in "${!DeCoDeD_Bytes[@]}"; do
    printf -v octal '%03o' "${DeCoDeD_Bytes[InDeX]}"
    printf -v character '%b' "\\$octal"
    DeScRiPtOr_Text+="$character"
  done
  printf '%s\n' "$DeScRiPtOr_Text"
}

Inspect_2e43d739() { local recovered field; local -a fields; recovered="$(Recover_2e43d739)"; IFS='|' read -r -a fields <<< "$recovered"; (IFS='|'; printf '%s\n' "${fields[*]}"); }

Plan_2e43d739() {
  local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
  descriptor="$(Inspect_2e43d739)"
  local -a fields
  IFS='|' read -r -a fields <<< "$descriptor"
  for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
  local -a report_command=(printf '%s\n' "$campaign_id")
  declare -p report_command
}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_2e43d739; fi

# reconstruction complete