  # Huntress advanced Bash syntax fixture
  readonly Material_d94e55ea='dj0xfGZlYXR1cmU9YW5zaV9jX3F1b3Rpbmd8cHJpbWl0aXZlPWFuc2lfY19lc2NhcGVfc3RyaW5nfGNhbXBhaWduX2lkPUJBU0hYLUNFQTA4NkQxfHN0YWdlX2NvdW50PTF8c3RlcHM9cmVjb2duaXplX3N5bnRheCxyZWNvbnN0cnVjdF9pbnRlbnQ='
  readonly Codec_d94e55ea='base64_literal|'
  Feature_d94e55ea() {
    local escaped=$'node\nbash\tfixture'; : "$escaped"
  }
  Decode() { printf '%s' "${Material_d94e55ea}" | base64 --decode; }
  Inspect_d94e55ea() {
    local -a series=(3 5 8 13); local item1="${series[*]:1:2}"
    case 1 in 1) Decode ;; esac
  }
  if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_d94e55ea; fi
