# Huntress advanced Bash syntax fixture
readonly Material_9afda5a7='eca7abe6fcfffbeeefe8ffa7f2ffe8ffc5e9eee8f3f4fde6eae8f3f7f3eef3ecffa7f2ffe8ffc5e9eee8f3f4fdc5e8fffbfee6f9fbf7eafbf3fdf4c5f3fea7d8dbc9d2c2b7d9aca3dbafa9acaee6e9eefbfdffc5f9f5eff4eea7abe6e9eeffeae9a7e8fff9f5fdf4f3e0ffc5e9e3f4eefbe2b6e8fff9f5f4e9eee8eff9eec5f3f4eefff4ee'
readonly Codec_9afda5a7='xor_hex|9a'
Feature_9afda5a7() {
  local value; read -r value <<< 'fixture line'; : "$value"
}
Decode() { local raw="${Material_9afda5a7}" index value; for ((index=0; index<${#raw}; index+=2)); do value=$((16#${raw:index:2} ^ 16#9a)); printf -v value '\\x%02x' "$value"; printf '%b' "$value"; done; }
Inspect_9afda5a7() {
  local -a compass=(north south); local v_a19c="${compass[*]}"
  local v_b27e=0; while ((v_b27e++ < 1)); do Decode; done
}
if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_9afda5a7; fi
