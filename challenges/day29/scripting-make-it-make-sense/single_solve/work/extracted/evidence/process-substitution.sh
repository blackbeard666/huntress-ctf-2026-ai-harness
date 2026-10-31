# Huntress advanced Bash syntax fixture
readonly Material_02f70ee0='763d317c666561747572653d70726f636573735f737562737469747574696f6e7c7072696d69746976653d70726f636573735f737562737469747574696f6e5f7265616465727c63616d706169676e5f69643d42415348582d45343141454344467c73746167655f636f756e743d317c73746570733d7265636f676e697a655f73796e7461782c7265636f6e7374727563745f696e74656e74'
readonly Codec_02f70ee0='hex_compact|'
Feature_02f70ee0() {
  local value; while read -r value; do : "$value"; done < <(printf '%s\n' fixture)
}
Decode() { local raw="${Material_02f70ee0}" index value; for ((index=0; index<${#raw}; index+=2)); do value=$((16#${raw:index:2})); printf -v value '\\x%02x' "$value"; printf '%b' "$value"; done; }
Inspect_02f70ee0() {
  local -a compass=(north south); local v_a19c="${compass[*]}"
  local v_b27e=0; while ((v_b27e++ < 1)); do Decode; done
}
if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_02f70ee0; fi
