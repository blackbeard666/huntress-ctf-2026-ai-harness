# Huntress advanced Bash syntax fixture

readonly Material_96e187de='118,61,49,124,102,101,97,116,117,114,101,61,97,110,115,105,95,99,95,113,117,111,116,105,110,103,124,112,114,105,109,105,116,105,118,101,61,97,110,115,105,95,99,95,101,115,99,97,112,101,95,115,116,114,105,110,103,124,99,97,109,112,97,105,103,110,95,105,100,61,66,65,83,72,88,45,65,51,70,69,67,56,56,55,124,115,116,97,103,101,95,99,111,117,110,116,61,49,124,115,116,101,112,115,61,114,101,99,111,103,110,105,122,101,95,115,121,110,116,97,120,44,114,101,99,111,110,115,116,114,117,99,116,95,105,110,116,101,110,116'

readonly Codec_96e187de='decimal_csv|'

Feature_96e187de() {

  local escaped=$'node\nbash\tfixture'; : "$escaped"

}

Decode() { local IFS=',' value; read -r -a values <<< "${Material_96e187de}"; for value in "${values[@]}"; do printf -v value '\\x%02x' "$value"; printf '%b' "$value"; done; }

Inspect_96e187de() {

  local harmless_value="${HUNTRESS_FIXTURE_CONTEXT:-host}"

  for decode_pass in 1; do Decode; done

}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_96e187de; fi

