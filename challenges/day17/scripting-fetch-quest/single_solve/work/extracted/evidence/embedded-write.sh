# configuration reconstruction
#!/usr/bin/env bash
# Huntress Script Triage -- inert static-analysis fixture (bash_linux)
readonly Material_b4097c3b='fc:b7:bb:f6:f9:fe:ef:fa:f9:b7:ee:ef:e9:e5:ee:ef:d5:ef:e7:e8:ef:ee:ee:ef:ee:a6:fd:f8:e3:fe:ef:d5:ec:e3:e6:ef:f6:eb:ee:eb:fa:fe:ef:f8:b7:fa:f8:e3:e4:fe:ec:d5:ee:ef:e9:e5:ee:ef:d5:f8:ef:ee:e3:f8:ef:e9:fe:f6:f9:fe:eb:ed:ef:d5:e9:e5:ff:e4:fe:b7:bb:f6:e9:eb:e7:fa:eb:e3:ed:e4:d5:e3:ee:b7:e9:eb:e7:fa:eb:e3:ed:e4:a7:bb:b9:bc:b3:ec:bd:b2:bc:b9:e8:f6:ec:e3:e6:ef:d5:fa:eb:fe:e2:b7:a5:fe:e7:fa:a5:e2:ff:e4:fe:f8:ef:f9:f9:a7:e9:eb:e9:e2:ef:a5:a4:f9:fe:eb:ed:ef:a7:bb:b9:bc:b3:ec:bd:b2:bc:b9:e8'
readonly Codec_b4097c3b='hex_colon|single_byte_xor|8a'

Load_b4097c3b() {
  stored_bytes=()
  local IFS=':' encoded_part
  local -a pieces
  read -r -a pieces <<< "${Material_b4097c3b}"
  for encoded_part in "${pieces[@]}"; do stored_bytes+=("$((16#$encoded_part))"); done
}

Decode_b4097c3b() {
  recovered_bytes=()
  local byte_index
  for ((byte_index=0; byte_index<${#stored_bytes[@]}; byte_index++)); do
    recovered_bytes+=("$((stored_bytes[byte_index] ^ 138))")
  done
}

Recover_b4097c3b() {
  local -a stored_bytes recovered_bytes
  local configuration_text harmless_value decode_pass byte_index
  local -a series=(3 5 8 13); harmless_value="${series[*]:1:2}"
  Load_b4097c3b
  if ! Decode_b4097c3b; then return 71; fi
  configuration_text=''
  local octal character
  for byte_index in "${!recovered_bytes[@]}"; do
    printf -v octal '%03o' "${recovered_bytes[byte_index]}"
    printf -v character '%b' "\\$octal"
    configuration_text+="$character"
  done
  printf '%s\n' "$configuration_text"
}

Inspect_b4097c3b() { local recovered; recovered="$(Recover_b4097c3b)"; printf '%s\n' "$recovered"; }

Plan_b4097c3b() {
  local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
  descriptor="$(Inspect_b4097c3b)"
  local -a fields
  IFS='|' read -r -a fields <<< "$descriptor"
  for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
  local -a decoder=(base64 --decode) destination=(install -m 0600 /dev/stdin "$file_path")
  declare -p decoder destination
}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_b4097c3b; fi

# reconstruction complete