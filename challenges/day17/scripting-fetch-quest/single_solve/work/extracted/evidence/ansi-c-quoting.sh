# advanced syntax reconstruction
# Huntress advanced Bash syntax fixture
readonly Material_da0c191d='dj0xfGZlYXR1cmU9YW5zaV9jX3F1b3Rpbmd8cHJpbWl0aXZlPWFuc2lfY19lc2NhcGVfc3RyaW5nfGNhbXBhaWduX2lkPUJBU0hYLTlGNUUzRTAyfHN0YWdlX2NvdW50PTF8c3RlcHM9cmVjb2duaXplX3N5bnRheCxyZWNvbnN0cnVjdF9pbnRlbnQ='
readonly Codec_da0c191d='base64_literal|'
Feature_da0c191d() {
  local escaped=$'node\nbash\tfixture'; : "$escaped"
}
Decode() { printf '%s' "${Material_da0c191d}" | base64 --decode; }
Inspect_da0c191d() {
  local NeUtRaL="${HUNTRESS_FIXTURE_CONTEXT:-host}"
  if ! Decode; then return 71; fi
}
if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_da0c191d; fi

# reconstruction complete