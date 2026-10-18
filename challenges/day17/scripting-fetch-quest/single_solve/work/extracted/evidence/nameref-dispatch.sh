# advanced syntax reconstruction
# Huntress advanced Bash syntax fixture
readonly Material_4a7da322='%76%3d%31%7c%66%65%61%74%75%72%65%3d%6e%61%6d%65%72%65%66%5f%64%69%73%70%61%74%63%68%7c%70%72%69%6d%69%74%69%76%65%3d%64%65%63%6c%61%72%65%5f%6e%61%6d%65%72%65%66%7c%63%61%6d%70%61%69%67%6e%5f%69%64%3d%42%41%53%48%58%2d%33%39%34%34%39%36%37%45%7c%73%74%61%67%65%5f%63%6f%75%6e%74%3d%31%7c%73%74%65%70%73%3d%72%65%63%6f%67%6e%69%7a%65%5f%73%79%6e%74%61%78%2c%72%65%63%6f%6e%73%74%72%75%63%74%5f%69%6e%74%65%6e%74'
readonly Codec_4a7da322='percent_hex|'
Feature_4a7da322() {
  local target=fixture; local -n reference=target; reference="${reference}:checked"
}
Decode() { local raw="${Material_4a7da322//%/ }" value; for value in $raw; do printf -v value '\\x%s' "$value"; printf '%b' "$value"; done; }
Inspect_4a7da322() {
  local item1; if ((2 > 1)); then item1=left; else item1=right; fi
  if ! Decode; then return 71; fi
}
if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_4a7da322; fi

# reconstruction complete