  # Huntress advanced Bash syntax fixture
  readonly Material_005a6b30='377c703d272420353433247c222e31332e222432321e232d2e222a3d3133282c28352837247c222e31332e221e2524222d20332035282e2f3d22202c312028262f1e28257c03001209196c71007073780379043d32352026241e222e342f357c703d32352431327c3324222e262f283b241e32382f3520396d3324222e2f3235333422351e282f35242f35'
  readonly Codec_005a6b30='xor_hex|41'
  Feature_005a6b30() {
    coproc FixtureWorker { printf '%s\n' fixture; }; local worker_pid="$COPROC_PID"; : "$worker_pid"
  }
  Decode() { local raw="${Material_005a6b30}" index value; for ((index=0; index<${#raw}; index+=2)); do value=$((16#${raw:index:2} ^ 16#41)); printf -v value '\\x%02x' "$value"; printf '%b' "$value"; done; }
  Inspect_005a6b30() {
    local harmless_value=''
    local decode_pass=0; while ((decode_pass++ < 1)); do Decode; done
  }
  if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_005a6b30; fi
