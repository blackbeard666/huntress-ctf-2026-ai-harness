  # Huntress advanced Bash syntax fixture
  readonly Material_f1920743='dj0xfGZlYXR1cmU9cmVjdXJzaXZlX3dhbGt8cHJpbWl0aXZlPWJvdW5kZWRfcmVjdXJzaXZlX2Z1bmN0aW9ufGNhbXBhaWduX2lkPUJBU0hYLUZGOTYyODMzfHN0YWdlX2NvdW50PTF8c3RlcHM9cmVjb2duaXplX3N5bnRheCxyZWNvbnN0cnVjdF9pbnRlbnQ='
  readonly Codec_f1920743='base64_literal|'
  Feature_f1920743() {
    walk_fixture() { local depth="$1"; ((depth <= 0)) && return 0; walk_fixture "$((depth - 1))"; }; walk_fixture 2
  }
  Decode() { printf '%s' "${Material_f1920743}" | base64 --decode; }
  Inspect_f1920743() {
    local item1=$((19 * 7 - 133))
    Decode
  }
  if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_f1920743; fi
