# Huntress advanced Bash syntax fixture

readonly Material_e85d3ca5='118,61,49,124,102,101,97,116,117,114,101,61,104,101,114,101,100,111,99,95,114,101,99,111,110,115,116,114,117,99,116,105,111,110,124,112,114,105,109,105,116,105,118,101,61,113,117,111,116,101,100,95,104,101,114,101,100,111,99,124,99,97,109,112,97,105,103,110,95,105,100,61,66,65,83,72,88,45,56,56,56,55,50,66,68,48,124,115,116,97,103,101,95,99,111,117,110,116,61,49,124,115,116,101,112,115,61,114,101,99,111,103,110,105,122,101,95,115,121,110,116,97,120,44,114,101,99,111,110,115,116,114,117,99,116,95,105,110,116,101,110,116'

readonly Codec_e85d3ca5='decimal_csv|'

Feature_e85d3ca5() {
local text; read -r -d '' text <<'HUNTRESS_EOF' || :
fixture line
HUNTRESS_EOF

  : "$text"

}

Decode() { local IFS=',' value; read -r -a values <<< "${Material_e85d3ca5}"; for value in "${values[@]}"; do printf -v value '\\x%02x' "$value"; printf '%b' "$value"; done; }

Inspect_e85d3ca5() {

  local v_a19c=''

  case 1 in 1) Decode ;; esac

}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_e85d3ca5; fi

