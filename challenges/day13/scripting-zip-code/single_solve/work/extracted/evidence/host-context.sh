#!/usr/bin/env bash

# Huntress Script Triage -- inert static-analysis fixture (bash_linux)

readonly Material_d8abdc63='%76%3d%31%7c%73%74%65%70%73%3d%64%65%63%6f%64%65%5f%63%6f%6e%66%69%67%75%72%61%74%69%6f%6e%2c%72%65%74%75%72%6e%5f%63%6f%6e%66%69%67%75%72%61%74%69%6f%6e%7c%61%64%61%70%74%65%72%3d%72%65%61%64%6f%6e%6c%79%5f%63%6f%6e%66%69%67%75%72%61%74%69%6f%6e%7c%73%74%61%67%65%5f%63%6f%75%6e%74%3d%31%7c%63%61%6d%70%61%69%67%6e%5f%69%64%3d%63%61%6d%70%61%69%67%6e%2d%61%61%30%61%62%38%31%38%39%35%7c%68%6f%73%74%5f%69%64%3d%68%6f%73%74%2d%61%61%30%61%62%38%31%38%39%35'

readonly Codec_d8abdc63='percent_hex|identity|'



Load_d8abdc63() {

  v_a19c=()

  local raw="${Material_d8abdc63}" v_f602

  for v_f602 in ${raw//%/ }; do [[ -n "$v_f602" ]] && v_a19c+=("$((16#$v_f602))"); done

}



Decode_d8abdc63() {

  v_b27e=()

  local v_e598

  for ((v_e598=0; v_e598<${#v_a19c[@]}; v_e598++)); do

    v_b27e+=("${v_a19c[v_e598]}")

  done

}



Recover_d8abdc63() {

  local -a v_a19c v_b27e

  local v_c304 v_d41a v_b803 v_e598

  v_d41a=$((19 * 7 - 133))

  Load_d8abdc63

  if ! Decode_d8abdc63; then return 71; fi

  v_c304=''

  local octal character

  for v_e598 in "${!v_b27e[@]}"; do

    printf -v octal '%03o' "${v_b27e[v_e598]}"

    printf -v character '%b' "\\$octal"

    v_c304+="$character"

  done

  printf '%s\n' "$v_c304"

}



Inspect_d8abdc63() { Recover_d8abdc63; }



Plan_d8abdc63() {

  local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''

  descriptor="$(Inspect_d8abdc63)"

  local -a fields

  IFS='|' read -r -a fields <<< "$descriptor"

  for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done

  local -a report_command=(printf '%s\n' "$campaign_id")

  declare -p report_command

}



if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_d8abdc63; fi

