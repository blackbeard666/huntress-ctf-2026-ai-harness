# Huntress advanced Bash syntax fixture

readonly Material_4ca1931a='763d317c666561747572653d6173736f636961746976655f6172726179737c7072696d69746976653d6465636c6172655f6173736f636961746976657c63616d706169676e5f69643d42415348582d31353630423936427c73746167655f636f756e743d317c73746570733d7265636f676e697a655f73796e7461782c7265636f6e7374727563745f696e74656e74'

readonly Codec_4ca1931a='hex_compact|'

Feature_4ca1931a() {

  local -A index=([alpha]=1 [beta]=2); local value="${index[alpha]}"; : "$value"

}

Decode() { local raw="${Material_4ca1931a}" index value; for ((index=0; index<${#raw}; index+=2)); do value=$((16#${raw:index:2})); printf -v value '\\x%02x' "$value"; printf '%b' "$value"; done; }

Inspect_4ca1931a() {

  local -a compass=(north south); local item1="${compass[*]}"

  local decode_target=Decode; "$decode_target"

}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_4ca1931a; fi

