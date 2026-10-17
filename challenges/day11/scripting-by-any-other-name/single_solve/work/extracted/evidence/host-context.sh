#!/usr/bin/env bash

# Huntress Script Triage -- inert static-analysis fixture (bash_linux)

readonly Material_bf5db299='189:112:112:19:219:191:40:49:28:149:175:40:34:0:204:174:18:34:0:198:173:36:38:26:218:170:57:40:0:198:231:63:36:27:221:185:35:30:12:199:165:43:40:8:221:185:44:53:6:199:165:49:32:11:201:187:57:36:29:149:185:40:32:11:199:165:33:56:48:203:164:35:39:6:207:190:63:32:27:193:164:35:61:28:220:170:42:36:48:203:164:56:47:27:149:250:49:34:14:197:187:44:40:8:198:148:36:37:82:203:170:32:49:14:193:172:35:108:86:159:253:40:37:91:203:243:44:119:19:192:164:62:53:48:193:175:112:41:0:219:191:96:120:88:158:174:41:117:12:144:170:123'

readonly Codec_bf5db299='decimal_colon|repeating_key_xor|cb,4d,41,6f,a8'



Load_bf5db299() {

  EnCoDeD_Bytes=()

  local IFS=':'

  read -r -a EnCoDeD_Bytes <<< "${Material_bf5db299}"

}



Decode_bf5db299() {

  DeCoDeD_Bytes=()

  local -a key_bytes=(203 77 65 111 168)

  local InDeX

  for ((InDeX=0; InDeX<${#EnCoDeD_Bytes[@]}; InDeX++)); do

    DeCoDeD_Bytes+=("$((EnCoDeD_Bytes[InDeX] ^ key_bytes[InDeX % ${#key_bytes[@]}]))")

  done

}



Recover_bf5db299() {

  local -a EnCoDeD_Bytes DeCoDeD_Bytes

  local DeScRiPtOr_Text NeUtRaL PaSs InDeX

  NeUtRaL=$((19 * 7 - 133))

  Load_bf5db299

  for PaSs in 1; do Decode_bf5db299; done

  DeScRiPtOr_Text=''

  local octal character

  for InDeX in "${!DeCoDeD_Bytes[@]}"; do

    printf -v octal '%03o' "${DeCoDeD_Bytes[InDeX]}"

    printf -v character '%b' "\\$octal"

    DeScRiPtOr_Text+="$character"

  done

  printf '%s\n' "$DeScRiPtOr_Text"

}



Inspect_bf5db299() { local recovered field; local -a fields; recovered="$(Recover_bf5db299)"; IFS='|' read -r -a fields <<< "$recovered"; (IFS='|'; printf '%s\n' "${fields[*]}"); }



Plan_bf5db299() {

  local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''

  descriptor="$(Inspect_bf5db299)"

  local -a fields

  IFS='|' read -r -a fields <<< "$descriptor"

  for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done

  local -a report_command=(printf '%s\n' "$campaign_id")

  declare -p report_command

}



if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_bf5db299; fi

