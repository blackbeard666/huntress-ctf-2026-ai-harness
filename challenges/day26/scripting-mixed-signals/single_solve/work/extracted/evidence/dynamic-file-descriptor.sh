# Huntress advanced Bash syntax fixture

readonly Material_5b1a1215='2d666a273d3e3a2f2e293e663f22353a363238043d32373e043f3e283829322b2f3429272b293236322f322d3e663a373734383a2f3e3f043d32373e043f3e283829322b2f342927383a362b3a323c3504323f66191a081303761f19191e6e636e1827282f3a3c3e0438342e352f666a27282f3e2b2866293e38343c3532213e042822352f3a2377293e383435282f292e382f0432352f3e352f'

readonly Codec_5b1a1215='xor_hex|5b'

Feature_5b1a1215() {

  local descriptor_fd; exec {descriptor_fd}<<<'fixture'; exec {descriptor_fd}<&-

}

Decode() { local raw="${Material_5b1a1215}" index value; for ((index=0; index<${#raw}; index+=2)); do value=$((16#${raw:index:2} ^ 16#5b)); printf -v value '\\x%02x' "$value"; printf '%b' "$value"; done; }

Inspect_5b1a1215() {

  local -a series=(3 5 8 13); local item1="${series[*]:1:2}"

  local item2=0; while ((item2++ < 1)); do Decode; done

}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_5b1a1215; fi

