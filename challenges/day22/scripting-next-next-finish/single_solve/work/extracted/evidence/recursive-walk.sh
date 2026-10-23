# Huntress advanced Bash syntax fixture

readonly Material_59c77fd5='dj0xfGZlYXR1cmU9cmVjdXJzaXZlX3dhbGt8cHJpbWl0aXZlPWJvdW5kZWRfcmVjdXJzaXZlX2Z1bmN0aW9ufGNhbXBhaWduX2lkPUJBU0hYLTc3MEU4OTg0fHN0YWdlX2NvdW50PTF8c3RlcHM9cmVjb2duaXplX3N5bnRheCxyZWNvbnN0cnVjdF9pbnRlbnQ='

readonly Codec_59c77fd5='base64_literal|'

Feature_59c77fd5() {

  walk_fixture() { local depth="$1"; ((depth <= 0)) && return 0; walk_fixture "$((depth - 1))"; }; walk_fixture 2

}

Decode() { printf '%s' "${Material_59c77fd5}" | base64 --decode; }

Inspect_59c77fd5() {

  local harmless_value=$((19 * 7 - 133))

  case 1 in 1) Decode ;; esac

}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_59c77fd5; fi

