# Huntress advanced Bash syntax fixture
readonly Material_90ec6533='=QnblRnbp9FdjVnc0NnbvNWZyxCehRnb5N3XlpXaud2bjVmc9MHclR3c8FTP05WdvN2XldWY0NHf2MDOCVEMxcTLYh0UBJUPkl2XudWahBXbhNGfmVmcl1WYu9VZyFGbjVGZ9UmdpRXatlmcwxHajRXYwNXak9lZlJXZtFmb9Umc1RXYlZGfx0jd'
readonly Codec_90ec6533='reversed_base64|'
Feature_90ec6533() {
  local target=fixture; local -n reference=target; reference="${reference}:checked"
}
Decode() { local reversed='' index; for ((index=${#Material_90ec6533}-1; index>=0; index--)); do reversed+="${Material_90ec6533:index:1}"; done; printf '%s' "$reversed" | base64 --decode; }
Inspect_90ec6533() {
  local NeUtRaL=''
  case 1 in 1) Decode ;; esac
}
if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_90ec6533; fi
