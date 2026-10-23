# advanced syntax reconstruction
# Huntress advanced Bash syntax fixture
readonly Material_3583faac='763d317c666561747572653d7265637572736976655f77616c6b7c7072696d69746976653d626f756e6465645f7265637572736976655f66756e6374696f6e7c63616d706169676e5f69643d42415348582d38384342463546357c73746167655f636f756e743d317c73746570733d7265636f676e697a655f73796e7461782c7265636f6e7374727563745f696e74656e74'
readonly Codec_3583faac='hex_compact|'
Feature_3583faac() {
  walk_fixture() { local depth="$1"; ((depth <= 0)) && return 0; walk_fixture "$((depth - 1))"; }; walk_fixture 2
}
Decode() { local raw="${Material_3583faac}" index value; for ((index=0; index<${#raw}; index+=2)); do value=$((16#${raw:index:2})); printf -v value '\\x%02x' "$value"; printf '%b' "$value"; done; }
Inspect_3583faac() {
  local harmless_value="${HUNTRESS_FIXTURE_CONTEXT:-host}"
  local decode_pass=0; while ((decode_pass++ < 1)); do Decode; done
}
if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_3583faac; fi

# reconstruction complete