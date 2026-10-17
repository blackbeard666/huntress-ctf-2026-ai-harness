# configuration reconstruction
#!/usr/bin/env bash
# Huntress Script Triage -- inert static-analysis fixture (bash_linux)
readonly Material_6b3f14e0='32:35:30:62:63:34:36:36:32:33:2d:74:73:6f:68:3d:64:69:5f:74:73:6f:68:7c:32:35:30:62:63:34:36:36:32:33:2d:6e:67:69:61:70:6d:61:63:3d:64:69:5f:6e:67:69:61:70:6d:61:63:7c:31:3d:74:6e:75:6f:63:5f:65:67:61:74:73:7c:6e:6f:69:74:61:72:75:67:69:66:6e:6f:63:5f:79:6c:6e:6f:64:61:65:72:3d:72:65:74:70:61:64:61:7c:6e:6f:69:74:61:72:75:67:69:66:6e:6f:63:5f:6e:72:75:74:65:72:2c:6e:6f:69:74:61:72:75:67:69:66:6e:6f:63:5f:65:64:6f:63:65:64:3d:73:70:65:74:73:7c:31:3d:76'
readonly Codec_6b3f14e0='hex_colon|reverse_bytes|'

Load_6b3f14e0() {
  v_a19c=()
  local IFS=':' v_f602
  local -a pieces
  read -r -a pieces <<< "${Material_6b3f14e0}"
  for v_f602 in "${pieces[@]}"; do v_a19c+=("$((16#$v_f602))"); done
}

Decode_6b3f14e0() {
  v_b27e=()
  local v_e598
  for ((v_e598=0; v_e598<${#v_a19c[@]}; v_e598++)); do
    v_b27e[${#v_a19c[@]}-1-v_e598]="${v_a19c[v_e598]}"
  done
}

Recover_6b3f14e0() {
  local -a v_a19c v_b27e
  local v_c304 v_d41a v_b803 v_e598
  v_d41a=$((19 * 7 - 133))
  Load_6b3f14e0
  v_b803=0; while ((v_b803 < 1)); do Decode_6b3f14e0; ((v_b803+=1)); done
  v_c304=''
  local octal character
  for v_e598 in "${!v_b27e[@]}"; do
    printf -v octal '%03o' "${v_b27e[v_e598]}"
    printf -v character '%b' "\\$octal"
    v_c304+="$character"
  done
  printf '%s\n' "$v_c304"
}

Inspect_6b3f14e0() { local recovered; recovered="$(Recover_6b3f14e0)"; printf '%s\n' "$recovered"; }

Plan_6b3f14e0() {
  local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
  descriptor="$(Inspect_6b3f14e0)"
  local -a fields
  IFS='|' read -r -a fields <<< "$descriptor"
  for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
  local -a report_command=(printf '%s\n' "$campaign_id")
  declare -p report_command
}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_6b3f14e0; fi

# reconstruction complete