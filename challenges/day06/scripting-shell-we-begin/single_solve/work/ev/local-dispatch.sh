# configuration reconstruction
#!/usr/bin/env bash
# Huntress Script Triage -- inert static-analysis fixture (bash_linux)
readonly Material_d967b787='dj0xfHN0ZXBzPWxvY2F0ZV9sb2NhbCxkaXNwYXRjaF9wcm9jZXNzfGFkYXB0ZXI9c2hfc2NyaXB0fHN0YWdlX2NvdW50PTF8Y2FtcGFpZ25faWQ9Y2FtcGFpZ24tMjNkZTc1NWY5Y3xmaWxlX3BhdGg9L3RtcC9odW50cmVzcy1jYWNoZS8uc3RhZ2UtMjNkZTc1NWY5Yw=='
readonly Codec_d967b787='base64_literal|identity|'

Load_d967b787() {
  stored_bytes=()
  local encoded_part
  while read -r encoded_part; do [[ -n "$encoded_part" ]] && stored_bytes+=("$encoded_part"); done < <(printf '%s' "${Material_d967b787}" | base64 --decode | od -An -v -tu1 | tr -s ' ' '\n' | sed '/^$/d')
}

Decode_d967b787() {
  recovered_bytes=()
  local byte_index
  for ((byte_index=0; byte_index<${#stored_bytes[@]}; byte_index++)); do
    recovered_bytes+=("${stored_bytes[byte_index]}")
  done
}

Recover_d967b787() {
  local -a stored_bytes recovered_bytes
  local configuration_text harmless_value decode_pass byte_index
  if ((2 > 1)); then harmless_value=left; else harmless_value=right; fi
  Load_d967b787
  for decode_pass in 1; do Decode_d967b787; done
  configuration_text=''
  local octal character
  for byte_index in "${!recovered_bytes[@]}"; do
    printf -v octal '%03o' "${recovered_bytes[byte_index]}"
    printf -v character '%b' "\\$octal"
    configuration_text+="$character"
  done
  printf '%s\n' "$configuration_text"
}

Inspect_d967b787() { local recovered; recovered="$(Recover_d967b787)"; printf '%s\n' "$recovered"; }

Plan_d967b787() {
  local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
  descriptor="$(Inspect_d967b787)"
  local -a fields
  IFS='|' read -r -a fields <<< "$descriptor"
  for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
  local -a launch_command=(sh "$file_path")
  declare -p launch_command
}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_d967b787; fi

# reconstruction complete