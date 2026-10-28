# Huntress advanced Bash syntax fixture
readonly Material_4090bb61='dj0xfGZlYXR1cmU9aGVyZV9zdHJpbmd8cHJpbWl0aXZlPWhlcmVfc3RyaW5nX3JlYWR8Y2FtcGFpZ25faWQ9QkFTSFgtNzY1QUJBNjF8c3RhZ2VfY291bnQ9MXxzdGVwcz1yZWNvZ25pemVfc3ludGF4LHJlY29uc3RydWN0X2ludGVudA=='
readonly Codec_4090bb61='base64_literal|'
Feature_4090bb61() {
  local value; read -r value <<< 'fixture line'; : "$value"
}
Decode() { printf '%s' "${Material_4090bb61}" | base64 --decode; }
Inspect_4090bb61() {
  local -a compass=(north south); local harmless_value="${compass[*]}"
  if ! Decode; then return 71; fi
}
if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_4090bb61; fi
