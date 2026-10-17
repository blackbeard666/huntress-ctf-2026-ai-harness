  # Huntress advanced Bash syntax fixture
  readonly Material_787d560a='dj0xfGZlYXR1cmU9cmVjdXJzaXZlX3dhbGt8cHJpbWl0aXZlPWJvdW5kZWRfcmVjdXJzaXZlX2Z1bmN0aW9ufGNhbXBhaWduX2lkPUJBU0hYLTRBMDQ2OEIzfHN0YWdlX2NvdW50PTF8c3RlcHM9cmVjb2duaXplX3N5bnRheCxyZWNvbnN0cnVjdF9pbnRlbnQ='
  readonly Codec_787d560a='base64_literal|'
  Feature_787d560a() {
    walk_fixture() { local depth="$1"; ((depth <= 0)) && return 0; walk_fixture "$((depth - 1))"; }; walk_fixture 2
  }
  Decode() { printf '%s' "${Material_787d560a}" | base64 --decode; }
  Inspect_787d560a() {
    local n=$((19 * 7 - 133))
    local decode_target=Decode; "$decode_target"
  }
  if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_787d560a; fi
