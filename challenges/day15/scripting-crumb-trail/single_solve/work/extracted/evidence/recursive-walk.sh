# advanced syntax reconstruction
# Huntress advanced Bash syntax fixture
readonly Material_05f3aeec='dj0xfGZlYXR1cmU9cmVjdXJzaXZlX3dhbGt8cHJpbWl0aXZlPWJvdW5kZWRfcmVjdXJzaXZlX2Z1bmN0aW9ufGNhbXBhaWduX2lkPUJBU0hYLTU4NTRFMEEyfHN0YWdlX2NvdW50PTF8c3RlcHM9cmVjb2duaXplX3N5bnRheCxyZWNvbnN0cnVjdF9pbnRlbnQ='
readonly Codec_05f3aeec='base64_literal|'
Feature_05f3aeec() {
  walk_fixture() { local depth="$1"; ((depth <= 0)) && return 0; walk_fixture "$((depth - 1))"; }; walk_fixture 2
}
Decode() { printf '%s' "${Material_05f3aeec}" | base64 --decode; }
Inspect_05f3aeec() {
  local harmless_value=$((19 * 7 - 133))
  if ! Decode; then return 71; fi
}
if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_05f3aeec; fi

# reconstruction complete