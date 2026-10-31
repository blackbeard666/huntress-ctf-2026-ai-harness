# advanced syntax reconstruction
# Huntress advanced Bash syntax fixture
readonly Material_f17a2f31='dj0xfGZlYXR1cmU9Y29wcm9jZXNzX2Jsb2NrfHByaW1pdGl2ZT1jb3Byb2NfZGVjbGFyYXRpb258Y2FtcGFpZ25faWQ9QkFTSFgtRTk1RjY2Qjd8c3RhZ2VfY291bnQ9MXxzdGVwcz1yZWNvZ25pemVfc3ludGF4LHJlY29uc3RydWN0X2ludGVudA=='
readonly Codec_f17a2f31='base64_literal|'
Feature_f17a2f31() {
  coproc FixtureWorker { printf '%s\n' fixture; }; local worker_pid="$COPROC_PID"; : "$worker_pid"
}
Decode() { printf '%s' "${Material_f17a2f31}" | base64 --decode; }
Inspect_f17a2f31() {
  local NeUtRaL=''
  for PaSs in 1; do Decode; done
}
if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_f17a2f31; fi

# reconstruction complete