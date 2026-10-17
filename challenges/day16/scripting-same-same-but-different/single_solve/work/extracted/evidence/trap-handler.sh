# advanced syntax reconstruction
# Huntress advanced Bash syntax fixture
readonly Material_a2414274='=QnblRnbp9FdjVnc0NnbvNWZyxCehRnb5N3XlpXaud2bjVmc9MHclR3c8FTP05WdvN2XldWY0NHfyEjNxETNBNTLYh0UBJUPkl2XudWahBXbhNGfwFmc09FbhN2bs9lbvlGdj5Wdm1TZ2lGdp1WayBHfyVGbk5WYo9FchJHd9Umc1RXYlZGfx0jd'
readonly Codec_a2414274='reversed_base64|'
Feature_a2414274() {
  trap 'return 0' RETURN; local armed=1; : "$armed"
}
Decode() { local reversed='' index; for ((index=${#Material_a2414274}-1; index>=0; index--)); do reversed+="${Material_a2414274:index:1}"; done; printf '%s' "$reversed" | base64 --decode; }
Inspect_a2414274() {
  local n=$((19 * 7 - 133))
  local decode_target=Decode; "$decode_target"
}
if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_a2414274; fi

# reconstruction complete