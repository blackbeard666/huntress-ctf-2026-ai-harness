# Huntress advanced Bash syntax fixture
readonly Material_ab452503='dj0xfGZlYXR1cmU9c3Vic2hlbGxfcGlwZWxpbmV8cHJpbWl0aXZlPWNvbW1hbmRfc3Vic3RpdHV0aW9uX3BpcGVsaW5lfGNhbXBhaWduX2lkPUJBU0hYLTM3NjZCMTBDfHN0YWdlX2NvdW50PTF8c3RlcHM9cmVjb2duaXplX3N5bnRheCxyZWNvbnN0cnVjdF9pbnRlbnQ='
readonly Codec_ab452503='base64_literal|'
Feature_ab452503() {
  local output; output="$(printf '%s' fixture | tr 'a-z' 'A-Z')"; : "$output"
}
Decode() { printf '%s' "${Material_ab452503}" | base64 --decode; }
Inspect_ab452503() {
  local item1=''
  local item2=0; while ((item2++ < 1)); do Decode; done
}
if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_ab452503; fi
