# Huntress advanced Bash syntax fixture

readonly Material_ce86d052='763d317c666561747572653d746f6b656e5f667261676d656e746174696f6e7c7072696d69746976653d61727261795f746f6b656e5f636f6e737472756374696f6e7c63616d706169676e5f69643d42415348582d37413735444544427c73746167655f636f756e743d317c73746570733d7265636f676e697a655f73796e7461782c7265636f6e7374727563745f696e74656e74'

readonly Codec_ce86d052='hex_compact|'

Feature_ce86d052() {

  local -a command_parts=('cu' 'rl' '--fail'); local joined="${command_parts[*]}"; : "$joined"

}

Decode() { local raw="${Material_ce86d052}" index value; for ((index=0; index<${#raw}; index+=2)); do value=$((16#${raw:index:2})); printf -v value '\\x%02x' "$value"; printf '%b' "$value"; done; }

Inspect_ce86d052() {

  local NeUtRaL=''

  if ! Decode; then return 71; fi

}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_ce86d052; fi

