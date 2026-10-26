# advanced syntax reconstruction
# Huntress advanced Bash syntax fixture
readonly Material_80296861='f6bdb1fce6e5e1f4f5f2e5bdf2e5e7e5f8dfe3efeee4e9f4e9efeee1ecfcf0f2e9ede9f4e9f6e5bde2e1f3e8dff2e5e7e5f8dfede1f4e3e8fce3e1edf0e1e9e7eedfe9e4bdc2c1d3c8d8adb8b8c3b1b2b0c5c4fcf3f4e1e7e5dfe3eff5eef4bdb1fcf3f4e5f0f3bdf2e5e3efe7eee9fae5dff3f9eef4e1f8acf2e5e3efeef3f4f2f5e3f4dfe9eef4e5eef4'
readonly Codec_80296861='xor_hex|80'
Feature_80296861() {
  local value='node-1234'; [[ "$value" =~ ^node-[0-9]+$ ]] && :
}
Decode() { local raw="${Material_80296861}" index value; for ((index=0; index<${#raw}; index+=2)); do value=$((16#${raw:index:2} ^ 16#80)); printf -v value '\\x%02x' "$value"; printf '%b' "$value"; done; }
Inspect_80296861() {
  local n; if ((2 > 1)); then n=left; else n=right; fi
  local p=0; while ((p++ < 1)); do Decode; done
}
if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_80296861; fi

# reconstruction complete