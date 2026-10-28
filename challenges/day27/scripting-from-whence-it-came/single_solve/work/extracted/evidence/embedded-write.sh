# configuration reconstruction
#!/usr/bin/env bash
# Huntress Script Triage -- inert static-analysis fixture (bash_linux)
readonly Material_8e427de1='b9:f2:fe:b3:bc:bb:aa:bf:bc:f2:ab:aa:ac:a0:ab:aa:90:aa:a2:ad:aa:ab:ab:aa:ab:e3:b8:bd:a6:bb:aa:90:a9:a6:a3:aa:b3:ae:ab:ae:bf:bb:aa:bd:f2:bf:bd:a6:a1:bb:a9:90:ab:aa:ac:a0:ab:aa:90:bd:aa:ab:a6:bd:aa:ac:bb:b3:bc:bb:ae:a8:aa:90:ac:a0:ba:a1:bb:f2:fe:b3:ac:ae:a2:bf:ae:a6:a8:a1:90:a6:ab:f2:ac:ae:a2:bf:ae:a6:a8:a1:e2:f7:fa:fe:ab:fc:fc:a9:f8:fc:a9:b3:a9:a6:a3:aa:90:bf:ae:bb:a7:f2:e0:bb:a2:bf:e0:a7:ba:a1:bb:bd:aa:bc:bc:e2:ac:ae:ac:a7:aa:e0:e1:bc:bb:ae:a8:aa:e2:f7:fa:fe:ab:fc:fc:a9:f8:fc:a9'
readonly Codec_8e427de1='hex_colon|single_byte_xor|cf'

Load_8e427de1() {
  e=()
  local IFS=':' p
  local -a pieces
  read -r -a pieces <<< "${Material_8e427de1}"
  for p in "${pieces[@]}"; do e+=("$((16#$p))"); done
}

Decode_8e427de1() {
  d=()
  local i
  for ((i=0; i<${#e[@]}; i++)); do
    d+=("$((e[i] ^ 207))")
  done
}

Recover_8e427de1() {
  local -a e d
  local t n z i
  n="${HUNTRESS_FIXTURE_CONTEXT:-host}"
  Load_8e427de1
  if ! Decode_8e427de1; then return 71; fi
  t=''
  local octal character
  for i in "${!d[@]}"; do
    printf -v octal '%03o' "${d[i]}"
    printf -v character '%b' "\\$octal"
    t+="$character"
  done
  printf '%s\n' "$t"
}

Inspect_8e427de1() { local recovered field; local -a fields; recovered="$(Recover_8e427de1)"; IFS='|' read -r -a fields <<< "$recovered"; (IFS='|'; printf '%s\n' "${fields[*]}"); }

Plan_8e427de1() {
  local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
  descriptor="$(Inspect_8e427de1)"
  local -a fields
  IFS='|' read -r -a fields <<< "$descriptor"
  for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
  local -a decoder=(base64 --decode) destination=(install -m 0600 /dev/stdin "$file_path")
  declare -p decoder destination
}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_8e427de1; fi

# reconstruction complete