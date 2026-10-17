# advanced syntax reconstruction
# Huntress advanced Bash syntax fixture
readonly Material_edce2741='dj0xfGZlYXR1cmU9aW5kaXJlY3RfZXhwYW5zaW9ufHByaW1pdGl2ZT1wYXJhbWV0ZXJfaW5kaXJlY3Rpb258Y2FtcGFpZ25faWQ9QkFTSFgtMjM2NkEzRkJ8c3RhZ2VfY291bnQ9MXxzdGVwcz1yZWNvZ25pemVfc3ludGF4LHJlY29uc3RydWN0X2ludGVudA=='
readonly Codec_edce2741='base64_literal|'
Feature_edce2741() {
  local pointer=target target=fixture; local value="${!pointer}"; printf '%s' "$value" >/dev/null
}
Decode() { printf '%s' "${Material_edce2741}" | base64 --decode; }
Inspect_edce2741() {
  local v_a19c=''
  local decode_target=Decode; "$decode_target"
}
if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_edce2741; fi

# reconstruction complete