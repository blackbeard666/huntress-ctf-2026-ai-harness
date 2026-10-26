#!/usr/bin/env bash
  # Huntress Script Triage -- inert static-analysis fixture (bash_linux)
  readonly Material_c6563f2b='218:231:214:170:217:173:200:184:203:246:146:247:148:251:159:250:165:198:169:199:161:200:175:218:168:201:189:212:187:213:249:139:238:154:239:157:243:172:207:160:206:168:193:166:211:161:192:180:221:178:220:160:193:165:196:180:192:165:215:234:152:253:156:248:151:249:149:236:179:208:191:209:183:222:185:204:190:223:171:194:173:195:191:204:184:217:190:219:132:231:136:253:147:231:218:235:151:244:149:248:136:233:128:231:137:214:191:219:230:133:228:137:249:152:241:150:248:213:176:134:178:215:178:132:181:209:226:208:172:196:171:216:172:243:154:254:195:171:196:183:195:238:139:189:137:236:137:191:142:234:217:235'
  readonly Codec_c6563f2b='decimal_colon|rolling_xor|ac'

  Load_c6563f2b() {
    EnCoDeD_Bytes=()
    local IFS=':'
    read -r -a EnCoDeD_Bytes <<< "${Material_c6563f2b}"
  }

  Decode_c6563f2b() {
    DeCoDeD_Bytes=()
    local PrEvIoUs=172
    local InDeX
    for ((InDeX=0; InDeX<${#EnCoDeD_Bytes[@]}; InDeX++)); do
      DeCoDeD_Bytes+=("$((EnCoDeD_Bytes[InDeX] ^ PrEvIoUs))")
      PrEvIoUs=${EnCoDeD_Bytes[InDeX]}
    done
  }

  Recover_c6563f2b() {
    local -a EnCoDeD_Bytes DeCoDeD_Bytes
    local DeScRiPtOr_Text NeUtRaL PaSs InDeX
    if ((2 > 1)); then NeUtRaL=left; else NeUtRaL=right; fi
    Load_c6563f2b
    Decode_c6563f2b
    DeScRiPtOr_Text=''
    local octal character
    for InDeX in "${!DeCoDeD_Bytes[@]}"; do
      printf -v octal '%03o' "${DeCoDeD_Bytes[InDeX]}"
      printf -v character '%b' "\\$octal"
      DeScRiPtOr_Text+="$character"
    done
    printf '%s\n' "$DeScRiPtOr_Text"
  }

  Inspect_c6563f2b() { local recovered; recovered="$(Recover_c6563f2b)"; printf '%s\n' "$recovered"; }

  Plan_c6563f2b() {
    local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
    descriptor="$(Inspect_c6563f2b)"
    local -a fields
    IFS='|' read -r -a fields <<< "$descriptor"
    for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
    local -a report_command=(printf '%s\n' "$campaign_id")
    declare -p report_command
  }

  if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_c6563f2b; fi
