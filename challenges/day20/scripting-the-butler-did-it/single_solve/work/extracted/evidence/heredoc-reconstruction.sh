# Huntress advanced Bash syntax fixture

readonly Material_28cfc8c5='%76%3d%31%7c%66%65%61%74%75%72%65%3d%68%65%72%65%64%6f%63%5f%72%65%63%6f%6e%73%74%72%75%63%74%69%6f%6e%7c%70%72%69%6d%69%74%69%76%65%3d%71%75%6f%74%65%64%5f%68%65%72%65%64%6f%63%7c%63%61%6d%70%61%69%67%6e%5f%69%64%3d%42%41%53%48%58%2d%34%30%41%38%46%32%45%37%7c%73%74%61%67%65%5f%63%6f%75%6e%74%3d%31%7c%73%74%65%70%73%3d%72%65%63%6f%67%6e%69%7a%65%5f%73%79%6e%74%61%78%2c%72%65%63%6f%6e%73%74%72%75%63%74%5f%69%6e%74%65%6e%74'

readonly Codec_28cfc8c5='percent_hex|'

Feature_28cfc8c5() {
local text; read -r -d '' text <<'HUNTRESS_EOF' || :
fixture line
HUNTRESS_EOF

  : "$text"

}

Decode() { local raw="${Material_28cfc8c5//%/ }" value; for value in $raw; do printf -v value '\\x%s' "$value"; printf '%b' "$value"; done; }

Inspect_28cfc8c5() {

  local -a series=(3 5 8 13); local n="${series[*]:1:2}"

  case 1 in 1) Decode ;; esac

}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_28cfc8c5; fi

