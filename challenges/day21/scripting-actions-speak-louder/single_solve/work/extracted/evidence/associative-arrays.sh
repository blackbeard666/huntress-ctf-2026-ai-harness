# Huntress advanced Bash syntax fixture

readonly Material_329d47cf='440f034e545753464740570f5341415d515b53465b44576d534040534b414e42405b5f5b465b44570f5657515e5340576d5341415d515b53465b44574e51535f42535b555c6d5b560f7073617a6a1f07730503050176074e41465355576d515d475c460f034e41465742410f4057515d555c5b48576d414b5c46534a1e4057515d5c4146404751466d5b5c46575c46'

readonly Codec_329d47cf='xor_hex|32'

Feature_329d47cf() {

  local -A index=([alpha]=1 [beta]=2); local value="${index[alpha]}"; : "$value"

}

Decode() { local raw="${Material_329d47cf}" index value; for ((index=0; index<${#raw}; index+=2)); do value=$((16#${raw:index:2} ^ 16#32)); printf -v value '\\x%02x' "$value"; printf '%b' "$value"; done; }

Inspect_329d47cf() {

  local harmless_value=''

  for decode_pass in 1; do Decode; done

}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_329d47cf; fi

