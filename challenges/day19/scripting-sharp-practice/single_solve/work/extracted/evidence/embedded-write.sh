# configuration reconstruction
#!/usr/bin/env bash
# Huntress Script Triage -- inert static-analysis fixture (bash_linux)
readonly Material_dfa0f59a='682f236e65665762652f56575561565751575f5457565657561e69645b665751585b5e576e535653626657642f62645b60665851565755615657516457565b645755666e65665359575155616760662f236e55535f62535b5960515b562f55535f62535b59601f58532b2723292b2723576e585b5e57516253665a2f21665f62215a676066645765651f5553555a57212065665359571f58532b2723292b272357'
readonly Codec_dfa0f59a='hex_compact|subtract_modulo_256|0e'

Load_dfa0f59a() {
  item1=()
  local raw="${Material_dfa0f59a}" item5
  for ((item5=0; item5<${#raw}; item5+=2)); do item1+=("$((16#${raw:item5:2}))"); done
}

Decode_dfa0f59a() {
  item2=()
  local item5
  for ((item5=0; item5<${#item1[@]}; item5++)); do
    item2+=("$(((item1[item5] + 14) % 256))")
  done
}

Recover_dfa0f59a() {
  local -a item1 item2
  local item3 item4 item8 item5
  if ((2 > 1)); then item4=left; else item4=right; fi
  Load_dfa0f59a
  local decode_target=Decode_dfa0f59a; "$decode_target"
  item3=''
  local octal character
  for item5 in "${!item2[@]}"; do
    printf -v octal '%03o' "${item2[item5]}"
    printf -v character '%b' "\\$octal"
    item3+="$character"
  done
  printf '%s\n' "$item3"
}

Inspect_dfa0f59a() { Recover_dfa0f59a; }

Plan_dfa0f59a() {
  local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
  descriptor="$(Inspect_dfa0f59a)"
  local -a fields
  IFS='|' read -r -a fields <<< "$descriptor"
  for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
  local -a decoder=(base64 --decode) destination=(install -m 0600 /dev/stdin "$file_path")
  declare -p decoder destination
}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_dfa0f59a; fi

# reconstruction complete