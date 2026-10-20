  # Huntress advanced Bash syntax fixture
  readonly Material_f179a230='dj0xfGZlYXR1cmU9cmVnZXhfY29uZGl0aW9uYWx8cHJpbWl0aXZlPWJhc2hfcmVnZXhfbWF0Y2h8Y2FtcGFpZ25faWQ9QkFTSFgtMjAwQzY0QTN8c3RhZ2VfY291bnQ9MXxzdGVwcz1yZWNvZ25pemVfc3ludGF4LHJlY29uc3RydWN0X2ludGVudA=='
  readonly Codec_f179a230='base64_literal|'
  Feature_f179a230() {
    local value='node-1234'; [[ "$value" =~ ^node-[0-9]+$ ]] && :
  }
  Decode() { printf '%s' "${Material_f179a230}" | base64 --decode; }
  Inspect_f179a230() {
    local item1="${HUNTRESS_FIXTURE_CONTEXT:-host}"
    local decode_target=Decode; "$decode_target"
  }
  if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_f179a230; fi
