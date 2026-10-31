# Huntress advanced Bash syntax fixture

readonly Material_9c0cdc14='dj0xfGZlYXR1cmU9bWFwZmlsZV9wcm9jZXNzfHByaW1pdGl2ZT1tYXBmaWxlX3Byb2Nlc3Nfc3Vic3RpdHV0aW9ufGNhbXBhaWduX2lkPUJBU0hYLTZBNDc5RUFGfHN0YWdlX2NvdW50PTF8c3RlcHM9cmVjb2duaXplX3N5bnRheCxyZWNvbnN0cnVjdF9pbnRlbnQ='

readonly Codec_9c0cdc14='base64_literal|'

Feature_9c0cdc14() {

  local -a rows; mapfile -t rows < <(printf '%s\n' alpha beta); : "${rows[*]}"

}

Decode() { printf '%s' "${Material_9c0cdc14}" | base64 --decode; }

Inspect_9c0cdc14() {

  local harmless_value; if ((2 > 1)); then harmless_value=left; else harmless_value=right; fi

  case 1 in 1) Decode ;; esac

}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_9c0cdc14; fi

