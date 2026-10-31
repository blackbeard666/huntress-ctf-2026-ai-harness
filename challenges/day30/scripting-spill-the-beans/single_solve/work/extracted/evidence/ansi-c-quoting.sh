# Huntress advanced Bash syntax fixture
readonly Material_6f0caacc='118,61,49,124,102,101,97,116,117,114,101,61,97,110,115,105,95,99,95,113,117,111,116,105,110,103,124,112,114,105,109,105,116,105,118,101,61,97,110,115,105,95,99,95,101,115,99,97,112,101,95,115,116,114,105,110,103,124,99,97,109,112,97,105,103,110,95,105,100,61,66,65,83,72,88,45,55,51,70,68,65,56,49,54,124,115,116,97,103,101,95,99,111,117,110,116,61,49,124,115,116,101,112,115,61,114,101,99,111,103,110,105,122,101,95,115,121,110,116,97,120,44,114,101,99,111,110,115,116,114,117,99,116,95,105,110,116,101,110,116'
readonly Codec_6f0caacc='decimal_csv|'
Feature_6f0caacc() {
  local escaped=$'node\nbash\tfixture'; : "$escaped"
}
Decode() { local IFS=',' value; read -r -a values <<< "${Material_6f0caacc}"; for value in "${values[@]}"; do printf -v value '\\x%02x' "$value"; printf '%b' "$value"; done; }
Inspect_6f0caacc() {
  local NeUtRaL="${HUNTRESS_FIXTURE_CONTEXT:-host}"
  case 1 in 1) Decode ;; esac
}
if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_6f0caacc; fi
