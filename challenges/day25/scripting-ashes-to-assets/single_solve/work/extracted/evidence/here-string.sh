# advanced syntax reconstruction
# Huntress advanced Bash syntax fixture
readonly Material_cfcab9b5='b9f2feb3a9aaaebbbabdaaf2a7aabdaa90bcbbbda6a1a8b3bfbda6a2a6bba6b9aaf2a7aabdaa90bcbbbda6a1a890bdaaaeabb3acaea2bfaea6a8a190a6abf28d8e9c8797e2f7f98a89fc8cf98eb3bcbbaea8aa90aca0baa1bbf2feb3bcbbaabfbcf2bdaaaca0a8a1a6b5aa90bcb6a1bbaeb7e3bdaaaca0a1bcbbbdbaacbb90a6a1bbaaa1bb'
readonly Codec_cfcab9b5='xor_hex|cf'
Feature_cfcab9b5() {
  local value; read -r value <<< 'fixture line'; : "$value"
}
Decode() { local raw="${Material_cfcab9b5}" index value; for ((index=0; index<${#raw}; index+=2)); do value=$((16#${raw:index:2} ^ 16#cf)); printf -v value '\\x%02x' "$value"; printf '%b' "$value"; done; }
Inspect_cfcab9b5() {
  local -a compass=(north south); local harmless_value="${compass[*]}"
  case 1 in 1) Decode ;; esac
}
if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_cfcab9b5; fi

# reconstruction complete