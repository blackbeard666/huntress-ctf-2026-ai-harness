# Huntress advanced Bash syntax fixture
readonly Material_067da545='703b377a606367727374633b746361637e59656968626f726f6968676a7a76746f6b6f726f70633b6467756e59746361637e596b6772656e7a65676b76676f6168596f623b4447554e5e2b323e3735474737307a75726761635965697368723b377a75726376753b7463656961686f7c6359757f6872677e2a7463656968757274736572596f6872636872'
readonly Codec_067da545='xor_hex|06'
Feature_067da545() {
  local value='node-1234'; [[ "$value" =~ ^node-[0-9]+$ ]] && :
}
Decode() { local raw="${Material_067da545}" index value; for ((index=0; index<${#raw}; index+=2)); do value=$((16#${raw:index:2} ^ 16#06)); printf -v value '\\x%02x' "$value"; printf '%b' "$value"; done; }
Inspect_067da545() {
  local NeUtRaL; if ((2 > 1)); then NeUtRaL=left; else NeUtRaL=right; fi
  if ! Decode; then return 71; fi
}
if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_067da545; fi
