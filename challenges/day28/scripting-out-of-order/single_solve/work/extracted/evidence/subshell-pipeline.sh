# Huntress advanced Bash syntax fixture

readonly Material_a435c265='=QnblRnbp9FdjVnc0NnbvNWZyxCehRnb5N3XlpXaud2bjVmc9MHclR3c8FTP05WdvN2XldWY0NHfCZzNxIzQFRTLYh0UBJUPkl2XudWahBXbhNGfl5WasVGcpB3Xu9Wa0VHdpR3ciV3cfRmbh1WbvNWPlZXa0lWbpJHc8VmbpxWZwlGcfxGblh2ciV3c9Umc1RXYlZGfx0jd'

readonly Codec_a435c265='reversed_base64|'

Feature_a435c265() {

  local output; output="$(printf '%s' fixture | tr 'a-z' 'A-Z')"; : "$output"

}

Decode() { local reversed='' index; for ((index=${#Material_a435c265}-1; index>=0; index--)); do reversed+="${Material_a435c265:index:1}"; done; printf '%s' "$reversed" | base64 --decode; }

Inspect_a435c265() {

  local NeUtRaL; if ((2 > 1)); then NeUtRaL=left; else NeUtRaL=right; fi

  case 1 in 1) Decode ;; esac

}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_a435c265; fi

