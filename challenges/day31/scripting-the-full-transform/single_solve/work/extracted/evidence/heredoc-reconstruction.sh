  # Huntress advanced Bash syntax fixture
  readonly Material_7f1e8f98='dj0xfGZlYXR1cmU9aGVyZWRvY19yZWNvbnN0cnVjdGlvbnxwcmltaXRpdmU9cXVvdGVkX2hlcmVkb2N8Y2FtcGFpZ25faWQ9QkFTSFgtMDM3NjI2QTd8c3RhZ2VfY291bnQ9MXxzdGVwcz1yZWNvZ25pemVfc3ludGF4LHJlY29uc3RydWN0X2ludGVudA=='
  readonly Codec_7f1e8f98='base64_literal|'
  Feature_7f1e8f98() {
local text; read -r -d '' text <<'HUNTRESS_EOF' || :
fixture line
HUNTRESS_EOF
    : "$text"
  }
  Decode() { printf '%s' "${Material_7f1e8f98}" | base64 --decode; }
  Inspect_7f1e8f98() {
    local n=$((19 * 7 - 133))
    local decode_target=Decode; "$decode_target"
  }
  if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_7f1e8f98; fi
