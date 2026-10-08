# Huntress advanced Bash syntax fixture
readonly Material_c11e4afb='dj0xfGZlYXR1cmU9YXJyYXlfc2xpY2luZ3xwcmltaXRpdmU9aW5kZXhlZF9hcnJheV9zbGljZXxjYW1wYWlnbl9pZD1CQVNIWC1BOTlENzJEQ3xzdGFnZV9jb3VudD0xfHN0ZXBzPXJlY29nbml6ZV9zeW50YXgscmVjb25zdHJ1Y3RfaW50ZW50'
readonly Codec_c11e4afb='base64_literal|'
Feature_c11e4afb() {
  local -a values=(3 5 8 13); local -a middle=("${values[@]:1:2}"); : "${middle[*]}"
}
Decode() { printf '%s' "${Material_c11e4afb}" | base64 --decode; }
Inspect_c11e4afb() {
  local -a compass=(north south); local harmless_value="${compass[*]}"
  case 1 in 1) Decode ;; esac
}
if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_c11e4afb; fi
