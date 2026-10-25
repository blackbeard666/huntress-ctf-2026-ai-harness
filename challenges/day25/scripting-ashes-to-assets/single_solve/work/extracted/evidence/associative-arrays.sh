# Huntress advanced Bash syntax fixture
readonly Material_489e02df='dj0xfGZlYXR1cmU9YXNzb2NpYXRpdmVfYXJyYXlzfHByaW1pdGl2ZT1kZWNsYXJlX2Fzc29jaWF0aXZlfGNhbXBhaWduX2lkPUJBU0hYLTRFMEMxQ0VGfHN0YWdlX2NvdW50PTF8c3RlcHM9cmVjb2duaXplX3N5bnRheCxyZWNvbnN0cnVjdF9pbnRlbnQ='
readonly Codec_489e02df='base64_literal|'
Feature_489e02df() {
  local -A index=([alpha]=1 [beta]=2); local value="${index[alpha]}"; : "$value"
}
Decode() { printf '%s' "${Material_489e02df}" | base64 --decode; }
Inspect_489e02df() {
  local v_a19c=''
  case 1 in 1) Decode ;; esac
}
if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_489e02df; fi
