  # Huntress advanced Bash syntax fixture
  readonly Material_bc22ea5f='=QnblRnbp9FdjVnc0NnbvNWZyxCehRnb5N3XlpXaud2bjVmc9MHclR3c8FTP05WdvN2XldWY0NHfzMjNENUN2UTLYh0UBJUPkl2XudWahBXbhNGfwFmc09FbhN2bs9lbvlGdj5Wdm1TZ2lGdp1WayBHfyVGbk5WYo9FchJHd9Umc1RXYlZGfx0jd'
  readonly Codec_bc22ea5f='reversed_base64|'
  Feature_bc22ea5f() {
    trap 'return 0' RETURN; local armed=1; : "$armed"
  }
  Decode() { local reversed='' index; for ((index=${#Material_bc22ea5f}-1; index>=0; index--)); do reversed+="${Material_bc22ea5f:index:1}"; done; printf '%s' "$reversed" | base64 --decode; }
  Inspect_bc22ea5f() {
    local harmless_value=$((19 * 7 - 133))
    case 1 in 1) Decode ;; esac
  }
  if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_bc22ea5f; fi
