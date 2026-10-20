# advanced syntax reconstruction
# Huntress advanced Bash syntax fixture
readonly Material_1a9993ff='6c272b667c7f7b6e6f687f277b7469734579456b6f756e73747d666a687377736e736c7f277b7469734579457f69797b6a7f45696e6873747d66797b776a7b737d7445737e27585b495242372a5f225e5f59295b66696e7b7d7f4579756f746e272b66696e7f6a6927687f79757d7473607f456963746e7b6236687f797574696e686f796e4573746e7f746e'
readonly Codec_1a9993ff='xor_hex|1a'
Feature_1a9993ff() {
  local escaped=$'node\nbash\tfixture'; : "$escaped"
}
Decode() { local raw="${Material_1a9993ff}" index value; for ((index=0; index<${#raw}; index+=2)); do value=$((16#${raw:index:2} ^ 16#1a)); printf -v value '\\x%02x' "$value"; printf '%b' "$value"; done; }
Inspect_1a9993ff() {
  local harmless_value=''
  Decode
}
if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_1a9993ff; fi

# reconstruction complete