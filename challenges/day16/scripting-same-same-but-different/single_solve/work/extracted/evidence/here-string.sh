# Huntress advanced Bash syntax fixture

readonly Material_696e2f29='118,61,49,124,102,101,97,116,117,114,101,61,104,101,114,101,95,115,116,114,105,110,103,124,112,114,105,109,105,116,105,118,101,61,104,101,114,101,95,115,116,114,105,110,103,95,114,101,97,100,124,99,97,109,112,97,105,103,110,95,105,100,61,66,65,83,72,88,45,67,50,68,49,67,68,54,51,124,115,116,97,103,101,95,99,111,117,110,116,61,49,124,115,116,101,112,115,61,114,101,99,111,103,110,105,122,101,95,115,121,110,116,97,120,44,114,101,99,111,110,115,116,114,117,99,116,95,105,110,116,101,110,116'

readonly Codec_696e2f29='decimal_csv|'

Feature_696e2f29() {

  local value; read -r value <<< 'fixture line'; : "$value"

}

Decode() { local IFS=',' value; read -r -a values <<< "${Material_696e2f29}"; for value in "${values[@]}"; do printf -v value '\\x%02x' "$value"; printf '%b' "$value"; done; }

Inspect_696e2f29() {

  local -a series=(3 5 8 13); local v_a19c="${series[*]:1:2}"

  local decode_target=Decode; "$decode_target"

}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_696e2f29; fi

