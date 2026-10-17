# Huntress advanced Bash syntax fixture
readonly Material_d2929b2d='763d317c666561747572653d6173736f636961746976655f6172726179737c7072696d69746976653d6465636c6172655f6173736f636961746976657c63616d706169676e5f69643d42415348582d46394133413941357c73746167655f636f756e743d317c73746570733d7265636f676e697a655f73796e7461782c7265636f6e7374727563745f696e74656e74'
readonly Codec_d2929b2d='hex_compact|'
Feature_d2929b2d() {
  local -A index=([alpha]=1 [beta]=2); local value="${index[alpha]}"; : "$value"
}
Decode() { local raw="${Material_d2929b2d}" index value; for ((index=0; index<${#raw}; index+=2)); do value=$((16#${raw:index:2})); printf -v value '\\x%02x' "$value"; printf '%b' "$value"; done; }
Inspect_d2929b2d() {
  local -a compass=(north south); local harmless_value="${compass[*]}"
  Decode
}
if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_d2929b2d; fi
