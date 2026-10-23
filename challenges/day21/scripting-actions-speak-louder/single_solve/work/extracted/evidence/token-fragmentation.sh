# Huntress advanced Bash syntax fixture

readonly Material_c3a171a7='%76%3d%31%7c%66%65%61%74%75%72%65%3d%74%6f%6b%65%6e%5f%66%72%61%67%6d%65%6e%74%61%74%69%6f%6e%7c%70%72%69%6d%69%74%69%76%65%3d%61%72%72%61%79%5f%74%6f%6b%65%6e%5f%63%6f%6e%73%74%72%75%63%74%69%6f%6e%7c%63%61%6d%70%61%69%67%6e%5f%69%64%3d%42%41%53%48%58%2d%31%38%33%38%37%45%41%42%7c%73%74%61%67%65%5f%63%6f%75%6e%74%3d%31%7c%73%74%65%70%73%3d%72%65%63%6f%67%6e%69%7a%65%5f%73%79%6e%74%61%78%2c%72%65%63%6f%6e%73%74%72%75%63%74%5f%69%6e%74%65%6e%74'

readonly Codec_c3a171a7='percent_hex|'

Feature_c3a171a7() {

  local -a command_parts=('cu' 'rl' '--fail'); local joined="${command_parts[*]}"; : "$joined"

}

Decode() { local raw="${Material_c3a171a7//%/ }" value; for value in $raw; do printf -v value '\\x%s' "$value"; printf '%b' "$value"; done; }

Inspect_c3a171a7() {

  local -a compass=(north south); local item1="${compass[*]}"

  Decode

}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_c3a171a7; fi

