# advanced syntax reconstruction
# Huntress advanced Bash syntax fixture
readonly Material_23013dd6='551e125f454642575651461e4250504c404a42574a55467c425151425a505f53514a4e4a574a55461e4746404f4251467c4250504c404a42574a55465f40424e53424a444d7c4a471e6162706b7b0e6613131a676066605f50574244467c404c564d571e125f50574653501e5146404c444d4a59467c505a4d57425b0f5146404c4d5057515640577c4a4d57464d57'
readonly Codec_23013dd6='xor_hex|23'
Feature_23013dd6() {
  local -A index=([alpha]=1 [beta]=2); local value="${index[alpha]}"; : "$value"
}
Decode() { local raw="${Material_23013dd6}" index value; for ((index=0; index<${#raw}; index+=2)); do value=$((16#${raw:index:2} ^ 16#23)); printf -v value '\\x%02x' "$value"; printf '%b' "$value"; done; }
Inspect_23013dd6() {
  local -a compass=(north south); local n="${compass[*]}"
  local p=0; while ((p++ < 1)); do Decode; done
}
if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_23013dd6; fi

# reconstruction complete