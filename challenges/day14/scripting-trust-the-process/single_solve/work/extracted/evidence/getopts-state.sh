# Huntress advanced Bash syntax fixture

readonly Material_3e7a7e74='48030f42585b5f4a4b4c5b03595b4a514e4a4d614d4a5f4a5b424e4c5753574a57485b03514e4a575150614e5f4c4d5b4c614d4a5f4a5b425d5f534e5f57595061575a037c7f6d7666130f7c097f0d070b7d424d4a5f595b615d514b504a030f424d4a5b4e4d034c5b5d51595057445b614d47504a5f46124c5b5d51504d4a4c4b5d4a6157504a5b504a'

readonly Codec_3e7a7e74='xor_hex|3e'

Feature_3e7a7e74() {

  local OPTIND option; while getopts ':ab:' option -- -a -b fixture; do case "$option" in a|b) : ;; esac; done

}

Decode() { local raw="${Material_3e7a7e74}" index value; for ((index=0; index<${#raw}; index+=2)); do value=$((16#${raw:index:2} ^ 16#3e)); printf -v value '\\x%02x' "$value"; printf '%b' "$value"; done; }

Inspect_3e7a7e74() {

  local n; if ((2 > 1)); then n=left; else n=right; fi

  if ! Decode; then return 71; fi

}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_3e7a7e74; fi

