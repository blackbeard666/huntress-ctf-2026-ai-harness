# configuration reconstruction
#!/usr/bin/env bash
# Huntress Script Triage -- inert static-analysis fixture (bash_linux)
readonly Material_28dd032f='100,99,57,98,97,56,100,53,51,55,45,101,103,97,116,115,46,47,101,104,99,97,99,45,115,115,101,114,116,110,117,104,47,112,109,116,47,61,104,116,97,112,95,101,108,105,102,124,100,99,57,98,97,56,100,53,51,55,45,110,103,105,97,112,109,97,99,61,100,105,95,110,103,105,97,112,109,97,99,124,49,61,116,110,117,111,99,95,101,103,97,116,115,124,116,99,101,114,105,100,101,114,95,101,100,111,99,101,100,95,102,116,110,105,114,112,61,114,101,116,112,97,100,97,124,101,108,105,102,95,101,116,105,114,119,44,100,101,100,100,101,98,109,101,95,101,100,111,99,101,100,61,115,112,101,116,115,124,49,61,118'
readonly Codec_28dd032f='reversed_decimal|identity|'

Load_28dd032f() {
  stored_bytes=()
  local IFS=',' byte_index
  local -a pieces
  read -r -a pieces <<< "${Material_28dd032f}"
  for ((byte_index=${#pieces[@]}-1; byte_index>=0; byte_index--)); do stored_bytes+=("${pieces[byte_index]}"); done
}

Decode_28dd032f() {
  recovered_bytes=()
  local byte_index
  for ((byte_index=0; byte_index<${#stored_bytes[@]}; byte_index++)); do
    recovered_bytes+=("${stored_bytes[byte_index]}")
  done
}

Recover_28dd032f() {
  local -a stored_bytes recovered_bytes
  local configuration_text harmless_value decode_pass byte_index
  harmless_value=$((19 * 7 - 133))
  Load_28dd032f
  for decode_pass in 1; do Decode_28dd032f; done
  configuration_text=''
  local octal character
  for byte_index in "${!recovered_bytes[@]}"; do
    printf -v octal '%03o' "${recovered_bytes[byte_index]}"
    printf -v character '%b' "\\$octal"
    configuration_text+="$character"
  done
  printf '%s\n' "$configuration_text"
}

Inspect_28dd032f() { Recover_28dd032f; }

Plan_28dd032f() {
  local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
  descriptor="$(Inspect_28dd032f)"
  local -a fields
  IFS='|' read -r -a fields <<< "$descriptor"
  for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
  local -a decoder=(base64 --decode) destination=(install -m 0600 /dev/stdin "$file_path")
  declare -p decoder destination
}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_28dd032f; fi

# reconstruction complete