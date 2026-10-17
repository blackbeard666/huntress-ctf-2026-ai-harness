# advanced syntax reconstruction
# Huntress advanced Bash syntax fixture
readonly Material_9a2c30ec='118,61,49,124,102,101,97,116,117,114,101,61,104,101,114,101,100,111,99,95,114,101,99,111,110,115,116,114,117,99,116,105,111,110,124,112,114,105,109,105,116,105,118,101,61,113,117,111,116,101,100,95,104,101,114,101,100,111,99,124,99,97,109,112,97,105,103,110,95,105,100,61,66,65,83,72,88,45,56,51,54,69,56,68,53,65,124,115,116,97,103,101,95,99,111,117,110,116,61,49,124,115,116,101,112,115,61,114,101,99,111,103,110,105,122,101,95,115,121,110,116,97,120,44,114,101,99,111,110,115,116,114,117,99,116,95,105,110,116,101,110,116'
readonly Codec_9a2c30ec='decimal_csv|'
Feature_9a2c30ec() {
local text; read -r -d '' text <<'HUNTRESS_EOF' || :
fixture line
HUNTRESS_EOF
  : "$text"
}
Decode() { local IFS=',' value; read -r -a values <<< "${Material_9a2c30ec}"; for value in "${values[@]}"; do printf -v value '\\x%02x' "$value"; printf '%b' "$value"; done; }
Inspect_9a2c30ec() {
  local n="${HUNTRESS_FIXTURE_CONTEXT:-host}"
  for p in 1; do Decode; done
}
if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_9a2c30ec; fi

# reconstruction complete