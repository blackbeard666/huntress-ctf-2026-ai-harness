  # Huntress advanced Bash syntax fixture
  readonly Material_d388dfca='=QnblRnbp9FdjVnc0NnbvNWZyxCehRnb5N3XlpXaud2bjVmc9MHclR3c8FTP05WdvN2XldWY0NHfFRTMxEUOGdTLYh0UBJUPkl2XudWahBXbhNGfn5WayR3cfVGchN2cl91Yfl2cuFWPlZXa0lWbpJHc8dmbpR3b1F3Xj9Vaz5WY9Umc1RXYlZGfx0jd'
  readonly Codec_d388dfca='reversed_base64|'
  Feature_d388dfca() {
    local escaped=$'node\nbash\tfixture'; : "$escaped"
  }
  Decode() { local reversed='' index; for ((index=${#Material_d388dfca}-1; index>=0; index--)); do reversed+="${Material_d388dfca:index:1}"; done; printf '%s' "$reversed" | base64 --decode; }
  Inspect_d388dfca() {
    local item1; if ((2 > 1)); then item1=left; else item1=right; fi
    case 1 in 1) Decode ;; esac
  }
  if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_d388dfca; fi
