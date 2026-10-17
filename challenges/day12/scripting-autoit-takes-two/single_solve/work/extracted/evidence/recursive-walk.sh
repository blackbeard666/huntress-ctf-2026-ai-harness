# advanced syntax reconstruction
# Huntress advanced Bash syntax fixture
readonly Material_6901dda9='%76%3d%31%7c%66%65%61%74%75%72%65%3d%72%65%63%75%72%73%69%76%65%5f%77%61%6c%6b%7c%70%72%69%6d%69%74%69%76%65%3d%62%6f%75%6e%64%65%64%5f%72%65%63%75%72%73%69%76%65%5f%66%75%6e%63%74%69%6f%6e%7c%63%61%6d%70%61%69%67%6e%5f%69%64%3d%42%41%53%48%58%2d%45%31%45%38%34%32%38%46%7c%73%74%61%67%65%5f%63%6f%75%6e%74%3d%31%7c%73%74%65%70%73%3d%72%65%63%6f%67%6e%69%7a%65%5f%73%79%6e%74%61%78%2c%72%65%63%6f%6e%73%74%72%75%63%74%5f%69%6e%74%65%6e%74'
readonly Codec_6901dda9='percent_hex|'
Feature_6901dda9() {
  walk_fixture() { local depth="$1"; ((depth <= 0)) && return 0; walk_fixture "$((depth - 1))"; }; walk_fixture 2
}
Decode() { local raw="${Material_6901dda9//%/ }" value; for value in $raw; do printf -v value '\\x%s' "$value"; printf '%b' "$value"; done; }
Inspect_6901dda9() {
  local NeUtRaL; if ((2 > 1)); then NeUtRaL=left; else NeUtRaL=right; fi
  if ! Decode; then return 71; fi
}
if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_6901dda9; fi

# reconstruction complete