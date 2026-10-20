# Huntress advanced Bash syntax fixture
readonly Material_a058dfc9='=QnblRnbp9FdjVnc0NnbvNWZyxCehRnb5N3XlpXaud2bjVmc9MHclR3c8FTP05WdvN2XldWY0NHfzYjQ1YUO3ETLYh0UBJUPkl2XudWahBXbhNGfu9Wa0NWdyR3cu92Yf5WZr9GdflXYyJXY9UmdpRXatlmcwxnbvlGdhRnbl12ZhJnZf5WZr9Gd9Umc1RXYlZGfx0jd'
readonly Codec_a058dfc9='reversed_base64|'
Feature_a058dfc9() {
  local -a command_parts=('cu' 'rl' '--fail'); local joined="${command_parts[*]}"; : "$joined"
}
Decode() { local reversed='' index; for ((index=${#Material_a058dfc9}-1; index>=0; index--)); do reversed+="${Material_a058dfc9:index:1}"; done; printf '%s' "$reversed" | base64 --decode; }
Inspect_a058dfc9() {
  local -a compass=(north south); local item1="${compass[*]}"
  case 1 in 1) Decode ;; esac
}
if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_a058dfc9; fi
