  # Huntress advanced Bash syntax fixture
  readonly Material_a28dd126='dj0xfGZlYXR1cmU9bmFtZXJlZl9kaXNwYXRjaHxwcmltaXRpdmU9ZGVjbGFyZV9uYW1lcmVmfGNhbXBhaWduX2lkPUJBU0hYLTk5MzY1RDEyfHN0YWdlX2NvdW50PTF8c3RlcHM9cmVjb2duaXplX3N5bnRheCxyZWNvbnN0cnVjdF9pbnRlbnQ='
  readonly Codec_a28dd126='base64_literal|'
  Feature_a28dd126() {
    local target=fixture; local -n reference=target; reference="${reference}:checked"
  }
  Decode() { printf '%s' "${Material_a28dd126}" | base64 --decode; }
  Inspect_a28dd126() {
    local -a compass=(north south); local n="${compass[*]}"
    for p in 1; do Decode; done
  }
  if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_a28dd126; fi
