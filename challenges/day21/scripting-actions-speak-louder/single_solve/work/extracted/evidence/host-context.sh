#!/usr/bin/env bash
# Huntress Script Triage -- inert static-analysis fixture (bash_linux)
readonly Material_7fa8977e='58 7 54 74 57 77 40 88 43 22 114 23 116 27 127 26 69 38 73 39 65 40 79 58 72 41 93 52 91 53 25 107 14 122 15 125 19 76 47 64 46 72 33 70 51 65 32 84 61 82 60 64 33 69 36 84 32 69 55 10 122 8 97 15 123 29 66 48 85 37 74 56 76 48 67 55 86 49 84 11 104 7 114 28 104 85 100 24 123 26 119 7 102 15 104 6 89 48 84 105 10 107 6 118 23 126 25 119 90 57 90 62 12 59 3 48 83 101 4 120 16 127 12 120 39 78 42 23 127 16 99 23 58 89 58 94 108 91 99 80 51 5 100'
readonly Codec_7fa8977e='decimal_space|rolling_xor|4c'

Load_7fa8977e() {
  v_a19c=()
  local IFS=' '
  read -r -a v_a19c <<< "${Material_7fa8977e}"
}

Decode_7fa8977e() {
  v_b27e=()
  local v_a702=76
  local v_e598
  for ((v_e598=0; v_e598<${#v_a19c[@]}; v_e598++)); do
    v_b27e+=("$((v_a19c[v_e598] ^ v_a702))")
    v_a702=${v_a19c[v_e598]}
  done
}

Recover_7fa8977e() {
  local -a v_a19c v_b27e
  local v_c304 v_d41a v_b803 v_e598
  v_d41a=''
  Load_7fa8977e
  case 1 in 1) Decode_7fa8977e ;; *) return 70 ;; esac
  v_c304=''
  local octal character
  for v_e598 in "${!v_b27e[@]}"; do
    printf -v octal '%03o' "${v_b27e[v_e598]}"
    printf -v character '%b' "\\$octal"
    v_c304+="$character"
  done
  printf '%s\n' "$v_c304"
}

Inspect_7fa8977e() { Recover_7fa8977e; }

Plan_7fa8977e() {
  local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
  descriptor="$(Inspect_7fa8977e)"
  local -a fields
  IFS='|' read -r -a fields <<< "$descriptor"
  for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
  local -a report_command=(printf '%s\n' "$campaign_id")
  declare -p report_command
}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_7fa8977e; fi
