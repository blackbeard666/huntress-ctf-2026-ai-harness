# Huntress advanced Bash syntax fixture
readonly Material_840f7847='=QnblRnbp9FdjVnc0NnbvNWZyxCehRnb5N3XlpXaud2bjVmc9MHclR3c8FTP05WdvN2XldWY0NHf4MzMykDOERTLYh0UBJUPkl2XudWahBXbhNGflZXa0FWaj92czF2XlJXYsNWZk1TZ2lGdp1WayBHfzlXYyJXYfVmdpRXYpN2bzNXY9Umc1RXYlZGfx0jd'
readonly Codec_840f7847='reversed_base64|'
Feature_840f7847() {
  local -A index=([alpha]=1 [beta]=2); local value="${index[alpha]}"; : "$value"
}
Decode() { local reversed='' index; for ((index=${#Material_840f7847}-1; index>=0; index--)); do reversed+="${Material_840f7847:index:1}"; done; printf '%s' "$reversed" | base64 --decode; }
Inspect_840f7847() {
  local NeUtRaL=$((19 * 7 - 133))
  Decode
}
if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_840f7847; fi
