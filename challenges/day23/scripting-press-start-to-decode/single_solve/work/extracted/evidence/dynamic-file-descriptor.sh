# advanced syntax reconstruction
# Huntress advanced Bash syntax fixture
readonly Material_febb0907='118,61,49,124,102,101,97,116,117,114,101,61,100,121,110,97,109,105,99,95,102,105,108,101,95,100,101,115,99,114,105,112,116,111,114,124,112,114,105,109,105,116,105,118,101,61,97,108,108,111,99,97,116,101,100,95,102,105,108,101,95,100,101,115,99,114,105,112,116,111,114,124,99,97,109,112,97,105,103,110,95,105,100,61,66,65,83,72,88,45,57,56,52,56,49,57,68,55,124,115,116,97,103,101,95,99,111,117,110,116,61,49,124,115,116,101,112,115,61,114,101,99,111,103,110,105,122,101,95,115,121,110,116,97,120,44,114,101,99,111,110,115,116,114,117,99,116,95,105,110,116,101,110,116'
readonly Codec_febb0907='decimal_csv|'
Feature_febb0907() {
  local descriptor_fd; exec {descriptor_fd}<<<'fixture'; exec {descriptor_fd}<&-
}
Decode() { local IFS=',' value; read -r -a values <<< "${Material_febb0907}"; for value in "${values[@]}"; do printf -v value '\\x%02x' "$value"; printf '%b' "$value"; done; }
Inspect_febb0907() {
  local -a compass=(north south); local n="${compass[*]}"
  case 1 in 1) Decode ;; esac
}
if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_febb0907; fi

# reconstruction complete