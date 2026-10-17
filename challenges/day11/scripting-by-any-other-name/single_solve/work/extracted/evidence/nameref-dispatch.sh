# Huntress advanced Bash syntax fixture

readonly Material_b9aecadf='118,61,49,124,102,101,97,116,117,114,101,61,110,97,109,101,114,101,102,95,100,105,115,112,97,116,99,104,124,112,114,105,109,105,116,105,118,101,61,100,101,99,108,97,114,101,95,110,97,109,101,114,101,102,124,99,97,109,112,97,105,103,110,95,105,100,61,66,65,83,72,88,45,50,65,54,70,49,70,52,67,124,115,116,97,103,101,95,99,111,117,110,116,61,49,124,115,116,101,112,115,61,114,101,99,111,103,110,105,122,101,95,115,121,110,116,97,120,44,114,101,99,111,110,115,116,114,117,99,116,95,105,110,116,101,110,116'

readonly Codec_b9aecadf='decimal_csv|'

Feature_b9aecadf() {

  local target=fixture; local -n reference=target; reference="${reference}:checked"

}

Decode() { local IFS=',' value; read -r -a values <<< "${Material_b9aecadf}"; for value in "${values[@]}"; do printf -v value '\\x%02x' "$value"; printf '%b' "$value"; done; }

Inspect_b9aecadf() {

  local harmless_value=''

  Decode

}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_b9aecadf; fi

