# Huntress advanced Bash syntax fixture
readonly Material_8ee1858d='f8b3bff2e8ebeffafbfcebb3efe0fde7d1edd1fffbe1fae7e0e9f2fefce7e3e7fae7f8ebb3efe0fde7d1edd1ebfdedeffeebd1fdfafce7e0e9f2edefe3feefe7e9e0d1e7eab3cccfddc6d6a3cdcdb6b6ccbab7bef2fdfaefe9ebd1ede1fbe0fab3bff2fdfaebfefdb3fcebede1e9e0e7f4ebd1fdf7e0faeff6a2fcebede1e0fdfafcfbedfad1e7e0faebe0fa'
readonly Codec_8ee1858d='xor_hex|8e'
Feature_8ee1858d() {
  local escaped=$'node\nbash\tfixture'; : "$escaped"
}
Decode() { local raw="${Material_8ee1858d}" index value; for ((index=0; index<${#raw}; index+=2)); do value=$((16#${raw:index:2} ^ 16#8e)); printf -v value '\\x%02x' "$value"; printf '%b' "$value"; done; }
Inspect_8ee1858d() {
  local -a compass=(north south); local harmless_value="${compass[*]}"
  Decode
}
if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_8ee1858d; fi
