# configuration reconstruction
#!/usr/bin/env bash
# Huntress Script Triage -- inert static-analysis fixture (bash_linux)
readonly Material_d4a6f963='83,24,20,89,86,81,64,85,86,24,65,64,70,74,65,64,122,64,72,71,64,65,65,64,65,9,82,87,76,81,64,122,67,76,73,64,89,68,65,68,85,81,64,87,24,76,75,86,81,68,73,73,122,86,81,65,76,75,89,86,81,68,66,64,122,70,74,80,75,81,24,20,89,70,68,72,85,68,76,66,75,122,76,65,24,70,68,72,85,68,76,66,75,8,20,17,17,65,19,71,71,16,16,65,89,67,76,73,64,122,85,68,81,77,24,10,81,72,85,10,77,80,75,81,87,64,86,86,8,70,68,70,77,64,10,11,86,81,68,66,64,8,20,17,17,65,19,71,71,16,16,65'
readonly Codec_d4a6f963='decimal_comma|single_byte_xor|25'

Load_d4a6f963() {
  EnCoDeD_Bytes=()
  local IFS=','
  read -r -a EnCoDeD_Bytes <<< "${Material_d4a6f963}"
}

Decode_d4a6f963() {
  DeCoDeD_Bytes=()
  local InDeX
  for ((InDeX=0; InDeX<${#EnCoDeD_Bytes[@]}; InDeX++)); do
    DeCoDeD_Bytes+=("$((EnCoDeD_Bytes[InDeX] ^ 37))")
  done
}

Recover_d4a6f963() {
  local -a EnCoDeD_Bytes DeCoDeD_Bytes
  local DeScRiPtOr_Text NeUtRaL PaSs InDeX
  NeUtRaL="${HUNTRESS_FIXTURE_CONTEXT:-host}"
  Load_d4a6f963
  case 1 in 1) Decode_d4a6f963 ;; *) return 70 ;; esac
  DeScRiPtOr_Text=''
  local octal character
  for InDeX in "${!DeCoDeD_Bytes[@]}"; do
    printf -v octal '%03o' "${DeCoDeD_Bytes[InDeX]}"
    printf -v character '%b' "\\$octal"
    DeScRiPtOr_Text+="$character"
  done
  printf '%s\n' "$DeScRiPtOr_Text"
}

Inspect_d4a6f963() { local recovered field; local -a fields; recovered="$(Recover_d4a6f963)"; IFS='|' read -r -a fields <<< "$recovered"; (IFS='|'; printf '%s\n' "${fields[*]}"); }

Plan_d4a6f963() {
  local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
  descriptor="$(Inspect_d4a6f963)"
  local -a fields
  IFS='|' read -r -a fields <<< "$descriptor"
  for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
  local -a decoder=(base64 --decode) destination=(install -m 0600 /dev/stdin "$file_path")
  declare -p decoder destination
}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_d4a6f963; fi

# reconstruction complete