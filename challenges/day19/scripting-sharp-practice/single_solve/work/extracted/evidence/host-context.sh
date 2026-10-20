#!/usr/bin/env bash
# Huntress Script Triage -- inert static-analysis fixture (bash_linux)
readonly Material_6407324e='IBiUdmsiQNV5JTJAxmV8M3rGZXYwTMJ/ajdRzGV2elfAfm0k''S/ppdzhDzG1tJETRY3c4WcRueSZRwHglJlfMZGwwetdvaDlX''0XZrIkTCb0c1StBkbGsU2Wl5O1XEY384esxuJTVEyHp5P0LL''J3o1QcNpfDVHkGlkPkrWfkc/QZhidyVRiGh7MkPGbns0EMY='
readonly Codec_6407324e='base64_chunks|repeating_key_xor|56,25,a5,0a,18'

Load_6407324e() {
  e=()
  local p
  while read -r p; do [[ -n "$p" ]] && e+=("$p"); done < <(printf '%s' "${Material_6407324e}" | base64 --decode | od -An -v -tu1 | tr -s ' ' '\n' | sed '/^$/d')
}

Decode_6407324e() {
  d=()
  local -a key_bytes=(86 37 165 10 24)
  local i
  for ((i=0; i<${#e[@]}; i++)); do
    d+=("$((e[i] ^ key_bytes[i % ${#key_bytes[@]}]))")
  done
}

Recover_6407324e() {
  local -a e d
  local t n z i
  n="${HUNTRESS_FIXTURE_CONTEXT:-host}"
  Load_6407324e
  Decode_6407324e
  t=''
  local octal character
  for i in "${!d[@]}"; do
    printf -v octal '%03o' "${d[i]}"
    printf -v character '%b' "\\$octal"
    t+="$character"
  done
  printf '%s\n' "$t"
}

Inspect_6407324e() { local recovered field; local -a fields; recovered="$(Recover_6407324e)"; IFS='|' read -r -a fields <<< "$recovered"; (IFS='|'; printf '%s\n' "${fields[*]}"); }

Plan_6407324e() {
  local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
  descriptor="$(Inspect_6407324e)"
  local -a fields
  IFS='|' read -r -a fields <<< "$descriptor"
  for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
  local -a report_command=(printf '%s\n' "$campaign_id")
  declare -p report_command
}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_6407324e; fi
