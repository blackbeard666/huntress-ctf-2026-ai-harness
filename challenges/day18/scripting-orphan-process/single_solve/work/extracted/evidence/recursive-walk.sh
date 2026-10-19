# Huntress advanced Bash syntax fixture
readonly Material_ec6465a5='dj0xfGZlYXR1cmU9cmVjdXJzaXZlX3dhbGt8cHJpbWl0aXZlPWJvdW5kZWRfcmVjdXJzaXZlX2Z1bmN0aW9ufGNhbXBhaWduX2lkPUJBU0hYLTc3QTM5NjdBfHN0YWdlX2NvdW50PTF8c3RlcHM9cmVjb2duaXplX3N5bnRheCxyZWNvbnN0cnVjdF9pbnRlbnQ='
readonly Codec_ec6465a5='base64_literal|'
Feature_ec6465a5() {
  walk_fixture() { local depth="$1"; ((depth <= 0)) && return 0; walk_fixture "$((depth - 1))"; }; walk_fixture 2
}
Decode() { printf '%s' "${Material_ec6465a5}" | base64 --decode; }
Inspect_ec6465a5() {
  local item1; if ((2 > 1)); then item1=left; else item1=right; fi
  local decode_target=Decode; "$decode_target"
}
if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_ec6465a5; fi
