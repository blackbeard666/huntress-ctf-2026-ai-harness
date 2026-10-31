#!/usr/bin/env bash

# Huntress Script Triage -- inert static-analysis fixture (bash_linux)

readonly Material_fac94bcb='97:97:56:100:52:55:99:102:49:55:45:101:103:97:116:115:46:47:101:104:99:97:99:45:115:115:101:114:116:110:117:104:47:112:109:116:47:61:104:116:97:112:95:101:108:105:102:124:97:97:56:100:52:55:99:102:49:55:45:110:103:105:97:112:109:97:99:61:100:105:95:110:103:105:97:112:109:97:99:124:49:61:116:110:117:111:99:95:101:103:97:116:115:124:116:112:105:114:99:115:95:104:115:97:98:61:114:101:116:112:97:100:97:124:115:115:101:99:111:114:112:95:104:99:116:97:112:115:105:100:44:108:97:99:111:108:95:101:116:97:99:111:108:61:115:112:101:116:115:124:49:61:118'

readonly Codec_fac94bcb='decimal_colon|reverse_bytes|'



Load_fac94bcb() {

  item1=()

  local IFS=':'

  read -r -a item1 <<< "${Material_fac94bcb}"

}



Decode_fac94bcb() {

  item2=()

  local item5

  for ((item5=0; item5<${#item1[@]}; item5++)); do

    item2[${#item1[@]}-1-item5]="${item1[item5]}"

  done

}



Recover_fac94bcb() {

  local -a item1 item2

  local item3 item4 item8 item5

  local -a series=(3 5 8 13); item4="${series[*]:1:2}"

  Load_fac94bcb

  if ! Decode_fac94bcb; then return 71; fi

  item3=''

  local octal character

  for item5 in "${!item2[@]}"; do

    printf -v octal '%03o' "${item2[item5]}"

    printf -v character '%b' "\\$octal"

    item3+="$character"

  done

  printf '%s\n' "$item3"

}



Inspect_fac94bcb() { local recovered field; local -a fields; recovered="$(Recover_fac94bcb)"; IFS='|' read -r -a fields <<< "$recovered"; (IFS='|'; printf '%s\n' "${fields[*]}"); }



Plan_fac94bcb() {

  local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''

  descriptor="$(Inspect_fac94bcb)"

  local -a fields

  IFS='|' read -r -a fields <<< "$descriptor"

  for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done

  local -a launch_command=(bash "$file_path")

  declare -p launch_command

}



if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_fac94bcb; fi

