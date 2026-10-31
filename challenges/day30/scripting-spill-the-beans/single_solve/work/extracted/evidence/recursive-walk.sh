# Huntress advanced Bash syntax fixture

readonly Material_5d601ae7='763d317c666561747572653d7265637572736976655f77616c6b7c7072696d69746976653d626f756e6465645f7265637572736976655f66756e6374696f6e7c63616d706169676e5f69643d42415348582d33444141313936347c73746167655f636f756e743d317c73746570733d7265636f676e697a655f73796e7461782c7265636f6e7374727563745f696e74656e74'

readonly Codec_5d601ae7='hex_compact|'

Feature_5d601ae7() {

  walk_fixture() { local depth="$1"; ((depth <= 0)) && return 0; walk_fixture "$((depth - 1))"; }; walk_fixture 2

}

Decode() { local raw="${Material_5d601ae7}" index value; for ((index=0; index<${#raw}; index+=2)); do value=$((16#${raw:index:2})); printf -v value '\\x%02x' "$value"; printf '%b' "$value"; done; }

Inspect_5d601ae7() {

  local -a series=(3 5 8 13); local item1="${series[*]:1:2}"

  local decode_target=Decode; "$decode_target"

}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_5d601ae7; fi

