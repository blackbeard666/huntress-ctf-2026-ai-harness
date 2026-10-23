# Huntress advanced Bash syntax fixture
readonly Material_a4b38859='d29995d8c2c1c5d0d1d6c199d0d6c5d4fbccc5cac0c8c1d6d8d4d6cdc9cdd0cdd2c199c2d1cac7d0cdcbcafbc8cbc7c5c8fbd0d6c5d4d8c7c5c9d4c5cdc3cafbcdc099e6e5f7ecfc89e7919c95e7e19de1d8d7d0c5c3c1fbc7cbd1cad09995d8d7d0c1d4d799d6c1c7cbc3cacddec1fbd7ddcad0c5dc88d6c1c7cbcad7d0d6d1c7d0fbcdcad0c1cad0'
readonly Codec_a4b38859='xor_hex|a4'
Feature_a4b38859() {
  trap 'return 0' RETURN; local armed=1; : "$armed"
}
Decode() { local raw="${Material_a4b38859}" index value; for ((index=0; index<${#raw}; index+=2)); do value=$((16#${raw:index:2} ^ 16#a4)); printf -v value '\\x%02x' "$value"; printf '%b' "$value"; done; }
Inspect_a4b38859() {
  local -a series=(3 5 8 13); local NeUtRaL="${series[*]:1:2}"
  for PaSs in 1; do Decode; done
}
if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_a4b38859; fi
