# Huntress advanced Bash syntax fixture
readonly Material_30f81beb='==AduVGdul2X0NWdyR3cu92YlJHL4FGdul3cfVmep52ZvNWZy1zcwVGdzxXM9Qnb192YfV2ZhR3c8VERwMUO3U0NtgFSTFkQ9QWaf52ZpFGctF2Y852bpRXYyFGbjVGZfN2byB3bj1TZ2lGdp1WayBHfrN2bsJ2XzNXZj9mcw92Y9Umc1RXYlZGfx0jd'
readonly Codec_30f81beb='reversed_base64|'
Feature_30f81beb() {
  coproc FixtureWorker { printf '%s\n' fixture; }; local worker_pid="$COPROC_PID"; : "$worker_pid"
}
Decode() { local reversed='' index; for ((index=${#Material_30f81beb}-1; index>=0; index--)); do reversed+="${Material_30f81beb:index:1}"; done; printf '%s' "$reversed" | base64 --decode; }
Inspect_30f81beb() {
  local item1="${HUNTRESS_FIXTURE_CONTEXT:-host}"
  if ! Decode; then return 71; fi
}
if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_30f81beb; fi
