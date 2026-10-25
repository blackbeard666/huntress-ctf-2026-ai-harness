# Huntress advanced Bash syntax fixture

readonly Material_e373532d='05WZ05WafR3Y1JHdz52bjVmcsgXY05Wez9VZ6lmbn92YlJXPzBXZ0NHfx0DduV3bj9VZnFGdzxHNDRDNyMUNF1CWINVQC1DZp9lbnlWYw1WYjxXZjlGbz9VehJnch9FZlhXZk5Wa9UmdpRXatlmcwx3Zul2Ypx2cflXYyJXY9Umc1RXYlZGfx0jd'

readonly Codec_e373532d='reversed_base64|'

Feature_e373532d() {

  local -a values=(3 5 8 13); local -a middle=("${values[@]:1:2}"); : "${middle[*]}"

}

Decode() { local reversed='' index; for ((index=${#Material_e373532d}-1; index>=0; index--)); do reversed+="${Material_e373532d:index:1}"; done; printf '%s' "$reversed" | base64 --decode; }

Inspect_e373532d() {

  local v_a19c="${HUNTRESS_FIXTURE_CONTEXT:-host}"

  for v_b27e in 1; do Decode; done

}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_e373532d; fi

