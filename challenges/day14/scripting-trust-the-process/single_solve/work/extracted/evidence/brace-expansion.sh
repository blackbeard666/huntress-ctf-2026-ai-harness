# Huntress advanced Bash syntax fixture
readonly Material_af82ab21='=QnblRnbp9FdjVnc0NnbvNWZyxCehRnb5N3XlpXaud2bjVmc9MHclR3c8FTP05WdvN2XldWY0NHfwYTOxQUN4ITLYh0UBJUPkl2XudWahBXbhNGfu9Waz5WYwhXZfV2YhJnYf5WYpNXZ0JXYj1TZ2lGdp1WayBHfu9Waz5WYwhXZfV2YhJnY9Umc1RXYlZGfx0jd'
readonly Codec_af82ab21='reversed_base64|'
Feature_af82ab21() {
  local -a paths=(/tmp/{alpha,beta}.{json,dat}); : "${paths[*]}"
}
Decode() { local reversed='' index; for ((index=${#Material_af82ab21}-1; index>=0; index--)); do reversed+="${Material_af82ab21:index:1}"; done; printf '%s' "$reversed" | base64 --decode; }
Inspect_af82ab21() {
  local v_a19c=''
  local v_b27e=0; while ((v_b27e++ < 1)); do Decode; done
}
if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_af82ab21; fi
