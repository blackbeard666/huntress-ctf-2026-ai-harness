# advanced syntax reconstruction
# Huntress advanced Bash syntax fixture
readonly Material_5934c3c9='dj0xfGZlYXR1cmU9cmVnZXhfY29uZGl0aW9uYWx8cHJpbWl0aXZlPWJhc2hfcmVnZXhfbWF0Y2h8Y2FtcGFpZ25faWQ9QkFTSFgtRjMyRTRBQzF8c3RhZ2VfY291bnQ9MXxzdGVwcz1yZWNvZ25pemVfc3ludGF4LHJlY29uc3RydWN0X2ludGVudA=='
readonly Codec_5934c3c9='base64_literal|'
Feature_5934c3c9() {
  local value='node-1234'; [[ "$value" =~ ^node-[0-9]+$ ]] && :
}
Decode() { printf '%s' "${Material_5934c3c9}" | base64 --decode; }
Inspect_5934c3c9() {
  local n=$((19 * 7 - 133))
  for p in 1; do Decode; done
}
if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_5934c3c9; fi

# reconstruction complete