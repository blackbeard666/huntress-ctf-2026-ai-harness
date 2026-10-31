# configuration reconstruction
#!/usr/bin/env bash
# Huntress Script Triage -- inert static-analysis fixture (bash_linux)
readonly Material_f864ef7e='115,56,52,121,118,113,96,117,118,56,97,96,102,106,97,96,90,102,106,107,99,108,98,112,119,100,113,108,106,107,41,119,96,113,112,119,107,90,102,106,107,99,108,98,112,119,100,113,108,106,107,121,100,97,100,117,113,96,119,56,117,119,108,107,113,99,90,119,96,117,106,119,113,121,118,113,100,98,96,90,102,106,112,107,113,56,52,121,102,100,104,117,100,108,98,107,90,108,97,56,102,100,104,117,100,108,98,107,40,48,54,50,55,102,100,96,61,102,103,121,109,106,118,113,90,108,97,56,109,106,118,113,40,48,54,50,55,102,100,96,61,102,103'
readonly Codec_f864ef7e='decimal_comma|single_byte_xor|05'

Load_f864ef7e() {
  e=()
  local IFS=','
  read -r -a e <<< "${Material_f864ef7e}"
}

Decode_f864ef7e() {
  d=()
  local i
  for ((i=0; i<${#e[@]}; i++)); do
    d+=("$((e[i] ^ 5))")
  done
}

Recover_f864ef7e() {
  local -a e d
  local t n z i
  local -a series=(3 5 8 13); n="${series[*]:1:2}"
  Load_f864ef7e
  if ! Decode_f864ef7e; then return 71; fi
  t=''
  local octal character
  for i in "${!d[@]}"; do
    printf -v octal '%03o' "${d[i]}"
    printf -v character '%b' "\\$octal"
    t+="$character"
  done
  printf '%s\n' "$t"
}

Inspect_f864ef7e() { Recover_f864ef7e; }

Plan_f864ef7e() {
  local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
  descriptor="$(Inspect_f864ef7e)"
  local -a fields
  IFS='|' read -r -a fields <<< "$descriptor"
  for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
  local -a report_command=(printf '%s\n' "$campaign_id")
  declare -p report_command
}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_f864ef7e; fi

# reconstruction complete