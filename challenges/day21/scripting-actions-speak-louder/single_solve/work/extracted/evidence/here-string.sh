# Huntress advanced Bash syntax fixture

readonly Material_0491d4df='dj0xfGZlYXR1cmU9aGVyZV9zdHJpbmd8cHJpbWl0aXZlPWhlcmVfc3RyaW5nX3JlYWR8Y2FtcGFpZ25faWQ9QkFTSFgtRTI3MDUzREN8c3RhZ2VfY291bnQ9MXxzdGVwcz1yZWNvZ25pemVfc3ludGF4LHJlY29uc3RydWN0X2ludGVudA=='

readonly Codec_0491d4df='base64_literal|'

Feature_0491d4df() {

  local value; read -r value <<< 'fixture line'; : "$value"

}

Decode() { printf '%s' "${Material_0491d4df}" | base64 --decode; }

Inspect_0491d4df() {

  local item1="${HUNTRESS_FIXTURE_CONTEXT:-host}"

  if ! Decode; then return 71; fi

}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_0491d4df; fi

