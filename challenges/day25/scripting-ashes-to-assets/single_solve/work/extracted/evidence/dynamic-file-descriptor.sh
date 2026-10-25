# Huntress advanced Bash syntax fixture

readonly Material_3f81bb75='%76%3d%31%7c%66%65%61%74%75%72%65%3d%64%79%6e%61%6d%69%63%5f%66%69%6c%65%5f%64%65%73%63%72%69%70%74%6f%72%7c%70%72%69%6d%69%74%69%76%65%3d%61%6c%6c%6f%63%61%74%65%64%5f%66%69%6c%65%5f%64%65%73%63%72%69%70%74%6f%72%7c%63%61%6d%70%61%69%67%6e%5f%69%64%3d%42%41%53%48%58%2d%39%42%46%35%44%32%38%43%7c%73%74%61%67%65%5f%63%6f%75%6e%74%3d%31%7c%73%74%65%70%73%3d%72%65%63%6f%67%6e%69%7a%65%5f%73%79%6e%74%61%78%2c%72%65%63%6f%6e%73%74%72%75%63%74%5f%69%6e%74%65%6e%74'

readonly Codec_3f81bb75='percent_hex|'

Feature_3f81bb75() {

  local descriptor_fd; exec {descriptor_fd}<<<'fixture'; exec {descriptor_fd}<&-

}

Decode() { local raw="${Material_3f81bb75//%/ }" value; for value in $raw; do printf -v value '\\x%s' "$value"; printf '%b' "$value"; done; }

Inspect_3f81bb75() {

  local n=$((19 * 7 - 133))

  local decode_target=Decode; "$decode_target"

}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_3f81bb75; fi

