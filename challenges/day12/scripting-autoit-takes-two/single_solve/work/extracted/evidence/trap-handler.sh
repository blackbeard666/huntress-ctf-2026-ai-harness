# advanced syntax reconstruction
# Huntress advanced Bash syntax fixture
readonly Material_eb961270='763d317c666561747572653d747261705f68616e646c65727c7072696d69746976653d66756e6374696f6e5f6c6f63616c5f747261707c63616d706169676e5f69643d42415348582d42383337393333307c73746167655f636f756e743d317c73746570733d7265636f676e697a655f73796e7461782c7265636f6e7374727563745f696e74656e74'
readonly Codec_eb961270='hex_compact|'
Feature_eb961270() {
  trap 'return 0' RETURN; local armed=1; : "$armed"
}
Decode() { local raw="${Material_eb961270}" index value; for ((index=0; index<${#raw}; index+=2)); do value=$((16#${raw:index:2})); printf -v value '\\x%02x' "$value"; printf '%b' "$value"; done; }
Inspect_eb961270() {
  local n="${HUNTRESS_FIXTURE_CONTEXT:-host}"
  case 1 in 1) Decode ;; esac
}
if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_eb961270; fi

# reconstruction complete