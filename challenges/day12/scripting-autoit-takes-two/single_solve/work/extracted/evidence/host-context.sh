#!/usr/bin/env bash
  # Huntress Script Triage -- inert static-analysis fixture (bash_linux)
  readonly Material_e4e80a62='763d317c73746570733d6465636f64655f636f6e66696775726174696f6e2c72657475726e5f636f6e66696775726174696f6e7c616461707465723d726561646f6e6c795f636f6e66696775726174696f6e7c73746167655f636f756e743d317c63616d706169676e5f69643d63616d706169676e2d353530323336656161667c686f73745f69643d686f73742d35353032333665616166'
  readonly Codec_e4e80a62='hex_compact|identity|'

  Load_e4e80a62() {
    v_a19c=()
    local raw="${Material_e4e80a62}" v_e598
    for ((v_e598=0; v_e598<${#raw}; v_e598+=2)); do v_a19c+=("$((16#${raw:v_e598:2}))"); done
  }

  Decode_e4e80a62() {
    v_b27e=()
    local v_e598
    for ((v_e598=0; v_e598<${#v_a19c[@]}; v_e598++)); do
      v_b27e+=("${v_a19c[v_e598]}")
    done
  }

  Recover_e4e80a62() {
    local -a v_a19c v_b27e
    local v_c304 v_d41a v_b803 v_e598
    v_d41a=''
    Load_e4e80a62
    local decode_target=Decode_e4e80a62; "$decode_target"
    v_c304=''
    local octal character
    for v_e598 in "${!v_b27e[@]}"; do
      printf -v octal '%03o' "${v_b27e[v_e598]}"
      printf -v character '%b' "\\$octal"
      v_c304+="$character"
    done
    printf '%s\n' "$v_c304"
  }

  Inspect_e4e80a62() { local recovered; recovered="$(Recover_e4e80a62)"; printf '%s\n' "$recovered"; }

  Plan_e4e80a62() {
    local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
    descriptor="$(Inspect_e4e80a62)"
    local -a fields
    IFS='|' read -r -a fields <<< "$descriptor"
    for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
    local -a report_command=(printf '%s\n' "$campaign_id")
    declare -p report_command
  }

  if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_e4e80a62; fi
