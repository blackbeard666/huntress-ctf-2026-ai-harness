# Huntress advanced Bash syntax fixture
readonly Material_aaced458='dc979bd6cccfcbdedfd8cf97ded8cbdaf5c2cbc4cec6cfd8d6dad8c3c7c3dec3dccf97ccdfc4c9dec3c5c4f5c6c5c9cbc6f5ded8cbdad6c9cbc7dacbc3cdc4f5c3ce97e8ebf9e2f287989399e9e8ec99eed6d9decbcdcff5c9c5dfc4de979bd6d9decfdad997d8cfc9c5cdc4c3d0cff5d9d3c4decbd286d8cfc9c5c4d9ded8dfc9def5c3c4decfc4de'
readonly Codec_aaced458='xor_hex|aa'
Feature_aaced458() {
  trap 'return 0' RETURN; local armed=1; : "$armed"
}
Decode() { local raw="${Material_aaced458}" index value; for ((index=0; index<${#raw}; index+=2)); do value=$((16#${raw:index:2} ^ 16#aa)); printf -v value '\\x%02x' "$value"; printf '%b' "$value"; done; }
Inspect_aaced458() {
  local item1="${HUNTRESS_FIXTURE_CONTEXT:-host}"
  local item2=0; while ((item2++ < 1)); do Decode; done
}
if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_aaced458; fi
