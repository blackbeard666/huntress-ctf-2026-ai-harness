# configuration reconstruction
#!/usr/bin/env bash
# Huntress Script Triage -- inert static-analysis fixture (bash_linux)
readonly Material_19388a26='%37%67%61%3d%36%60%33%3d%35%61%28%60%62%64%71%76%2b%2a%60%6d%66%64%66%28%76%76%60%77%71%6b%70%6d%2a%75%68%71%2a%38%6d%71%64%75%5a%60%69%6c%63%79%37%67%61%3d%36%60%33%3d%35%61%28%6b%62%6c%64%75%68%64%66%38%61%6c%5a%6b%62%6c%64%75%68%64%66%79%34%38%71%6b%70%6a%66%5a%60%62%64%71%76%79%77%6a%71%75%6c%77%66%76%60%61%5a%66%60%7d%60%38%77%60%71%75%64%61%64%79%76%76%60%66%6a%77%75%5a%6d%66%71%64%75%76%6c%61%29%69%64%66%6a%69%5a%60%71%64%66%6a%69%38%76%75%60%71%76%79%34%38%73'
readonly Codec_19388a26='percent_hex|reverse_then_xor|05'

Load_19388a26() {
  e=()
  local raw="${Material_19388a26}" p
  for p in ${raw//%/ }; do [[ -n "$p" ]] && e+=("$((16#$p))"); done
}

Decode_19388a26() {
  d=()
  local i
  for ((i=0; i<${#e[@]}; i++)); do
    d[${#e[@]}-1-i]="$((e[i] ^ 5))"
  done
}

Recover_19388a26() {
  local -a e d
  local t n z i
  local -a compass=(north south); n="$(IFS=:; printf '%s' "${compass[*]}")"
  Load_19388a26
  Decode_19388a26
  t=''
  local octal character
  for i in "${!d[@]}"; do
    printf -v octal '%03o' "${d[i]}"
    printf -v character '%b' "\\$octal"
    t+="$character"
  done
  printf '%s\n' "$t"
}

Inspect_19388a26() { local recovered field; local -a fields; recovered="$(Recover_19388a26)"; IFS='|' read -r -a fields <<< "$recovered"; (IFS='|'; printf '%s\n' "${fields[*]}"); }

Plan_19388a26() {
  local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
  descriptor="$(Inspect_19388a26)"
  local -a fields
  IFS='|' read -r -a fields <<< "$descriptor"
  for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
  local -a launch_command=(env -- "$file_path")
  declare -p launch_command
}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_19388a26; fi

# reconstruction complete