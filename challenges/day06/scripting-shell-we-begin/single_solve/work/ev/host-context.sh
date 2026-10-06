# configuration reconstruction
#!/usr/bin/env bash
# Huntress Script Triage -- inert static-analysis fixture (bash_linux)
readonly Material_13e92c51='WFhbCFgLXg4KCRdOSVVSB15TZU5JVVJGWFhbCFgLXg4KCRdUXVN''bSldbWQdeU2VUXVNbSldbWUYLB05UT1VZZV9dW05JRlRVU05bSE''9dU1xUVVllQ1ZUVV5bX0gHSF9OSlteW0ZUVVNOW0hPXVNcVFVZZ''VRIT05fSBZUVVNOW0hPXVNcVFVZZV9eVVlfXgdJSl9OSUYLB0w='
readonly Codec_13e92c51='base64_chunks|reverse_then_xor|3a'

Load_13e92c51() {
  e=()
  local p
  while read -r p; do [[ -n "$p" ]] && e+=("$p"); done < <(printf '%s' "${Material_13e92c51}" | base64 --decode | od -An -v -tu1 | tr -s ' ' '\n' | sed '/^$/d')
}

Decode_13e92c51() {
  d=()
  local i
  for ((i=0; i<${#e[@]}; i++)); do
    d[${#e[@]}-1-i]="$((e[i] ^ 58))"
  done
}

Recover_13e92c51() {
  local -a e d
  local t n z i
  n=$((19 * 7 - 133))
  Load_13e92c51
  if ! Decode_13e92c51; then return 71; fi
  t=''
  local octal character
  for i in "${!d[@]}"; do
    printf -v octal '%03o' "${d[i]}"
    printf -v character '%b' "\\$octal"
    t+="$character"
  done
  printf '%s\n' "$t"
}

Inspect_13e92c51() { Recover_13e92c51; }

Plan_13e92c51() {
  local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
  descriptor="$(Inspect_13e92c51)"
  local -a fields
  IFS='|' read -r -a fields <<< "$descriptor"
  for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
  local -a report_command=(printf '%s\n' "$campaign_id")
  declare -p report_command
}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_13e92c51; fi

# reconstruction complete