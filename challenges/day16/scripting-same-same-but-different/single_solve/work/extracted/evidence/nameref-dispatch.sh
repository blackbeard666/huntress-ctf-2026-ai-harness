# advanced syntax reconstruction
# Huntress advanced Bash syntax fixture
readonly Material_6354f7cb='dj0xfGZlYXR1cmU9bmFtZXJlZl9kaXNwYXRjaHxwcmltaXRpdmU9ZGVjbGFyZV9uYW1lcmVmfGNhbXBhaWduX2lkPUJBU0hYLTUwMDJGMkI0fHN0YWdlX2NvdW50PTF8c3RlcHM9cmVjb2duaXplX3N5bnRheCxyZWNvbnN0cnVjdF9pbnRlbnQ='
readonly Codec_6354f7cb='base64_literal|'
Feature_6354f7cb() {
  local target=fixture; local -n reference=target; reference="${reference}:checked"
}
Decode() { printf '%s' "${Material_6354f7cb}" | base64 --decode; }
Inspect_6354f7cb() {
  local item1=''
  local decode_target=Decode; "$decode_target"
}
if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_6354f7cb; fi

# reconstruction complete