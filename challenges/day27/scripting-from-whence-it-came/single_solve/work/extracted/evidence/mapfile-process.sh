# Huntress advanced Bash syntax fixture

readonly Material_d976535e='dj0xfGZlYXR1cmU9bWFwZmlsZV9wcm9jZXNzfHByaW1pdGl2ZT1tYXBmaWxlX3Byb2Nlc3Nfc3Vic3RpdHV0aW9ufGNhbXBhaWduX2lkPUJBU0hYLTA5NEQ0RkNGfHN0YWdlX2NvdW50PTF8c3RlcHM9cmVjb2duaXplX3N5bnRheCxyZWNvbnN0cnVjdF9pbnRlbnQ='

readonly Codec_d976535e='base64_literal|'

Feature_d976535e() {

  local -a rows; mapfile -t rows < <(printf '%s\n' alpha beta); : "${rows[*]}"

}

Decode() { printf '%s' "${Material_d976535e}" | base64 --decode; }

Inspect_d976535e() {

  local -a series=(3 5 8 13); local n="${series[*]:1:2}"

  local p=0; while ((p++ < 1)); do Decode; done

}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_d976535e; fi

