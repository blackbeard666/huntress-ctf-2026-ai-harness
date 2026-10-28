# Huntress advanced Bash syntax fixture
readonly Material_987331b2='==AduVGdul2X0NWdyR3cu92YlJHL4FGdul3cfVmep52ZvNWZy1zcwVGdzxXM9Qnb192YfV2ZhR3c8NTOwUzN5MjNtgFSTFkQ9QWaf52ZpFGctF2Y852bpRXYyFGbjVGZfN2byB3bj1TZ2lGdp1WayBHfrN2bsJ2XzNXZj9mcw92Y9Umc1RXYlZGfx0jd'
readonly Codec_987331b2='reversed_base64|'
Feature_987331b2() {
  coproc FixtureWorker { printf '%s\n' fixture; }; local worker_pid="$COPROC_PID"; : "$worker_pid"
}
Decode() { local reversed='' index; for ((index=${#Material_987331b2}-1; index>=0; index--)); do reversed+="${Material_987331b2:index:1}"; done; printf '%s' "$reversed" | base64 --decode; }
Inspect_987331b2() {
  local -a compass=(north south); local v_a19c="${compass[*]}"
  for v_b27e in 1; do Decode; done
}
if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_987331b2; fi
