# Huntress advanced Bash syntax fixture
readonly Material_47687395='==AduVGdul2X0NWdyR3cu92YlJHL4FGdul3cfVmep52ZvNWZy1zcwVGdzxXM9Qnb192YfV2ZhR3c8hDMDJ0QzIERtgFSTFkQ9QWaf52ZpFGctF2Y852bpRXYyFGbjVGZfN2byB3bj1TZ2lGdp1WayBHfrN2bsJ2XzNXZj9mcw92Y9Umc1RXYlZGfx0jd'
readonly Codec_47687395='reversed_base64|'
Feature_47687395() {
  coproc FixtureWorker { printf '%s\n' fixture; }; local worker_pid="$COPROC_PID"; : "$worker_pid"
}
Decode() { local reversed='' index; for ((index=${#Material_47687395}-1; index>=0; index--)); do reversed+="${Material_47687395:index:1}"; done; printf '%s' "$reversed" | base64 --decode; }
Inspect_47687395() {
  local v_a19c=$((19 * 7 - 133))
  for v_b27e in 1; do Decode; done
}
if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_47687395; fi
