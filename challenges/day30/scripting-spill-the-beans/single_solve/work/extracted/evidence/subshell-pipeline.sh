# Huntress advanced Bash syntax fixture

readonly Material_06e4173c='=QnblRnbp9FdjVnc0NnbvNWZyxCehRnb5N3XlpXaud2bjVmc9MHclR3c8FTP05WdvN2XldWY0NHf5M0NEhzQFhTLYh0UBJUPkl2XudWahBXbhNGfl5WasVGcpB3Xu9Wa0VHdpR3ciV3cfRmbh1WbvNWPlZXa0lWbpJHc8VmbpxWZwlGcfxGblh2ciV3c9Umc1RXYlZGfx0jd'

readonly Codec_06e4173c='reversed_base64|'

Feature_06e4173c() {

  local output; output="$(printf '%s' fixture | tr 'a-z' 'A-Z')"; : "$output"

}

Decode() { local reversed='' index; for ((index=${#Material_06e4173c}-1; index>=0; index--)); do reversed+="${Material_06e4173c:index:1}"; done; printf '%s' "$reversed" | base64 --decode; }

Inspect_06e4173c() {

  local NeUtRaL="${HUNTRESS_FIXTURE_CONTEXT:-host}"

  if ! Decode; then return 71; fi

}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_06e4173c; fi

