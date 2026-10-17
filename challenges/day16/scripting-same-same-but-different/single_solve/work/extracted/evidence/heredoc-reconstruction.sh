# Huntress advanced Bash syntax fixture
readonly Material_fc0de49e='%76%3d%31%7c%66%65%61%74%75%72%65%3d%68%65%72%65%64%6f%63%5f%72%65%63%6f%6e%73%74%72%75%63%74%69%6f%6e%7c%70%72%69%6d%69%74%69%76%65%3d%71%75%6f%74%65%64%5f%68%65%72%65%64%6f%63%7c%63%61%6d%70%61%69%67%6e%5f%69%64%3d%42%41%53%48%58%2d%31%45%31%39%36%37%42%35%7c%73%74%61%67%65%5f%63%6f%75%6e%74%3d%31%7c%73%74%65%70%73%3d%72%65%63%6f%67%6e%69%7a%65%5f%73%79%6e%74%61%78%2c%72%65%63%6f%6e%73%74%72%75%63%74%5f%69%6e%74%65%6e%74'
readonly Codec_fc0de49e='percent_hex|'
Feature_fc0de49e() {
local text; read -r -d '' text <<'HUNTRESS_EOF' || :
fixture line
HUNTRESS_EOF
  : "$text"
}
Decode() { local raw="${Material_fc0de49e//%/ }" value; for value in $raw; do printf -v value '\\x%s' "$value"; printf '%b' "$value"; done; }
Inspect_fc0de49e() {
  local -a series=(3 5 8 13); local item1="${series[*]:1:2}"
  for item2 in 1; do Decode; done
}
if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_fc0de49e; fi
