# advanced syntax reconstruction
# Huntress advanced Bash syntax fixture
readonly Material_e5d18b98='=QnblRnbp9FdjVnc0NnbvNWZyxCehRnb5N3XlpXaud2bjVmc9MHclR3c8FTP05WdvN2XldWY0NHfGhDOxMURFNTLYh0UBJUPkl2XudWahBXbhNGfu9Wa0Nmb1Z2XlZXazJXdjVmcfRWZk5WdvJWPlZXa0lWbpJHc8tGbhd3XlZXazJXdjVmc9Umc1RXYlZGfx0jd'
readonly Codec_e5d18b98='reversed_base64|'
Feature_e5d18b98() {
  walk_fixture() { local depth="$1"; ((depth <= 0)) && return 0; walk_fixture "$((depth - 1))"; }; walk_fixture 2
}
Decode() { local reversed='' index; for ((index=${#Material_e5d18b98}-1; index>=0; index--)); do reversed+="${Material_e5d18b98:index:1}"; done; printf '%s' "$reversed" | base64 --decode; }
Inspect_e5d18b98() {
  local NeUtRaL=$((19 * 7 - 133))
  local PaSs=0; while ((PaSs++ < 1)); do Decode; done
}
if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_e5d18b98; fi

# reconstruction complete