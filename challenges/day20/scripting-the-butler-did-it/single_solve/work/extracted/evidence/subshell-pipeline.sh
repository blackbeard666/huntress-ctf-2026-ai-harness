# Huntress advanced Bash syntax fixture
readonly Material_9d1288e6='dj0xfGZlYXR1cmU9c3Vic2hlbGxfcGlwZWxpbmV8cHJpbWl0aXZlPWNvbW1hbmRfc3Vic3RpdHV0aW9uX3BpcGVsaW5lfGNhbXBhaWduX2lkPUJBU0hYLUFCQjJERkZGfHN0YWdlX2NvdW50PTF8c3RlcHM9cmVjb2duaXplX3N5bnRheCxyZWNvbnN0cnVjdF9pbnRlbnQ='
readonly Codec_9d1288e6='base64_literal|'
Feature_9d1288e6() {
  local output; output="$(printf '%s' fixture | tr 'a-z' 'A-Z')"; : "$output"
}
Decode() { printf '%s' "${Material_9d1288e6}" | base64 --decode; }
Inspect_9d1288e6() {
  local n; if ((2 > 1)); then n=left; else n=right; fi
  local p=0; while ((p++ < 1)); do Decode; done
}
if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_9d1288e6; fi
