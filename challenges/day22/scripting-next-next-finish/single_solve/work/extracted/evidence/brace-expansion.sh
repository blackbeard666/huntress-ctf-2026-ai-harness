# Huntress advanced Bash syntax fixture

readonly Material_71e3f7f5='118,61,49,124,102,101,97,116,117,114,101,61,98,114,97,99,101,95,101,120,112,97,110,115,105,111,110,124,112,114,105,109,105,116,105,118,101,61,99,97,114,116,101,115,105,97,110,95,98,114,97,99,101,95,101,120,112,97,110,115,105,111,110,124,99,97,109,112,97,105,103,110,95,105,100,61,66,65,83,72,88,45,67,67,68,65,55,48,55,54,124,115,116,97,103,101,95,99,111,117,110,116,61,49,124,115,116,101,112,115,61,114,101,99,111,103,110,105,122,101,95,115,121,110,116,97,120,44,114,101,99,111,110,115,116,114,117,99,116,95,105,110,116,101,110,116'

readonly Codec_71e3f7f5='decimal_csv|'

Feature_71e3f7f5() {

  local -a paths=(/tmp/{alpha,beta}.{json,dat}); : "${paths[*]}"

}

Decode() { local IFS=',' value; read -r -a values <<< "${Material_71e3f7f5}"; for value in "${values[@]}"; do printf -v value '\\x%02x' "$value"; printf '%b' "$value"; done; }

Inspect_71e3f7f5() {

  local -a compass=(north south); local item1="${compass[*]}"

  Decode

}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_71e3f7f5; fi

