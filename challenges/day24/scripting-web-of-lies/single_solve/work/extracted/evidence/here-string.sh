# Huntress advanced Bash syntax fixture

readonly Material_53a8760a='==AduVGdul2X0NWdyR3cu92YlJHL4FGdul3cfVmep52ZvNWZy1zcwVGdzxXM9Qnb192YfV2ZhR3c8hzQzYkQGZ0NtgFSTFkQ9QWaf52ZpFGctF2Y8RWYlJ3Xn5WayR3cfVmclhWPlZXa0lWbpJHc8dmbpJHdz9VZyVGa9Umc1RXYlZGfx0jd'

readonly Codec_53a8760a='reversed_base64|'

Feature_53a8760a() {

  local value; read -r value <<< 'fixture line'; : "$value"

}

Decode() { local reversed='' index; for ((index=${#Material_53a8760a}-1; index>=0; index--)); do reversed+="${Material_53a8760a:index:1}"; done; printf '%s' "$reversed" | base64 --decode; }

Inspect_53a8760a() {

  local item1; if ((2 > 1)); then item1=left; else item1=right; fi

  for item2 in 1; do Decode; done

}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_53a8760a; fi

