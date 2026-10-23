# advanced syntax reconstruction
# Huntress advanced Bash syntax fixture
readonly Material_db587b8f='%76%3d%31%7c%66%65%61%74%75%72%65%3d%67%65%74%6f%70%74%73%5f%73%74%61%74%65%7c%70%72%69%6d%69%74%69%76%65%3d%6f%70%74%69%6f%6e%5f%70%61%72%73%65%72%5f%73%74%61%74%65%7c%63%61%6d%70%61%69%67%6e%5f%69%64%3d%42%41%53%48%58%2d%45%36%31%30%33%32%31%31%7c%73%74%61%67%65%5f%63%6f%75%6e%74%3d%31%7c%73%74%65%70%73%3d%72%65%63%6f%67%6e%69%7a%65%5f%73%79%6e%74%61%78%2c%72%65%63%6f%6e%73%74%72%75%63%74%5f%69%6e%74%65%6e%74'
readonly Codec_db587b8f='percent_hex|'
Feature_db587b8f() {
  local OPTIND option; while getopts ':ab:' option -- -a -b fixture; do case "$option" in a|b) : ;; esac; done
}
Decode() { local raw="${Material_db587b8f//%/ }" value; for value in $raw; do printf -v value '\\x%s' "$value"; printf '%b' "$value"; done; }
Inspect_db587b8f() {
  local harmless_value="${HUNTRESS_FIXTURE_CONTEXT:-host}"
  if ! Decode; then return 71; fi
}
if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_db587b8f; fi

# reconstruction complete