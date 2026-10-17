# Huntress advanced Bash syntax fixture

readonly Material_c2d8b804='dj0xfGZlYXR1cmU9aGVyZV9zdHJpbmd8cHJpbWl0aXZlPWhlcmVfc3RyaW5nX3JlYWR8Y2FtcGFpZ25faWQ9QkFTSFgtQUU4RjM4RUZ8c3RhZ2VfY291bnQ9MXxzdGVwcz1yZWNvZ25pemVfc3ludGF4LHJlY29uc3RydWN0X2ludGVudA=='

readonly Codec_c2d8b804='base64_literal|'

Feature_c2d8b804() {

  local value; read -r value <<< 'fixture line'; : "$value"

}

Decode() { printf '%s' "${Material_c2d8b804}" | base64 --decode; }

Inspect_c2d8b804() {

  local -a series=(3 5 8 13); local n="${series[*]:1:2}"

  for p in 1; do Decode; done

}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_c2d8b804; fi

