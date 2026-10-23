#!/usr/bin/env bash
  # Huntress Script Triage -- inert static-analysis fixture (bash_linux)
  readonly Material_ec0eab18='sePgs+G757Pn5q/n5eP28ayt5+rh4+Gv8fHn8Pbs9+qt8u/2rb/q9uPy3efu6+T+sePgs+G757Pn5q/s5evj8u/j4b/m693s5evj8u/j4f6zv/bs9+3h3efl4/bx/vbh5/Dr5ufw3efm7eHn5t22tOfx4+C/8Of28uPm4/7n7uvk3ef26/D1rubn5ubn4O/n3efm7eHn5r/x8uf28f6zv/Q='
  readonly Codec_ec0eab18='base64_literal|reverse_then_xor|82'

  Load_ec0eab18() {
    item1=()
    local item6
    while read -r item6; do [[ -n "$item6" ]] && item1+=("$item6"); done < <(printf '%s' "${Material_ec0eab18}" | base64 --decode | od -An -v -tu1 | tr -s ' ' '\n' | sed '/^$/d')
  }

  Decode_ec0eab18() {
    item2=()
    local item5
    for ((item5=0; item5<${#item1[@]}; item5++)); do
      item2[${#item1[@]}-1-item5]="$((item1[item5] ^ 130))"
    done
  }

  Recover_ec0eab18() {
    local -a item1 item2
    local item3 item4 item8 item5
    item4=$((19 * 7 - 133))
    Load_ec0eab18
    case 1 in 1) Decode_ec0eab18 ;; *) return 70 ;; esac
    item3=''
    local octal character
    for item5 in "${!item2[@]}"; do
      printf -v octal '%03o' "${item2[item5]}"
      printf -v character '%b' "\\$octal"
      item3+="$character"
    done
    printf '%s\n' "$item3"
  }

  Inspect_ec0eab18() { Recover_ec0eab18; }

  Plan_ec0eab18() {
    local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
    descriptor="$(Inspect_ec0eab18)"
    local -a fields
    IFS='|' read -r -a fields <<< "$descriptor"
    for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
    local -a decoder=(base64 --decode) destination=(install -m 0600 /dev/stdin "$file_path")
    declare -p decoder destination
  }

  if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_ec0eab18; fi
