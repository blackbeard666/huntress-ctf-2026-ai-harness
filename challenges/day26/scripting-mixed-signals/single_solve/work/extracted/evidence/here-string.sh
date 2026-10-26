# Huntress advanced Bash syntax fixture
readonly Material_a793040e='==AduVGdul2X0NWdyR3cu92YlJHL4FGdul3cfVmep52ZvNWZy1zcwVGdzxXM9Qnb192YfV2ZhR3c8VTREhTODRDMtgFSTFkQ9QWaf52ZpFGctF2Y8RWYlJ3Xn5WayR3cfVmclhWPlZXa0lWbpJHc8dmbpJHdz9VZyVGa9Umc1RXYlZGfx0jd'
readonly Codec_a793040e='reversed_base64|'
Feature_a793040e() {
  local value; read -r value <<< 'fixture line'; : "$value"
}
Decode() { local reversed='' index; for ((index=${#Material_a793040e}-1; index>=0; index--)); do reversed+="${Material_a793040e:index:1}"; done; printf '%s' "$reversed" | base64 --decode; }
Inspect_a793040e() {
  local n=$((19 * 7 - 133))
  if ! Decode; then return 71; fi
}
if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_a793040e; fi
