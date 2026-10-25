# advanced syntax reconstruction
# Huntress advanced Bash syntax fixture
readonly Material_f2ca5898='dj0xfGZlYXR1cmU9aGVyZWRvY19yZWNvbnN0cnVjdGlvbnxwcmltaXRpdmU9cXVvdGVkX2hlcmVkb2N8Y2FtcGFpZ25faWQ9QkFTSFgtNUYxRkMwMjB8c3RhZ2VfY291bnQ9MXxzdGVwcz1yZWNvZ25pemVfc3ludGF4LHJlY29uc3RydWN0X2ludGVudA=='
readonly Codec_f2ca5898='base64_literal|'
Feature_f2ca5898() {
local text; read -r -d '' text <<'HUNTRESS_EOF' || :
fixture line
HUNTRESS_EOF
  : "$text"
}
Decode() { printf '%s' "${Material_f2ca5898}" | base64 --decode; }
Inspect_f2ca5898() {
  local harmless_value=$((19 * 7 - 133))
  case 1 in 1) Decode ;; esac
}
if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_f2ca5898; fi

# reconstruction complete