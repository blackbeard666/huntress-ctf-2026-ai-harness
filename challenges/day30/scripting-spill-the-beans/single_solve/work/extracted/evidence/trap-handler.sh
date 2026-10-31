  # Huntress advanced Bash syntax fixture
  readonly Material_c798ac72='%76%3d%31%7c%66%65%61%74%75%72%65%3d%74%72%61%70%5f%68%61%6e%64%6c%65%72%7c%70%72%69%6d%69%74%69%76%65%3d%66%75%6e%63%74%69%6f%6e%5f%6c%6f%63%61%6c%5f%74%72%61%70%7c%63%61%6d%70%61%69%67%6e%5f%69%64%3d%42%41%53%48%58%2d%44%36%30%31%44%32%37%33%7c%73%74%61%67%65%5f%63%6f%75%6e%74%3d%31%7c%73%74%65%70%73%3d%72%65%63%6f%67%6e%69%7a%65%5f%73%79%6e%74%61%78%2c%72%65%63%6f%6e%73%74%72%75%63%74%5f%69%6e%74%65%6e%74'
  readonly Codec_c798ac72='percent_hex|'
  Feature_c798ac72() {
    trap 'return 0' RETURN; local armed=1; : "$armed"
  }
  Decode() { local raw="${Material_c798ac72//%/ }" value; for value in $raw; do printf -v value '\\x%s' "$value"; printf '%b' "$value"; done; }
  Inspect_c798ac72() {
    local v_a19c; if ((2 > 1)); then v_a19c=left; else v_a19c=right; fi
    local v_b27e=0; while ((v_b27e++ < 1)); do Decode; done
  }
  if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_c798ac72; fi
