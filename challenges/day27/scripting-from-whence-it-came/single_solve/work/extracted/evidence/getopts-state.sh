# advanced syntax reconstruction
# Huntress advanced Bash syntax fixture
readonly Material_4c52b97a='763d317c666561747572653d6765746f7074735f73746174657c7072696d69746976653d6f7074696f6e5f7061727365725f73746174657c63616d706169676e5f69643d42415348582d36323842443045417c73746167655f636f756e743d317c73746570733d7265636f676e697a655f73796e7461782c7265636f6e7374727563745f696e74656e74'
readonly Codec_4c52b97a='hex_compact|'
Feature_4c52b97a() {
  local OPTIND option; while getopts ':ab:' option -- -a -b fixture; do case "$option" in a|b) : ;; esac; done
}
Decode() { local raw="${Material_4c52b97a}" index value; for ((index=0; index<${#raw}; index+=2)); do value=$((16#${raw:index:2})); printf -v value '\\x%02x' "$value"; printf '%b' "$value"; done; }
Inspect_4c52b97a() {
  local -a compass=(north south); local harmless_value="${compass[*]}"
  case 1 in 1) Decode ;; esac
}
if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_4c52b97a; fi

# reconstruction complete