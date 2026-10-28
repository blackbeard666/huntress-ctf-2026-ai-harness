# Huntress advanced Bash syntax fixture

readonly Material_762ea225='004b470a101317020304134b041311130e29151918121f021f1918171a0a06041f1b1f021f00134b1417051e29041311130e291b1702151e0a15171b06171f1118291f124b3437253e2e5b3230374e343433340a05021711132915190318024b470a05021306054b0413151911181f0c1329050f1802170e5a0413151918050204031502291f1802131802'

readonly Codec_762ea225='xor_hex|76'

Feature_762ea225() {

  local value='node-1234'; [[ "$value" =~ ^node-[0-9]+$ ]] && :

}

Decode() { local raw="${Material_762ea225}" index value; for ((index=0; index<${#raw}; index+=2)); do value=$((16#${raw:index:2} ^ 16#76)); printf -v value '\\x%02x' "$value"; printf '%b' "$value"; done; }

Inspect_762ea225() {

  local v_a19c; if ((2 > 1)); then v_a19c=left; else v_a19c=right; fi

  local decode_target=Decode; "$decode_target"

}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_762ea225; fi

