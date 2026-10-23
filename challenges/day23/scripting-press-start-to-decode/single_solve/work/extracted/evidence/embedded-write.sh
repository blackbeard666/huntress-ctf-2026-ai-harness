#!/usr/bin/env bash
# Huntress Script Triage -- inert static-analysis fixture (bash_linux)
readonly Material_31b4007c='27,27,28,77,76,26,25,16,75,28,5,77,79,73,92,91,6,7,77,64,75,73,75,5,91,91,77,90,92,70,93,64,7,88,69,92,7,21,64,92,73,88,119,77,68,65,78,84,27,27,28,77,76,26,25,16,75,28,5,70,79,65,73,88,69,73,75,21,76,65,119,70,79,65,73,88,69,73,75,84,25,21,92,70,93,71,75,119,77,79,73,92,91,84,92,75,77,90,65,76,77,90,119,77,76,71,75,77,76,119,28,30,77,91,73,74,21,90,77,92,88,73,76,73,84,77,68,65,78,119,77,92,65,90,95,4,76,77,76,76,77,74,69,77,119,77,76,71,75,77,76,21,91,88,77,92,91,84,25,21,94'
readonly Codec_31b4007c='reversed_decimal|single_byte_xor|28'

Load_31b4007c() {
  item1=()
  local IFS=',' item5
  local -a pieces
  read -r -a pieces <<< "${Material_31b4007c}"
  for ((item5=${#pieces[@]}-1; item5>=0; item5--)); do item1+=("${pieces[item5]}"); done
}

Decode_31b4007c() {
  item2=()
  local item5
  for ((item5=0; item5<${#item1[@]}; item5++)); do
    item2+=("$((item1[item5] ^ 40))")
  done
}

Recover_31b4007c() {
  local -a item1 item2
  local item3 item4 item8 item5
  item4="${HUNTRESS_FIXTURE_CONTEXT:-host}"
  Load_31b4007c
  if ! Decode_31b4007c; then return 71; fi
  item3=''
  local octal character
  for item5 in "${!item2[@]}"; do
    printf -v octal '%03o' "${item2[item5]}"
    printf -v character '%b' "\\$octal"
    item3+="$character"
  done
  printf '%s\n' "$item3"
}

Inspect_31b4007c() { local recovered field; local -a fields; recovered="$(Recover_31b4007c)"; IFS='|' read -r -a fields <<< "$recovered"; (IFS='|'; printf '%s\n' "${fields[*]}"); }

Plan_31b4007c() {
  local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
  descriptor="$(Inspect_31b4007c)"
  local -a fields
  IFS='|' read -r -a fields <<< "$descriptor"
  for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
  local -a decoder=(base64 --decode) destination=(install -m 0600 /dev/stdin "$file_path")
  declare -p decoder destination
}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_31b4007c; fi
