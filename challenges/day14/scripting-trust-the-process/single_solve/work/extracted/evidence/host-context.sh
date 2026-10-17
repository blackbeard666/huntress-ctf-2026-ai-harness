#!/usr/bin/env bash

# Huntress Script Triage -- inert static-analysis fixture (bash_linux)

readonly Material_70fbd075='a3-9e-af-d3-a0-d4-b1-c1-b2-8f-eb-8e-ed-82-e6-83-dc-bf-d0-be-d8-b1-d6-a3-d1-b0-c4-ad-c2-ac-80-f2-97-e3-96-e4-8a-d5-b6-d9-b7-d1-b8-df-aa-d8-b9-cd-a4-cb-a5-d9-b8-dc-bd-cd-b9-dc-ae-93-e1-84-e5-81-ee-80-ec-95-ca-a9-c6-a8-ce-a7-c0-b5-c7-a6-d2-bb-d4-ba-c6-b5-c1-a0-c7-a2-fd-9e-f1-84-ea-9e-a3-92-ee-8d-ec-81-f1-90-f9-9e-f0-af-c6-a2-9f-fc-9d-f0-80-e1-88-ef-81-ac-9b-fe-9f-a8-ce-af-c9-fe-cc-fb-87-ef-80-f3-87-d8-b1-d5-e8-80-ef-9c-e8-c5-f2-97-f6-c1-a7-c6-a0-97-a5-92'

readonly Codec_70fbd075='hex_dash|rolling_xor|d5'



Load_70fbd075() {

  EnCoDeD_Bytes=()

  local IFS='-' PaRt

  local -a pieces

  read -r -a pieces <<< "${Material_70fbd075}"

  for PaRt in "${pieces[@]}"; do EnCoDeD_Bytes+=("$((16#$PaRt))"); done

}



Decode_70fbd075() {

  DeCoDeD_Bytes=()

  local PrEvIoUs=213

  local InDeX

  for ((InDeX=0; InDeX<${#EnCoDeD_Bytes[@]}; InDeX++)); do

    DeCoDeD_Bytes+=("$((EnCoDeD_Bytes[InDeX] ^ PrEvIoUs))")

    PrEvIoUs=${EnCoDeD_Bytes[InDeX]}

  done

}



Recover_70fbd075() {

  local -a EnCoDeD_Bytes DeCoDeD_Bytes

  local DeScRiPtOr_Text NeUtRaL PaSs InDeX

  NeUtRaL="${HUNTRESS_FIXTURE_CONTEXT:-host}"

  Load_70fbd075

  PaSs=0; while ((PaSs < 1)); do Decode_70fbd075; ((PaSs+=1)); done

  DeScRiPtOr_Text=''

  local octal character

  for InDeX in "${!DeCoDeD_Bytes[@]}"; do

    printf -v octal '%03o' "${DeCoDeD_Bytes[InDeX]}"

    printf -v character '%b' "\\$octal"

    DeScRiPtOr_Text+="$character"

  done

  printf '%s\n' "$DeScRiPtOr_Text"

}



Inspect_70fbd075() { Recover_70fbd075; }



Plan_70fbd075() {

  local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''

  descriptor="$(Inspect_70fbd075)"

  local -a fields

  IFS='|' read -r -a fields <<< "$descriptor"

  for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done

  local -a report_command=(printf '%s\n' "$campaign_id")

  declare -p report_command

}



if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_70fbd075; fi

