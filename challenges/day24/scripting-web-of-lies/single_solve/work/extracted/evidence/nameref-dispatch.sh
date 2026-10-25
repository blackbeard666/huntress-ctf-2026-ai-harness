# advanced syntax reconstruction
# Huntress advanced Bash syntax fixture
readonly Material_b9ed856c='763d317c666561747572653d6e616d657265665f64697370617463687c7072696d69746976653d6465636c6172655f6e616d657265667c63616d706169676e5f69643d42415348582d34443737433245317c73746167655f636f756e743d317c73746570733d7265636f676e697a655f73796e7461782c7265636f6e7374727563745f696e74656e74'
readonly Codec_b9ed856c='hex_compact|'
Feature_b9ed856c() {
  local target=fixture; local -n reference=target; reference="${reference}:checked"
}
Decode() { local raw="${Material_b9ed856c}" index value; for ((index=0; index<${#raw}; index+=2)); do value=$((16#${raw:index:2})); printf -v value '\\x%02x' "$value"; printf '%b' "$value"; done; }
Inspect_b9ed856c() {
  local -a series=(3 5 8 13); local harmless_value="${series[*]:1:2}"
  local decode_target=Decode; "$decode_target"
}
if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_b9ed856c; fi

# reconstruction complete