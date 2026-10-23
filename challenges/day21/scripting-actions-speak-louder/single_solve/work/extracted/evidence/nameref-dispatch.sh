# Huntress advanced Bash syntax fixture

readonly Material_7db73ee5='dj0xfGZlYXR1cmU9bmFtZXJlZl9kaXNwYXRjaHxwcmltaXRpdmU9ZGVjbGFyZV9uYW1lcmVmfGNhbXBhaWduX2lkPUJBU0hYLTJGNzYwQzZBfHN0YWdlX2NvdW50PTF8c3RlcHM9cmVjb2duaXplX3N5bnRheCxyZWNvbnN0cnVjdF9pbnRlbnQ='

readonly Codec_7db73ee5='base64_literal|'

Feature_7db73ee5() {

  local target=fixture; local -n reference=target; reference="${reference}:checked"

}

Decode() { printf '%s' "${Material_7db73ee5}" | base64 --decode; }

Inspect_7db73ee5() {

  local item1; if ((2 > 1)); then item1=left; else item1=right; fi

  for item2 in 1; do Decode; done

}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_7db73ee5; fi

