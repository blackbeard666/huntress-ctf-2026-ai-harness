# Huntress advanced Bash syntax fixture
readonly Material_081a10cd='7e3539746e6d697c7d7a6d356c71666965616b576e61646d576c6d7b6b7a61787c677a74787a6165617c617e6d35696464676b697c6d6c576e61646d576c6d7b6b7a61787c677a746b69657869616f6657616c354a495b4050254c3849314b313f38747b7c696f6d576b677d667c3539747b7c6d787b357a6d6b676f6661726d577b71667c6970247a6d6b67667b7c7a7d6b7c5761667c6d667c'
readonly Codec_081a10cd='xor_hex|08'
Feature_081a10cd() {
  local descriptor_fd; exec {descriptor_fd}<<<'fixture'; exec {descriptor_fd}<&-
}
Decode() { local raw="${Material_081a10cd}" index value; for ((index=0; index<${#raw}; index+=2)); do value=$((16#${raw:index:2} ^ 16#08)); printf -v value '\\x%02x' "$value"; printf '%b' "$value"; done; }
Inspect_081a10cd() {
  local v_a19c=''
  case 1 in 1) Decode ;; esac
}
if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_081a10cd; fi
