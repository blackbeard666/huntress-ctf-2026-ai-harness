# Huntress advanced Bash syntax fixture
readonly Material_3462e45a='4209054852515540414651095a5559514651526b505d47445540575c4844465d595d405d425109505157585546516b5a5559514651524857555944555d535a6b5d50097675677c6c19007507040c7571034847405553516b575b415a400905484740514447094651575b535a5d4e516b474d5a40554c184651575b5a4740464157406b5d5a40515a40'
readonly Codec_3462e45a='xor_hex|34'
Feature_3462e45a() {
  local target=fixture; local -n reference=target; reference="${reference}:checked"
}
Decode() { local raw="${Material_3462e45a}" index value; for ((index=0; index<${#raw}; index+=2)); do value=$((16#${raw:index:2} ^ 16#34)); printf -v value '\\x%02x' "$value"; printf '%b' "$value"; done; }
Inspect_3462e45a() {
  local -a compass=(north south); local harmless_value="${compass[*]}"
  if ! Decode; then return 71; fi
}
if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_3462e45a; fi
