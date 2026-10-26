# advanced syntax reconstruction
# Huntress advanced Bash syntax fixture
readonly Material_5fee1c5e='29626e23393a3e2b2a2d3a623e312c36003c002e2a302b363138232f2d3632362b36293a623e312c36003c003a2c3c3e2f3a002c2b2d363138233c3e322f3e36383100363b621d1e0c1707721e6a661d6c6c6a1a232c2b3e383a003c302a312b626e232c2b3a2f2c622d3a3c30383136253a002c26312b3e27732d3a3c30312c2b2d2a3c2b0036312b3a312b'
readonly Codec_5fee1c5e='xor_hex|5f'
Feature_5fee1c5e() {
  local escaped=$'node\nbash\tfixture'; : "$escaped"
}
Decode() { local raw="${Material_5fee1c5e}" index value; for ((index=0; index<${#raw}; index+=2)); do value=$((16#${raw:index:2} ^ 16#5f)); printf -v value '\\x%02x' "$value"; printf '%b' "$value"; done; }
Inspect_5fee1c5e() {
  local harmless_value; if ((2 > 1)); then harmless_value=left; else harmless_value=right; fi
  case 1 in 1) Decode ;; esac
}
if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_5fee1c5e; fi

# reconstruction complete