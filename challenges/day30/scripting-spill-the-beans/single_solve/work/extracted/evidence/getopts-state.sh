  # Huntress advanced Bash syntax fixture
  readonly Material_0bae2db2='118,61,49,124,102,101,97,116,117,114,101,61,103,101,116,111,112,116,115,95,115,116,97,116,101,124,112,114,105,109,105,116,105,118,101,61,111,112,116,105,111,110,95,112,97,114,115,101,114,95,115,116,97,116,101,124,99,97,109,112,97,105,103,110,95,105,100,61,66,65,83,72,88,45,70,48,54,68,52,50,57,69,124,115,116,97,103,101,95,99,111,117,110,116,61,49,124,115,116,101,112,115,61,114,101,99,111,103,110,105,122,101,95,115,121,110,116,97,120,44,114,101,99,111,110,115,116,114,117,99,116,95,105,110,116,101,110,116'
  readonly Codec_0bae2db2='decimal_csv|'
  Feature_0bae2db2() {
    local OPTIND option; while getopts ':ab:' option -- -a -b fixture; do case "$option" in a|b) : ;; esac; done
  }
  Decode() { local IFS=',' value; read -r -a values <<< "${Material_0bae2db2}"; for value in "${values[@]}"; do printf -v value '\\x%02x' "$value"; printf '%b' "$value"; done; }
  Inspect_0bae2db2() {
    local harmless_value=''
    Decode
  }
  if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_0bae2db2; fi
