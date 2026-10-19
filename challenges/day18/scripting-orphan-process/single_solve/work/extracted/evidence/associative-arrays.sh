# Huntress advanced Bash syntax fixture
readonly Material_b4348a7c='dj0xfGZlYXR1cmU9YXNzb2NpYXRpdmVfYXJyYXlzfHByaW1pdGl2ZT1kZWNsYXJlX2Fzc29jaWF0aXZlfGNhbXBhaWduX2lkPUJBU0hYLTkyRTc0RUMyfHN0YWdlX2NvdW50PTF8c3RlcHM9cmVjb2duaXplX3N5bnRheCxyZWNvbnN0cnVjdF9pbnRlbnQ='
readonly Codec_b4348a7c='base64_literal|'
Feature_b4348a7c() {
  local -A index=([alpha]=1 [beta]=2); local value="${index[alpha]}"; : "$value"
}
Decode() { printf '%s' "${Material_b4348a7c}" | base64 --decode; }
Inspect_b4348a7c() {
  local harmless_value; if ((2 > 1)); then harmless_value=left; else harmless_value=right; fi
  if ! Decode; then return 71; fi
}
if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_b4348a7c; fi
