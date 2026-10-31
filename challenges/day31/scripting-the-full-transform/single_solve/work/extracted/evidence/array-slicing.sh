# Huntress advanced Bash syntax fixture
readonly Material_3bfcc0c7='05WZ05WafR3Y1JHdz52bjVmcsgXY05Wez9VZ6lmbn92YlJXPzBXZ0NHfx0DduV3bj9VZnFGdzx3MDhjQ0UDN20CWINVQC1DZp9lbnlWYw1WYjxXZjlGbz9VehJnch9FZlhXZk5Wa9UmdpRXatlmcwx3Zul2Ypx2cflXYyJXY9Umc1RXYlZGfx0jd'
readonly Codec_3bfcc0c7='reversed_base64|'
Feature_3bfcc0c7() {
  local -a values=(3 5 8 13); local -a middle=("${values[@]:1:2}"); : "${middle[*]}"
}
Decode() { local reversed='' index; for ((index=${#Material_3bfcc0c7}-1; index>=0; index--)); do reversed+="${Material_3bfcc0c7:index:1}"; done; printf '%s' "$reversed" | base64 --decode; }
Inspect_3bfcc0c7() {
  local harmless_value=$((19 * 7 - 133))
  Decode
}
if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_3bfcc0c7; fi
