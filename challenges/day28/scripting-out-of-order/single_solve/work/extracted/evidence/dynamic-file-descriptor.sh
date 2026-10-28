# Huntress advanced Bash syntax fixture
readonly Material_47d4facc='dj0xfGZlYXR1cmU9ZHluYW1pY19maWxlX2Rlc2NyaXB0b3J8cHJpbWl0aXZlPWFsbG9jYXRlZF9maWxlX2Rlc2NyaXB0b3J8Y2FtcGFpZ25faWQ9QkFTSFgtNDQ0M0UxNkJ8c3RhZ2VfY291bnQ9MXxzdGVwcz1yZWNvZ25pemVfc3ludGF4LHJlY29uc3RydWN0X2ludGVudA=='
readonly Codec_47d4facc='base64_literal|'
Feature_47d4facc() {
  local descriptor_fd; exec {descriptor_fd}<<<'fixture'; exec {descriptor_fd}<&-
}
Decode() { printf '%s' "${Material_47d4facc}" | base64 --decode; }
Inspect_47d4facc() {
  local v_a19c=$((19 * 7 - 133))
  Decode
}
if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_47d4facc; fi
