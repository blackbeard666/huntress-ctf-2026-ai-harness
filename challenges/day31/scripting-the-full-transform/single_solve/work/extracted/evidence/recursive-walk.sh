# Huntress advanced Bash syntax fixture

readonly Material_bf22ddec='=QnblRnbp9FdjVnc0NnbvNWZyxCehRnb5N3XlpXaud2bjVmc9MHclR3c8FTP05WdvN2XldWY0NHfGVTQGNDRFRULYh0UBJUPkl2XudWahBXbhNGfu9Wa0Nmb1Z2XlZXazJXdjVmcfRWZk5WdvJWPlZXa0lWbpJHc8tGbhd3XlZXazJXdjVmc9Umc1RXYlZGfx0jd'

readonly Codec_bf22ddec='reversed_base64|'

Feature_bf22ddec() {

  walk_fixture() { local depth="$1"; ((depth <= 0)) && return 0; walk_fixture "$((depth - 1))"; }; walk_fixture 2

}

Decode() { local reversed='' index; for ((index=${#Material_bf22ddec}-1; index>=0; index--)); do reversed+="${Material_bf22ddec:index:1}"; done; printf '%s' "$reversed" | base64 --decode; }

Inspect_bf22ddec() {

  local -a compass=(north south); local item1="${compass[*]}"

  Decode

}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_bf22ddec; fi

