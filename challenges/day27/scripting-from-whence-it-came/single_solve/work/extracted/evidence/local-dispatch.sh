#!/usr/bin/env bash

# Huntress Script Triage -- inert static-analysis fixture (bash_linux)

readonly Material_b53e3adf='30,36,79,79,84,82,84,84,30,34,27,83,85,79,98,97,28,29,83,86,81,79,81,27,97,97,83,96,98,92,99,86,29,94,91,98,29,43,86,98,79,94,77,83,90,87,84,106,30,36,79,79,84,82,84,84,30,34,27,92,85,87,79,94,91,79,81,43,82,87,77,92,85,87,79,94,91,79,81,106,31,43,98,92,99,93,81,77,83,85,79,98,97,106,96,93,98,94,87,96,81,97,83,82,77,81,83,102,83,43,96,83,98,94,79,82,79,106,97,97,83,81,93,96,94,77,86,81,98,79,94,97,87,82,26,90,79,81,93,90,77,83,98,79,81,93,90,43,97,94,83,98,97,106,31,43,100'

readonly Codec_b53e3adf='reversed_decimal|subtract_modulo_256|12'



Load_b53e3adf() {

  e=()

  local IFS=',' i

  local -a pieces

  read -r -a pieces <<< "${Material_b53e3adf}"

  for ((i=${#pieces[@]}-1; i>=0; i--)); do e+=("${pieces[i]}"); done

}



Decode_b53e3adf() {

  d=()

  local i

  for ((i=0; i<${#e[@]}; i++)); do

    d+=("$(((e[i] + 18) % 256))")

  done

}



Recover_b53e3adf() {

  local -a e d

  local t n z i

  if ((2 > 1)); then n=left; else n=right; fi

  Load_b53e3adf

  case 1 in 1) Decode_b53e3adf ;; *) return 70 ;; esac

  t=''

  local octal character

  for i in "${!d[@]}"; do

    printf -v octal '%03o' "${d[i]}"

    printf -v character '%b' "\\$octal"

    t+="$character"

  done

  printf '%s\n' "$t"

}



Inspect_b53e3adf() { Recover_b53e3adf; }



Plan_b53e3adf() {

  local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''

  descriptor="$(Inspect_b53e3adf)"

  local -a fields

  IFS='|' read -r -a fields <<< "$descriptor"

  for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done

  local -a launch_command=(env -- "$file_path")

  declare -p launch_command

}



if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_b53e3adf; fi

