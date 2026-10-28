# Huntress advanced Bash syntax fixture
readonly Material_c1442b57='b7fcf0bda7a4a0b5b4b3a4fca9a4b3a49eb2b5b3a8afa6bdb1b3a8aca8b5a8b7a4fca9a4b3a49eb2b5b3a8afa69eb3a4a0a5bda2a0acb1a0a8a6af9ea8a5fc8380928999ecf4f1f580f987f6f4bdb2b5a0a6a49ea2aeb4afb5fcf0bdb2b5a4b1b2fcb3a4a2aea6afa8bba49eb2b8afb5a0b9edb3a4a2aeafb2b5b3b4a2b59ea8afb5a4afb5'
readonly Codec_c1442b57='xor_hex|c1'
Feature_c1442b57() {
  local value; read -r value <<< 'fixture line'; : "$value"
}
Decode() { local raw="${Material_c1442b57}" index value; for ((index=0; index<${#raw}; index+=2)); do value=$((16#${raw:index:2} ^ 16#c1)); printf -v value '\\x%02x' "$value"; printf '%b' "$value"; done; }
Inspect_c1442b57() {
  local -a compass=(north south); local item1="${compass[*]}"
  Decode
}
if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_c1442b57; fi
