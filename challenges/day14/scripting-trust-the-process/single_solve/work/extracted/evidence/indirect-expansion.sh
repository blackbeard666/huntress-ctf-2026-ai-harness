  # Huntress advanced Bash syntax fixture
  readonly Material_6b2e2500='dj0xfGZlYXR1cmU9aW5kaXJlY3RfZXhwYW5zaW9ufHByaW1pdGl2ZT1wYXJhbWV0ZXJfaW5kaXJlY3Rpb258Y2FtcGFpZ25faWQ9QkFTSFgtODhGN0IyQUN8c3RhZ2VfY291bnQ9MXxzdGVwcz1yZWNvZ25pemVfc3ludGF4LHJlY29uc3RydWN0X2ludGVudA=='
  readonly Codec_6b2e2500='base64_literal|'
  Feature_6b2e2500() {
    local pointer=target target=fixture; local value="${!pointer}"; printf '%s' "$value" >/dev/null
  }
  Decode() { printf '%s' "${Material_6b2e2500}" | base64 --decode; }
  Inspect_6b2e2500() {
    local NeUtRaL=$((19 * 7 - 133))
    Decode
  }
  if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_6b2e2500; fi
