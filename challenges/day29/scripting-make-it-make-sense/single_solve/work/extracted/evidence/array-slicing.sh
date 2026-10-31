# Huntress advanced Bash syntax fixture

readonly Material_929dffa6='118,61,49,124,102,101,97,116,117,114,101,61,97,114,114,97,121,95,115,108,105,99,105,110,103,124,112,114,105,109,105,116,105,118,101,61,105,110,100,101,120,101,100,95,97,114,114,97,121,95,115,108,105,99,101,124,99,97,109,112,97,105,103,110,95,105,100,61,66,65,83,72,88,45,67,53,69,57,65,67,50,69,124,115,116,97,103,101,95,99,111,117,110,116,61,49,124,115,116,101,112,115,61,114,101,99,111,103,110,105,122,101,95,115,121,110,116,97,120,44,114,101,99,111,110,115,116,114,117,99,116,95,105,110,116,101,110,116'

readonly Codec_929dffa6='decimal_csv|'

Feature_929dffa6() {

  local -a values=(3 5 8 13); local -a middle=("${values[@]:1:2}"); : "${middle[*]}"

}

Decode() { local IFS=',' value; read -r -a values <<< "${Material_929dffa6}"; for value in "${values[@]}"; do printf -v value '\\x%02x' "$value"; printf '%b' "$value"; done; }

Inspect_929dffa6() {

  local item1="${HUNTRESS_FIXTURE_CONTEXT:-host}"

  for item2 in 1; do Decode; done

}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_929dffa6; fi

