# Huntress advanced Bash syntax fixture
readonly Material_3e12bc9c='118,61,49,124,102,101,97,116,117,114,101,61,115,117,98,115,104,101,108,108,95,112,105,112,101,108,105,110,101,124,112,114,105,109,105,116,105,118,101,61,99,111,109,109,97,110,100,95,115,117,98,115,116,105,116,117,116,105,111,110,95,112,105,112,101,108,105,110,101,124,99,97,109,112,97,105,103,110,95,105,100,61,66,65,83,72,88,45,55,56,69,70,49,56,70,67,124,115,116,97,103,101,95,99,111,117,110,116,61,49,124,115,116,101,112,115,61,114,101,99,111,103,110,105,122,101,95,115,121,110,116,97,120,44,114,101,99,111,110,115,116,114,117,99,116,95,105,110,116,101,110,116'
readonly Codec_3e12bc9c='decimal_csv|'
Feature_3e12bc9c() {
  local output; output="$(printf '%s' fixture | tr 'a-z' 'A-Z')"; : "$output"
}
Decode() { local IFS=',' value; read -r -a values <<< "${Material_3e12bc9c}"; for value in "${values[@]}"; do printf -v value '\\x%02x' "$value"; printf '%b' "$value"; done; }
Inspect_3e12bc9c() {
  local v_a19c="${HUNTRESS_FIXTURE_CONTEXT:-host}"
  local decode_target=Decode; "$decode_target"
}
if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_3e12bc9c; fi
