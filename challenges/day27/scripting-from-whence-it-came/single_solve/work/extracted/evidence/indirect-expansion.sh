# advanced syntax reconstruction
# Huntress advanced Bash syntax fixture
readonly Material_cb50737b='763d317c666561747572653d696e6469726563745f657870616e73696f6e7c7072696d69746976653d706172616d657465725f696e646972656374696f6e7c63616d706169676e5f69643d42415348582d31433933343342437c73746167655f636f756e743d317c73746570733d7265636f676e697a655f73796e7461782c7265636f6e7374727563745f696e74656e74'
readonly Codec_cb50737b='hex_compact|'
Feature_cb50737b() {
  local pointer=target target=fixture; local value="${!pointer}"; printf '%s' "$value" >/dev/null
}
Decode() { local raw="${Material_cb50737b}" index value; for ((index=0; index<${#raw}; index+=2)); do value=$((16#${raw:index:2})); printf -v value '\\x%02x' "$value"; printf '%b' "$value"; done; }
Inspect_cb50737b() {
  local NeUtRaL="${HUNTRESS_FIXTURE_CONTEXT:-host}"
  local decode_target=Decode; "$decode_target"
}
if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_cb50737b; fi

# reconstruction complete