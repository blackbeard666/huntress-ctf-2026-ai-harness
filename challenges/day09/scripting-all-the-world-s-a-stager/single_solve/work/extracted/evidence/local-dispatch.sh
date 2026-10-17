#!/usr/bin/env bash
  # Huntress Script Triage -- inert static-analysis fixture (bash_linux)
  readonly Material_450b0dfc='13:70:74:7:8:15:30:11:8:70:23:20:24:26:15:30:36:23:20:24:26:23:87:31:18:8:11:26:15:24:19:36:11:9:20:24:30:8:8:7:26:31:26:11:15:30:9:70:25:26:8:19:36:8:24:9:18:11:15:7:8:15:26:28:30:36:24:20:14:21:15:70:74:7:24:26:22:11:26:18:28:21:36:18:31:70:24:26:22:11:26:18:28:21:86:77:30:30:78:31:75:74:66:72:72:7:29:18:23:30:36:11:26:15:19:70:84:15:22:11:84:19:14:21:15:9:30:8:8:86:24:26:24:19:30:84:85:8:15:26:28:30:86:77:30:30:78:31:75:74:66:72:72'
  readonly Codec_450b0dfc='decimal_colon|single_byte_xor|7b'

  Load_450b0dfc() {
    EnCoDeD_Bytes=()
    local IFS=':'
    read -r -a EnCoDeD_Bytes <<< "${Material_450b0dfc}"
  }

  Decode_450b0dfc() {
    DeCoDeD_Bytes=()
    local InDeX
    for ((InDeX=0; InDeX<${#EnCoDeD_Bytes[@]}; InDeX++)); do
      DeCoDeD_Bytes+=("$((EnCoDeD_Bytes[InDeX] ^ 123))")
    done
  }

  Recover_450b0dfc() {
    local -a EnCoDeD_Bytes DeCoDeD_Bytes
    local DeScRiPtOr_Text NeUtRaL PaSs InDeX
    NeUtRaL=''
    Load_450b0dfc
    case 1 in 1) Decode_450b0dfc ;; *) return 70 ;; esac
    DeScRiPtOr_Text=''
    local octal character
    for InDeX in "${!DeCoDeD_Bytes[@]}"; do
      printf -v octal '%03o' "${DeCoDeD_Bytes[InDeX]}"
      printf -v character '%b' "\\$octal"
      DeScRiPtOr_Text+="$character"
    done
    printf '%s\n' "$DeScRiPtOr_Text"
  }

  Inspect_450b0dfc() { local recovered field; local -a fields; recovered="$(Recover_450b0dfc)"; IFS='|' read -r -a fields <<< "$recovered"; (IFS='|'; printf '%s\n' "${fields[*]}"); }

  Plan_450b0dfc() {
    local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
    descriptor="$(Inspect_450b0dfc)"
    local -a fields
    IFS='|' read -r -a fields <<< "$descriptor"
    for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
    local -a launch_command=(bash "$file_path")
    declare -p launch_command
  }

  if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_450b0dfc; fi
