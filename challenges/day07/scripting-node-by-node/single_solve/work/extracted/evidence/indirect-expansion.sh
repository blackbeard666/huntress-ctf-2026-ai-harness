# Huntress advanced Bash syntax fixture
readonly Material_7465425b='dj0xfGZlYXR1cmU9aW5kaXJlY3RfZXhwYW5zaW9ufHByaW1pdGl2ZT1wYXJhbWV0ZXJfaW5kaXJlY3Rpb258Y2FtcGFpZ25faWQ9QkFTSFgtRjQzNEFFQTl8c3RhZ2VfY291bnQ9MXxzdGVwcz1yZWNvZ25pemVfc3ludGF4LHJlY29uc3RydWN0X2ludGVudA=='
readonly Codec_7465425b='base64_literal|'
Feature_7465425b() {
  local pointer=target target=fixture; local value="${!pointer}"; printf '%s' "$value" >/dev/null
}
Decode() { printf '%s' "${Material_7465425b}" | base64 --decode; }
Inspect_7465425b() {
  local -a compass=(north south); local item1="${compass[*]}"
  for item2 in 1; do Decode; done
}
if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_7465425b; fi
