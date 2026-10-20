  # Huntress advanced Bash syntax fixture
  readonly Material_021086e0='dj0xfGZlYXR1cmU9cHJvY2Vzc19zdWJzdGl0dXRpb258cHJpbWl0aXZlPXByb2Nlc3Nfc3Vic3RpdHV0aW9uX3JlYWRlcnxjYW1wYWlnbl9pZD1CQVNIWC0xOTM1MjQzM3xzdGFnZV9jb3VudD0xfHN0ZXBzPXJlY29nbml6ZV9zeW50YXgscmVjb25zdHJ1Y3RfaW50ZW50'
  readonly Codec_021086e0='base64_literal|'
  Feature_021086e0() {
    local value; while read -r value; do : "$value"; done < <(printf '%s\n' fixture)
  }
  Decode() { printf '%s' "${Material_021086e0}" | base64 --decode; }
  Inspect_021086e0() {
    local -a series=(3 5 8 13); local v_a19c="${series[*]:1:2}"
    local decode_target=Decode; "$decode_target"
  }
  if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_021086e0; fi
