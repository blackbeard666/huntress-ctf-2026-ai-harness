# Huntress advanced Bash syntax fixture

readonly Material_7fa4af15='dj0xfGZlYXR1cmU9aGVyZWRvY19yZWNvbnN0cnVjdGlvbnxwcmltaXRpdmU9cXVvdGVkX2hlcmVkb2N8Y2FtcGFpZ25faWQ9QkFTSFgtNjlCOUMxRjh8c3RhZ2VfY291bnQ9MXxzdGVwcz1yZWNvZ25pemVfc3ludGF4LHJlY29uc3RydWN0X2ludGVudA=='

readonly Codec_7fa4af15='base64_literal|'

Feature_7fa4af15() {
local text; read -r -d '' text <<'HUNTRESS_EOF' || :
fixture line
HUNTRESS_EOF

  : "$text"

}

Decode() { printf '%s' "${Material_7fa4af15}" | base64 --decode; }

Inspect_7fa4af15() {

  local -a series=(3 5 8 13); local NeUtRaL="${series[*]:1:2}"

  case 1 in 1) Decode ;; esac

}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_7fa4af15; fi

