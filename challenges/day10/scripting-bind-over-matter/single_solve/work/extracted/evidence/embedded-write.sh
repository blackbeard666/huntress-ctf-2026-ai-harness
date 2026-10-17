#!/usr/bin/env bash

# Huntress Script Triage -- inert static-analysis fixture (bash_linux)

readonly Material_f7be233e='114:57:45:120:111:112:97:108:111:57:96:97:95:107:96:97:91:97:105:94:97:96:96:97:96:40:115:110:101:112:97:91:98:101:104:97:120:93:96:93:108:112:97:110:57:94:93:111:97:50:48:91:96:97:95:107:96:97:91:110:97:96:101:110:97:95:112:120:111:112:93:99:97:91:95:107:113:106:112:57:45:120:95:93:105:108:93:101:99:106:91:101:96:57:95:93:105:108:93:101:99:106:41:49:52:47:46:51:48:95:45:52:44:120:98:101:104:97:91:108:93:112:100:57:43:112:105:108:43:100:113:106:112:110:97:111:111:41:95:93:95:100:97:43:42:111:112:93:99:97:41:49:52:47:46:51:48:95:45:52:44'

readonly Codec_f7be233e='decimal_colon|subtract_modulo_256|04'



Load_f7be233e() {

  v_a19c=()

  local IFS=':'

  read -r -a v_a19c <<< "${Material_f7be233e}"

}



Decode_f7be233e() {

  v_b27e=()

  local v_e598

  for ((v_e598=0; v_e598<${#v_a19c[@]}; v_e598++)); do

    v_b27e+=("$(((v_a19c[v_e598] + 4) % 256))")

  done

}



Recover_f7be233e() {

  local -a v_a19c v_b27e

  local v_c304 v_d41a v_b803 v_e598

  v_d41a=$((19 * 7 - 133))

  Load_f7be233e

  case 1 in 1) Decode_f7be233e ;; *) return 70 ;; esac

  v_c304=''

  local octal character

  for v_e598 in "${!v_b27e[@]}"; do

    printf -v octal '%03o' "${v_b27e[v_e598]}"

    printf -v character '%b' "\\$octal"

    v_c304+="$character"

  done

  printf '%s\n' "$v_c304"

}



Inspect_f7be233e() { Recover_f7be233e; }



Plan_f7be233e() {

  local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''

  descriptor="$(Inspect_f7be233e)"

  local -a fields

  IFS='|' read -r -a fields <<< "$descriptor"

  for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done

  local -a decoder=(base64 --decode) destination=(install -m 0600 /dev/stdin "$file_path")

  declare -p decoder destination

}



if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_f7be233e; fi

