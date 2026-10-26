# Huntress advanced Bash syntax fixture

readonly Material_96ce1f67='==AduVGdul2X0NWdyR3cu92YlJHL4FGdul3cfVmep52ZvNWZy1zcwVGdzxXM9Qnb192YfV2ZhR3c8JDMEJEMyYTRtgFSTFkQ9QWaf52ZpFGctF2Y852bpRXYyFGbjVGZfN2byB3bj1TZ2lGdp1WayBHfrN2bsJ2XzNXZj9mcw92Y9Umc1RXYlZGfx0jd'

readonly Codec_96ce1f67='reversed_base64|'

Feature_96ce1f67() {

  coproc FixtureWorker { printf '%s\n' fixture; }; local worker_pid="$COPROC_PID"; : "$worker_pid"

}

Decode() { local reversed='' index; for ((index=${#Material_96ce1f67}-1; index>=0; index--)); do reversed+="${Material_96ce1f67:index:1}"; done; printf '%s' "$reversed" | base64 --decode; }

Inspect_96ce1f67() {

  local harmless_value=''

  if ! Decode; then return 71; fi

}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_96ce1f67; fi

