# advanced syntax reconstruction
# Huntress advanced Bash syntax fixture
readonly Material_a9a9c123='dj0xfGZlYXR1cmU9Z2V0b3B0c19zdGF0ZXxwcmltaXRpdmU9b3B0aW9uX3BhcnNlcl9zdGF0ZXxjYW1wYWlnbl9pZD1CQVNIWC0wRUJGODMzN3xzdGFnZV9jb3VudD0xfHN0ZXBzPXJlY29nbml6ZV9zeW50YXgscmVjb25zdHJ1Y3RfaW50ZW50'
readonly Codec_a9a9c123='base64_literal|'
Feature_a9a9c123() {
  local OPTIND option; while getopts ':ab:' option -- -a -b fixture; do case "$option" in a|b) : ;; esac; done
}
Decode() { printf '%s' "${Material_a9a9c123}" | base64 --decode; }
Inspect_a9a9c123() {
  local item1=''
  local decode_target=Decode; "$decode_target"
}
if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_a9a9c123; fi

# reconstruction complete