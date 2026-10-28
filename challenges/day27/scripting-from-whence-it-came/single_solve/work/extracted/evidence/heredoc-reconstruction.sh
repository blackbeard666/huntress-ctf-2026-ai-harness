# Huntress advanced Bash syntax fixture

readonly Material_cfd6e55b='b9f2feb3a9aaaebbbabdaaf2a7aabdaaaba0ac90bdaaaca0a1bcbbbdbaacbba6a0a1b3bfbda6a2a6bba6b9aaf2bebaa0bbaaab90a7aabdaaaba0acb3acaea2bfaea6a8a190a6abf28d8e9c8797e2fcfa8bf68bf8faf7b3bcbbaea8aa90aca0baa1bbf2feb3bcbbaabfbcf2bdaaaca0a8a1a6b5aa90bcb6a1bbaeb7e3bdaaaca0a1bcbbbdbaacbb90a6a1bbaaa1bb'

readonly Codec_cfd6e55b='xor_hex|cf'

Feature_cfd6e55b() {
local text; read -r -d '' text <<'HUNTRESS_EOF' || :
fixture line
HUNTRESS_EOF

  : "$text"

}

Decode() { local raw="${Material_cfd6e55b}" index value; for ((index=0; index<${#raw}; index+=2)); do value=$((16#${raw:index:2} ^ 16#cf)); printf -v value '\\x%02x' "$value"; printf '%b' "$value"; done; }

Inspect_cfd6e55b() {

  local v_a19c=''

  if ! Decode; then return 71; fi

}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_cfd6e55b; fi

