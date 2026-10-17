# Huntress advanced Bash syntax fixture

readonly Material_5af67c8c='dj0xfGZlYXR1cmU9cmVjdXJzaXZlX3dhbGt8cHJpbWl0aXZlPWJvdW5kZWRfcmVjdXJzaXZlX2Z1bmN0aW9ufGNhbXBhaWduX2lkPUJBU0hYLUJENERBOUZGfHN0YWdlX2NvdW50PTF8c3RlcHM9cmVjb2duaXplX3N5bnRheCxyZWNvbnN0cnVjdF9pbnRlbnQ='

readonly Codec_5af67c8c='base64_literal|'

Feature_5af67c8c() {

  walk_fixture() { local depth="$1"; ((depth <= 0)) && return 0; walk_fixture "$((depth - 1))"; }; walk_fixture 2

}

Decode() { printf '%s' "${Material_5af67c8c}" | base64 --decode; }

Inspect_5af67c8c() {

  local -a compass=(north south); local NeUtRaL="${compass[*]}"

  local decode_target=Decode; "$decode_target"

}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_5af67c8c; fi

