# Huntress advanced Bash syntax fixture

readonly Material_614d88ae='175c501d070400151413045c05180f000c08023e07080d043e05041202130811150e131d1113080c08150817045c000d0d0e02001504053e07080d043e05041202130811150e131d02000c110008060f3e08055c23203229394c53225453245923541d12150006043e020e140f155c501d12150411125c1304020e060f081b043e12180f1500194d1304020e0f1215131402153e080f15040f15'

readonly Codec_614d88ae='xor_hex|61'

Feature_614d88ae() {

  local descriptor_fd; exec {descriptor_fd}<<<'fixture'; exec {descriptor_fd}<&-

}

Decode() { local raw="${Material_614d88ae}" index value; for ((index=0; index<${#raw}; index+=2)); do value=$((16#${raw:index:2} ^ 16#61)); printf -v value '\\x%02x' "$value"; printf '%b' "$value"; done; }

Inspect_614d88ae() {

  local harmless_value; if ((2 > 1)); then harmless_value=left; else harmless_value=right; fi

  for decode_pass in 1; do Decode; done

}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_614d88ae; fi

