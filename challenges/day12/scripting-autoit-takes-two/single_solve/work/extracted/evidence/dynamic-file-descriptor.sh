# Huntress advanced Bash syntax fixture
readonly Material_9e3b85a8='==AduVGdul2X0NWdyR3cu92YlJHL4FGdul3cfVmep52ZvNWZy1zcwVGdzxXM9Qnb192YfV2ZhR3c8VzN0ADMGJTRtgFSTFkQ9QWaf52ZpFGctF2Y8J3b0BXayN2clR2XlxWam9FZlRXYj9GbsFWPlZXa0lWbpJHc8J3b0BXayN2clR2XlxWam91Yp1WYulHZ9Umc1RXYlZGfx0jd'
readonly Codec_9e3b85a8='reversed_base64|'
Feature_9e3b85a8() {
  local descriptor_fd; exec {descriptor_fd}<<<'fixture'; exec {descriptor_fd}<&-
}
Decode() { local reversed='' index; for ((index=${#Material_9e3b85a8}-1; index>=0; index--)); do reversed+="${Material_9e3b85a8:index:1}"; done; printf '%s' "$reversed" | base64 --decode; }
Inspect_9e3b85a8() {
  local -a series=(3 5 8 13); local n="${series[*]:1:2}"
  for p in 1; do Decode; done
}
if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_9e3b85a8; fi
