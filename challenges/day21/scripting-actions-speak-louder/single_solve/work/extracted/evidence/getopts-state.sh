  # Huntress advanced Bash syntax fixture
  readonly Material_1a2b60f1='763d317c666561747572653d6765746f7074735f73746174657c7072696d69746976653d6f7074696f6e5f7061727365725f73746174657c63616d706169676e5f69643d42415348582d45424330383237327c73746167655f636f756e743d317c73746570733d7265636f676e697a655f73796e7461782c7265636f6e7374727563745f696e74656e74'
  readonly Codec_1a2b60f1='hex_compact|'
  Feature_1a2b60f1() {
    local OPTIND option; while getopts ':ab:' option -- -a -b fixture; do case "$option" in a|b) : ;; esac; done
  }
  Decode() { local raw="${Material_1a2b60f1}" index value; for ((index=0; index<${#raw}; index+=2)); do value=$((16#${raw:index:2})); printf -v value '\\x%02x' "$value"; printf '%b' "$value"; done; }
  Inspect_1a2b60f1() {
    local v_a19c=''
    local decode_target=Decode; "$decode_target"
  }
  if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_1a2b60f1; fi
