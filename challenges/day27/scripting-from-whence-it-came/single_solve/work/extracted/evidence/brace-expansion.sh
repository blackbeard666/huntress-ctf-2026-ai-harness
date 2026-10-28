# Huntress advanced Bash syntax fixture

readonly Material_d4926593='dj0xfGZlYXR1cmU9YnJhY2VfZXhwYW5zaW9ufHByaW1pdGl2ZT1jYXJ0ZXNpYW5fYnJhY2VfZXhwYW5zaW9ufGNhbXBhaWduX2lkPUJBU0hYLTREMTBDMDBBfHN0YWdlX2NvdW50PTF8c3RlcHM9cmVjb2duaXplX3N5bnRheCxyZWNvbnN0cnVjdF9pbnRlbnQ='

readonly Codec_d4926593='base64_literal|'

Feature_d4926593() {

  local -a paths=(/tmp/{alpha,beta}.{json,dat}); : "${paths[*]}"

}

Decode() { printf '%s' "${Material_d4926593}" | base64 --decode; }

Inspect_d4926593() {

  local item1="${HUNTRESS_FIXTURE_CONTEXT:-host}"

  local decode_target=Decode; "$decode_target"

}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_d4926593; fi

