# advanced syntax reconstruction
# Huntress advanced Bash syntax fixture
readonly Material_5cb130a3='=QnblRnbp9FdjVnc0NnbvNWZyxCehRnb5N3XlpXaud2bjVmc9MHclR3c8FTP05WdvN2XldWY0NHf5MjRwYTMFNTLYh0UBJUPkl2XudWahBXbhNGfu9Wa0NWdyR3cu92Yf5WZr9GdflXYyJXY9UmdpRXatlmcwxnbvlGdhRnbl12ZhJnZf5WZr9Gd9Umc1RXYlZGfx0jd'
readonly Codec_5cb130a3='reversed_base64|'
Feature_5cb130a3() {
  local -a command_parts=('cu' 'rl' '--fail'); local joined="${command_parts[*]}"; : "$joined"
}
Decode() { local reversed='' index; for ((index=${#Material_5cb130a3}-1; index>=0; index--)); do reversed+="${Material_5cb130a3:index:1}"; done; printf '%s' "$reversed" | base64 --decode; }
Inspect_5cb130a3() {
  local v_a19c="${HUNTRESS_FIXTURE_CONTEXT:-host}"
  local v_b27e=0; while ((v_b27e++ < 1)); do Decode; done
}
if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_5cb130a3; fi

# reconstruction complete