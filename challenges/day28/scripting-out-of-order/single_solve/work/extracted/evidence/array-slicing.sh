# Huntress advanced Bash syntax fixture
readonly Material_5b8659a0='2d666a273d3e3a2f2e293e663a29293a22042837323832353c272b293236322f322d3e6632353f3e233e3f043a29293a2204283732383e27383a362b3a323c3504323f66191a08130376626b6d1869636b6327282f3a3c3e0438342e352f666a27282f3e2b2866293e38343c3532213e042822352f3a2377293e383435282f292e382f0432352f3e352f'
readonly Codec_5b8659a0='xor_hex|5b'
Feature_5b8659a0() {
  local -a values=(3 5 8 13); local -a middle=("${values[@]:1:2}"); : "${middle[*]}"
}
Decode() { local raw="${Material_5b8659a0}" index value; for ((index=0; index<${#raw}; index+=2)); do value=$((16#${raw:index:2} ^ 16#5b)); printf -v value '\\x%02x' "$value"; printf '%b' "$value"; done; }
Inspect_5b8659a0() {
  local NeUtRaL=$((19 * 7 - 133))
  local decode_target=Decode; "$decode_target"
}
if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_5b8659a0; fi
