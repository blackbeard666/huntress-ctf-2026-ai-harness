# Huntress advanced Bash syntax fixture
readonly Material_834816bd='dj0xfGZlYXR1cmU9cmVjdXJzaXZlX3dhbGt8cHJpbWl0aXZlPWJvdW5kZWRfcmVjdXJzaXZlX2Z1bmN0aW9ufGNhbXBhaWduX2lkPUJBU0hYLTlEQzU3MjM2fHN0YWdlX2NvdW50PTF8c3RlcHM9cmVjb2duaXplX3N5bnRheCxyZWNvbnN0cnVjdF9pbnRlbnQ='
readonly Codec_834816bd='base64_literal|'
Feature_834816bd() {
  walk_fixture() { local depth="$1"; ((depth <= 0)) && return 0; walk_fixture "$((depth - 1))"; }; walk_fixture 2
}
Decode() { printf '%s' "${Material_834816bd}" | base64 --decode; }
Inspect_834816bd() {
  local -a series=(3 5 8 13); local item1="${series[*]:1:2}"
  for item2 in 1; do Decode; done
}
if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_834816bd; fi
