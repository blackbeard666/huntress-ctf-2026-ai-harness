# Huntress advanced Bash syntax fixture

readonly Material_cb0178ef='dj0xfGZlYXR1cmU9aW5kaXJlY3RfZXhwYW5zaW9ufHByaW1pdGl2ZT1wYXJhbWV0ZXJfaW5kaXJlY3Rpb258Y2FtcGFpZ25faWQ9QkFTSFgtNjc1MjAwMUR8c3RhZ2VfY291bnQ9MXxzdGVwcz1yZWNvZ25pemVfc3ludGF4LHJlY29uc3RydWN0X2ludGVudA=='

readonly Codec_cb0178ef='base64_literal|'

Feature_cb0178ef() {

  local pointer=target target=fixture; local value="${!pointer}"; printf '%s' "$value" >/dev/null

}

Decode() { printf '%s' "${Material_cb0178ef}" | base64 --decode; }

Inspect_cb0178ef() {

  local -a series=(3 5 8 13); local harmless_value="${series[*]:1:2}"

  Decode

}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_cb0178ef; fi

