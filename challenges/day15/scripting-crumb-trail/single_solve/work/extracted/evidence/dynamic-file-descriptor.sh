# Huntress advanced Bash syntax fixture
readonly Material_fdda5ac8='==AduVGdul2X0NWdyR3cu92YlJHL4FGdul3cfVmep52ZvNWZy1zcwVGdzxXM9Qnb192YfV2ZhR3c8FTRwQ0M1YzQtgFSTFkQ9QWaf52ZpFGctF2Y8J3b0BXayN2clR2XlxWam9FZlRXYj9GbsFWPlZXa0lWbpJHc8J3b0BXayN2clR2XlxWam91Yp1WYulHZ9Umc1RXYlZGfx0jd'
readonly Codec_fdda5ac8='reversed_base64|'
Feature_fdda5ac8() {
  local descriptor_fd; exec {descriptor_fd}<<<'fixture'; exec {descriptor_fd}<&-
}
Decode() { local reversed='' index; for ((index=${#Material_fdda5ac8}-1; index>=0; index--)); do reversed+="${Material_fdda5ac8:index:1}"; done; printf '%s' "$reversed" | base64 --decode; }
Inspect_fdda5ac8() {
  local harmless_value="${HUNTRESS_FIXTURE_CONTEXT:-host}"
  case 1 in 1) Decode ;; esac
}
if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_fdda5ac8; fi
