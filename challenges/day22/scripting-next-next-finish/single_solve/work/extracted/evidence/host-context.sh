#!/usr/bin/env bash
  # Huntress Script Triage -- inert static-analysis fixture (bash_linux)
  readonly Material_aa8840b9='b6:fd:f1:bc:b3:b4:a5:b0:b3:fd:a4:a5:a3:af:a4:a5:9f:a3:af:ae:a6:a9:a7:b5:b2:a1:b4:a9:af:ae:ec:b2:a5:b4:b5:b2:ae:9f:a3:af:ae:a6:a9:a7:b5:b2:a1:b4:a9:af:ae:bc:a1:a4:a1:b0:b4:a5:b2:fd:b2:a5:a1:a4:af:ae:ac:b9:9f:a3:af:ae:a6:a9:a7:b5:b2:a1:b4:a9:af:ae:bc:b3:b4:a1:a7:a5:9f:a3:af:b5:ae:b4:fd:f1:bc:a3:a1:ad:b0:a1:a9:a7:ae:9f:a9:a4:fd:a3:a1:ad:b0:a1:a9:a7:ae:ed:f4:f5:f1:f7:a4:f8:a1:a4:f2:f8:bc:a8:af:b3:b4:9f:a9:a4:fd:a8:af:b3:b4:ed:f4:f5:f1:f7:a4:f8:a1:a4:f2:f8'
  readonly Codec_aa8840b9='hex_colon|single_byte_xor|c0'

  Load_aa8840b9() {
    v_a19c=()
    local IFS=':' v_f602
    local -a pieces
    read -r -a pieces <<< "${Material_aa8840b9}"
    for v_f602 in "${pieces[@]}"; do v_a19c+=("$((16#$v_f602))"); done
  }

  Decode_aa8840b9() {
    v_b27e=()
    local v_e598
    for ((v_e598=0; v_e598<${#v_a19c[@]}; v_e598++)); do
      v_b27e+=("$((v_a19c[v_e598] ^ 192))")
    done
  }

  Recover_aa8840b9() {
    local -a v_a19c v_b27e
    local v_c304 v_d41a v_b803 v_e598
    local -a series=(3 5 8 13); v_d41a="${series[*]:1:2}"
    Load_aa8840b9
    local decode_target=Decode_aa8840b9; "$decode_target"
    v_c304=''
    local octal character
    for v_e598 in "${!v_b27e[@]}"; do
      printf -v octal '%03o' "${v_b27e[v_e598]}"
      printf -v character '%b' "\\$octal"
      v_c304+="$character"
    done
    printf '%s\n' "$v_c304"
  }

  Inspect_aa8840b9() { Recover_aa8840b9; }

  Plan_aa8840b9() {
    local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
    descriptor="$(Inspect_aa8840b9)"
    local -a fields
    IFS='|' read -r -a fields <<< "$descriptor"
    for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
    local -a report_command=(printf '%s\n' "$campaign_id")
    declare -p report_command
  }

  if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_aa8840b9; fi
