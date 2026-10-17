  # Huntress advanced Bash syntax fixture
  readonly Material_ec455dc7='9ad1dd908a898d98999e89d19e898b8994b38f83828885988583828d80909c9e85818598859a89d18e8d9f84b39e898b8994b3818d988f84908f8d819c8d858b82b38588d1aeadbfa4b4c1ddddd5ddd5dfdada909f988d8b89b38f83998298d1dd909f98899c9fd19e898f838b82859689b39f9582988d94c09e898f83829f989e998f98b3858298898298'
  readonly Codec_ec455dc7='xor_hex|ec'
  Feature_ec455dc7() {
    local value='node-1234'; [[ "$value" =~ ^node-[0-9]+$ ]] && :
  }
  Decode() { local raw="${Material_ec455dc7}" index value; for ((index=0; index<${#raw}; index+=2)); do value=$((16#${raw:index:2} ^ 16#ec)); printf -v value '\\x%02x' "$value"; printf '%b' "$value"; done; }
  Inspect_ec455dc7() {
    local n; if ((2 > 1)); then n=left; else n=right; fi
    if ! Decode; then return 71; fi
  }
  if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_ec455dc7; fi
