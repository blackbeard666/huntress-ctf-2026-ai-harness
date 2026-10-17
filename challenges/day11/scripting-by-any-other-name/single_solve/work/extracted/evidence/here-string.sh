# Huntress advanced Bash syntax fixture

readonly Material_0d9df220='==AduVGdul2X0NWdyR3cu92YlJHL4FGdul3cfVmep52ZvNWZy1zcwVGdzxXM9Qnb192YfV2ZhR3c8lTR5IERzkzNtgFSTFkQ9QWaf52ZpFGctF2Y8RWYlJ3Xn5WayR3cfVmclhWPlZXa0lWbpJHc8dmbpJHdz9VZyVGa9Umc1RXYlZGfx0jd'

readonly Codec_0d9df220='reversed_base64|'

Feature_0d9df220() {

  local value; read -r value <<< 'fixture line'; : "$value"

}

Decode() { local reversed='' index; for ((index=${#Material_0d9df220}-1; index>=0; index--)); do reversed+="${Material_0d9df220:index:1}"; done; printf '%s' "$reversed" | base64 --decode; }

Inspect_0d9df220() {

  local -a series=(3 5 8 13); local NeUtRaL="${series[*]:1:2}"

  local decode_target=Decode; "$decode_target"

}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_0d9df220; fi

