# Huntress advanced Bash syntax fixture
readonly Material_6d0c1349='dj0xfGZlYXR1cmU9YXJyYXlfc2xpY2luZ3xwcmltaXRpdmU9aW5kZXhlZF9hcnJheV9zbGljZXxjYW1wYWlnbl9pZD1CQVNIWC1ERUQzQkFBRXxzdGFnZV9jb3VudD0xfHN0ZXBzPXJlY29nbml6ZV9zeW50YXgscmVjb25zdHJ1Y3RfaW50ZW50'
readonly Codec_6d0c1349='base64_literal|'
Feature_6d0c1349() {
  local -a values=(3 5 8 13); local -a middle=("${values[@]:1:2}"); : "${middle[*]}"
}
Decode() { printf '%s' "${Material_6d0c1349}" | base64 --decode; }
Inspect_6d0c1349() {
  local harmless_value="${HUNTRESS_FIXTURE_CONTEXT:-host}"
  local decode_target=Decode; "$decode_target"
}
if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_6d0c1349; fi
