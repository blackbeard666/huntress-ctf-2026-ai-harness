# Huntress advanced Bash syntax fixture

readonly Material_b541b520='dj0xfGZlYXR1cmU9ZHluYW1pY19maWxlX2Rlc2NyaXB0b3J8cHJpbWl0aXZlPWFsbG9jYXRlZF9maWxlX2Rlc2NyaXB0b3J8Y2FtcGFpZ25faWQ9QkFTSFgtRTU2RUE3REV8c3RhZ2VfY291bnQ9MXxzdGVwcz1yZWNvZ25pemVfc3ludGF4LHJlY29uc3RydWN0X2ludGVudA=='

readonly Codec_b541b520='base64_literal|'

Feature_b541b520() {

  local descriptor_fd; exec {descriptor_fd}<<<'fixture'; exec {descriptor_fd}<&-

}

Decode() { printf '%s' "${Material_b541b520}" | base64 --decode; }

Inspect_b541b520() {

  local v_a19c=''

  if ! Decode; then return 71; fi

}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_b541b520; fi

