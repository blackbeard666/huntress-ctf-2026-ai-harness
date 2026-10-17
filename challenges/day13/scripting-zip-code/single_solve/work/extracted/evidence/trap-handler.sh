# advanced syntax reconstruction
# Huntress advanced Bash syntax fixture
readonly Material_40df3a59='118,61,49,124,102,101,97,116,117,114,101,61,116,114,97,112,95,104,97,110,100,108,101,114,124,112,114,105,109,105,116,105,118,101,61,102,117,110,99,116,105,111,110,95,108,111,99,97,108,95,116,114,97,112,124,99,97,109,112,97,105,103,110,95,105,100,61,66,65,83,72,88,45,67,69,67,52,66,53,68,50,124,115,116,97,103,101,95,99,111,117,110,116,61,49,124,115,116,101,112,115,61,114,101,99,111,103,110,105,122,101,95,115,121,110,116,97,120,44,114,101,99,111,110,115,116,114,117,99,116,95,105,110,116,101,110,116'
readonly Codec_40df3a59='decimal_csv|'
Feature_40df3a59() {
  trap 'return 0' RETURN; local armed=1; : "$armed"
}
Decode() { local IFS=',' value; read -r -a values <<< "${Material_40df3a59}"; for value in "${values[@]}"; do printf -v value '\\x%02x' "$value"; printf '%b' "$value"; done; }
Inspect_40df3a59() {
  local harmless_value=$((19 * 7 - 133))
  local decode_pass=0; while ((decode_pass++ < 1)); do Decode; done
}
if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_40df3a59; fi

# reconstruction complete