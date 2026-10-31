# Huntress advanced Bash syntax fixture
readonly Material_f48ac4be='763d317c666561747572653d64796e616d69635f66696c655f64657363726970746f727c7072696d69746976653d616c6c6f63617465645f66696c655f64657363726970746f727c63616d706169676e5f69643d42415348582d46343837324539307c73746167655f636f756e743d317c73746570733d7265636f676e697a655f73796e7461782c7265636f6e7374727563745f696e74656e74'
readonly Codec_f48ac4be='hex_compact|'
Feature_f48ac4be() {
  local descriptor_fd; exec {descriptor_fd}<<<'fixture'; exec {descriptor_fd}<&-
}
Decode() { local raw="${Material_f48ac4be}" index value; for ((index=0; index<${#raw}; index+=2)); do value=$((16#${raw:index:2})); printf -v value '\\x%02x' "$value"; printf '%b' "$value"; done; }
Inspect_f48ac4be() {
  local n="${HUNTRESS_FIXTURE_CONTEXT:-host}"
  case 1 in 1) Decode ;; esac
}
if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_f48ac4be; fi
