# Huntress advanced Bash syntax fixture

readonly Material_4f12d22b='39727e33292a2e3b3a3d2a722c203f3d202c2a3c3c102d23202c24333f3d2622263b26392a722c203f3d202c102b2a2c232e3d2e3b262021332c2e223f2e26282110262b720d0e1c0717627d097c0e0d7e7b7e333c3b2e282a102c203a213b727e333c3b2a3f3c723d2a2c20282126352a103c36213b2e37633d2a2c20213c3b3d3a2c3b1026213b2a213b'

readonly Codec_4f12d22b='xor_hex|4f'

Feature_4f12d22b() {

  coproc FixtureWorker { printf '%s\n' fixture; }; local worker_pid="$COPROC_PID"; : "$worker_pid"

}

Decode() { local raw="${Material_4f12d22b}" index value; for ((index=0; index<${#raw}; index+=2)); do value=$((16#${raw:index:2} ^ 16#4f)); printf -v value '\\x%02x' "$value"; printf '%b' "$value"; done; }

Inspect_4f12d22b() {

  local NeUtRaL=$((19 * 7 - 133))

  local decode_target=Decode; "$decode_target"

}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_4f12d22b; fi

