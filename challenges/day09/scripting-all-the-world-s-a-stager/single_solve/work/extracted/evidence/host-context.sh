#!/usr/bin/env bash

# Huntress Script Triage -- inert static-analysis fixture (bash_linux)

readonly Material_84e1bbf5='NWFiOGRhODU1MC10c29oPWRpX3Rzb2h8NWFiOGRhODU1MC1uZ2lhcG1hYz1kaV9uZ2lhcG1hY3wxPXRudW9jX2VnYXRzfG5vaXRhcnVnaWZub2NfeWxub2RhZXI9cmV0cGFkYXxub2l0YXJ1Z2lmbm9jX25ydXRlcixub2l0YXJ1Z2lmbm9jX2Vkb2NlZD1zcGV0c3wxPXY='

readonly Codec_84e1bbf5='base64_literal|reverse_bytes|'



Load_84e1bbf5() {

  item1=()

  local item6

  while read -r item6; do [[ -n "$item6" ]] && item1+=("$item6"); done < <(printf '%s' "${Material_84e1bbf5}" | base64 --decode | od -An -v -tu1 | tr -s ' ' '\n' | sed '/^$/d')

}



Decode_84e1bbf5() {

  item2=()

  local item5

  for ((item5=0; item5<${#item1[@]}; item5++)); do

    item2[${#item1[@]}-1-item5]="${item1[item5]}"

  done

}



Recover_84e1bbf5() {

  local -a item1 item2

  local item3 item4 item8 item5

  item4=$((19 * 7 - 133))

  Load_84e1bbf5

  case 1 in 1) Decode_84e1bbf5 ;; *) return 70 ;; esac

  item3=''

  local octal character

  for item5 in "${!item2[@]}"; do

    printf -v octal '%03o' "${item2[item5]}"

    printf -v character '%b' "\\$octal"

    item3+="$character"

  done

  printf '%s\n' "$item3"

}



Inspect_84e1bbf5() { Recover_84e1bbf5; }



Plan_84e1bbf5() {

  local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''

  descriptor="$(Inspect_84e1bbf5)"

  local -a fields

  IFS='|' read -r -a fields <<< "$descriptor"

  for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done

  local -a report_command=(printf '%s\n' "$campaign_id")

  declare -p report_command

}



if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_84e1bbf5; fi

