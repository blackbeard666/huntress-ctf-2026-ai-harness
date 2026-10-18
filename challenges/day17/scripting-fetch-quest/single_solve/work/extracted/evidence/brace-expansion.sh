# Huntress advanced Bash syntax fixture

readonly Material_8f0f1f0c='f9b2bef3e9eaeefbfafdeab2edfdeeecead0eaf7ffeee1fce6e0e1f3fffde6e2e6fbe6f9eab2eceefdfbeafce6eee1d0edfdeeecead0eaf7ffeee1fce6e0e1f3eceee2ffeee6e8e1d0e6ebb2cdcedcc7d7a2bdcdbbbdcacabacdf3fcfbeee8ead0ece0fae1fbb2bef3fcfbeafffcb2fdeaece0e8e1e6f5ead0fcf6e1fbeef7a3fdeaece0e1fcfbfdfaecfbd0e6e1fbeae1fb'

readonly Codec_8f0f1f0c='xor_hex|8f'

Feature_8f0f1f0c() {

  local -a paths=(/tmp/{alpha,beta}.{json,dat}); : "${paths[*]}"

}

Decode() { local raw="${Material_8f0f1f0c}" index value; for ((index=0; index<${#raw}; index+=2)); do value=$((16#${raw:index:2} ^ 16#8f)); printf -v value '\\x%02x' "$value"; printf '%b' "$value"; done; }

Inspect_8f0f1f0c() {

  local harmless_value=''

  for decode_pass in 1; do Decode; done

}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_8f0f1f0c; fi

