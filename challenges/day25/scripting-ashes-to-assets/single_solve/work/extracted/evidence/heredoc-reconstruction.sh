# Huntress advanced Bash syntax fixture
readonly Material_293f420d='5f1418554f4c485d5c5b4c14414c5b4c4d464a765b4c4a46475a5d5b5c4a5d40464755595b4044405d405f4c14585c465d4c4d76414c5b4c4d464a554a48445948404e4776404d146b687a61710418681e6d1d1d6d1b555a5d484e4c764a465c475d1418555a5d4c595a145b4c4a464e4740534c765a50475d4851055b4c4a46475a5d5b5c4a5d7640475d4c475d'
readonly Codec_293f420d='xor_hex|29'
Feature_293f420d() {
local text; read -r -d '' text <<'HUNTRESS_EOF' || :
fixture line
HUNTRESS_EOF
  : "$text"
}
Decode() { local raw="${Material_293f420d}" index value; for ((index=0; index<${#raw}; index+=2)); do value=$((16#${raw:index:2} ^ 16#29)); printf -v value '\\x%02x' "$value"; printf '%b' "$value"; done; }
Inspect_293f420d() {
  local -a compass=(north south); local NeUtRaL="${compass[*]}"
  Decode
}
if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_293f420d; fi
