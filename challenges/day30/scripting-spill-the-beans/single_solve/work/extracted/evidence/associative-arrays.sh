# Huntress advanced Bash syntax fixture
readonly Material_ee17b1ce='118,61,49,124,102,101,97,116,117,114,101,61,97,115,115,111,99,105,97,116,105,118,101,95,97,114,114,97,121,115,124,112,114,105,109,105,116,105,118,101,61,100,101,99,108,97,114,101,95,97,115,115,111,99,105,97,116,105,118,101,124,99,97,109,112,97,105,103,110,95,105,100,61,66,65,83,72,88,45,70,57,57,49,53,53,68,65,124,115,116,97,103,101,95,99,111,117,110,116,61,49,124,115,116,101,112,115,61,114,101,99,111,103,110,105,122,101,95,115,121,110,116,97,120,44,114,101,99,111,110,115,116,114,117,99,116,95,105,110,116,101,110,116'
readonly Codec_ee17b1ce='decimal_csv|'
Feature_ee17b1ce() {
  local -A index=([alpha]=1 [beta]=2); local value="${index[alpha]}"; : "$value"
}
Decode() { local IFS=',' value; read -r -a values <<< "${Material_ee17b1ce}"; for value in "${values[@]}"; do printf -v value '\\x%02x' "$value"; printf '%b' "$value"; done; }
Inspect_ee17b1ce() {
  local NeUtRaL=''
  local decode_target=Decode; "$decode_target"
}
if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_ee17b1ce; fi
