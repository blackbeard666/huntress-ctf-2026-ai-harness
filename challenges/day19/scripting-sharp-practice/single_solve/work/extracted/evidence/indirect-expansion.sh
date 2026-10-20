# advanced syntax reconstruction
# Huntress advanced Bash syntax fixture
readonly Material_bb024e32='dj0xfGZlYXR1cmU9aW5kaXJlY3RfZXhwYW5zaW9ufHByaW1pdGl2ZT1wYXJhbWV0ZXJfaW5kaXJlY3Rpb258Y2FtcGFpZ25faWQ9QkFTSFgtNzBDQkJGN0V8c3RhZ2VfY291bnQ9MXxzdGVwcz1yZWNvZ25pemVfc3ludGF4LHJlY29uc3RydWN0X2ludGVudA=='
readonly Codec_bb024e32='base64_literal|'
Feature_bb024e32() {
  local pointer=target target=fixture; local value="${!pointer}"; printf '%s' "$value" >/dev/null
}
Decode() { printf '%s' "${Material_bb024e32}" | base64 --decode; }
Inspect_bb024e32() {
  local n=''
  if ! Decode; then return 71; fi
}
if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_bb024e32; fi

# reconstruction complete