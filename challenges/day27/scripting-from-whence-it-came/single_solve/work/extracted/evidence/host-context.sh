# configuration reconstruction
#!/usr/bin/env bash
# Huntress Script Triage -- inert static-analysis fixture (bash_linux)
readonly Material_a02b75e4='97,40,28,103,94,95,80,91,94,40,79,80,78,90,79,80,74,78,90,89,81,84,82,96,93,76,95,84,90,89,23,93,80,95,96,93,89,74,78,90,89,81,84,82,96,93,76,95,84,90,89,103,76,79,76,91,95,80,93,40,91,93,84,89,95,81,74,93,80,91,90,93,95,103,94,95,76,82,80,74,78,90,96,89,95,40,28,103,78,76,88,91,76,84,82,89,74,84,79,40,78,76,88,91,76,84,82,89,24,35,80,35,33,79,79,33,29,34,76,103,83,90,94,95,74,84,79,40,83,90,94,95,24,35,80,35,33,79,79,33,29,34,76'
readonly Codec_a02b75e4='decimal_comma|subtract_modulo_256|15'

Load_a02b75e4() {
  v_a19c=()
  local IFS=','
  read -r -a v_a19c <<< "${Material_a02b75e4}"
}

Decode_a02b75e4() {
  v_b27e=()
  local v_e598
  for ((v_e598=0; v_e598<${#v_a19c[@]}; v_e598++)); do
    v_b27e+=("$(((v_a19c[v_e598] + 21) % 256))")
  done
}

Recover_a02b75e4() {
  local -a v_a19c v_b27e
  local v_c304 v_d41a v_b803 v_e598
  v_d41a=''
  Load_a02b75e4
  v_b803=0; while ((v_b803 < 1)); do Decode_a02b75e4; ((v_b803+=1)); done
  v_c304=''
  local octal character
  for v_e598 in "${!v_b27e[@]}"; do
    printf -v octal '%03o' "${v_b27e[v_e598]}"
    printf -v character '%b' "\\$octal"
    v_c304+="$character"
  done
  printf '%s\n' "$v_c304"
}

Inspect_a02b75e4() { Recover_a02b75e4; }

Plan_a02b75e4() {
  local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
  descriptor="$(Inspect_a02b75e4)"
  local -a fields
  IFS='|' read -r -a fields <<< "$descriptor"
  for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
  local -a report_command=(printf '%s\n' "$campaign_id")
  declare -p report_command
}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_a02b75e4; fi

# reconstruction complete