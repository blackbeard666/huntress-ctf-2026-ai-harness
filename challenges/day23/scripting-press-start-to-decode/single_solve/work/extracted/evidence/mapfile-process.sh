# Huntress advanced Bash syntax fixture

readonly Material_af945ce0='d9929ed3c9cacedbdaddca92c2cedfc9c6c3caf0dfddc0cccadcdcd3dfddc6c2c6dbc6d9ca92c2cedfc9c6c3caf0dfddc0cccadcdcf0dcdacddcdbc6dbdadbc6c0c1d3cccec2dfcec6c8c1f0c6cb92edeefce7f782eceb97989b9d99edd3dcdbcec8caf0ccc0dac1db929ed3dcdbcadfdc92ddcaccc0c8c1c6d5caf0dcd6c1dbced783ddcaccc0c1dcdbdddaccdbf0c6c1dbcac1db'

readonly Codec_af945ce0='xor_hex|af'

Feature_af945ce0() {

  local -a rows; mapfile -t rows < <(printf '%s\n' alpha beta); : "${rows[*]}"

}

Decode() { local raw="${Material_af945ce0}" index value; for ((index=0; index<${#raw}; index+=2)); do value=$((16#${raw:index:2} ^ 16#af)); printf -v value '\\x%02x' "$value"; printf '%b' "$value"; done; }

Inspect_af945ce0() {

  local v_a19c=$((19 * 7 - 133))

  local decode_target=Decode; "$decode_target"

}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_af945ce0; fi

