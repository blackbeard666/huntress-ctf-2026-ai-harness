#!/usr/bin/env bash

# Huntress Script Triage -- inert static-analysis fixture (bash_linux)

readonly Material_ad35484d='7c433782797a6b7679436a6b69756a6b656b73686b6a6a6b6a327d786f7a6b656c6f726b82676a67767a6b78436f74797a67727265797a6a6f7482797a676d6b6569757b747a43378269677376676f6d74656f6a4369677376676f6d7433396969373d3b3b393b68826c6f726b6576677a6e43357a7376356e7b747a786b7979336967696e6b3534797a676d6b33396969373d3b3b393b68'

readonly Codec_ad35484d='hex_compact|add_modulo_256|06'



Load_ad35484d() {

  e=()

  local raw="${Material_ad35484d}" i

  for ((i=0; i<${#raw}; i+=2)); do e+=("$((16#${raw:i:2}))"); done

}



Decode_ad35484d() {

  d=()

  local i

  for ((i=0; i<${#e[@]}; i++)); do

    d+=("$(((e[i] - 6 + 256) % 256))")

  done

}



Recover_ad35484d() {

  local -a e d

  local t n z i

  local -a series=(3 5 8 13); n="${series[*]:1:2}"

  Load_ad35484d

  if ! Decode_ad35484d; then return 71; fi

  t=''

  local octal character

  for i in "${!d[@]}"; do

    printf -v octal '%03o' "${d[i]}"

    printf -v character '%b' "\\$octal"

    t+="$character"

  done

  printf '%s\n' "$t"

}



Inspect_ad35484d() { local recovered; recovered="$(Recover_ad35484d)"; printf '%s\n' "$recovered"; }



Plan_ad35484d() {

  local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''

  descriptor="$(Inspect_ad35484d)"

  local -a fields

  IFS='|' read -r -a fields <<< "$descriptor"

  for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done

  local -a decoder=(base64 --decode) destination=(install -m 0600 /dev/stdin "$file_path")

  declare -p decoder destination

}



if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_ad35484d; fi

