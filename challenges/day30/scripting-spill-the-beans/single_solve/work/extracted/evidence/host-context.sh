#!/usr/bin/env bash
  # Huntress Script Triage -- inert static-analysis fixture (bash_linux)
  readonly Material_91240394='184,16,99,242,143,186,72,34,253,193,170,72,49,225,152,171,114,49,225,146,168,68,53,251,142,175,89,59,225,146,226,95,55,250,137,188,67,13,237,147,160,75,59,233,137,188,76,38,231,147,160,81,51,234,157,190,89,55,252,193,190,95,59,224,136,168,114,32,235,140,161,95,38,242,143,186,76,53,235,163,173,66,39,224,136,243,28,46,237,157,163,93,51,231,155,160,114,59,234,193,173,76,63,254,157,167,74,60,163,200,173,30,103,190,201,171,21,55,191,128,166,66,33,250,163,167,73,111,230,147,189,89,127,186,159,253,24,98,187,153,246,72,99'
  readonly Codec_91240394='decimal_comma|repeating_key_xor|ce,2d,52,8e,fc'

  Load_91240394() {
    e=()
    local IFS=','
    read -r -a e <<< "${Material_91240394}"
  }

  Decode_91240394() {
    d=()
    local -a key_bytes=(206 45 82 142 252)
    local i
    for ((i=0; i<${#e[@]}; i++)); do
      d+=("$((e[i] ^ key_bytes[i % ${#key_bytes[@]}]))")
    done
  }

  Recover_91240394() {
    local -a e d
    local t n z i
    n="${HUNTRESS_FIXTURE_CONTEXT:-host}"
    Load_91240394
    case 1 in 1) Decode_91240394 ;; *) return 70 ;; esac
    t=''
    local octal character
    for i in "${!d[@]}"; do
      printf -v octal '%03o' "${d[i]}"
      printf -v character '%b' "\\$octal"
      t+="$character"
    done
    printf '%s\n' "$t"
  }

  Inspect_91240394() { Recover_91240394; }

  Plan_91240394() {
    local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
    descriptor="$(Inspect_91240394)"
    local -a fields
    IFS='|' read -r -a fields <<< "$descriptor"
    for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
    local -a report_command=(printf '%s\n' "$campaign_id")
    declare -p report_command
  }

  if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_91240394; fi
