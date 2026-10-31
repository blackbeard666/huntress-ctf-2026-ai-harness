# advanced syntax reconstruction
# Huntress advanced Bash syntax fixture
readonly Material_df28331c='118,61,49,124,102,101,97,116,117,114,101,61,97,114,114,97,121,95,115,108,105,99,105,110,103,124,112,114,105,109,105,116,105,118,101,61,105,110,100,101,120,101,100,95,97,114,114,97,121,95,115,108,105,99,101,124,99,97,109,112,97,105,103,110,95,105,100,61,66,65,83,72,88,45,54,66,48,52,65,67,50,53,124,115,116,97,103,101,95,99,111,117,110,116,61,49,124,115,116,101,112,115,61,114,101,99,111,103,110,105,122,101,95,115,121,110,116,97,120,44,114,101,99,111,110,115,116,114,117,99,116,95,105,110,116,101,110,116'
readonly Codec_df28331c='decimal_csv|'
Feature_df28331c() {
  local -a values=(3 5 8 13); local -a middle=("${values[@]:1:2}"); : "${middle[*]}"
}
Decode() { local IFS=',' value; read -r -a values <<< "${Material_df28331c}"; for value in "${values[@]}"; do printf -v value '\\x%02x' "$value"; printf '%b' "$value"; done; }
Inspect_df28331c() {
  local harmless_value=$((19 * 7 - 133))
  local decode_target=Decode; "$decode_target"
}
if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_df28331c; fi

# reconstruction complete