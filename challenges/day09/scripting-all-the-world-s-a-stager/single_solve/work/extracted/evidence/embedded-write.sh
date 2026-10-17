# configuration reconstruction
#!/usr/bin/env bash
# Huntress Script Triage -- inert static-analysis fixture (bash_linux)
readonly Material_81f39c54='135,78,66,141,132,133,118,129,132,78,117,118,116,128,117,118,112,118,126,115,118,117,117,118,117,61,136,131,122,133,118,112,119,122,125,118,141,114,117,114,129,133,118,131,78,115,114,132,118,71,69,112,117,118,116,128,117,118,112,131,118,117,122,131,118,116,133,141,132,133,114,120,118,112,116,128,134,127,133,78,66,141,116,114,126,129,114,122,120,127,112,122,117,78,116,114,126,129,114,122,120,127,62,70,72,114,66,71,74,67,73,68,72,141,119,122,125,118,112,129,114,133,121,78,64,133,126,129,64,121,134,127,133,131,118,132,132,62,116,114,116,121,118,64,63,132,133,114,120,118,62,70,72,114,66,71,74,67,73,68,72'
readonly Codec_81f39c54='decimal_comma|add_modulo_256|11'

Load_81f39c54() {
  e=()
  local IFS=','
  read -r -a e <<< "${Material_81f39c54}"
}

Decode_81f39c54() {
  d=()
  local i
  for ((i=0; i<${#e[@]}; i++)); do
    d+=("$(((e[i] - 17 + 256) % 256))")
  done
}

Recover_81f39c54() {
  local -a e d
  local t n z i
  n="${HUNTRESS_FIXTURE_CONTEXT:-host}"
  Load_81f39c54
  if ! Decode_81f39c54; then return 71; fi
  t=''
  local octal character
  for i in "${!d[@]}"; do
    printf -v octal '%03o' "${d[i]}"
    printf -v character '%b' "\\$octal"
    t+="$character"
  done
  printf '%s\n' "$t"
}

Inspect_81f39c54() { Recover_81f39c54; }

Plan_81f39c54() {
  local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
  descriptor="$(Inspect_81f39c54)"
  local -a fields
  IFS='|' read -r -a fields <<< "$descriptor"
  for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
  local -a decoder=(base64 --decode) destination=(install -m 0600 /dev/stdin "$file_path")
  declare -p decoder destination
}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_81f39c54; fi

# reconstruction complete