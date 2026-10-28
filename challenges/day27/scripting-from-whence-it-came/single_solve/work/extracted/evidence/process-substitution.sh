# Huntress advanced Bash syntax fixture
readonly Material_4a64b57b='05WZ05WafR3Y1JHdz52bjVmcsgXY05Wez9VZ6lmbn92YlJXPzBXZ0NHfx0DduV3bj9VZnFGdzxnQ3IjNGFTMF1CWINVQC1DZp9lbnlWYw1WYjxnclRWYlJ3Xu9Wa0VHdpR3ciV3cfN3clN2byBXPlZXa0lWbpJHc852bpRXd0lGdzJWdz91czV2YvJHc9Umc1RXYlZGfx0jd'
readonly Codec_4a64b57b='reversed_base64|'
Feature_4a64b57b() {
  local value; while read -r value; do : "$value"; done < <(printf '%s\n' fixture)
}
Decode() { local reversed='' index; for ((index=${#Material_4a64b57b}-1; index>=0; index--)); do reversed+="${Material_4a64b57b:index:1}"; done; printf '%s' "$reversed" | base64 --decode; }
Inspect_4a64b57b() {
  local -a series=(3 5 8 13); local NeUtRaL="${series[*]:1:2}"
  Decode
}
if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_4a64b57b; fi
