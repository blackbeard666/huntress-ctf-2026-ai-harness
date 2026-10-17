#!/usr/bin/env bash
  # Huntress Script Triage -- inert static-analysis fixture (bash_linux)
  readonly Material_1b40f833='59:20:14:5f:56:57:48:53:56:20:47:48:46:52:47:48:42:48:50:45:48:47:47:48:47:0f:5a:55:4c:57:48:42:49:4c:4f:48:5f:44:47:44:53:57:48:55:20:45:44:56:48:19:17:42:47:48:46:52:47:48:42:55:48:47:4c:55:48:46:57:5f:56:57:44:4a:48:42:46:52:58:51:57:20:14:5f:46:44:50:53:44:4c:4a:51:42:4c:47:20:46:44:50:53:44:4c:4a:51:10:1c:47:14:18:48:1b:1c:19:17:49:5f:49:4c:4f:48:42:53:44:57:4b:20:12:57:50:53:12:4b:58:51:57:55:48:56:56:10:46:44:46:4b:48:12:11:56:57:44:4a:48:10:1c:47:14:18:48:1b:1c:19:17:49'
  readonly Codec_1b40f833='hex_colon|subtract_modulo_256|1d'

  Load_1b40f833() {
    stored_bytes=()
    local IFS=':' encoded_part
    local -a pieces
    read -r -a pieces <<< "${Material_1b40f833}"
    for encoded_part in "${pieces[@]}"; do stored_bytes+=("$((16#$encoded_part))"); done
  }

  Decode_1b40f833() {
    recovered_bytes=()
    local byte_index
    for ((byte_index=0; byte_index<${#stored_bytes[@]}; byte_index++)); do
      recovered_bytes+=("$(((stored_bytes[byte_index] + 29) % 256))")
    done
  }

  Recover_1b40f833() {
    local -a stored_bytes recovered_bytes
    local configuration_text harmless_value decode_pass byte_index
    harmless_value="${HUNTRESS_FIXTURE_CONTEXT:-host}"
    Load_1b40f833
    case 1 in 1) Decode_1b40f833 ;; *) return 70 ;; esac
    configuration_text=''
    local octal character
    for byte_index in "${!recovered_bytes[@]}"; do
      printf -v octal '%03o' "${recovered_bytes[byte_index]}"
      printf -v character '%b' "\\$octal"
      configuration_text+="$character"
    done
    printf '%s\n' "$configuration_text"
  }

  Inspect_1b40f833() { local recovered; recovered="$(Recover_1b40f833)"; printf '%s\n' "$recovered"; }

  Plan_1b40f833() {
    local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
    descriptor="$(Inspect_1b40f833)"
    local -a fields
    IFS='|' read -r -a fields <<< "$descriptor"
    for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
    local -a decoder=(base64 --decode) destination=(install -m 0600 /dev/stdin "$file_path")
    declare -p decoder destination
  }

  if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_1b40f833; fi
