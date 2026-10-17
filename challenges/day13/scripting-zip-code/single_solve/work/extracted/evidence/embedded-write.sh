# configuration reconstruction
#!/usr/bin/env bash
# Huntress Script Triage -- inert static-analysis fixture (bash_linux)
readonly Material_454a1e60='56:1d:11:5c:53:54:45:50:53:1d:44:45:43:4f:44:45:7f:45:4d:42:45:44:44:45:44:0c:57:52:49:54:45:7f:46:49:4c:45:5c:41:44:41:50:54:45:52:1d:49:4e:53:54:41:4c:4c:7f:53:54:44:49:4e:5c:53:54:41:47:45:7f:43:4f:55:4e:54:1d:11:5c:43:41:4d:50:41:49:47:4e:7f:49:44:1d:43:41:4d:50:41:49:47:4e:0d:19:46:43:16:44:11:17:10:10:46:5c:46:49:4c:45:7f:50:41:54:48:1d:0f:54:4d:50:0f:48:55:4e:54:52:45:53:53:0d:43:41:43:48:45:0f:0e:53:54:41:47:45:0d:19:46:43:16:44:11:17:10:10:46'
readonly Codec_454a1e60='hex_colon|single_byte_xor|20'

Load_454a1e60() {
  EnCoDeD_Bytes=()
  local IFS=':' PaRt
  local -a pieces
  read -r -a pieces <<< "${Material_454a1e60}"
  for PaRt in "${pieces[@]}"; do EnCoDeD_Bytes+=("$((16#$PaRt))"); done
}

Decode_454a1e60() {
  DeCoDeD_Bytes=()
  local InDeX
  for ((InDeX=0; InDeX<${#EnCoDeD_Bytes[@]}; InDeX++)); do
    DeCoDeD_Bytes+=("$((EnCoDeD_Bytes[InDeX] ^ 32))")
  done
}

Recover_454a1e60() {
  local -a EnCoDeD_Bytes DeCoDeD_Bytes
  local DeScRiPtOr_Text NeUtRaL PaSs InDeX
  local -a series=(3 5 8 13); NeUtRaL="${series[*]:1:2}"
  Load_454a1e60
  local decode_target=Decode_454a1e60; "$decode_target"
  DeScRiPtOr_Text=''
  local octal character
  for InDeX in "${!DeCoDeD_Bytes[@]}"; do
    printf -v octal '%03o' "${DeCoDeD_Bytes[InDeX]}"
    printf -v character '%b' "\\$octal"
    DeScRiPtOr_Text+="$character"
  done
  printf '%s\n' "$DeScRiPtOr_Text"
}

Inspect_454a1e60() { Recover_454a1e60; }

Plan_454a1e60() {
  local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
  descriptor="$(Inspect_454a1e60)"
  local -a fields
  IFS='|' read -r -a fields <<< "$descriptor"
  for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
  local -a decoder=(base64 --decode) destination=(install -m 0600 /dev/stdin "$file_path")
  declare -p decoder destination
}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_454a1e60; fi

# reconstruction complete