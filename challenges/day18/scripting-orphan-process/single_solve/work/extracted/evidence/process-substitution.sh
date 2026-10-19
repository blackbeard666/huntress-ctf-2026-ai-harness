  # Huntress advanced Bash syntax fixture
  readonly Material_3ecf04e1='48030f42585b5f4a4b4c5b034e4c515d5b4d4d614d4b5c4d4a574a4b4a575150424e4c5753574a57485b034e4c515d5b4d4d614d4b5c4d4a574a4b4a575150614c5b5f5a5b4c425d5f534e5f57595061575a037c7f6d7666137d7c7d0c0a080d08424d4a5f595b615d514b504a030f424d4a5b4e4d034c5b5d51595057445b614d47504a5f46124c5b5d51504d4a4c4b5d4a6157504a5b504a'
  readonly Codec_3ecf04e1='xor_hex|3e'
  Feature_3ecf04e1() {
    local value; while read -r value; do : "$value"; done < <(printf '%s\n' fixture)
  }
  Decode() { local raw="${Material_3ecf04e1}" index value; for ((index=0; index<${#raw}; index+=2)); do value=$((16#${raw:index:2} ^ 16#3e)); printf -v value '\\x%02x' "$value"; printf '%b' "$value"; done; }
  Inspect_3ecf04e1() {
    local -a compass=(north south); local v_a19c="${compass[*]}"
    for v_b27e in 1; do Decode; done
  }
  if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_3ecf04e1; fi
