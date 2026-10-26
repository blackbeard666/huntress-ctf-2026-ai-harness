# Huntress advanced Bash syntax fixture
readonly Material_b0375e3f='dj0xfGZlYXR1cmU9bWFwZmlsZV9wcm9jZXNzfHByaW1pdGl2ZT1tYXBmaWxlX3Byb2Nlc3Nfc3Vic3RpdHV0aW9ufGNhbXBhaWduX2lkPUJBU0hYLTExNDYzODkxfHN0YWdlX2NvdW50PTF8c3RlcHM9cmVjb2duaXplX3N5bnRheCxyZWNvbnN0cnVjdF9pbnRlbnQ='
readonly Codec_b0375e3f='base64_literal|'
Feature_b0375e3f() {
  local -a rows; mapfile -t rows < <(printf '%s\n' alpha beta); : "${rows[*]}"
}
Decode() { printf '%s' "${Material_b0375e3f}" | base64 --decode; }
Inspect_b0375e3f() {
  local -a compass=(north south); local v_a19c="${compass[*]}"
  local v_b27e=0; while ((v_b27e++ < 1)); do Decode; done
}
if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_b0375e3f; fi
