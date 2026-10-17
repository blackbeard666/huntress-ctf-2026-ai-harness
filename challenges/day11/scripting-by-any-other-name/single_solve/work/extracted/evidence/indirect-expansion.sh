# Huntress advanced Bash syntax fixture
readonly Material_4754a64a='==AduVGdul2X0NWdyR3cu92YlJHL4FGdul3cfVmep52ZvNWZy1zcwVGdzxXM9Qnb192YfV2ZhR3c8FTOzcjNBZERtgFSTFkQ9QWaf52ZpFGctF2Y852bpR3YlJXak5WafJXZ0VWbhJXYw1TZ2lGdp1WayBHfu9Waz5WYwhXZfR3YlJXak5Wa9Umc1RXYlZGfx0jd'
readonly Codec_4754a64a='reversed_base64|'
Feature_4754a64a() {
  local pointer=target target=fixture; local value="${!pointer}"; printf '%s' "$value" >/dev/null
}
Decode() { local reversed='' index; for ((index=${#Material_4754a64a}-1; index>=0; index--)); do reversed+="${Material_4754a64a:index:1}"; done; printf '%s' "$reversed" | base64 --decode; }
Inspect_4754a64a() {
  local NeUtRaL; if ((2 > 1)); then NeUtRaL=left; else NeUtRaL=right; fi
  Decode
}
if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_4754a64a; fi
