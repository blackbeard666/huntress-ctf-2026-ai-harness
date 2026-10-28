# configuration reconstruction
#!/usr/bin/env bash
# Huntress Script Triage -- inert static-analysis fixture (bash_linux)
readonly Material_fc810dd7='111:36:40:101:106:109:124:105:106:36:125:124:122:118:125:124:70:122:118:119:127:112:126:108:107:120:109:112:118:119:53:107:124:109:108:107:119:70:122:118:119:127:112:126:108:107:120:109:112:118:119:101:120:125:120:105:109:124:107:36:107:124:120:125:118:119:117:96:70:122:118:119:127:112:126:108:107:120:109:112:118:119:101:106:109:120:126:124:70:122:118:108:119:109:36:40:101:122:120:116:105:120:112:126:119:70:112:125:36:122:120:116:105:120:112:126:119:52:47:41:44:47:40:120:32:124:32:33:101:113:118:106:109:70:112:125:36:113:118:106:109:52:47:41:44:47:40:120:32:124:32:33'
readonly Codec_fc810dd7='decimal_colon|single_byte_xor|19'

Load_fc810dd7() {
  EnCoDeD_Bytes=()
  local IFS=':'
  read -r -a EnCoDeD_Bytes <<< "${Material_fc810dd7}"
}

Decode_fc810dd7() {
  DeCoDeD_Bytes=()
  local InDeX
  for ((InDeX=0; InDeX<${#EnCoDeD_Bytes[@]}; InDeX++)); do
    DeCoDeD_Bytes+=("$((EnCoDeD_Bytes[InDeX] ^ 25))")
  done
}

Recover_fc810dd7() {
  local -a EnCoDeD_Bytes DeCoDeD_Bytes
  local DeScRiPtOr_Text NeUtRaL PaSs InDeX
  NeUtRaL=''
  Load_fc810dd7
  case 1 in 1) Decode_fc810dd7 ;; *) return 70 ;; esac
  DeScRiPtOr_Text=''
  local octal character
  for InDeX in "${!DeCoDeD_Bytes[@]}"; do
    printf -v octal '%03o' "${DeCoDeD_Bytes[InDeX]}"
    printf -v character '%b' "\\$octal"
    DeScRiPtOr_Text+="$character"
  done
  printf '%s\n' "$DeScRiPtOr_Text"
}

Inspect_fc810dd7() { local recovered; recovered="$(Recover_fc810dd7)"; printf '%s\n' "$recovered"; }

Plan_fc810dd7() {
  local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
  descriptor="$(Inspect_fc810dd7)"
  local -a fields
  IFS='|' read -r -a fields <<< "$descriptor"
  for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
  local -a report_command=(printf '%s\n' "$campaign_id")
  declare -p report_command
}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_fc810dd7; fi

# reconstruction complete