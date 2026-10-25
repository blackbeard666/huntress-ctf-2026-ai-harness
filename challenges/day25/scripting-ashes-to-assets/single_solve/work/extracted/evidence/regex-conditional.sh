# Huntress advanced Bash syntax fixture

readonly Material_c73004f3='dj0xfGZlYXR1cmU9cmVnZXhfY29uZGl0aW9uYWx8cHJpbWl0aXZlPWJhc2hfcmVnZXhfbWF0Y2h8Y2FtcGFpZ25faWQ9QkFTSFgtQTRCQjA4NTB8c3RhZ2VfY291bnQ9MXxzdGVwcz1yZWNvZ25pemVfc3ludGF4LHJlY29uc3RydWN0X2ludGVudA=='

readonly Codec_c73004f3='base64_literal|'

Feature_c73004f3() {

  local value='node-1234'; [[ "$value" =~ ^node-[0-9]+$ ]] && :

}

Decode() { printf '%s' "${Material_c73004f3}" | base64 --decode; }

Inspect_c73004f3() {

  local n="${HUNTRESS_FIXTURE_CONTEXT:-host}"

  local p=0; while ((p++ < 1)); do Decode; done

}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_c73004f3; fi

