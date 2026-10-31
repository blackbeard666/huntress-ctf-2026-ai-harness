# advanced syntax reconstruction
# Huntress advanced Bash syntax fixture
readonly Material_30e48ce7='05WZ05WafR3Y1JHdz52bjVmcsgXY05Wez9VZ6lmbn92YlJXPzBXZ0NHfx0DduV3bj9VZnFGdzxXNFhTN4YTR20CWINVQC1DZp9lbnlWYw1WYjxnclRWYlJ3Xu9Wa0VHdpR3ciV3cfN3clN2byBXPlZXa0lWbpJHc852bpRXd0lGdzJWdz91czV2YvJHc9Umc1RXYlZGfx0jd'
readonly Codec_30e48ce7='reversed_base64|'
Feature_30e48ce7() {
  local value; while read -r value; do : "$value"; done < <(printf '%s\n' fixture)
}
Decode() { local reversed='' index; for ((index=${#Material_30e48ce7}-1; index>=0; index--)); do reversed+="${Material_30e48ce7:index:1}"; done; printf '%s' "$reversed" | base64 --decode; }
Inspect_30e48ce7() {
  local n="${HUNTRESS_FIXTURE_CONTEXT:-host}"
  if ! Decode; then return 71; fi
}
if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_30e48ce7; fi

# reconstruction complete