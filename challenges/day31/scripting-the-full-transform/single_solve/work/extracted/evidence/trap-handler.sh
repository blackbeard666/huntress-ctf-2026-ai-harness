# Huntress advanced Bash syntax fixture
readonly Material_f0b9338e='=QnblRnbp9FdjVnc0NnbvNWZyxCehRnb5N3XlpXaud2bjVmc9MHclR3c8FTP05WdvN2XldWY0NHf3QEOycjQ5MULYh0UBJUPkl2XudWahBXbhNGfwFmc09FbhN2bs9lbvlGdj5Wdm1TZ2lGdp1WayBHfyVGbk5WYo9FchJHd9Umc1RXYlZGfx0jd'
readonly Codec_f0b9338e='reversed_base64|'
Feature_f0b9338e() {
  trap 'return 0' RETURN; local armed=1; : "$armed"
}
Decode() { local reversed='' index; for ((index=${#Material_f0b9338e}-1; index>=0; index--)); do reversed+="${Material_f0b9338e:index:1}"; done; printf '%s' "$reversed" | base64 --decode; }
Inspect_f0b9338e() {
  local NeUtRaL; if ((2 > 1)); then NeUtRaL=left; else NeUtRaL=right; fi
  Decode
}
if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_f0b9338e; fi
