# configuration reconstruction
#!/usr/bin/env bash
# Huntress Script Triage -- inert static-analysis fixture (bash_linux)
readonly Material_5151f01a='663238363831626665642d65676174732e2f65686361632d73736572746e75682f706d742f3d687461705f656c69667c663238363831626665642d6e676961706d61633d64695f6e676961706d61637c313d746e756f635f65676174737c74636572696465725f65646f6365645f3436657361623d726574706164617c656c69665f65746972772c6465646465626d655f65646f6365643d73706574737c313d76'
readonly Codec_5151f01a='hex_compact|reverse_bytes|'

Load_5151f01a() {
  item1=()
  local raw="${Material_5151f01a}" item5
  for ((item5=0; item5<${#raw}; item5+=2)); do item1+=("$((16#${raw:item5:2}))"); done
}

Decode_5151f01a() {
  item2=()
  local item5
  for ((item5=0; item5<${#item1[@]}; item5++)); do
    item2[${#item1[@]}-1-item5]="${item1[item5]}"
  done
}

Recover_5151f01a() {
  local -a item1 item2
  local item3 item4 item8 item5
  item4="${HUNTRESS_FIXTURE_CONTEXT:-host}"
  Load_5151f01a
  if ! Decode_5151f01a; then return 71; fi
  item3=''
  local octal character
  for item5 in "${!item2[@]}"; do
    printf -v octal '%03o' "${item2[item5]}"
    printf -v character '%b' "\\$octal"
    item3+="$character"
  done
  printf '%s\n' "$item3"
}

Inspect_5151f01a() { local recovered; recovered="$(Recover_5151f01a)"; printf '%s\n' "$recovered"; }

Plan_5151f01a() {
  local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
  descriptor="$(Inspect_5151f01a)"
  local -a fields
  IFS='|' read -r -a fields <<< "$descriptor"
  for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
  local -a decoder=(base64 --decode) destination=(install -m 0600 /dev/stdin "$file_path")
  declare -p decoder destination
}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_5151f01a; fi

# reconstruction complete