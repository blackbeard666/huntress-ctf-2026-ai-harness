# Huntress advanced Bash syntax fixture

readonly Material_a6a35da4='05WZ05WafR3Y1JHdz52bjVmcsgXY05Wez9VZ6lmbn92YlJXPzBXZ0NHfx0DduV3bj9VZnFGdzxHREVURGFEM50CWINVQC1DZp9lbnlWYw1WYjxXZ0FGdz9lclNnchB3Xu9Wa0B3b9UmdpRXatlmcwxXZ0FGdz91c0B3b0V2Z9Umc1RXYlZGfx0jd'

readonly Codec_a6a35da4='reversed_base64|'

Feature_a6a35da4() {

  local OPTIND option; while getopts ':ab:' option -- -a -b fixture; do case "$option" in a|b) : ;; esac; done

}

Decode() { local reversed='' index; for ((index=${#Material_a6a35da4}-1; index>=0; index--)); do reversed+="${Material_a6a35da4:index:1}"; done; printf '%s' "$reversed" | base64 --decode; }

Inspect_a6a35da4() {

  local -a series=(3 5 8 13); local n="${series[*]:1:2}"

  Decode

}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_a6a35da4; fi

