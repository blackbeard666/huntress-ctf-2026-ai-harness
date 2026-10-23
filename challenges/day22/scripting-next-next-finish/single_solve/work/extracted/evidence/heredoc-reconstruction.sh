# Huntress advanced Bash syntax fixture
readonly Material_0e5638ac='78333f72686b6f7a7b7c6b33666b7c6b6a616d517c6b6d61607d7a7c7b6d7a676160727e7c6763677a67786b337f7b617a6b6a51666b7c6b6a616d726d6f637e6f67696051676a334c4f5d4656234d4f4b4c3e3e4f3a727d7a6f696b516d617b607a333f727d7a6b7e7d337c6b6d61696067746b517d77607a6f76227c6b6d61607d7a7c7b6d7a5167607a6b607a'
readonly Codec_0e5638ac='xor_hex|0e'
Feature_0e5638ac() {
local text; read -r -d '' text <<'HUNTRESS_EOF' || :
fixture line
HUNTRESS_EOF
  : "$text"
}
Decode() { local raw="${Material_0e5638ac}" index value; for ((index=0; index<${#raw}; index+=2)); do value=$((16#${raw:index:2} ^ 16#0e)); printf -v value '\\x%02x' "$value"; printf '%b' "$value"; done; }
Inspect_0e5638ac() {
  local n=$((19 * 7 - 133))
  if ! Decode; then return 71; fi
}
if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_0e5638ac; fi
