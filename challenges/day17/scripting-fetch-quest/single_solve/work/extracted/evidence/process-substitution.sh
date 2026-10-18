# advanced syntax reconstruction
# Huntress advanced Bash syntax fixture
readonly Material_0176219f='773c307d676460757473643c71736e626472725e727463727568757475686e6f7d7173686c68756877643c71736e626472725e727463727568757475686e6f5e7364606564737d62606c716068666f5e68653c43405249592c31354433324434367d72756066645e626e746f753c307d72756471723c7364626e666f687b645e72786f7560792d7364626e6f7275737462755e686f75646f75'
readonly Codec_0176219f='xor_hex|01'
Feature_0176219f() {
  local value; while read -r value; do : "$value"; done < <(printf '%s\n' fixture)
}
Decode() { local raw="${Material_0176219f}" index value; for ((index=0; index<${#raw}; index+=2)); do value=$((16#${raw:index:2} ^ 16#01)); printf -v value '\\x%02x' "$value"; printf '%b' "$value"; done; }
Inspect_0176219f() {
  local item1=$((19 * 7 - 133))
  Decode
}
if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_0176219f; fi

# reconstruction complete