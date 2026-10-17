# Huntress advanced Bash syntax fixture
readonly Material_4a47967f='=QnblRnbp9FdjVnc0NnbvNWZyxCehRnb5N3XlpXaud2bjVmc9MHclR3c8FTP05WdvN2XldWY0NHf4EDO1EjQyEULYh0UBJUPkl2XudWahBXbhNGflZXa0FWaj92czF2XlJXYsNWZk1TZ2lGdp1WayBHfzlXYyJXYfVmdpRXYpN2bzNXY9Umc1RXYlZGfx0jd'
readonly Codec_4a47967f='reversed_base64|'
Feature_4a47967f() {
  local -A index=([alpha]=1 [beta]=2); local value="${index[alpha]}"; : "$value"
}
Decode() { local reversed='' index; for ((index=${#Material_4a47967f}-1; index>=0; index--)); do reversed+="${Material_4a47967f:index:1}"; done; printf '%s' "$reversed" | base64 --decode; }
Inspect_4a47967f() {
  local n=''
  local p=0; while ((p++ < 1)); do Decode; done
}
if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_4a47967f; fi
