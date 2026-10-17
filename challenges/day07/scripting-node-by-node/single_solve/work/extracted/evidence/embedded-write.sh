# configuration reconstruction
#!/usr/bin/env bash
# Huntress Script Triage -- inert static-analysis fixture (bash_linux)
readonly Material_77ed519d='118 61 49 124 115 116 101 112 115 61 100 101 99 111 100 101 95 101 109 98 101 100 100 101 100 44 119 114 105 116 101 95 102 105 108 101 124 97 100 97 112 116 101 114 61 105 110 115 116 97 108 108 95 115 116 100 105 110 124 115 116 97 103 101 95 99 111 117 110 116 61 49 124 99 97 109 112 97 105 103 110 95 105 100 61 99 97 109 112 97 105 103 110 45 56 57 49 57 51 101 49 54 55 100 124 102 105 108 101 95 112 97 116 104 61 47 116 109 112 47 104 117 110 116 114 101 115 115 45 99 97 99 104 101 47 46 115 116 97 103 101 45 56 57 49 57 51 101 49 54 55 100'
readonly Codec_77ed519d='decimal_space|identity|'

Load_77ed519d() {
  stored_bytes=()
  local IFS=' '
  read -r -a stored_bytes <<< "${Material_77ed519d}"
}

Decode_77ed519d() {
  recovered_bytes=()
  local byte_index
  for ((byte_index=0; byte_index<${#stored_bytes[@]}; byte_index++)); do
    recovered_bytes+=("${stored_bytes[byte_index]}")
  done
}

Recover_77ed519d() {
  local -a stored_bytes recovered_bytes
  local configuration_text harmless_value decode_pass byte_index
  harmless_value=''
  Load_77ed519d
  Decode_77ed519d
  configuration_text=''
  local octal character
  for byte_index in "${!recovered_bytes[@]}"; do
    printf -v octal '%03o' "${recovered_bytes[byte_index]}"
    printf -v character '%b' "\\$octal"
    configuration_text+="$character"
  done
  printf '%s\n' "$configuration_text"
}

Inspect_77ed519d() { local recovered; recovered="$(Recover_77ed519d)"; printf '%s\n' "$recovered"; }

Plan_77ed519d() {
  local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
  descriptor="$(Inspect_77ed519d)"
  local -a fields
  IFS='|' read -r -a fields <<< "$descriptor"
  for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
  local -a decoder=(base64 --decode) destination=(install -m 0600 /dev/stdin "$file_path")
  declare -p decoder destination
}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_77ed519d; fi

# reconstruction complete