# advanced syntax reconstruction
# Huntress advanced Bash syntax fixture
readonly Material_6694a39d='%76%3d%31%7c%66%65%61%74%75%72%65%3d%67%65%74%6f%70%74%73%5f%73%74%61%74%65%7c%70%72%69%6d%69%74%69%76%65%3d%6f%70%74%69%6f%6e%5f%70%61%72%73%65%72%5f%73%74%61%74%65%7c%63%61%6d%70%61%69%67%6e%5f%69%64%3d%42%41%53%48%58%2d%35%31%46%37%31%38%38%42%7c%73%74%61%67%65%5f%63%6f%75%6e%74%3d%31%7c%73%74%65%70%73%3d%72%65%63%6f%67%6e%69%7a%65%5f%73%79%6e%74%61%78%2c%72%65%63%6f%6e%73%74%72%75%63%74%5f%69%6e%74%65%6e%74'
readonly Codec_6694a39d='percent_hex|'
Feature_6694a39d() {
  local OPTIND option; while getopts ':ab:' option -- -a -b fixture; do case "$option" in a|b) : ;; esac; done
}
Decode() { local raw="${Material_6694a39d//%/ }" value; for value in $raw; do printf -v value '\\x%s' "$value"; printf '%b' "$value"; done; }
Inspect_6694a39d() {
  local -a series=(3 5 8 13); local n="${series[*]:1:2}"
  case 1 in 1) Decode ;; esac
}
if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_6694a39d; fi

# reconstruction complete