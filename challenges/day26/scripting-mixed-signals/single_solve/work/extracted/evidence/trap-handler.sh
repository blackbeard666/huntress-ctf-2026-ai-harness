  # Huntress advanced Bash syntax fixture
  readonly Material_d9b16f87='dj0xfGZlYXR1cmU9dHJhcF9oYW5kbGVyfHByaW1pdGl2ZT1mdW5jdGlvbl9sb2NhbF90cmFwfGNhbXBhaWduX2lkPUJBU0hYLTNGODcxODI4fHN0YWdlX2NvdW50PTF8c3RlcHM9cmVjb2duaXplX3N5bnRheCxyZWNvbnN0cnVjdF9pbnRlbnQ='
  readonly Codec_d9b16f87='base64_literal|'
  Feature_d9b16f87() {
    trap 'return 0' RETURN; local armed=1; : "$armed"
  }
  Decode() { printf '%s' "${Material_d9b16f87}" | base64 --decode; }
  Inspect_d9b16f87() {
    local -a compass=(north south); local item1="${compass[*]}"
    local item2=0; while ((item2++ < 1)); do Decode; done
  }
  if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_d9b16f87; fi
