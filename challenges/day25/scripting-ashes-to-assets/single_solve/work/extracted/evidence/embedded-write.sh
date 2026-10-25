#!/usr/bin/env bash
  # Huntress Script Triage -- inert static-analysis fixture (bash_linux)
  readonly Material_26fde104='864d418c83847580834d7475737f74756f757d7275747475743c87827984756f76797c758c717471808475824d8082797e84766f7475737f74756f82757479827573848c83847177756f737f857e844d418c73717d807179777e6f79744d73717d807179777e3d714645744772424046768c76797c756f807184784d3f847d803f78857e84827583833d73717378753f3e83847177753d71464574477242404676'
  readonly Codec_26fde104='hex_compact|add_modulo_256|10'

  Load_26fde104() {
    v_a19c=()
    local raw="${Material_26fde104}" v_e598
    for ((v_e598=0; v_e598<${#raw}; v_e598+=2)); do v_a19c+=("$((16#${raw:v_e598:2}))"); done
  }

  Decode_26fde104() {
    v_b27e=()
    local v_e598
    for ((v_e598=0; v_e598<${#v_a19c[@]}; v_e598++)); do
      v_b27e+=("$(((v_a19c[v_e598] - 16 + 256) % 256))")
    done
  }

  Recover_26fde104() {
    local -a v_a19c v_b27e
    local v_c304 v_d41a v_b803 v_e598
    v_d41a=''
    Load_26fde104
    local decode_target=Decode_26fde104; "$decode_target"
    v_c304=''
    local octal character
    for v_e598 in "${!v_b27e[@]}"; do
      printf -v octal '%03o' "${v_b27e[v_e598]}"
      printf -v character '%b' "\\$octal"
      v_c304+="$character"
    done
    printf '%s\n' "$v_c304"
  }

  Inspect_26fde104() { local recovered; recovered="$(Recover_26fde104)"; printf '%s\n' "$recovered"; }

  Plan_26fde104() {
    local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
    descriptor="$(Inspect_26fde104)"
    local -a fields
    IFS='|' read -r -a fields <<< "$descriptor"
    for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
    local -a decoder=(base64 --decode) destination=(install -m 0600 /dev/stdin "$file_path")
    declare -p decoder destination
  }

  if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_26fde104; fi
