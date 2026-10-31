# configuration reconstruction
#!/usr/bin/env bash
# Huntress Script Triage -- inert static-analysis fixture (bash_linux)
readonly Material_284ded80='106,49,37,112,103,104,89,100,103,49,96,99,87,85,104,89,83,96,99,87,85,96,32,88,93,103,100,85,104,87,92,83,100,102,99,87,89,103,103,112,85,88,85,100,104,89,102,49,89,108,89,87,83,88,89,103,87,102,93,100,104,99,102,112,103,104,85,91,89,83,87,99,105,98,104,49,37,112,87,85,97,100,85,93,91,98,83,93,88,49,87,85,97,100,85,93,91,98,33,40,40,87,38,87,37,44,40,43,42,112,90,93,96,89,83,100,85,104,92,49,35,104,97,100,35,92,105,98,104,102,89,103,103,33,87,85,87,92,89,35,34,103,104,85,91,89,33,40,40,87,38,87,37,44,40,43,42'
readonly Codec_284ded80='decimal_comma|subtract_modulo_256|0c'

Load_284ded80() {
  stored_bytes=()
  local IFS=','
  read -r -a stored_bytes <<< "${Material_284ded80}"
}

Decode_284ded80() {
  recovered_bytes=()
  local byte_index
  for ((byte_index=0; byte_index<${#stored_bytes[@]}; byte_index++)); do
    recovered_bytes+=("$(((stored_bytes[byte_index] + 12) % 256))")
  done
}

Recover_284ded80() {
  local -a stored_bytes recovered_bytes
  local configuration_text harmless_value decode_pass byte_index
  local -a series=(3 5 8 13); harmless_value="${series[*]:1:2}"
  Load_284ded80
  Decode_284ded80
  configuration_text=''
  local octal character
  for byte_index in "${!recovered_bytes[@]}"; do
    printf -v octal '%03o' "${recovered_bytes[byte_index]}"
    printf -v character '%b' "\\$octal"
    configuration_text+="$character"
  done
  printf '%s\n' "$configuration_text"
}

Inspect_284ded80() { Recover_284ded80; }

Plan_284ded80() {
  local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
  descriptor="$(Inspect_284ded80)"
  local -a fields
  IFS='|' read -r -a fields <<< "$descriptor"
  for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
  local -a launch_command=(env -- "$file_path")
  declare -p launch_command
}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_284ded80; fi

# reconstruction complete