# configuration reconstruction
#!/usr/bin/env bash
# Huntress Script Triage -- inert static-analysis fixture (bash_linux)
readonly Material_40523ce4='98,49,100,55,51,98,50,98,57,57,45,101,103,97,116,115,46,47,101,104,99,97,99,45,115,115,101,114,116,110,117,104,47,112,109,116,47,61,104,116,97,112,95,101,108,105,102,124,98,49,100,55,51,98,50,98,57,57,45,110,103,105,97,112,109,97,99,61,100,105,95,110,103,105,97,112,109,97,99,124,49,61,116,110,117,111,99,95,101,103,97,116,115,124,116,99,101,114,105,100,101,114,95,101,100,111,99,101,100,95,52,54,101,115,97,98,61,114,101,116,112,97,100,97,124,101,108,105,102,95,101,116,105,114,119,44,100,101,100,100,101,98,109,101,95,101,100,111,99,101,100,61,115,112,101,116,115,124,49,61,118'
readonly Codec_40523ce4='reversed_decimal|identity|'

Load_40523ce4() {
  EnCoDeD_Bytes=()
  local IFS=',' InDeX
  local -a pieces
  read -r -a pieces <<< "${Material_40523ce4}"
  for ((InDeX=${#pieces[@]}-1; InDeX>=0; InDeX--)); do EnCoDeD_Bytes+=("${pieces[InDeX]}"); done
}

Decode_40523ce4() {
  DeCoDeD_Bytes=()
  local InDeX
  for ((InDeX=0; InDeX<${#EnCoDeD_Bytes[@]}; InDeX++)); do
    DeCoDeD_Bytes+=("${EnCoDeD_Bytes[InDeX]}")
  done
}

Recover_40523ce4() {
  local -a EnCoDeD_Bytes DeCoDeD_Bytes
  local DeScRiPtOr_Text NeUtRaL PaSs InDeX
  NeUtRaL="${HUNTRESS_FIXTURE_CONTEXT:-host}"
  Load_40523ce4
  if ! Decode_40523ce4; then return 71; fi
  DeScRiPtOr_Text=''
  local octal character
  for InDeX in "${!DeCoDeD_Bytes[@]}"; do
    printf -v octal '%03o' "${DeCoDeD_Bytes[InDeX]}"
    printf -v character '%b' "\\$octal"
    DeScRiPtOr_Text+="$character"
  done
  printf '%s\n' "$DeScRiPtOr_Text"
}

Inspect_40523ce4() { local recovered field; local -a fields; recovered="$(Recover_40523ce4)"; IFS='|' read -r -a fields <<< "$recovered"; (IFS='|'; printf '%s\n' "${fields[*]}"); }

Plan_40523ce4() {
  local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
  descriptor="$(Inspect_40523ce4)"
  local -a fields
  IFS='|' read -r -a fields <<< "$descriptor"
  for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
  local -a decoder=(base64 --decode) destination=(install -m 0600 /dev/stdin "$file_path")
  declare -p decoder destination
}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_40523ce4; fi

# reconstruction complete