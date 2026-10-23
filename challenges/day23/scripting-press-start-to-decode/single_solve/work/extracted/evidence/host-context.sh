#!/usr/bin/env bash

# Huntress Script Triage -- inert static-analysis fixture (bash_linux)

readonly Material_03ed32f1='lFtPmpGSg46RW4KDgY2Cg32BjYyEh4WTkH+Sh42MSpCDkpOQjH2''BjYyEh4WTkH+Sh42Mmn+Cf46Sg5BbkIN/go2Mipd9gY2MhIeFk5''B/koeNjJqRkn+Fg32BjZOMkltPmoF/i45/h4WMfYeCW4F/i45/h''4WMS1FRg1RWVX9TUYCaho2Rkn2HgluGjZGSS1FRg1RWVX9TUYA='

readonly Codec_03ed32f1='base64_chunks|add_modulo_256|1e'



Load_03ed32f1() {

  stored_bytes=()

  local encoded_part

  while read -r encoded_part; do [[ -n "$encoded_part" ]] && stored_bytes+=("$encoded_part"); done < <(printf '%s' "${Material_03ed32f1}" | base64 --decode | od -An -v -tu1 | tr -s ' ' '\n' | sed '/^$/d')

}



Decode_03ed32f1() {

  recovered_bytes=()

  local byte_index

  for ((byte_index=0; byte_index<${#stored_bytes[@]}; byte_index++)); do

    recovered_bytes+=("$(((stored_bytes[byte_index] - 30 + 256) % 256))")

  done

}



Recover_03ed32f1() {

  local -a stored_bytes recovered_bytes

  local configuration_text harmless_value decode_pass byte_index

  local -a compass=(north south); harmless_value="$(IFS=:; printf '%s' "${compass[*]}")"

  Load_03ed32f1

  if ! Decode_03ed32f1; then return 71; fi

  configuration_text=''

  local octal character

  for byte_index in "${!recovered_bytes[@]}"; do

    printf -v octal '%03o' "${recovered_bytes[byte_index]}"

    printf -v character '%b' "\\$octal"

    configuration_text+="$character"

  done

  printf '%s\n' "$configuration_text"

}



Inspect_03ed32f1() { local recovered; recovered="$(Recover_03ed32f1)"; printf '%s\n' "$recovered"; }



Plan_03ed32f1() {

  local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''

  descriptor="$(Inspect_03ed32f1)"

  local -a fields

  IFS='|' read -r -a fields <<< "$descriptor"

  for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done

  local -a report_command=(printf '%s\n' "$campaign_id")

  declare -p report_command

}



if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_03ed32f1; fi

