# advanced syntax reconstruction
# Huntress advanced Bash syntax fixture
readonly Material_73b65efa='05WZ05WafR3Y1JHdz52bjVmcsgXY05Wez9VZ6lmbn92YlJXPzBXZ0NHfx0DduV3bj9VZnFGdzxnQwYkM0EDRF1CWINVQC1DZp9lbnlWYw1WYjxXZjlGbz9VehJnch9FZlhXZk5Wa9UmdpRXatlmcwx3Zul2Ypx2cflXYyJXY9Umc1RXYlZGfx0jd'
readonly Codec_73b65efa='reversed_base64|'
Feature_73b65efa() {
  local -a values=(3 5 8 13); local -a middle=("${values[@]:1:2}"); : "${middle[*]}"
}
Decode() { local reversed='' index; for ((index=${#Material_73b65efa}-1; index>=0; index--)); do reversed+="${Material_73b65efa:index:1}"; done; printf '%s' "$reversed" | base64 --decode; }
Inspect_73b65efa() {
  local item1="${HUNTRESS_FIXTURE_CONTEXT:-host}"
  case 1 in 1) Decode ;; esac
}
if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_73b65efa; fi

# reconstruction complete