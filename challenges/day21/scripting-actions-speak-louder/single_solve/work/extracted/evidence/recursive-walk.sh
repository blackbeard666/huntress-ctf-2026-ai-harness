# Huntress advanced Bash syntax fixture
readonly Material_733be002='118,61,49,124,102,101,97,116,117,114,101,61,114,101,99,117,114,115,105,118,101,95,119,97,108,107,124,112,114,105,109,105,116,105,118,101,61,98,111,117,110,100,101,100,95,114,101,99,117,114,115,105,118,101,95,102,117,110,99,116,105,111,110,124,99,97,109,112,97,105,103,110,95,105,100,61,66,65,83,72,88,45,56,56,57,49,49,68,53,67,124,115,116,97,103,101,95,99,111,117,110,116,61,49,124,115,116,101,112,115,61,114,101,99,111,103,110,105,122,101,95,115,121,110,116,97,120,44,114,101,99,111,110,115,116,114,117,99,116,95,105,110,116,101,110,116'
readonly Codec_733be002='decimal_csv|'
Feature_733be002() {
  walk_fixture() { local depth="$1"; ((depth <= 0)) && return 0; walk_fixture "$((depth - 1))"; }; walk_fixture 2
}
Decode() { local IFS=',' value; read -r -a values <<< "${Material_733be002}"; for value in "${values[@]}"; do printf -v value '\\x%02x' "$value"; printf '%b' "$value"; done; }
Inspect_733be002() {
  local n; if ((2 > 1)); then n=left; else n=right; fi
  Decode
}
if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_733be002; fi
