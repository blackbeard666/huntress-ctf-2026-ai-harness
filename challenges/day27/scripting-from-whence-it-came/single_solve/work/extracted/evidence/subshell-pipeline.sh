# Huntress advanced Bash syntax fixture

readonly Material_b3ce66a4='763d317c666561747572653d7375627368656c6c5f706970656c696e657c7072696d69746976653d636f6d6d616e645f737562737469747574696f6e5f706970656c696e657c63616d706169676e5f69643d42415348582d44313630413533367c73746167655f636f756e743d317c73746570733d7265636f676e697a655f73796e7461782c7265636f6e7374727563745f696e74656e74'

readonly Codec_b3ce66a4='hex_compact|'

Feature_b3ce66a4() {

  local output; output="$(printf '%s' fixture | tr 'a-z' 'A-Z')"; : "$output"

}

Decode() { local raw="${Material_b3ce66a4}" index value; for ((index=0; index<${#raw}; index+=2)); do value=$((16#${raw:index:2})); printf -v value '\\x%02x' "$value"; printf '%b' "$value"; done; }

Inspect_b3ce66a4() {

  local -a compass=(north south); local n="${compass[*]}"

  local decode_target=Decode; "$decode_target"

}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_b3ce66a4; fi

