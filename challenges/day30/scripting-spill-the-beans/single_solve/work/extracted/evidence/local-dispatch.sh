# configuration reconstruction
#!/usr/bin/env bash
# Huntress Script Triage -- inert static-analysis fixture (bash_linux)
readonly Material_f35621f6='118,61,49,124,115,116,101,112,115,61,108,111,99,97,116,101,95,108,111,99,97,108,44,100,105,115,112,97,116,99,104,95,112,114,111,99,101,115,115,124,97,100,97,112,116,101,114,61,101,120,101,99,95,100,101,115,99,114,105,112,116,111,114,124,115,116,97,103,101,95,99,111,117,110,116,61,49,124,99,97,109,112,97,105,103,110,95,105,100,61,99,97,109,112,97,105,103,110,45,99,52,100,50,49,53,101,57,50,97,124,102,105,108,101,95,112,97,116,104,61,47,116,109,112,47,104,117,110,116,114,101,115,115,45,99,97,99,104,101,47,46,115,116,97,103,101,45,99,52,100,50,49,53,101,57,50,97'
readonly Codec_f35621f6='reversed_decimal|reverse_bytes|'

Load_f35621f6() {
  stored_bytes=()
  local IFS=',' byte_index
  local -a pieces
  read -r -a pieces <<< "${Material_f35621f6}"
  for ((byte_index=${#pieces[@]}-1; byte_index>=0; byte_index--)); do stored_bytes+=("${pieces[byte_index]}"); done
}

Decode_f35621f6() {
  recovered_bytes=()
  local byte_index
  for ((byte_index=0; byte_index<${#stored_bytes[@]}; byte_index++)); do
    recovered_bytes[${#stored_bytes[@]}-1-byte_index]="${stored_bytes[byte_index]}"
  done
}

Recover_f35621f6() {
  local -a stored_bytes recovered_bytes
  local configuration_text harmless_value decode_pass byte_index
  if ((2 > 1)); then harmless_value=left; else harmless_value=right; fi
  Load_f35621f6
  if ! Decode_f35621f6; then return 71; fi
  configuration_text=''
  local octal character
  for byte_index in "${!recovered_bytes[@]}"; do
    printf -v octal '%03o' "${recovered_bytes[byte_index]}"
    printf -v character '%b' "\\$octal"
    configuration_text+="$character"
  done
  printf '%s\n' "$configuration_text"
}

Inspect_f35621f6() { local recovered; recovered="$(Recover_f35621f6)"; printf '%s\n' "$recovered"; }

Plan_f35621f6() {
  local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
  descriptor="$(Inspect_f35621f6)"
  local -a fields
  IFS='|' read -r -a fields <<< "$descriptor"
  for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
  local -a launch_command=(env -- "$file_path")
  declare -p launch_command
}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_f35621f6; fi

# reconstruction complete