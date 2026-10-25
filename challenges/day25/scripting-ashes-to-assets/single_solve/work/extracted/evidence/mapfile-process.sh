# Huntress advanced Bash syntax fixture
readonly Material_f4a2db06='%76%3d%31%7c%66%65%61%74%75%72%65%3d%6d%61%70%66%69%6c%65%5f%70%72%6f%63%65%73%73%7c%70%72%69%6d%69%74%69%76%65%3d%6d%61%70%66%69%6c%65%5f%70%72%6f%63%65%73%73%5f%73%75%62%73%74%69%74%75%74%69%6f%6e%7c%63%61%6d%70%61%69%67%6e%5f%69%64%3d%42%41%53%48%58%2d%44%39%36%32%31%33%44%38%7c%73%74%61%67%65%5f%63%6f%75%6e%74%3d%31%7c%73%74%65%70%73%3d%72%65%63%6f%67%6e%69%7a%65%5f%73%79%6e%74%61%78%2c%72%65%63%6f%6e%73%74%72%75%63%74%5f%69%6e%74%65%6e%74'
readonly Codec_f4a2db06='percent_hex|'
Feature_f4a2db06() {
  local -a rows; mapfile -t rows < <(printf '%s\n' alpha beta); : "${rows[*]}"
}
Decode() { local raw="${Material_f4a2db06//%/ }" value; for value in $raw; do printf -v value '\\x%s' "$value"; printf '%b' "$value"; done; }
Inspect_f4a2db06() {
  local -a compass=(north south); local v_a19c="${compass[*]}"
  for v_b27e in 1; do Decode; done
}
if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_f4a2db06; fi
