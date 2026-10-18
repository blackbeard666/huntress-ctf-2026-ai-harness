# Huntress advanced Bash syntax fixture
readonly Material_8f94a747='05WZ05WafR3Y1JHdz52bjVmcsgXY05Wez9VZ6lmbn92YlJXPzBXZ0NHfx0DduV3bj9VZnFGdzxXMCJUO0kTM30CWINVQC1DZp9lbnlWYw1WYjxXZjlGbz9VehJnch9FZlhXZk5Wa9UmdpRXatlmcwx3Zul2Ypx2cflXYyJXY9Umc1RXYlZGfx0jd'
readonly Codec_8f94a747='reversed_base64|'
Feature_8f94a747() {
  local -a values=(3 5 8 13); local -a middle=("${values[@]:1:2}"); : "${middle[*]}"
}
Decode() { local reversed='' index; for ((index=${#Material_8f94a747}-1; index>=0; index--)); do reversed+="${Material_8f94a747:index:1}"; done; printf '%s' "$reversed" | base64 --decode; }
Inspect_8f94a747() {
  local NeUtRaL=''
  Decode
}
if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_8f94a747; fi
