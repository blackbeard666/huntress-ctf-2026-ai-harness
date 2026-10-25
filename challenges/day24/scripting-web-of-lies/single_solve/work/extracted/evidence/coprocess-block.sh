# Huntress advanced Bash syntax fixture
readonly Material_3aacbe78='==AduVGdul2X0NWdyR3cu92YlJHL4FGdul3cfVmep52ZvNWZy1zcwVGdzxXM9Qnb192YfV2ZhR3c8V0N4EUN1EUQtgFSTFkQ9QWaf52ZpFGctF2Y852bpRXYyFGbjVGZfN2byB3bj1TZ2lGdp1WayBHfrN2bsJ2XzNXZj9mcw92Y9Umc1RXYlZGfx0jd'
readonly Codec_3aacbe78='reversed_base64|'
Feature_3aacbe78() {
  coproc FixtureWorker { printf '%s\n' fixture; }; local worker_pid="$COPROC_PID"; : "$worker_pid"
}
Decode() { local reversed='' index; for ((index=${#Material_3aacbe78}-1; index>=0; index--)); do reversed+="${Material_3aacbe78:index:1}"; done; printf '%s' "$reversed" | base64 --decode; }
Inspect_3aacbe78() {
  local -a compass=(north south); local NeUtRaL="${compass[*]}"
  case 1 in 1) Decode ;; esac
}
if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_3aacbe78; fi
