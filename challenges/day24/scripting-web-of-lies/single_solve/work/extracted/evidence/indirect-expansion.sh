# Huntress advanced Bash syntax fixture

readonly Material_edcdd1ca='%76%3d%31%7c%66%65%61%74%75%72%65%3d%69%6e%64%69%72%65%63%74%5f%65%78%70%61%6e%73%69%6f%6e%7c%70%72%69%6d%69%74%69%76%65%3d%70%61%72%61%6d%65%74%65%72%5f%69%6e%64%69%72%65%63%74%69%6f%6e%7c%63%61%6d%70%61%69%67%6e%5f%69%64%3d%42%41%53%48%58%2d%34%32%34%45%39%38%33%37%7c%73%74%61%67%65%5f%63%6f%75%6e%74%3d%31%7c%73%74%65%70%73%3d%72%65%63%6f%67%6e%69%7a%65%5f%73%79%6e%74%61%78%2c%72%65%63%6f%6e%73%74%72%75%63%74%5f%69%6e%74%65%6e%74'

readonly Codec_edcdd1ca='percent_hex|'

Feature_edcdd1ca() {

  local pointer=target target=fixture; local value="${!pointer}"; printf '%s' "$value" >/dev/null

}

Decode() { local raw="${Material_edcdd1ca//%/ }" value; for value in $raw; do printf -v value '\\x%s' "$value"; printf '%b' "$value"; done; }

Inspect_edcdd1ca() {

  local v_a19c=$((19 * 7 - 133))

  if ! Decode; then return 71; fi

}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_edcdd1ca; fi

