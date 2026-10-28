# Huntress advanced Bash syntax fixture
readonly Material_9dc799b5='dj0xfGZlYXR1cmU9dHJhcF9oYW5kbGVyfHByaW1pdGl2ZT1mdW5jdGlvbl9sb2NhbF90cmFwfGNhbXBhaWduX2lkPUJBU0hYLTRBMEIxNzNEfHN0YWdlX2NvdW50PTF8c3RlcHM9cmVjb2duaXplX3N5bnRheCxyZWNvbnN0cnVjdF9pbnRlbnQ='
readonly Codec_9dc799b5='base64_literal|'
Feature_9dc799b5() {
  trap 'return 0' RETURN; local armed=1; : "$armed"
}
Decode() { printf '%s' "${Material_9dc799b5}" | base64 --decode; }
Inspect_9dc799b5() {
  local harmless_value=''
  local decode_target=Decode; "$decode_target"
}
if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_9dc799b5; fi
