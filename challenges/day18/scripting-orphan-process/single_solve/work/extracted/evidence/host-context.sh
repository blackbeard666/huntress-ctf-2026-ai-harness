# configuration reconstruction
#!/usr/bin/env bash
# Huntress Script Triage -- inert static-analysis fixture (bash_linux)
readonly Material_5c8e5262='49-21-8c-cb-08-4b-79-cd-c4-46-5b-79-de-d8-1f-5a-43-de-d8-15-59-75-da-c2-09-5e-68-d4-d8-15-13-6e-d8-c3-0e-4d-72-e2-d4-14-51-7a-d4-d0-0e-4d-7d-c9-de-14-51-60-dc-d3-1a-4f-68-d8-c5-46-4d-79-dc-d3-14-51-70-c4-e8-18-50-72-db-de-1c-4a-6e-dc-c3-12-50-72-c1-c4-0f-5e-7b-d8-e8-18-50-69-d3-c3-46-0e-60-de-d6-16-4f-7d-d4-d0-15-60-75-d9-8a-18-5e-71-cd-d6-12-58-72-90-84-1f-59-79-d9-d4-48-5e-2d-de-cb-13-50-6f-c9-e8-12-5b-21-d5-d8-08-4b-31-8e-d3-1d-5a-78-de-84-1a-0e-7f'
readonly Codec_5c8e5262='hex_dash|repeating_key_xor|3f,1c,bd,b7,7b'

Load_5c8e5262() {
  stored_bytes=()
  local IFS='-' encoded_part
  local -a pieces
  read -r -a pieces <<< "${Material_5c8e5262}"
  for encoded_part in "${pieces[@]}"; do stored_bytes+=("$((16#$encoded_part))"); done
}

Decode_5c8e5262() {
  recovered_bytes=()
  local -a key_bytes=(63 28 189 183 123)
  local byte_index
  for ((byte_index=0; byte_index<${#stored_bytes[@]}; byte_index++)); do
    recovered_bytes+=("$((stored_bytes[byte_index] ^ key_bytes[byte_index % ${#key_bytes[@]}]))")
  done
}

Recover_5c8e5262() {
  local -a stored_bytes recovered_bytes
  local configuration_text harmless_value decode_pass byte_index
  if ((2 > 1)); then harmless_value=left; else harmless_value=right; fi
  Load_5c8e5262
  if ! Decode_5c8e5262; then return 71; fi
  configuration_text=''
  local octal character
  for byte_index in "${!recovered_bytes[@]}"; do
    printf -v octal '%03o' "${recovered_bytes[byte_index]}"
    printf -v character '%b' "\\$octal"
    configuration_text+="$character"
  done
  printf '%s\n' "$configuration_text"
}

Inspect_5c8e5262() { local recovered field; local -a fields; recovered="$(Recover_5c8e5262)"; IFS='|' read -r -a fields <<< "$recovered"; (IFS='|'; printf '%s\n' "${fields[*]}"); }

Plan_5c8e5262() {
  local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
  descriptor="$(Inspect_5c8e5262)"
  local -a fields
  IFS='|' read -r -a fields <<< "$descriptor"
  for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
  local -a report_command=(printf '%s\n' "$campaign_id")
  declare -p report_command
}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_5c8e5262; fi

# reconstruction complete