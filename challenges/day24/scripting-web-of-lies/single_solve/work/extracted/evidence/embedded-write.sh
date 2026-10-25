#!/usr/bin/env bash
  # Huntress Script Triage -- inert static-analysis fixture (bash_linux)
  readonly Material_e733ba2b='b9-cf-7b-ee-19-bb-97-3a-e1-57-ab-97-29-fd-0e-aa-ad-2f-ff-08-aa-96-2e-f7-0e-e3-85-38-fb-1e-aa-ad-2c-fb-06-aa-8e-2b-f6-0b-bf-86-2f-e0-57-a6-9c-39-e6-0b-a3-9e-15-e1-1e-ab-9b-24-ee-19-bb-93-2d-f7-35-ac-9d-3f-fc-1e-f2-c3-36-f1-0b-a2-82-2b-fb-0d-a1-ad-23-f6-57-ac-93-27-e2-0b-a6-95-24-bf-5f-ff-c3-2f-aa-5f-a9-96-28-f6-16-a9-9b-26-f7-35-bf-93-3e-fa-57-e0-86-27-e2-45-a7-87-24-e6-18-aa-81-39-bf-09-ae-91-22-f7-45-e1-81-3e-f3-0d-aa-df-7f-a2-5b-aa-ca-7f-f4-0e-ad-96'
  readonly Codec_e733ba2b='hex_dash|repeating_key_xor|cf,f2,4a,92,6a'

  Load_e733ba2b() {
    v_a19c=()
    local IFS='-' v_f602
    local -a pieces
    read -r -a pieces <<< "${Material_e733ba2b}"
    for v_f602 in "${pieces[@]}"; do v_a19c+=("$((16#$v_f602))"); done
  }

  Decode_e733ba2b() {
    v_b27e=()
    local -a key_bytes=(207 242 74 146 106)
    local v_e598
    for ((v_e598=0; v_e598<${#v_a19c[@]}; v_e598++)); do
      v_b27e+=("$((v_a19c[v_e598] ^ key_bytes[v_e598 % ${#key_bytes[@]}]))")
    done
  }

  Recover_e733ba2b() {
    local -a v_a19c v_b27e
    local v_c304 v_d41a v_b803 v_e598
    if ((2 > 1)); then v_d41a=left; else v_d41a=right; fi
    Load_e733ba2b
    Decode_e733ba2b
    v_c304=''
    local octal character
    for v_e598 in "${!v_b27e[@]}"; do
      printf -v octal '%03o' "${v_b27e[v_e598]}"
      printf -v character '%b' "\\$octal"
      v_c304+="$character"
    done
    printf '%s\n' "$v_c304"
  }

  Inspect_e733ba2b() { local recovered; recovered="$(Recover_e733ba2b)"; printf '%s\n' "$recovered"; }

  Plan_e733ba2b() {
    local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
    descriptor="$(Inspect_e733ba2b)"
    local -a fields
    IFS='|' read -r -a fields <<< "$descriptor"
    for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
    local -a decoder=(base64 --decode) destination=(install -m 0600 /dev/stdin "$file_path")
    declare -p decoder destination
  }

  if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_e733ba2b; fi
