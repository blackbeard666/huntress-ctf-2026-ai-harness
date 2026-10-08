#!/usr/bin/env bash
# Huntress Script Triage -- inert static-analysis fixture (bash_linux)
readonly Material_4a7da36e='dj0xfHN0ZXBzPWxvY2F0ZV9sb2NhbCxkaXNwYXRjaF9wcm9jZXNzfGFkYXB0ZXI9YmFzaF9zY3JpcHR8c3RhZ2VfY291bnQ9MXxjYW1wYWlnbl9pZD1jYW1wYWlnbi1iYThjODBhYzZjfGZpbGVfcGF0aD0vdG1wL2h1bnRyZXNzLWNhY2hlLy5zdGFnZS1iYThjODBhYzZj'
readonly Codec_4a7da36e='base64_literal|identity|'

Load_4a7da36e() {
  item1=()
  local item6
  while read -r item6; do [[ -n "$item6" ]] && item1+=("$item6"); done < <(printf '%s' "${Material_4a7da36e}" | base64 --decode | od -An -v -tu1 | tr -s ' ' '\n' | sed '/^$/d')
}

Decode_4a7da36e() {
  item2=()
  local item5
  for ((item5=0; item5<${#item1[@]}; item5++)); do
    item2+=("${item1[item5]}")
  done
}

Recover_4a7da36e() {
  local -a item1 item2
  local item3 item4 item8 item5
  item4=''
  Load_4a7da36e
  item8=0; while ((item8 < 1)); do Decode_4a7da36e; ((item8+=1)); done
  item3=''
  local octal character
  for item5 in "${!item2[@]}"; do
    printf -v octal '%03o' "${item2[item5]}"
    printf -v character '%b' "\\$octal"
    item3+="$character"
  done
  printf '%s\n' "$item3"
}

Inspect_4a7da36e() { Recover_4a7da36e; }

Plan_4a7da36e() {
  local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
  descriptor="$(Inspect_4a7da36e)"
  local -a fields
  IFS='|' read -r -a fields <<< "$descriptor"
  for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
  local -a launch_command=(bash "$file_path")
  declare -p launch_command
}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_4a7da36e; fi
