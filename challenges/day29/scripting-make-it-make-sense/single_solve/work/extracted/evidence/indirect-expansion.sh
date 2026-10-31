  # Huntress advanced Bash syntax fixture
  readonly Material_22c36399='118,61,49,124,102,101,97,116,117,114,101,61,105,110,100,105,114,101,99,116,95,101,120,112,97,110,115,105,111,110,124,112,114,105,109,105,116,105,118,101,61,112,97,114,97,109,101,116,101,114,95,105,110,100,105,114,101,99,116,105,111,110,124,99,97,109,112,97,105,103,110,95,105,100,61,66,65,83,72,88,45,53,55,52,55,70,57,57,49,124,115,116,97,103,101,95,99,111,117,110,116,61,49,124,115,116,101,112,115,61,114,101,99,111,103,110,105,122,101,95,115,121,110,116,97,120,44,114,101,99,111,110,115,116,114,117,99,116,95,105,110,116,101,110,116'
  readonly Codec_22c36399='decimal_csv|'
  Feature_22c36399() {
    local pointer=target target=fixture; local value="${!pointer}"; printf '%s' "$value" >/dev/null
  }
  Decode() { local IFS=',' value; read -r -a values <<< "${Material_22c36399}"; for value in "${values[@]}"; do printf -v value '\\x%02x' "$value"; printf '%b' "$value"; done; }
  Inspect_22c36399() {
    local NeUtRaL="${HUNTRESS_FIXTURE_CONTEXT:-host}"
    for PaSs in 1; do Decode; done
  }
  if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_22c36399; fi
