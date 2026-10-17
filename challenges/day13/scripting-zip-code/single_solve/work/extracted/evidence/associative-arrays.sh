# Huntress advanced Bash syntax fixture
readonly Material_a965f8c4='=QnblRnbp9FdjVnc0NnbvNWZyxCehRnb5N3XlpXaud2bjVmc9MHclR3c8FTP05WdvN2XldWY0NHfClzMGVzQFZULYh0UBJUPkl2XudWahBXbhNGflZXa0FWaj92czF2XlJXYsNWZk1TZ2lGdp1WayBHfzlXYyJXYfVmdpRXYpN2bzNXY9Umc1RXYlZGfx0jd'
readonly Codec_a965f8c4='reversed_base64|'
Feature_a965f8c4() {
  local -A index=([alpha]=1 [beta]=2); local value="${index[alpha]}"; : "$value"
}
Decode() { local reversed='' index; for ((index=${#Material_a965f8c4}-1; index>=0; index--)); do reversed+="${Material_a965f8c4:index:1}"; done; printf '%s' "$reversed" | base64 --decode; }
Inspect_a965f8c4() {
  local n=''
  for p in 1; do Decode; done
}
if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_a965f8c4; fi
