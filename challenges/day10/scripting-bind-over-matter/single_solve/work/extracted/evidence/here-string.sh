# Huntress advanced Bash syntax fixture
readonly Material_692760fb='%76%3d%31%7c%66%65%61%74%75%72%65%3d%68%65%72%65%5f%73%74%72%69%6e%67%7c%70%72%69%6d%69%74%69%76%65%3d%68%65%72%65%5f%73%74%72%69%6e%67%5f%72%65%61%64%7c%63%61%6d%70%61%69%67%6e%5f%69%64%3d%42%41%53%48%58%2d%33%35%42%37%44%42%35%46%7c%73%74%61%67%65%5f%63%6f%75%6e%74%3d%31%7c%73%74%65%70%73%3d%72%65%63%6f%67%6e%69%7a%65%5f%73%79%6e%74%61%78%2c%72%65%63%6f%6e%73%74%72%75%63%74%5f%69%6e%74%65%6e%74'
readonly Codec_692760fb='percent_hex|'
Feature_692760fb() {
  local value; read -r value <<< 'fixture line'; : "$value"
}
Decode() { local raw="${Material_692760fb//%/ }" value; for value in $raw; do printf -v value '\\x%s' "$value"; printf '%b' "$value"; done; }
Inspect_692760fb() {
  local harmless_value=$((19 * 7 - 133))
  local decode_target=Decode; "$decode_target"
}
if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_692760fb; fi
