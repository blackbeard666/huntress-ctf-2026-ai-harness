# advanced syntax reconstruction
# Huntress advanced Bash syntax fixture
readonly Material_6c1f13ea='dj0xfGZlYXR1cmU9YnJhY2VfZXhwYW5zaW9ufHByaW1pdGl2ZT1jYXJ0ZXNpYW5fYnJhY2VfZXhwYW5zaW9ufGNhbXBhaWduX2lkPUJBU0hYLTk0Rjk4MzRGfHN0YWdlX2NvdW50PTF8c3RlcHM9cmVjb2duaXplX3N5bnRheCxyZWNvbnN0cnVjdF9pbnRlbnQ='
readonly Codec_6c1f13ea='base64_literal|'
Feature_6c1f13ea() {
  local -a paths=(/tmp/{alpha,beta}.{json,dat}); : "${paths[*]}"
}
Decode() { printf '%s' "${Material_6c1f13ea}" | base64 --decode; }
Inspect_6c1f13ea() {
  local v_a19c=''
  if ! Decode; then return 71; fi
}
if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_6c1f13ea; fi

# reconstruction complete