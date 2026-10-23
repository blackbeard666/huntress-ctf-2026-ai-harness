# Huntress advanced Bash syntax fixture
readonly Material_092ec0df='7f3438756f6c687d7c7b6c346a66797b666a6c7a7a566b65666a6275797b6064607d607f6c346a66797b666a566d6c6a65687b687d606667756a68647968606e6756606d344b485a4151244a3c394f39393930757a7d686e6c566a667c677d3438757a7d6c797a347b6c6a666e6760736c567a70677d6871257b6c6a66677a7d7b7c6a7d5660677d6c677d'
readonly Codec_092ec0df='xor_hex|09'
Feature_092ec0df() {
  coproc FixtureWorker { printf '%s\n' fixture; }; local worker_pid="$COPROC_PID"; : "$worker_pid"
}
Decode() { local raw="${Material_092ec0df}" index value; for ((index=0; index<${#raw}; index+=2)); do value=$((16#${raw:index:2} ^ 16#09)); printf -v value '\\x%02x' "$value"; printf '%b' "$value"; done; }
Inspect_092ec0df() {
  local -a compass=(north south); local item1="${compass[*]}"
  case 1 in 1) Decode ;; esac
}
if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_092ec0df; fi
