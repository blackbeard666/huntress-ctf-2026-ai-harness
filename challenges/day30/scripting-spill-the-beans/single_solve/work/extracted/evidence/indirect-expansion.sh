# Huntress advanced Bash syntax fixture
readonly Material_2a7f7a98='5c171b564c4f4b5e5f584f1743444e43584f495e754f525a4b4459434544565a584347435e435c4f175a4b584b474f5e4f587543444e43584f495e43454456494b475a4b434d4475434e17686b79627207686c6b6c1b6b1c6f56595e4b4d4f7549455f445e171b56595e4f5a5917584f49454d4443504f755953445e4b5206584f494544595e585f495e7543445e4f445e'
readonly Codec_2a7f7a98='xor_hex|2a'
Feature_2a7f7a98() {
  local pointer=target target=fixture; local value="${!pointer}"; printf '%s' "$value" >/dev/null
}
Decode() { local raw="${Material_2a7f7a98}" index value; for ((index=0; index<${#raw}; index+=2)); do value=$((16#${raw:index:2} ^ 16#2a)); printf -v value '\\x%02x' "$value"; printf '%b' "$value"; done; }
Inspect_2a7f7a98() {
  local item1="${HUNTRESS_FIXTURE_CONTEXT:-host}"
  if ! Decode; then return 71; fi
}
if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_2a7f7a98; fi
