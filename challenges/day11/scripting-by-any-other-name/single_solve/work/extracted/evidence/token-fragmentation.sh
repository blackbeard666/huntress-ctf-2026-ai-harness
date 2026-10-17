# Huntress advanced Bash syntax fixture

readonly Material_f2036bb8='dj0xfGZlYXR1cmU9dG9rZW5fZnJhZ21lbnRhdGlvbnxwcmltaXRpdmU9YXJyYXlfdG9rZW5fY29uc3RydWN0aW9ufGNhbXBhaWduX2lkPUJBU0hYLTAwNzdGRTQxfHN0YWdlX2NvdW50PTF8c3RlcHM9cmVjb2duaXplX3N5bnRheCxyZWNvbnN0cnVjdF9pbnRlbnQ='

readonly Codec_f2036bb8='base64_literal|'

Feature_f2036bb8() {

  local -a command_parts=('cu' 'rl' '--fail'); local joined="${command_parts[*]}"; : "$joined"

}

Decode() { printf '%s' "${Material_f2036bb8}" | base64 --decode; }

Inspect_f2036bb8() {

  local -a compass=(north south); local NeUtRaL="${compass[*]}"

  Decode

}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_f2036bb8; fi

