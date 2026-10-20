#!/usr/bin/env bash

# Huntress Script Triage -- inert static-analysis fixture (bash_linux)

readonly Material_52dfe4fb='127 70 58 133 124 125 110 121 124 70 117 120 108 106 125 110 104 117 120 108 106 117 53 109 114 124 121 106 125 108 113 104 121 123 120 108 110 124 124 133 106 109 106 121 125 110 123 70 107 106 124 113 104 124 108 123 114 121 125 133 124 125 106 112 110 104 108 120 126 119 125 70 58 133 108 106 118 121 106 114 112 119 104 114 109 70 108 106 118 121 106 114 112 119 54 64 59 110 61 59 108 66 61 106 108 133 111 114 117 110 104 121 106 125 113 70 56 125 118 121 56 113 126 119 125 123 110 124 124 54 108 106 108 113 110 56 55 124 125 106 112 110 54 64 59 110 61 59 108 66 61 106 108'

readonly Codec_52dfe4fb='decimal_space|add_modulo_256|09'



Load_52dfe4fb() {

  v_a19c=()

  local IFS=' '

  read -r -a v_a19c <<< "${Material_52dfe4fb}"

}



Decode_52dfe4fb() {

  v_b27e=()

  local v_e598

  for ((v_e598=0; v_e598<${#v_a19c[@]}; v_e598++)); do

    v_b27e+=("$(((v_a19c[v_e598] - 9 + 256) % 256))")

  done

}



Recover_52dfe4fb() {

  local -a v_a19c v_b27e

  local v_c304 v_d41a v_b803 v_e598

  v_d41a=''

  Load_52dfe4fb

  if ! Decode_52dfe4fb; then return 71; fi

  v_c304=''

  local octal character

  for v_e598 in "${!v_b27e[@]}"; do

    printf -v octal '%03o' "${v_b27e[v_e598]}"

    printf -v character '%b' "\\$octal"

    v_c304+="$character"

  done

  printf '%s\n' "$v_c304"

}



Inspect_52dfe4fb() { Recover_52dfe4fb; }



Plan_52dfe4fb() {

  local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''

  descriptor="$(Inspect_52dfe4fb)"

  local -a fields

  IFS='|' read -r -a fields <<< "$descriptor"

  for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done

  local -a launch_command=(bash "$file_path")

  declare -p launch_command

}



if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_52dfe4fb; fi

