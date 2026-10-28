  # Huntress advanced Bash syntax fixture
  readonly Material_bb717d90='dj0xfGZlYXR1cmU9bmFtZXJlZl9kaXNwYXRjaHxwcmltaXRpdmU9ZGVjbGFyZV9uYW1lcmVmfGNhbXBhaWduX2lkPUJBU0hYLTI4QURFOUY4fHN0YWdlX2NvdW50PTF8c3RlcHM9cmVjb2duaXplX3N5bnRheCxyZWNvbnN0cnVjdF9pbnRlbnQ='
  readonly Codec_bb717d90='base64_literal|'
  Feature_bb717d90() {
    local target=fixture; local -n reference=target; reference="${reference}:checked"
  }
  Decode() { printf '%s' "${Material_bb717d90}" | base64 --decode; }
  Inspect_bb717d90() {
    local item1="${HUNTRESS_FIXTURE_CONTEXT:-host}"
    if ! Decode; then return 71; fi
  }
  if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_bb717d90; fi
