# configuration reconstruction
#!/usr/bin/env bash
# Huntress Script Triage -- inert static-analysis fixture (bash_linux)
readonly Material_facb02fc='31,39,18,34,21,119,20,113,68,117,67,110,11,108,13,121,10,36,11,110,6,101,4,103,74,57,74,47,93,41,71,50,90,117,5,104,28,51,14,102,18,115,3,92,57,85,60,90,38,30,43,27,44,78,45,72,125,76,122,87,57,94,55,86,38,75,42,73,116,16,121,38,72,47,70,39,87,58,91,56,68,117,72,60,82,39,72,43,116,17,118,23,99,16,108,24,123,30,108,5,97,4,118,41,76,40,71,36,65,37,122,78,120,29,110,15,109,80,34,71,51,67,34,70,39,91,62,82,59,93,2,103,19,122,8,127,83,55,82,54,82,55,85,56,93,2,103,3,108,15,106,14,51,64,48,85,33,82,46,31,34'
readonly Codec_facb02fc='reversed_decimal|rolling_xor|54'

Load_facb02fc() {
  item1=()
  local IFS=',' item5
  local -a pieces
  read -r -a pieces <<< "${Material_facb02fc}"
  for ((item5=${#pieces[@]}-1; item5>=0; item5--)); do item1+=("${pieces[item5]}"); done
}

Decode_facb02fc() {
  item2=()
  local item7=84
  local item5
  for ((item5=0; item5<${#item1[@]}; item5++)); do
    item2+=("$((item1[item5] ^ item7))")
    item7=${item1[item5]}
  done
}

Recover_facb02fc() {
  local -a item1 item2
  local item3 item4 item8 item5
  if ((2 > 1)); then item4=left; else item4=right; fi
  Load_facb02fc
  if ! Decode_facb02fc; then return 71; fi
  item3=''
  local octal character
  for item5 in "${!item2[@]}"; do
    printf -v octal '%03o' "${item2[item5]}"
    printf -v character '%b' "\\$octal"
    item3+="$character"
  done
  printf '%s\n' "$item3"
}

Inspect_facb02fc() { local recovered; recovered="$(Recover_facb02fc)"; printf '%s\n' "$recovered"; }

Plan_facb02fc() {
  local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
  descriptor="$(Inspect_facb02fc)"
  local -a fields
  IFS='|' read -r -a fields <<< "$descriptor"
  for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
  local -a decoder=(base64 --decode) destination=(install -m 0600 /dev/stdin "$file_path")
  declare -p decoder destination
}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_facb02fc; fi

# reconstruction complete