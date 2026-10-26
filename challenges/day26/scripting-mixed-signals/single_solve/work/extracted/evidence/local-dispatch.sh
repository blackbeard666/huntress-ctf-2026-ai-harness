#!/usr/bin/env bash
# Huntress Script Triage -- inert static-analysis fixture (bash_linux)
readonly Material_d053b2e4='01578f5ad1030fce559f1b05dd47d61235d249c116069242cb041adf52c11f35ce54cd140fcd55de160edf56d612188355ca2819dd54cb071ec255d6160ddb79c1181fd0529f4616dd47cf070bd741cc2803da1bc11607ce47cb10049342c3415f89119b1259dc5ac41e06db79d2161ed61b8d0307ce09ca0204ca54c704199345c31402db098c041edf41c75a0edf1097405d87439115'
readonly Codec_d053b2e4='hex_compact|repeating_key_xor|77,6a,be,26,a2'

Load_d053b2e4() {
  v_a19c=()
  local raw="${Material_d053b2e4}" v_e598
  for ((v_e598=0; v_e598<${#raw}; v_e598+=2)); do v_a19c+=("$((16#${raw:v_e598:2}))"); done
}

Decode_d053b2e4() {
  v_b27e=()
  local -a key_bytes=(119 106 190 38 162)
  local v_e598
  for ((v_e598=0; v_e598<${#v_a19c[@]}; v_e598++)); do
    v_b27e+=("$((v_a19c[v_e598] ^ key_bytes[v_e598 % ${#key_bytes[@]}]))")
  done
}

Recover_d053b2e4() {
  local -a v_a19c v_b27e
  local v_c304 v_d41a v_b803 v_e598
  v_d41a="${HUNTRESS_FIXTURE_CONTEXT:-host}"
  Load_d053b2e4
  v_b803=0; while ((v_b803 < 1)); do Decode_d053b2e4; ((v_b803+=1)); done
  v_c304=''
  local octal character
  for v_e598 in "${!v_b27e[@]}"; do
    printf -v octal '%03o' "${v_b27e[v_e598]}"
    printf -v character '%b' "\\$octal"
    v_c304+="$character"
  done
  printf '%s\n' "$v_c304"
}

Inspect_d053b2e4() { Recover_d053b2e4; }

Plan_d053b2e4() {
  local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
  descriptor="$(Inspect_d053b2e4)"
  local -a fields
  IFS='|' read -r -a fields <<< "$descriptor"
  for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
  local -a launch_command=(sh "$file_path")
  declare -p launch_command
}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_d053b2e4; fi
