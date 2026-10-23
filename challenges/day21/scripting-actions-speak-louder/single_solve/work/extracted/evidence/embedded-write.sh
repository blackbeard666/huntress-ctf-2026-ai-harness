#!/usr/bin/env bash
# Huntress Script Triage -- inert static-analysis fixture (bash_linux)
readonly Material_a1a9534e='94387493f59660359cbb86602680e2875a2082e48761218ae2ce723786f2875a2386ea8779248be79271209dbb8b6b369be78e691a9cf2866c2b93f59664228ad9816a3081f2df34398ce78f752486e18c5a2c8bbb8164289fe78b622bc2e3813621dcb387677dd6fa846c298ad992643187bbcd71289fa98a702b9bf4877636c2e583662d8aa9cc76318ee18728208cb58636708ae4da3c'
readonly Codec_a1a9534e='hex_compact|repeating_key_xor|e2,05,45,ef,86'

Load_a1a9534e() {
  stored_bytes=()
  local raw="${Material_a1a9534e}" byte_index
  for ((byte_index=0; byte_index<${#raw}; byte_index+=2)); do stored_bytes+=("$((16#${raw:byte_index:2}))"); done
}

Decode_a1a9534e() {
  recovered_bytes=()
  local -a key_bytes=(226 5 69 239 134)
  local byte_index
  for ((byte_index=0; byte_index<${#stored_bytes[@]}; byte_index++)); do
    recovered_bytes+=("$((stored_bytes[byte_index] ^ key_bytes[byte_index % ${#key_bytes[@]}]))")
  done
}

Recover_a1a9534e() {
  local -a stored_bytes recovered_bytes
  local configuration_text harmless_value decode_pass byte_index
  harmless_value="${HUNTRESS_FIXTURE_CONTEXT:-host}"
  Load_a1a9534e
  if ! Decode_a1a9534e; then return 71; fi
  configuration_text=''
  local octal character
  for byte_index in "${!recovered_bytes[@]}"; do
    printf -v octal '%03o' "${recovered_bytes[byte_index]}"
    printf -v character '%b' "\\$octal"
    configuration_text+="$character"
  done
  printf '%s\n' "$configuration_text"
}

Inspect_a1a9534e() { local recovered field; local -a fields; recovered="$(Recover_a1a9534e)"; IFS='|' read -r -a fields <<< "$recovered"; (IFS='|'; printf '%s\n' "${fields[*]}"); }

Plan_a1a9534e() {
  local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
  descriptor="$(Inspect_a1a9534e)"
  local -a fields
  IFS='|' read -r -a fields <<< "$descriptor"
  for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
  local -a decoder=(base64 --decode) destination=(install -m 0600 /dev/stdin "$file_path")
  declare -p decoder destination
}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_a1a9534e; fi
