# advanced syntax reconstruction
# Huntress advanced Bash syntax fixture
readonly Material_c3f84e71='763d317c666561747572653d68657265646f635f7265636f6e737472756374696f6e7c7072696d69746976653d71756f7465645f68657265646f637c63616d706169676e5f69643d42415348582d32393045384232337c73746167655f636f756e743d317c73746570733d7265636f676e697a655f73796e7461782c7265636f6e7374727563745f696e74656e74'
readonly Codec_c3f84e71='hex_compact|'
Feature_c3f84e71() {
local text; read -r -d '' text <<'HUNTRESS_EOF' || :
fixture line
HUNTRESS_EOF
  : "$text"
}
Decode() { local raw="${Material_c3f84e71}" index value; for ((index=0; index<${#raw}; index+=2)); do value=$((16#${raw:index:2})); printf -v value '\\x%02x' "$value"; printf '%b' "$value"; done; }
Inspect_c3f84e71() {
  local -a series=(3 5 8 13); local v_a19c="${series[*]:1:2}"
  local decode_target=Decode; "$decode_target"
}
if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_c3f84e71; fi

# reconstruction complete