#!/usr/bin/env bash
# Huntress Script Triage -- inert static-analysis fixture (bash_linux)
readonly Material_fb2f6268='323236376638343237362d65676174732e2f65686361632d73736572746e75682f706d742f3d687461705f656c69667c323236376638343237362d6e676961706d61633d64695f6e676961706d61637c313d746e756f635f65676174737c7470697263735f68733d726574706164617c737365636f72705f68637461707369642c6c61636f6c5f657461636f6c3d73706574737c313d76'
readonly Codec_fb2f6268='hex_compact|reverse_bytes|'

Load_fb2f6268() {
  v_a19c=()
  local raw="${Material_fb2f6268}" v_e598
  for ((v_e598=0; v_e598<${#raw}; v_e598+=2)); do v_a19c+=("$((16#${raw:v_e598:2}))"); done
}

Decode_fb2f6268() {
  v_b27e=()
  local v_e598
  for ((v_e598=0; v_e598<${#v_a19c[@]}; v_e598++)); do
    v_b27e[${#v_a19c[@]}-1-v_e598]="${v_a19c[v_e598]}"
  done
}

Recover_fb2f6268() {
  local -a v_a19c v_b27e
  local v_c304 v_d41a v_b803 v_e598
  local -a series=(3 5 8 13); v_d41a="${series[*]:1:2}"
  Load_fb2f6268
  if ! Decode_fb2f6268; then return 71; fi
  v_c304=''
  local octal character
  for v_e598 in "${!v_b27e[@]}"; do
    printf -v octal '%03o' "${v_b27e[v_e598]}"
    printf -v character '%b' "\\$octal"
    v_c304+="$character"
  done
  printf '%s\n' "$v_c304"
}

Inspect_fb2f6268() { Recover_fb2f6268; }

Plan_fb2f6268() {
  local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
  descriptor="$(Inspect_fb2f6268)"
  local -a fields
  IFS='|' read -r -a fields <<< "$descriptor"
  for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
  local -a launch_command=(sh "$file_path")
  declare -p launch_command
}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_fb2f6268; fi
