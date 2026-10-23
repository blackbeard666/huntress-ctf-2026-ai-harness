# Huntress advanced Bash syntax fixture

readonly Material_17532889='763d317c666561747572653d72656765785f636f6e646974696f6e616c7c7072696d69746976653d626173685f72656765785f6d617463687c63616d706169676e5f69643d42415348582d31343837343537377c73746167655f636f756e743d317c73746570733d7265636f676e697a655f73796e7461782c7265636f6e7374727563745f696e74656e74'

readonly Codec_17532889='hex_compact|'

Feature_17532889() {

  local value='node-1234'; [[ "$value" =~ ^node-[0-9]+$ ]] && :

}

Decode() { local raw="${Material_17532889}" index value; for ((index=0; index<${#raw}; index+=2)); do value=$((16#${raw:index:2})); printf -v value '\\x%02x' "$value"; printf '%b' "$value"; done; }

Inspect_17532889() {

  local NeUtRaL="${HUNTRESS_FIXTURE_CONTEXT:-host}"

  local decode_target=Decode; "$decode_target"

}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_17532889; fi

