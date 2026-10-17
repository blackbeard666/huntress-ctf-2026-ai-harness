# Huntress advanced Bash syntax fixture

readonly Material_56b746e0='763d317c666561747572653d6e616d657265665f64697370617463687c7072696d69746976653d6465636c6172655f6e616d657265667c63616d706169676e5f69643d42415348582d35413131434339337c73746167655f636f756e743d317c73746570733d7265636f676e697a655f73796e7461782c7265636f6e7374727563745f696e74656e74'

readonly Codec_56b746e0='hex_compact|'

Feature_56b746e0() {

  local target=fixture; local -n reference=target; reference="${reference}:checked"

}

Decode() { local raw="${Material_56b746e0}" index value; for ((index=0; index<${#raw}; index+=2)); do value=$((16#${raw:index:2})); printf -v value '\\x%02x' "$value"; printf '%b' "$value"; done; }

Inspect_56b746e0() {

  local NeUtRaL=$((19 * 7 - 133))

  for PaSs in 1; do Decode; done

}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_56b746e0; fi

