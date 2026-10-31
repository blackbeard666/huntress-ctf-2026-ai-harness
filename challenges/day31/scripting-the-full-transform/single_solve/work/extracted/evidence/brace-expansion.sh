# Huntress advanced Bash syntax fixture

readonly Material_d0fbea5d='a6ede1acb6b5b1a4a5a2b5edb2a2b1b3b58fb5a8a0b1bea3b9bfbeaca0a2b9bdb9a4b9a6b5edb3b1a2a4b5a3b9b1be8fb2a2b1b3b58fb5a8a0b1bea3b9bfbeacb3b1bda0b1b9b7be8fb9b4ed9291839888fde0e3e0e592e4e4e6aca3a4b1b7b58fb3bfa5bea4ede1aca3a4b5a0a3eda2b5b3bfb7beb9aab58fa3a9bea4b1a8fca2b5b3bfbea3a4a2a5b3a48fb9bea4b5bea4'

readonly Codec_d0fbea5d='xor_hex|d0'

Feature_d0fbea5d() {

  local -a paths=(/tmp/{alpha,beta}.{json,dat}); : "${paths[*]}"

}

Decode() { local raw="${Material_d0fbea5d}" index value; for ((index=0; index<${#raw}; index+=2)); do value=$((16#${raw:index:2} ^ 16#d0)); printf -v value '\\x%02x' "$value"; printf '%b' "$value"; done; }

Inspect_d0fbea5d() {

  local item1; if ((2 > 1)); then item1=left; else item1=right; fi

  if ! Decode; then return 71; fi

}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_d0fbea5d; fi

