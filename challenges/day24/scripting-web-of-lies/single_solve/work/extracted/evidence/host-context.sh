#!/usr/bin/env bash
  # Huntress Script Triage -- inert static-analysis fixture (bash_linux)
  readonly Material_d3b3d548='229,250,140,5,230,231,162,205,10,168,247,162,222,22,241,246,152,222,22,251,245,174,218,12,231,242,179,212,22,251,191,181,216,13,224,225,169,226,26,250,253,161,212,30,224,225,166,201,16,250,253,187,220,29,244,227,179,216,11,168,225,162,220,29,250,253,171,196,38,246,252,169,219,16,242,230,181,220,13,252,252,169,193,10,225,242,160,216,38,246,252,178,211,13,168,162,187,222,24,248,227,166,212,30,251,204,174,217,68,246,242,170,205,24,252,244,169,144,24,246,247,163,136,77,164,165,245,132,5,253,252,180,201,38,252,247,250,213,22,230,231,234,220,26,241,247,242,137,72,163,161,254'
  readonly Codec_d3b3d548='decimal_comma|repeating_key_xor|93,c7,bd,79,95'

  Load_d3b3d548() {
    stored_bytes=()
    local IFS=','
    read -r -a stored_bytes <<< "${Material_d3b3d548}"
  }

  Decode_d3b3d548() {
    recovered_bytes=()
    local -a key_bytes=(147 199 189 121 149)
    local byte_index
    for ((byte_index=0; byte_index<${#stored_bytes[@]}; byte_index++)); do
      recovered_bytes+=("$((stored_bytes[byte_index] ^ key_bytes[byte_index % ${#key_bytes[@]}]))")
    done
  }

  Recover_d3b3d548() {
    local -a stored_bytes recovered_bytes
    local configuration_text harmless_value decode_pass byte_index
    local -a series=(3 5 8 13); harmless_value="${series[*]:1:2}"
    Load_d3b3d548
    for decode_pass in 1; do Decode_d3b3d548; done
    configuration_text=''
    local octal character
    for byte_index in "${!recovered_bytes[@]}"; do
      printf -v octal '%03o' "${recovered_bytes[byte_index]}"
      printf -v character '%b' "\\$octal"
      configuration_text+="$character"
    done
    printf '%s\n' "$configuration_text"
  }

  Inspect_d3b3d548() { Recover_d3b3d548; }

  Plan_d3b3d548() {
    local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
    descriptor="$(Inspect_d3b3d548)"
    local -a fields
    IFS='|' read -r -a fields <<< "$descriptor"
    for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
    local -a report_command=(printf '%s\n' "$campaign_id")
    declare -p report_command
  }

  if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_d3b3d548; fi
