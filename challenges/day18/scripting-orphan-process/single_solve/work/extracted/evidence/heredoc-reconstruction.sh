# Huntress advanced Bash syntax fixture
readonly Material_46664110='==AduVGdul2X0NWdyR3cu92YlJHL4FGdul3cfVmep52ZvNWZy1zcwVGdzxXM9Qnb192YfV2ZhR3c8FzQ5ETRDRjQtgFSTFkQ9QWaf52ZpFGctF2Y8N2bkVmclh2XkVGdvVXc9UmdpRXatlmcwxnbvlGdjVnc0NnbvNWZy91YvRWZyVGa9Umc1RXYlZGfx0jd'
readonly Codec_46664110='reversed_base64|'
Feature_46664110() {
local text; read -r -d '' text <<'HUNTRESS_EOF' || :
fixture line
HUNTRESS_EOF
  : "$text"
}
Decode() { local reversed='' index; for ((index=${#Material_46664110}-1; index>=0; index--)); do reversed+="${Material_46664110:index:1}"; done; printf '%s' "$reversed" | base64 --decode; }
Inspect_46664110() {
  local -a compass=(north south); local v_a19c="${compass[*]}"
  if ! Decode; then return 71; fi
}
if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_46664110; fi
