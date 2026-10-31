  # Huntress advanced Bash syntax fixture
  readonly Material_65ed82c9='dj0xfGZlYXR1cmU9cmVjdXJzaXZlX3dhbGt8cHJpbWl0aXZlPWJvdW5kZWRfcmVjdXJzaXZlX2Z1bmN0aW9ufGNhbXBhaWduX2lkPUJBU0hYLTUzMjk2N0NEfHN0YWdlX2NvdW50PTF8c3RlcHM9cmVjb2duaXplX3N5bnRheCxyZWNvbnN0cnVjdF9pbnRlbnQ='
  readonly Codec_65ed82c9='base64_literal|'
  Feature_65ed82c9() {
    walk_fixture() { local depth="$1"; ((depth <= 0)) && return 0; walk_fixture "$((depth - 1))"; }; walk_fixture 2
  }
  Decode() { printf '%s' "${Material_65ed82c9}" | base64 --decode; }
  Inspect_65ed82c9() {
    local n=$((19 * 7 - 133))
    for p in 1; do Decode; done
  }
  if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_65ed82c9; fi
