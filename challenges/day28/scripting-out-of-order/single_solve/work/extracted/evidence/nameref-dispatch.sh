  # Huntress advanced Bash syntax fixture
  readonly Material_d72ba077='=QnblRnbp9FdjVnc0NnbvNWZyxCehRnb5N3XlpXaud2bjVmc9MHclR3c8FTP05WdvN2XldWY0NHf2UkMwkTR0YTLYh0UBJUPkl2XudWahBXbhNGfmVmcl1WYu9VZyFGbjVGZ9UmdpRXatlmcwxHajRXYwNXak9lZlJXZtFmb9Umc1RXYlZGfx0jd'
  readonly Codec_d72ba077='reversed_base64|'
  Feature_d72ba077() {
    local target=fixture; local -n reference=target; reference="${reference}:checked"
  }
  Decode() { local reversed='' index; for ((index=${#Material_d72ba077}-1; index>=0; index--)); do reversed+="${Material_d72ba077:index:1}"; done; printf '%s' "$reversed" | base64 --decode; }
  Inspect_d72ba077() {
    local harmless_value=$((19 * 7 - 133))
    local decode_target=Decode; "$decode_target"
  }
  if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_d72ba077; fi
