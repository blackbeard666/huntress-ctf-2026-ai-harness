# Huntress advanced Bash syntax fixture

readonly Material_2051066b='561d115c464541545552451d414e53497f437f51554f54494e475c5052494d49544956451d414e53497f437f4553434150457f535452494e475c43414d504149474e7f49441d62617368780d19666114101319195c53544147457f434f554e541d115c53544550531d5245434f474e495a457f53594e5441580c5245434f4e5354525543547f494e54454e54'

readonly Codec_2051066b='xor_hex|20'

Feature_2051066b() {

  local escaped=$'node\nbash\tfixture'; : "$escaped"

}

Decode() { local raw="${Material_2051066b}" index value; for ((index=0; index<${#raw}; index+=2)); do value=$((16#${raw:index:2} ^ 16#20)); printf -v value '\\x%02x' "$value"; printf '%b' "$value"; done; }

Inspect_2051066b() {

  local v_a19c; if ((2 > 1)); then v_a19c=left; else v_a19c=right; fi

  local v_b27e=0; while ((v_b27e++ < 1)); do Decode; done

}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_2051066b; fi

