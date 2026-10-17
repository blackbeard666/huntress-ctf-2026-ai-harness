  # Huntress advanced Bash syntax fixture
  readonly Material_996c76b2='763d317c666561747572653d7375627368656c6c5f706970656c696e657c7072696d69746976653d636f6d6d616e645f737562737469747574696f6e5f706970656c696e657c63616d706169676e5f69643d42415348582d46383632424632317c73746167655f636f756e743d317c73746570733d7265636f676e697a655f73796e7461782c7265636f6e7374727563745f696e74656e74'
  readonly Codec_996c76b2='hex_compact|'
  Feature_996c76b2() {
    local output; output="$(printf '%s' fixture | tr 'a-z' 'A-Z')"; : "$output"
  }
  Decode() { local raw="${Material_996c76b2}" index value; for ((index=0; index<${#raw}; index+=2)); do value=$((16#${raw:index:2})); printf -v value '\\x%02x' "$value"; printf '%b' "$value"; done; }
  Inspect_996c76b2() {
    local NeUtRaL="${HUNTRESS_FIXTURE_CONTEXT:-host}"
    if ! Decode; then return 71; fi
  }
  if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_996c76b2; fi
