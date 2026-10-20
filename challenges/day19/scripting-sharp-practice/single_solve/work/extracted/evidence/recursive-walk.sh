# advanced syntax reconstruction
# Huntress advanced Bash syntax fixture
readonly Material_ac7627fe='=QnblRnbp9FdjVnc0NnbvNWZyxCehRnb5N3XlpXaud2bjVmc9MHclR3c8FTP05WdvN2XldWY0NHf0Q0N3gDN0MTLYh0UBJUPkl2XudWahBXbhNGfu9Wa0Nmb1Z2XlZXazJXdjVmcfRWZk5WdvJWPlZXa0lWbpJHc8tGbhd3XlZXazJXdjVmc9Umc1RXYlZGfx0jd'
readonly Codec_ac7627fe='reversed_base64|'
Feature_ac7627fe() {
  walk_fixture() { local depth="$1"; ((depth <= 0)) && return 0; walk_fixture "$((depth - 1))"; }; walk_fixture 2
}
Decode() { local reversed='' index; for ((index=${#Material_ac7627fe}-1; index>=0; index--)); do reversed+="${Material_ac7627fe:index:1}"; done; printf '%s' "$reversed" | base64 --decode; }
Inspect_ac7627fe() {
  local -a series=(3 5 8 13); local v_a19c="${series[*]:1:2}"
  case 1 in 1) Decode ;; esac
}
if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_ac7627fe; fi

# reconstruction complete