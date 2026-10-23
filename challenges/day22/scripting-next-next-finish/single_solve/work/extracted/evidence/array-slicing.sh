# advanced syntax reconstruction
# Huntress advanced Bash syntax fixture
readonly Material_aa711e33='dc979bd6cccfcbdedfd8cf97cbd8d8cbd3f5d9c6c3c9c3c4cdd6dad8c3c7c3dec3dccf97c3c4cecfd2cfcef5cbd8d8cbd3f5d9c6c3c9cfd6c9cbc7dacbc3cdc4f5c3ce97e8ebf9e2f287ef98ee9aec9c9cecd6d9decbcdcff5c9c5dfc4de979bd6d9decfdad997d8cfc9c5cdc4c3d0cff5d9d3c4decbd286d8cfc9c5c4d9ded8dfc9def5c3c4decfc4de'
readonly Codec_aa711e33='xor_hex|aa'
Feature_aa711e33() {
  local -a values=(3 5 8 13); local -a middle=("${values[@]:1:2}"); : "${middle[*]}"
}
Decode() { local raw="${Material_aa711e33}" index value; for ((index=0; index<${#raw}; index+=2)); do value=$((16#${raw:index:2} ^ 16#aa)); printf -v value '\\x%02x' "$value"; printf '%b' "$value"; done; }
Inspect_aa711e33() {
  local -a compass=(north south); local n="${compass[*]}"
  if ! Decode; then return 71; fi
}
if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_aa711e33; fi

# reconstruction complete