# advanced syntax reconstruction
# Huntress advanced Bash syntax fixture
readonly Material_5f35fed7='%76%3d%31%7c%66%65%61%74%75%72%65%3d%61%73%73%6f%63%69%61%74%69%76%65%5f%61%72%72%61%79%73%7c%70%72%69%6d%69%74%69%76%65%3d%64%65%63%6c%61%72%65%5f%61%73%73%6f%63%69%61%74%69%76%65%7c%63%61%6d%70%61%69%67%6e%5f%69%64%3d%42%41%53%48%58%2d%42%31%46%37%31%42%41%34%7c%73%74%61%67%65%5f%63%6f%75%6e%74%3d%31%7c%73%74%65%70%73%3d%72%65%63%6f%67%6e%69%7a%65%5f%73%79%6e%74%61%78%2c%72%65%63%6f%6e%73%74%72%75%63%74%5f%69%6e%74%65%6e%74'
readonly Codec_5f35fed7='percent_hex|'
Feature_5f35fed7() {
  local -A index=([alpha]=1 [beta]=2); local value="${index[alpha]}"; : "$value"
}
Decode() { local raw="${Material_5f35fed7//%/ }" value; for value in $raw; do printf -v value '\\x%s' "$value"; printf '%b' "$value"; done; }
Inspect_5f35fed7() {
  local NeUtRaL="${HUNTRESS_FIXTURE_CONTEXT:-host}"
  local decode_target=Decode; "$decode_target"
}
if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_5f35fed7; fi

# reconstruction complete