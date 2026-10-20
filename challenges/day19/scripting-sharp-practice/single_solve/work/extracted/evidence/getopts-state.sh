# Huntress advanced Bash syntax fixture
readonly Material_52bde40d='%76%3d%31%7c%66%65%61%74%75%72%65%3d%67%65%74%6f%70%74%73%5f%73%74%61%74%65%7c%70%72%69%6d%69%74%69%76%65%3d%6f%70%74%69%6f%6e%5f%70%61%72%73%65%72%5f%73%74%61%74%65%7c%63%61%6d%70%61%69%67%6e%5f%69%64%3d%42%41%53%48%58%2d%41%42%44%41%31%36%43%30%7c%73%74%61%67%65%5f%63%6f%75%6e%74%3d%31%7c%73%74%65%70%73%3d%72%65%63%6f%67%6e%69%7a%65%5f%73%79%6e%74%61%78%2c%72%65%63%6f%6e%73%74%72%75%63%74%5f%69%6e%74%65%6e%74'
readonly Codec_52bde40d='percent_hex|'
Feature_52bde40d() {
  local OPTIND option; while getopts ':ab:' option -- -a -b fixture; do case "$option" in a|b) : ;; esac; done
}
Decode() { local raw="${Material_52bde40d//%/ }" value; for value in $raw; do printf -v value '\\x%s' "$value"; printf '%b' "$value"; done; }
Inspect_52bde40d() {
  local v_a19c=$((19 * 7 - 133))
  for v_b27e in 1; do Decode; done
}
if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_52bde40d; fi
