# Huntress advanced Bash syntax fixture
readonly Material_f498b292='dj0xfGZlYXR1cmU9aGVyZV9zdHJpbmd8cHJpbWl0aXZlPWhlcmVfc3RyaW5nX3JlYWR8Y2FtcGFpZ25faWQ9QkFTSFgtQUZFMkY5RjN8c3RhZ2VfY291bnQ9MXxzdGVwcz1yZWNvZ25pemVfc3ludGF4LHJlY29uc3RydWN0X2ludGVudA=='
readonly Codec_f498b292='base64_literal|'
Feature_f498b292() {
  local value; read -r value <<< 'fixture line'; : "$value"
}
Decode() { printf '%s' "${Material_f498b292}" | base64 --decode; }
Inspect_f498b292() {
  local -a series=(3 5 8 13); local item1="${series[*]:1:2}"
  Decode
}
if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_f498b292; fi
