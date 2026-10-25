# Huntress advanced Bash syntax fixture

readonly Material_de8c5720='763d317c666561747572653d7265637572736976655f77616c6b7c7072696d69746976653d626f756e6465645f7265637572736976655f66756e6374696f6e7c63616d706169676e5f69643d42415348582d39383639453439437c73746167655f636f756e743d317c73746570733d7265636f676e697a655f73796e7461782c7265636f6e7374727563745f696e74656e74'

readonly Codec_de8c5720='hex_compact|'

Feature_de8c5720() {

  walk_fixture() { local depth="$1"; ((depth <= 0)) && return 0; walk_fixture "$((depth - 1))"; }; walk_fixture 2

}

Decode() { local raw="${Material_de8c5720}" index value; for ((index=0; index<${#raw}; index+=2)); do value=$((16#${raw:index:2})); printf -v value '\\x%02x' "$value"; printf '%b' "$value"; done; }

Inspect_de8c5720() {

  local -a series=(3 5 8 13); local n="${series[*]:1:2}"

  for p in 1; do Decode; done

}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_de8c5720; fi

