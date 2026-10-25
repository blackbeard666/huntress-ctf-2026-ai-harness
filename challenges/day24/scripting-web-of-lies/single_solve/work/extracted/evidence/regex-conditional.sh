# Huntress advanced Bash syntax fixture

readonly Material_24917e46='521915584241455051564119564143415c7b474b4a404d504d4b4a45485854564d494d504d5241194645574c7b564143415c7b494550474c5847454954454d434a7b4d40196665776c7c0961666762111015135857504543417b474b514a501915585750415457195641474b434a4d5e417b575d4a50455c085641474b4a5750565147507b4d4a50414a50'

readonly Codec_24917e46='xor_hex|24'

Feature_24917e46() {

  local value='node-1234'; [[ "$value" =~ ^node-[0-9]+$ ]] && :

}

Decode() { local raw="${Material_24917e46}" index value; for ((index=0; index<${#raw}; index+=2)); do value=$((16#${raw:index:2} ^ 16#24)); printf -v value '\\x%02x' "$value"; printf '%b' "$value"; done; }

Inspect_24917e46() {

  local NeUtRaL=''

  if ! Decode; then return 71; fi

}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_24917e46; fi

