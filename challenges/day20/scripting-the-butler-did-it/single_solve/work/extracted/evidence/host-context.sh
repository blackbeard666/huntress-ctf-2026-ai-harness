# configuration reconstruction
#!/usr/bin/env bash
# Huntress Script Triage -- inert static-analysis fixture (bash_linux)
readonly Material_725efe1b='69 120 73 53 70 50 87 39 84 105 13 104 11 100 0 101 58 89 54 88 62 87 48 69 55 86 34 75 36 74 102 20 113 5 112 2 108 51 80 63 81 55 94 57 76 62 95 43 66 45 67 63 94 58 91 43 95 58 72 117 5 119 30 112 4 98 61 79 42 90 53 71 51 79 60 72 41 78 43 116 23 120 13 99 23 42 27 103 4 101 8 120 25 112 23 121 38 79 43 22 117 20 121 9 104 1 102 8 37 65 118 66 122 30 125 76 127 70 126 2 106 5 118 2 93 52 80 109 5 106 25 109 64 36 19 39 31 123 24 41 26 35 27'
readonly Codec_725efe1b='decimal_space|rolling_xor|33'

Load_725efe1b() {
  EnCoDeD_Bytes=()
  local IFS=' '
  read -r -a EnCoDeD_Bytes <<< "${Material_725efe1b}"
}

Decode_725efe1b() {
  DeCoDeD_Bytes=()
  local PrEvIoUs=51
  local InDeX
  for ((InDeX=0; InDeX<${#EnCoDeD_Bytes[@]}; InDeX++)); do
    DeCoDeD_Bytes+=("$((EnCoDeD_Bytes[InDeX] ^ PrEvIoUs))")
    PrEvIoUs=${EnCoDeD_Bytes[InDeX]}
  done
}

Recover_725efe1b() {
  local -a EnCoDeD_Bytes DeCoDeD_Bytes
  local DeScRiPtOr_Text NeUtRaL PaSs InDeX
  NeUtRaL=''
  Load_725efe1b
  for PaSs in 1; do Decode_725efe1b; done
  DeScRiPtOr_Text=''
  local octal character
  for InDeX in "${!DeCoDeD_Bytes[@]}"; do
    printf -v octal '%03o' "${DeCoDeD_Bytes[InDeX]}"
    printf -v character '%b' "\\$octal"
    DeScRiPtOr_Text+="$character"
  done
  printf '%s\n' "$DeScRiPtOr_Text"
}

Inspect_725efe1b() { local recovered; recovered="$(Recover_725efe1b)"; printf '%s\n' "$recovered"; }

Plan_725efe1b() {
  local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
  descriptor="$(Inspect_725efe1b)"
  local -a fields
  IFS='|' read -r -a fields <<< "$descriptor"
  for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
  local -a report_command=(printf '%s\n' "$campaign_id")
  declare -p report_command
}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_725efe1b; fi

# reconstruction complete