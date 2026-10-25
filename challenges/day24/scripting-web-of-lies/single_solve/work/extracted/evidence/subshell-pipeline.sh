# Huntress advanced Bash syntax fixture
readonly Material_0a1098a4='=QnblRnbp9FdjVnc0NnbvNWZyxCehRnb5N3XlpXaud2bjVmc9MHclR3c8FTP05WdvN2XldWY0NHfEhTN5MDN2UTLYh0UBJUPkl2XudWahBXbhNGfl5WasVGcpB3Xu9Wa0VHdpR3ciV3cfRmbh1WbvNWPlZXa0lWbpJHc8VmbpxWZwlGcfxGblh2ciV3c9Umc1RXYlZGfx0jd'
readonly Codec_0a1098a4='reversed_base64|'
Feature_0a1098a4() {
  local output; output="$(printf '%s' fixture | tr 'a-z' 'A-Z')"; : "$output"
}
Decode() { local reversed='' index; for ((index=${#Material_0a1098a4}-1; index>=0; index--)); do reversed+="${Material_0a1098a4:index:1}"; done; printf '%s' "$reversed" | base64 --decode; }
Inspect_0a1098a4() {
  local harmless_value="${HUNTRESS_FIXTURE_CONTEXT:-host}"
  case 1 in 1) Decode ;; esac
}
if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_0a1098a4; fi
