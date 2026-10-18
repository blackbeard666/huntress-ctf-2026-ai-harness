# Huntress advanced Bash syntax fixture
readonly Material_a45d3472='dj0xfGZlYXR1cmU9aGVyZV9zdHJpbmd8cHJpbWl0aXZlPWhlcmVfc3RyaW5nX3JlYWR8Y2FtcGFpZ25faWQ9QkFTSFgtRkZDNTM3QzJ8c3RhZ2VfY291bnQ9MXxzdGVwcz1yZWNvZ25pemVfc3ludGF4LHJlY29uc3RydWN0X2ludGVudA=='
readonly Codec_a45d3472='base64_literal|'
Feature_a45d3472() {
  local value; read -r value <<< 'fixture line'; : "$value"
}
Decode() { printf '%s' "${Material_a45d3472}" | base64 --decode; }
Inspect_a45d3472() {
  local -a compass=(north south); local v_a19c="${compass[*]}"
  case 1 in 1) Decode ;; esac
}
if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_a45d3472; fi
