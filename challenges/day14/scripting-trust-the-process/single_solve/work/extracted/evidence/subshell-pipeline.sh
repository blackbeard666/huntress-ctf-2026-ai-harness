# Huntress advanced Bash syntax fixture
readonly Material_d9b2e985='%76%3d%31%7c%66%65%61%74%75%72%65%3d%73%75%62%73%68%65%6c%6c%5f%70%69%70%65%6c%69%6e%65%7c%70%72%69%6d%69%74%69%76%65%3d%63%6f%6d%6d%61%6e%64%5f%73%75%62%73%74%69%74%75%74%69%6f%6e%5f%70%69%70%65%6c%69%6e%65%7c%63%61%6d%70%61%69%67%6e%5f%69%64%3d%42%41%53%48%58%2d%45%36%32%35%42%42%45%43%7c%73%74%61%67%65%5f%63%6f%75%6e%74%3d%31%7c%73%74%65%70%73%3d%72%65%63%6f%67%6e%69%7a%65%5f%73%79%6e%74%61%78%2c%72%65%63%6f%6e%73%74%72%75%63%74%5f%69%6e%74%65%6e%74'
readonly Codec_d9b2e985='percent_hex|'
Feature_d9b2e985() {
  local output; output="$(printf '%s' fixture | tr 'a-z' 'A-Z')"; : "$output"
}
Decode() { local raw="${Material_d9b2e985//%/ }" value; for value in $raw; do printf -v value '\\x%s' "$value"; printf '%b' "$value"; done; }
Inspect_d9b2e985() {
  local harmless_value="${HUNTRESS_FIXTURE_CONTEXT:-host}"
  local decode_pass=0; while ((decode_pass++ < 1)); do Decode; done
}
if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_d9b2e985; fi
