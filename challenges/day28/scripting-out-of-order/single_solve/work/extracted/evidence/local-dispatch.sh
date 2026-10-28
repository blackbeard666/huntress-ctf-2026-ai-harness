#!/usr/bin/env bash
# Huntress Script Triage -- inert static-analysis fixture (bash_linux)
readonly Material_96a15bb3='96 48 100 48 49 48 48 102 61 61 40 96 98 100 113 118 43 42 96 109 102 100 102 40 118 118 96 119 113 107 112 109 42 117 104 113 42 56 109 113 100 117 90 96 105 108 99 121 96 48 100 48 49 48 48 102 61 61 40 107 98 108 100 117 104 100 102 56 97 108 90 107 98 108 100 117 104 100 102 121 52 56 113 107 112 106 102 90 96 98 100 113 118 121 113 117 108 119 102 118 90 109 118 56 119 96 113 117 100 97 100 121 118 118 96 102 106 119 117 90 109 102 113 100 117 118 108 97 41 105 100 102 106 105 90 96 113 100 102 106 105 56 118 117 96 113 118 121 52 56 115'
readonly Codec_96a15bb3='decimal_space|reverse_then_xor|05'

Load_96a15bb3() {
  e=()
  local IFS=' '
  read -r -a e <<< "${Material_96a15bb3}"
}

Decode_96a15bb3() {
  d=()
  local i
  for ((i=0; i<${#e[@]}; i++)); do
    d[${#e[@]}-1-i]="$((e[i] ^ 5))"
  done
}

Recover_96a15bb3() {
  local -a e d
  local t n z i
  n=$((19 * 7 - 133))
  Load_96a15bb3
  if ! Decode_96a15bb3; then return 71; fi
  t=''
  local octal character
  for i in "${!d[@]}"; do
    printf -v octal '%03o' "${d[i]}"
    printf -v character '%b' "\\$octal"
    t+="$character"
  done
  printf '%s\n' "$t"
}

Inspect_96a15bb3() { local recovered field; local -a fields; recovered="$(Recover_96a15bb3)"; IFS='|' read -r -a fields <<< "$recovered"; (IFS='|'; printf '%s\n' "${fields[*]}"); }

Plan_96a15bb3() {
  local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
  descriptor="$(Inspect_96a15bb3)"
  local -a fields
  IFS='|' read -r -a fields <<< "$descriptor"
  for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
  local -a launch_command=(sh "$file_path")
  declare -p launch_command
}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_96a15bb3; fi
