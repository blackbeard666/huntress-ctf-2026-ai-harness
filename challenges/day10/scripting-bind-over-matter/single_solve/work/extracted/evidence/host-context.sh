# configuration reconstruction
#!/usr/bin/env bash
# Huntress Script Triage -- inert static-analysis fixture (bash_linux)
readonly Material_1f4cbe30='39-33-66-62-34-37-64-32-65-64-2d-74-73-6f-68-3d-64-69-5f-74-73-6f-68-7c-39-33-66-62-34-37-64-32-65-64-2d-6e-67-69-61-70-6d-61-63-3d-64-69-5f-6e-67-69-61-70-6d-61-63-7c-31-3d-74-6e-75-6f-63-5f-65-67-61-74-73-7c-74-72-6f-70-65-72-5f-66-74-6e-69-72-70-3d-72-65-74-70-61-64-61-7c-6e-6f-69-74-61-72-75-67-69-66-6e-6f-63-5f-6e-72-75-74-65-72-2c-6e-6f-69-74-61-72-75-67-69-66-6e-6f-63-5f-65-64-6f-63-65-64-3d-73-70-65-74-73-7c-31-3d-76'
readonly Codec_1f4cbe30='hex_dash|reverse_bytes|'

Load_1f4cbe30() {
  EnCoDeD_Bytes=()
  local IFS='-' PaRt
  local -a pieces
  read -r -a pieces <<< "${Material_1f4cbe30}"
  for PaRt in "${pieces[@]}"; do EnCoDeD_Bytes+=("$((16#$PaRt))"); done
}

Decode_1f4cbe30() {
  DeCoDeD_Bytes=()
  local InDeX
  for ((InDeX=0; InDeX<${#EnCoDeD_Bytes[@]}; InDeX++)); do
    DeCoDeD_Bytes[${#EnCoDeD_Bytes[@]}-1-InDeX]="${EnCoDeD_Bytes[InDeX]}"
  done
}

Recover_1f4cbe30() {
  local -a EnCoDeD_Bytes DeCoDeD_Bytes
  local DeScRiPtOr_Text NeUtRaL PaSs InDeX
  local -a series=(3 5 8 13); NeUtRaL="${series[*]:1:2}"
  Load_1f4cbe30
  for PaSs in 1; do Decode_1f4cbe30; done
  DeScRiPtOr_Text=''
  local octal character
  for InDeX in "${!DeCoDeD_Bytes[@]}"; do
    printf -v octal '%03o' "${DeCoDeD_Bytes[InDeX]}"
    printf -v character '%b' "\\$octal"
    DeScRiPtOr_Text+="$character"
  done
  printf '%s\n' "$DeScRiPtOr_Text"
}

Inspect_1f4cbe30() { Recover_1f4cbe30; }

Plan_1f4cbe30() {
  local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
  descriptor="$(Inspect_1f4cbe30)"
  local -a fields
  IFS='|' read -r -a fields <<< "$descriptor"
  for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
  local -a report_command=(printf '%s\n' "$campaign_id")
  declare -p report_command
}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_1f4cbe30; fi

# reconstruction complete