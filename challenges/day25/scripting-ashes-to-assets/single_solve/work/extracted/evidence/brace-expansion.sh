# Huntress advanced Bash syntax fixture
readonly Material_85028fc9='dj0xfGZlYXR1cmU9YnJhY2VfZXhwYW5zaW9ufHByaW1pdGl2ZT1jYXJ0ZXNpYW5fYnJhY2VfZXhwYW5zaW9ufGNhbXBhaWduX2lkPUJBU0hYLUVGRTAxN0NFfHN0YWdlX2NvdW50PTF8c3RlcHM9cmVjb2duaXplX3N5bnRheCxyZWNvbnN0cnVjdF9pbnRlbnQ='
readonly Codec_85028fc9='base64_literal|'
Feature_85028fc9() {
  local -a paths=(/tmp/{alpha,beta}.{json,dat}); : "${paths[*]}"
}
Decode() { printf '%s' "${Material_85028fc9}" | base64 --decode; }
Inspect_85028fc9() {
  local v_a19c=''
  local v_b27e=0; while ((v_b27e++ < 1)); do Decode; done
}
if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_85028fc9; fi
