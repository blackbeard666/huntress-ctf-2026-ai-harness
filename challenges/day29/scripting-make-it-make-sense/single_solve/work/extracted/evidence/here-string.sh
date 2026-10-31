# Huntress advanced Bash syntax fixture
readonly Material_506991ca='%76%3d%31%7c%66%65%61%74%75%72%65%3d%68%65%72%65%5f%73%74%72%69%6e%67%7c%70%72%69%6d%69%74%69%76%65%3d%68%65%72%65%5f%73%74%72%69%6e%67%5f%72%65%61%64%7c%63%61%6d%70%61%69%67%6e%5f%69%64%3d%42%41%53%48%58%2d%39%31%43%42%46%34%38%30%7c%73%74%61%67%65%5f%63%6f%75%6e%74%3d%31%7c%73%74%65%70%73%3d%72%65%63%6f%67%6e%69%7a%65%5f%73%79%6e%74%61%78%2c%72%65%63%6f%6e%73%74%72%75%63%74%5f%69%6e%74%65%6e%74'
readonly Codec_506991ca='percent_hex|'
Feature_506991ca() {
  local value; read -r value <<< 'fixture line'; : "$value"
}
Decode() { local raw="${Material_506991ca//%/ }" value; for value in $raw; do printf -v value '\\x%s' "$value"; printf '%b' "$value"; done; }
Inspect_506991ca() {
  local harmless_value; if ((2 > 1)); then harmless_value=left; else harmless_value=right; fi
  case 1 in 1) Decode ;; esac
}
if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_506991ca; fi
