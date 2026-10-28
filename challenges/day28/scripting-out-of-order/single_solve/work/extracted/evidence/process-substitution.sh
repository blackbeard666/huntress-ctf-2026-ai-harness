# Huntress advanced Bash syntax fixture
readonly Material_d63603a8='05WZ05WafR3Y1JHdz52bjVmcsgXY05Wez9VZ6lmbn92YlJXPzBXZ0NHfx0DduV3bj9VZnFGdzx3N3cjQ2MTRD1CWINVQC1DZp9lbnlWYw1WYjxnclRWYlJ3Xu9Wa0VHdpR3ciV3cfN3clN2byBXPlZXa0lWbpJHc852bpRXd0lGdzJWdz91czV2YvJHc9Umc1RXYlZGfx0jd'
readonly Codec_d63603a8='reversed_base64|'
Feature_d63603a8() {
  local value; while read -r value; do : "$value"; done < <(printf '%s\n' fixture)
}
Decode() { local reversed='' index; for ((index=${#Material_d63603a8}-1; index>=0; index--)); do reversed+="${Material_d63603a8:index:1}"; done; printf '%s' "$reversed" | base64 --decode; }
Inspect_d63603a8() {
  local harmless_value; if ((2 > 1)); then harmless_value=left; else harmless_value=right; fi
  Decode
}
if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_d63603a8; fi
