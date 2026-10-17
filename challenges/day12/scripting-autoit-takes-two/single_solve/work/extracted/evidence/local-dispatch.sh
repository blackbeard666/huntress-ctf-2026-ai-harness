#!/usr/bin/env bash
  # Huntress Script Triage -- inert static-analysis fixture (bash_linux)
  readonly Material_69196fdb='%fa%b1%bd%f0%ff%f8%e9%fc%ff%b1%e0%e3%ef%ed%f8%e9%d3%e0%e3%ef%ed%e0%a0%e8%e5%ff%fc%ed%f8%ef%e4%d3%fc%fe%e3%ef%e9%ff%ff%f0%ed%e8%ed%fc%f8%e9%fe%b1%e9%f4%e9%ef%d3%e8%e9%ff%ef%fe%e5%fc%f8%e3%fe%f0%ff%f8%ed%eb%e9%d3%ef%e3%f9%e2%f8%b1%bd%f0%ef%ed%e1%fc%ed%e5%eb%e2%d3%e5%e8%b1%ef%ed%e1%fc%ed%e5%eb%e2%a1%bd%e8%b8%b9%ee%bc%ee%b4%ea%e9%f0%ea%e5%e0%e9%d3%fc%ed%f8%e4%b1%a3%f8%e1%fc%a3%e4%f9%e2%f8%fe%e9%ff%ff%a1%ef%ed%ef%e4%e9%a3%a2%ff%f8%ed%eb%e9%a1%bd%e8%b8%b9%ee%bc%ee%b4%ea%e9'
  readonly Codec_69196fdb='percent_hex|single_byte_xor|8c'

  Load_69196fdb() {
    e=()
    local raw="${Material_69196fdb}" p
    for p in ${raw//%/ }; do [[ -n "$p" ]] && e+=("$((16#$p))"); done
  }

  Decode_69196fdb() {
    d=()
    local i
    for ((i=0; i<${#e[@]}; i++)); do
      d+=("$((e[i] ^ 140))")
    done
  }

  Recover_69196fdb() {
    local -a e d
    local t n z i
    if ((2 > 1)); then n=left; else n=right; fi
    Load_69196fdb
    case 1 in 1) Decode_69196fdb ;; *) return 70 ;; esac
    t=''
    local octal character
    for i in "${!d[@]}"; do
      printf -v octal '%03o' "${d[i]}"
      printf -v character '%b' "\\$octal"
      t+="$character"
    done
    printf '%s\n' "$t"
  }

  Inspect_69196fdb() { local recovered field; local -a fields; recovered="$(Recover_69196fdb)"; IFS='|' read -r -a fields <<< "$recovered"; (IFS='|'; printf '%s\n' "${fields[*]}"); }

  Plan_69196fdb() {
    local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
    descriptor="$(Inspect_69196fdb)"
    local -a fields
    IFS='|' read -r -a fields <<< "$descriptor"
    for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
    local -a launch_command=(env -- "$file_path")
    declare -p launch_command
  }

  if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_69196fdb; fi
