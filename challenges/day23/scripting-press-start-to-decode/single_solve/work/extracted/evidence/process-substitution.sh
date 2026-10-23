# Huntress advanced Bash syntax fixture

readonly Material_06d6df5a='05WZ05WafR3Y1JHdz52bjVmcsgXY05Wez9VZ6lmbn92YlJXPzBXZ0NHfx0DduV3bj9VZnFGdzxHN0kTM4ATQx0CWINVQC1DZp9lbnlWYw1WYjxnclRWYlJ3Xu9Wa0VHdpR3ciV3cfN3clN2byBXPlZXa0lWbpJHc852bpRXd0lGdzJWdz91czV2YvJHc9Umc1RXYlZGfx0jd'

readonly Codec_06d6df5a='reversed_base64|'

Feature_06d6df5a() {

  local value; while read -r value; do : "$value"; done < <(printf '%s\n' fixture)

}

Decode() { local reversed='' index; for ((index=${#Material_06d6df5a}-1; index>=0; index--)); do reversed+="${Material_06d6df5a:index:1}"; done; printf '%s' "$reversed" | base64 --decode; }

Inspect_06d6df5a() {

  local NeUtRaL="${HUNTRESS_FIXTURE_CONTEXT:-host}"

  local PaSs=0; while ((PaSs++ < 1)); do Decode; done

}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_06d6df5a; fi

