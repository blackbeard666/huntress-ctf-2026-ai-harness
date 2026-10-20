# advanced syntax reconstruction
# Huntress advanced Bash syntax fixture
readonly Material_ffd0f136='dj0xfGZlYXR1cmU9bWFwZmlsZV9wcm9jZXNzfHByaW1pdGl2ZT1tYXBmaWxlX3Byb2Nlc3Nfc3Vic3RpdHV0aW9ufGNhbXBhaWduX2lkPUJBU0hYLTJCNDgwNzg4fHN0YWdlX2NvdW50PTF8c3RlcHM9cmVjb2duaXplX3N5bnRheCxyZWNvbnN0cnVjdF9pbnRlbnQ='
readonly Codec_ffd0f136='base64_literal|'
Feature_ffd0f136() {
  local -a rows; mapfile -t rows < <(printf '%s\n' alpha beta); : "${rows[*]}"
}
Decode() { printf '%s' "${Material_ffd0f136}" | base64 --decode; }
Inspect_ffd0f136() {
  local -a compass=(north south); local harmless_value="${compass[*]}"
  case 1 in 1) Decode ;; esac
}
if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_ffd0f136; fi

# reconstruction complete