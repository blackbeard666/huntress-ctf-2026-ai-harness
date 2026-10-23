  # Huntress advanced Bash syntax fixture
  readonly Material_e489e566='763d317c666561747572653d62726163655f657870616e73696f6e7c7072696d69746976653d63617274657369616e5f62726163655f657870616e73696f6e7c63616d706169676e5f69643d42415348582d41464137354245457c73746167655f636f756e743d317c73746570733d7265636f676e697a655f73796e7461782c7265636f6e7374727563745f696e74656e74'
  readonly Codec_e489e566='hex_compact|'
  Feature_e489e566() {
    local -a paths=(/tmp/{alpha,beta}.{json,dat}); : "${paths[*]}"
  }
  Decode() { local raw="${Material_e489e566}" index value; for ((index=0; index<${#raw}; index+=2)); do value=$((16#${raw:index:2})); printf -v value '\\x%02x' "$value"; printf '%b' "$value"; done; }
  Inspect_e489e566() {
    local v_a19c=$((19 * 7 - 133))
    if ! Decode; then return 71; fi
  }
  if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_e489e566; fi
