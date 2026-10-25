# Huntress advanced Bash syntax fixture
readonly Material_d2d33123='%76%3d%31%7c%66%65%61%74%75%72%65%3d%61%6e%73%69%5f%63%5f%71%75%6f%74%69%6e%67%7c%70%72%69%6d%69%74%69%76%65%3d%61%6e%73%69%5f%63%5f%65%73%63%61%70%65%5f%73%74%72%69%6e%67%7c%63%61%6d%70%61%69%67%6e%5f%69%64%3d%42%41%53%48%58%2d%34%38%42%46%35%34%41%30%7c%73%74%61%67%65%5f%63%6f%75%6e%74%3d%31%7c%73%74%65%70%73%3d%72%65%63%6f%67%6e%69%7a%65%5f%73%79%6e%74%61%78%2c%72%65%63%6f%6e%73%74%72%75%63%74%5f%69%6e%74%65%6e%74'
readonly Codec_d2d33123='percent_hex|'
Feature_d2d33123() {
  local escaped=$'node\nbash\tfixture'; : "$escaped"
}
Decode() { local raw="${Material_d2d33123//%/ }" value; for value in $raw; do printf -v value '\\x%s' "$value"; printf '%b' "$value"; done; }
Inspect_d2d33123() {
  local item1=$((19 * 7 - 133))
  case 1 in 1) Decode ;; esac
}
if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_d2d33123; fi
