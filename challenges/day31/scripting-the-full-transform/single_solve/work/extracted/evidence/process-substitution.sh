# advanced syntax reconstruction
# Huntress advanced Bash syntax fixture
readonly Material_d9576ce8='118,61,49,124,102,101,97,116,117,114,101,61,112,114,111,99,101,115,115,95,115,117,98,115,116,105,116,117,116,105,111,110,124,112,114,105,109,105,116,105,118,101,61,112,114,111,99,101,115,115,95,115,117,98,115,116,105,116,117,116,105,111,110,95,114,101,97,100,101,114,124,99,97,109,112,97,105,103,110,95,105,100,61,66,65,83,72,88,45,50,52,70,50,55,51,55,48,124,115,116,97,103,101,95,99,111,117,110,116,61,49,124,115,116,101,112,115,61,114,101,99,111,103,110,105,122,101,95,115,121,110,116,97,120,44,114,101,99,111,110,115,116,114,117,99,116,95,105,110,116,101,110,116'
readonly Codec_d9576ce8='decimal_csv|'
Feature_d9576ce8() {
  local value; while read -r value; do : "$value"; done < <(printf '%s\n' fixture)
}
Decode() { local IFS=',' value; read -r -a values <<< "${Material_d9576ce8}"; for value in "${values[@]}"; do printf -v value '\\x%02x' "$value"; printf '%b' "$value"; done; }
Inspect_d9576ce8() {
  local harmless_value; if ((2 > 1)); then harmless_value=left; else harmless_value=right; fi
  local decode_pass=0; while ((decode_pass++ < 1)); do Decode; done
}
if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_d9576ce8; fi

# reconstruction complete