# Huntress advanced Bash syntax fixture

readonly Material_f8ae8aba='8ec5c9849e9d998c8d8a9dc59599889e91949da7888a979b9d8b8b84888a9195918c918e9dc59599889e91949da7888a979b9d8b8ba78b8d9a8b8c918c8d8c919796849b99958899919f96a7919cc5bab9abb0a0d5ccbebdcfcdbebacc848b8c999f9da79b978d968cc5c9848b8c9d888bc58a9d9b979f9691829da78b81968c9980d48a9d9b97968b8c8a8d9b8ca791968c9d968c'

readonly Codec_f8ae8aba='xor_hex|f8'

Feature_f8ae8aba() {

  local -a rows; mapfile -t rows < <(printf '%s\n' alpha beta); : "${rows[*]}"

}

Decode() { local raw="${Material_f8ae8aba}" index value; for ((index=0; index<${#raw}; index+=2)); do value=$((16#${raw:index:2} ^ 16#f8)); printf -v value '\\x%02x' "$value"; printf '%b' "$value"; done; }

Inspect_f8ae8aba() {

  local -a compass=(north south); local item1="${compass[*]}"

  case 1 in 1) Decode ;; esac

}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_f8ae8aba; fi

