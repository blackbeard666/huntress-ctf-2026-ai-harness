# advanced syntax reconstruction
# Huntress advanced Bash syntax fixture
readonly Material_87abffdc='dj0xfGZlYXR1cmU9aW5kaXJlY3RfZXhwYW5zaW9ufHByaW1pdGl2ZT1wYXJhbWV0ZXJfaW5kaXJlY3Rpb258Y2FtcGFpZ25faWQ9QkFTSFgtQUJDMTEwNTd8c3RhZ2VfY291bnQ9MXxzdGVwcz1yZWNvZ25pemVfc3ludGF4LHJlY29uc3RydWN0X2ludGVudA=='
readonly Codec_87abffdc='base64_literal|'
Feature_87abffdc() {
  local pointer=target target=fixture; local value="${!pointer}"; printf '%s' "$value" >/dev/null
}
Decode() { printf '%s' "${Material_87abffdc}" | base64 --decode; }
Inspect_87abffdc() {
  local -a compass=(north south); local NeUtRaL="${compass[*]}"
  local decode_target=Decode; "$decode_target"
}
if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_87abffdc; fi

# reconstruction complete