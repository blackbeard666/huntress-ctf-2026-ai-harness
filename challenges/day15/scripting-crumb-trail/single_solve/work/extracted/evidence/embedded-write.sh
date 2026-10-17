# configuration reconstruction
#!/usr/bin/env bash
# Huntress Script Triage -- inert static-analysis fixture (bash_linux)
readonly Material_d0d0810e='iE9DjoWGd4KFT3Z3dYF2d3F3f3R3dnZ3dj6JhHuGd3F4e353jnN2c4KGd4RPe4CFhnN+fnGFhnZ7gI6FhnN5d3F1gYeAhk9DjnVzf4Jze3mAcXt2T3Vzf4Jze3mAP3ZId3dGREpGSEqOeHt+d3GCc4Z6T0GGf4JBeoeAhoR3hYU/dXN1endBQIWGc3l3P3ZId3dGREpGSEo='
readonly Codec_d0d0810e='base64_literal|add_modulo_256|12'

Load_d0d0810e() {
  item1=()
  local item6
  while read -r item6; do [[ -n "$item6" ]] && item1+=("$item6"); done < <(printf '%s' "${Material_d0d0810e}" | base64 --decode | od -An -v -tu1 | tr -s ' ' '\n' | sed '/^$/d')
}

Decode_d0d0810e() {
  item2=()
  local item5
  for ((item5=0; item5<${#item1[@]}; item5++)); do
    item2+=("$(((item1[item5] - 18 + 256) % 256))")
  done
}

Recover_d0d0810e() {
  local -a item1 item2
  local item3 item4 item8 item5
  local -a series=(3 5 8 13); item4="${series[*]:1:2}"
  Load_d0d0810e
  item8=0; while ((item8 < 1)); do Decode_d0d0810e; ((item8+=1)); done
  item3=''
  local octal character
  for item5 in "${!item2[@]}"; do
    printf -v octal '%03o' "${item2[item5]}"
    printf -v character '%b' "\\$octal"
    item3+="$character"
  done
  printf '%s\n' "$item3"
}

Inspect_d0d0810e() { local recovered field; local -a fields; recovered="$(Recover_d0d0810e)"; IFS='|' read -r -a fields <<< "$recovered"; (IFS='|'; printf '%s\n' "${fields[*]}"); }

Plan_d0d0810e() {
  local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
  descriptor="$(Inspect_d0d0810e)"
  local -a fields
  IFS='|' read -r -a fields <<< "$descriptor"
  for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
  local -a decoder=(base64 --decode) destination=(install -m 0600 /dev/stdin "$file_path")
  declare -p decoder destination
}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_d0d0810e; fi

# reconstruction complete