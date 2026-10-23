#!/usr/bin/env bash
# Huntress Script Triage -- inert static-analysis fixture (bash_linux)
readonly Material_db64e33a='118 61 49 124 115 116 101 112 115 61 108 111 99 97 116 101 95 108 111 99 97 108 44 100 105 115 112 97 116 99 104 95 112 114 111 99 101 115 115 124 97 100 97 112 116 101 114 61 101 120 101 99 95 100 101 115 99 114 105 112 116 111 114 124 115 116 97 103 101 95 99 111 117 110 116 61 49 124 99 97 109 112 97 105 103 110 95 105 100 61 99 97 109 112 97 105 103 110 45 55 52 98 52 50 57 57 99 53 53 124 102 105 108 101 95 112 97 116 104 61 47 116 109 112 47 104 117 110 116 114 101 115 115 45 99 97 99 104 101 47 46 115 116 97 103 101 45 55 52 98 52 50 57 57 99 53 53'
readonly Codec_db64e33a='decimal_space|identity|'

Load_db64e33a() {
  item1=()
  local IFS=' '
  read -r -a item1 <<< "${Material_db64e33a}"
}

Decode_db64e33a() {
  item2=()
  local item5
  for ((item5=0; item5<${#item1[@]}; item5++)); do
    item2+=("${item1[item5]}")
  done
}

Recover_db64e33a() {
  local -a item1 item2
  local item3 item4 item8 item5
  local -a compass=(north south); item4="$(IFS=:; printf '%s' "${compass[*]}")"
  Load_db64e33a
  for item8 in 1; do Decode_db64e33a; done
  item3=''
  local octal character
  for item5 in "${!item2[@]}"; do
    printf -v octal '%03o' "${item2[item5]}"
    printf -v character '%b' "\\$octal"
    item3+="$character"
  done
  printf '%s\n' "$item3"
}

Inspect_db64e33a() { local recovered field; local -a fields; recovered="$(Recover_db64e33a)"; IFS='|' read -r -a fields <<< "$recovered"; (IFS='|'; printf '%s\n' "${fields[*]}"); }

Plan_db64e33a() {
  local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
  descriptor="$(Inspect_db64e33a)"
  local -a fields
  IFS='|' read -r -a fields <<< "$descriptor"
  for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
  local -a launch_command=(env -- "$file_path")
  declare -p launch_command
}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_db64e33a; fi
