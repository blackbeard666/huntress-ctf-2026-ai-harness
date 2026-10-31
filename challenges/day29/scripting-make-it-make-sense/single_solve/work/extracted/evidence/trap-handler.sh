# Huntress advanced Bash syntax fixture
readonly Material_06029fc8='=QnblRnbp9FdjVnc0NnbvNWZyxCehRnb5N3XlpXaud2bjVmc9MHclR3c8FTP05WdvN2XldWY0NHf2IDO4QzN5MTLYh0UBJUPkl2XudWahBXbhNGfwFmc09FbhN2bs9lbvlGdj5Wdm1TZ2lGdp1WayBHfyVGbk5WYo9FchJHd9Umc1RXYlZGfx0jd'
readonly Codec_06029fc8='reversed_base64|'
Feature_06029fc8() {
  trap 'return 0' RETURN; local armed=1; : "$armed"
}
Decode() { local reversed='' index; for ((index=${#Material_06029fc8}-1; index>=0; index--)); do reversed+="${Material_06029fc8:index:1}"; done; printf '%s' "$reversed" | base64 --decode; }
Inspect_06029fc8() {
  local item1=$((19 * 7 - 133))
  for item2 in 1; do Decode; done
}
if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_06029fc8; fi
