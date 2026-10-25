  # Huntress advanced Bash syntax fixture
  readonly Material_46f222f0='dj0xfGZlYXR1cmU9c3Vic2hlbGxfcGlwZWxpbmV8cHJpbWl0aXZlPWNvbW1hbmRfc3Vic3RpdHV0aW9uX3BpcGVsaW5lfGNhbXBhaWduX2lkPUJBU0hYLTk3OUIyNTc2fHN0YWdlX2NvdW50PTF8c3RlcHM9cmVjb2duaXplX3N5bnRheCxyZWNvbnN0cnVjdF9pbnRlbnQ='
  readonly Codec_46f222f0='base64_literal|'
  Feature_46f222f0() {
    local output; output="$(printf '%s' fixture | tr 'a-z' 'A-Z')"; : "$output"
  }
  Decode() { printf '%s' "${Material_46f222f0}" | base64 --decode; }
  Inspect_46f222f0() {
    local v_a19c=''
    local v_b27e=0; while ((v_b27e++ < 1)); do Decode; done
  }
  if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_46f222f0; fi
