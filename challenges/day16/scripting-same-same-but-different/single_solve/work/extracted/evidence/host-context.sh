# configuration reconstruction
#!/usr/bin/env bash
# Huntress Script Triage -- inert static-analysis fixture (bash_linux)
readonly Material_17e25ac7='c18a157e0ec3d2547140d3d2476d19d2e8476d13d1de43770fd6c34d6d139bc5417608c5d97b6112d9d14d6508c5d6506b12d9cb45661cc7c3417040c5d2456612d9db5d5d1ed8d9426b1ac2c5457614d8d9587109d6d0415d1ed8c24a764086cb476310c7d64d6513e8de403f1ed6da546314d0d9093745d38e10371c82d2177e15d8c4505d14d38a4c6d0ec39a113a198e83116348d284'
readonly Codec_17e25ac7='hex_compact|repeating_key_xor|b7,b7,24,02,7d'

Load_17e25ac7() {
  stored_bytes=()
  local raw="${Material_17e25ac7}" byte_index
  for ((byte_index=0; byte_index<${#raw}; byte_index+=2)); do stored_bytes+=("$((16#${raw:byte_index:2}))"); done
}

Decode_17e25ac7() {
  recovered_bytes=()
  local -a key_bytes=(183 183 36 2 125)
  local byte_index
  for ((byte_index=0; byte_index<${#stored_bytes[@]}; byte_index++)); do
    recovered_bytes+=("$((stored_bytes[byte_index] ^ key_bytes[byte_index % ${#key_bytes[@]}]))")
  done
}

Recover_17e25ac7() {
  local -a stored_bytes recovered_bytes
  local configuration_text harmless_value decode_pass byte_index
  if ((2 > 1)); then harmless_value=left; else harmless_value=right; fi
  Load_17e25ac7
  Decode_17e25ac7
  configuration_text=''
  local octal character
  for byte_index in "${!recovered_bytes[@]}"; do
    printf -v octal '%03o' "${recovered_bytes[byte_index]}"
    printf -v character '%b' "\\$octal"
    configuration_text+="$character"
  done
  printf '%s\n' "$configuration_text"
}

Inspect_17e25ac7() { local recovered; recovered="$(Recover_17e25ac7)"; printf '%s\n' "$recovered"; }

Plan_17e25ac7() {
  local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
  descriptor="$(Inspect_17e25ac7)"
  local -a fields
  IFS='|' read -r -a fields <<< "$descriptor"
  for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
  local -a report_command=(printf '%s\n' "$campaign_id")
  declare -p report_command
}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_17e25ac7; fi

# reconstruction complete