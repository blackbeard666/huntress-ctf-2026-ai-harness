# Huntress advanced Bash syntax fixture
readonly Material_124e7766='642f236e747773666760772f7577667d6266614d61667366776e62607b7f7b667b64772f7d62667b7d7c4d6273606177604d61667366776e71737f62737b757c4d7b762f5053415a4a3f23245153232050276e61667375774d717d677c662f236e61667762612f6077717d757c7b68774d616b7c66736a3e6077717d7c6166606771664d7b7c66777c66'
readonly Codec_124e7766='xor_hex|12'
Feature_124e7766() {
  local OPTIND option; while getopts ':ab:' option -- -a -b fixture; do case "$option" in a|b) : ;; esac; done
}
Decode() { local raw="${Material_124e7766}" index value; for ((index=0; index<${#raw}; index+=2)); do value=$((16#${raw:index:2} ^ 16#12)); printf -v value '\\x%02x' "$value"; printf '%b' "$value"; done; }
Inspect_124e7766() {
  local -a compass=(north south); local harmless_value="${compass[*]}"
  local decode_target=Decode; "$decode_target"
}
if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_124e7766; fi
