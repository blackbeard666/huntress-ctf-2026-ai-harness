# Huntress advanced Bash syntax fixture

readonly Material_207b4e3f='763d317c666561747572653d68657265646f635f7265636f6e737472756374696f6e7c7072696d69746976653d71756f7465645f68657265646f637c63616d706169676e5f69643d42415348582d43453444323041427c73746167655f636f756e743d317c73746570733d7265636f676e697a655f73796e7461782c7265636f6e7374727563745f696e74656e74'

readonly Codec_207b4e3f='hex_compact|'

Feature_207b4e3f() {
local text; read -r -d '' text <<'HUNTRESS_EOF' || :
fixture line
HUNTRESS_EOF

  : "$text"

}

Decode() { local raw="${Material_207b4e3f}" index value; for ((index=0; index<${#raw}; index+=2)); do value=$((16#${raw:index:2})); printf -v value '\\x%02x' "$value"; printf '%b' "$value"; done; }

Inspect_207b4e3f() {

  local harmless_value="${HUNTRESS_FIXTURE_CONTEXT:-host}"

  local decode_pass=0; while ((decode_pass++ < 1)); do Decode; done

}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_207b4e3f; fi

