#!/usr/bin/env bash
  # Huntress Script Triage -- inert static-analysis fixture (bash_linux)
  readonly Material_0176b27d='145:88:76:151:142:143:128:139:142:88:135:138:126:124:143:128:122:135:138:126:124:135:71:127:132:142:139:124:143:126:131:122:139:141:138:126:128:142:142:151:124:127:124:139:143:128:141:88:125:124:142:131:122:142:126:141:132:139:143:151:142:143:124:130:128:122:126:138:144:137:143:88:76:151:126:124:136:139:124:132:130:137:122:132:127:88:126:124:136:139:124:132:130:137:72:125:128:75:84:76:126:78:77:76:82:151:129:132:135:128:122:139:124:143:131:88:74:143:136:139:74:131:144:137:143:141:128:142:142:72:126:124:126:131:128:74:73:142:143:124:130:128:72:125:128:75:84:76:126:78:77:76:82'
  readonly Codec_0176b27d='decimal_colon|add_modulo_256|1b'

  Load_0176b27d() {
    stored_bytes=()
    local IFS=':'
    read -r -a stored_bytes <<< "${Material_0176b27d}"
  }

  Decode_0176b27d() {
    recovered_bytes=()
    local byte_index
    for ((byte_index=0; byte_index<${#stored_bytes[@]}; byte_index++)); do
      recovered_bytes+=("$(((stored_bytes[byte_index] - 27 + 256) % 256))")
    done
  }

  Recover_0176b27d() {
    local -a stored_bytes recovered_bytes
    local configuration_text harmless_value decode_pass byte_index
    harmless_value=$((19 * 7 - 133))
    Load_0176b27d
    decode_pass=0; while ((decode_pass < 1)); do Decode_0176b27d; ((decode_pass+=1)); done
    configuration_text=''
    local octal character
    for byte_index in "${!recovered_bytes[@]}"; do
      printf -v octal '%03o' "${recovered_bytes[byte_index]}"
      printf -v character '%b' "\\$octal"
      configuration_text+="$character"
    done
    printf '%s\n' "$configuration_text"
  }

  Inspect_0176b27d() { Recover_0176b27d; }

  Plan_0176b27d() {
    local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
    descriptor="$(Inspect_0176b27d)"
    local -a fields
    IFS='|' read -r -a fields <<< "$descriptor"
    for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
    local -a launch_command=(bash "$file_path")
    declare -p launch_command
  }

  if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_0176b27d; fi
