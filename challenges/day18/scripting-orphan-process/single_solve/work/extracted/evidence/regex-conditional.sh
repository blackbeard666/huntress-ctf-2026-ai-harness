# advanced syntax reconstruction
# Huntress advanced Bash syntax fixture
readonly Material_d4e2098e='a2e9e5a8b2b1b5a0a1a6b1e9a6b1b3b1ac8bb7bbbab0bda0bdbbbab5b8a8a4a6bdb9bda0bda2b1e9b6b5a7bc8ba6b1b3b1ac8bb9b5a0b7bca8b7b5b9a4b5bdb3ba8bbdb0e99695879c8cf997e295e0e5ece3eca8a7a0b5b3b18bb7bba1baa0e9e5a8a7a0b1a4a7e9a6b1b7bbb3babdaeb18ba7adbaa0b5acf8a6b1b7bbbaa7a0a6a1b7a08bbdbaa0b1baa0'
readonly Codec_d4e2098e='xor_hex|d4'
Feature_d4e2098e() {
  local value='node-1234'; [[ "$value" =~ ^node-[0-9]+$ ]] && :
}
Decode() { local raw="${Material_d4e2098e}" index value; for ((index=0; index<${#raw}; index+=2)); do value=$((16#${raw:index:2} ^ 16#d4)); printf -v value '\\x%02x' "$value"; printf '%b' "$value"; done; }
Inspect_d4e2098e() {
  local n="${HUNTRESS_FIXTURE_CONTEXT:-host}"
  if ! Decode; then return 71; fi
}
if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_d4e2098e; fi

# reconstruction complete