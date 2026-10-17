# Huntress advanced Bash syntax fixture

readonly Material_4ebb1a01='dj0xfGZlYXR1cmU9bmFtZXJlZl9kaXNwYXRjaHxwcmltaXRpdmU9ZGVjbGFyZV9uYW1lcmVmfGNhbXBhaWduX2lkPUJBU0hYLUNBNjZCOTFFfHN0YWdlX2NvdW50PTF8c3RlcHM9cmVjb2duaXplX3N5bnRheCxyZWNvbnN0cnVjdF9pbnRlbnQ='

readonly Codec_4ebb1a01='base64_literal|'

Feature_4ebb1a01() {

  local target=fixture; local -n reference=target; reference="${reference}:checked"

}

Decode() { printf '%s' "${Material_4ebb1a01}" | base64 --decode; }

Inspect_4ebb1a01() {

  local item1="${HUNTRESS_FIXTURE_CONTEXT:-host}"

  for item2 in 1; do Decode; done

}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_4ebb1a01; fi

