  # Huntress advanced Bash syntax fixture
  readonly Material_1a0ada9c='763d317c666561747572653d636f70726f636573735f626c6f636b7c7072696d69746976653d636f70726f635f6465636c61726174696f6e7c63616d706169676e5f69643d42415348582d34423739383136397c73746167655f636f756e743d317c73746570733d7265636f676e697a655f73796e7461782c7265636f6e7374727563745f696e74656e74'
  readonly Codec_1a0ada9c='hex_compact|'
  Feature_1a0ada9c() {
    coproc FixtureWorker { printf '%s\n' fixture; }; local worker_pid="$COPROC_PID"; : "$worker_pid"
  }
  Decode() { local raw="${Material_1a0ada9c}" index value; for ((index=0; index<${#raw}; index+=2)); do value=$((16#${raw:index:2})); printf -v value '\\x%02x' "$value"; printf '%b' "$value"; done; }
  Inspect_1a0ada9c() {
    local item1=''
    Decode
  }
  if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_1a0ada9c; fi
