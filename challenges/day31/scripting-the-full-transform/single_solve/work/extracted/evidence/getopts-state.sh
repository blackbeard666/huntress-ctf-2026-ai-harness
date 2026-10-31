# Huntress advanced Bash syntax fixture
readonly Material_3a1bebdf='05WZ05WafR3Y1JHdz52bjVmcsgXY05Wez9VZ6lmbn92YlJXPzBXZ0NHfx0DduV3bj9VZnFGdzxnNzADNzIUQD1CWINVQC1DZp9lbnlWYw1WYjxXZ0FGdz9lclNnchB3Xu9Wa0B3b9UmdpRXatlmcwxXZ0FGdz91c0B3b0V2Z9Umc1RXYlZGfx0jd'
readonly Codec_3a1bebdf='reversed_base64|'
Feature_3a1bebdf() {
  local OPTIND option; while getopts ':ab:' option -- -a -b fixture; do case "$option" in a|b) : ;; esac; done
}
Decode() { local reversed='' index; for ((index=${#Material_3a1bebdf}-1; index>=0; index--)); do reversed+="${Material_3a1bebdf:index:1}"; done; printf '%s' "$reversed" | base64 --decode; }
Inspect_3a1bebdf() {
  local -a series=(3 5 8 13); local v_a19c="${series[*]:1:2}"
  if ! Decode; then return 71; fi
}
if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_3a1bebdf; fi
