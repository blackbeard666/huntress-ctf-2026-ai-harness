# Huntress advanced Bash syntax fixture
readonly Material_916916dc='763d317c666561747572653d616e73695f635f71756f74696e677c7072696d69746976653d616e73695f635f6573636170655f737472696e677c63616d706169676e5f69643d42415348582d39343539393736337c73746167655f636f756e743d317c73746570733d7265636f676e697a655f73796e7461782c7265636f6e7374727563745f696e74656e74'
readonly Codec_916916dc='hex_compact|'
Feature_916916dc() {
  local escaped=$'node\nbash\tfixture'; : "$escaped"
}
Decode() { local raw="${Material_916916dc}" index value; for ((index=0; index<${#raw}; index+=2)); do value=$((16#${raw:index:2})); printf -v value '\\x%02x' "$value"; printf '%b' "$value"; done; }
Inspect_916916dc() {
  local v_a19c="${HUNTRESS_FIXTURE_CONTEXT:-host}"
  for v_b27e in 1; do Decode; done
}
if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_916916dc; fi
