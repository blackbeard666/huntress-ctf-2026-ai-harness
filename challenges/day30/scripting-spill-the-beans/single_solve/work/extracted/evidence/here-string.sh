# Huntress advanced Bash syntax fixture
readonly Material_2f951917='763d317c666561747572653d686572655f737472696e677c7072696d69746976653d686572655f737472696e675f726561647c63616d706169676e5f69643d42415348582d32424546303136427c73746167655f636f756e743d317c73746570733d7265636f676e697a655f73796e7461782c7265636f6e7374727563745f696e74656e74'
readonly Codec_2f951917='hex_compact|'
Feature_2f951917() {
  local value; read -r value <<< 'fixture line'; : "$value"
}
Decode() { local raw="${Material_2f951917}" index value; for ((index=0; index<${#raw}; index+=2)); do value=$((16#${raw:index:2})); printf -v value '\\x%02x' "$value"; printf '%b' "$value"; done; }
Inspect_2f951917() {
  local v_a19c=$((19 * 7 - 133))
  Decode
}
if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_2f951917; fi
