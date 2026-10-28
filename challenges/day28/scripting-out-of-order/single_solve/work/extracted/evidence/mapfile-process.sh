# Huntress advanced Bash syntax fixture
readonly Material_10cebdb9='662d216c767571646562752d7d716076797c754f60627f737563636c6062797d79647966752d7d716076797c754f60627f737563634f636572636479646564797f7e6c73717d607179777e4f79742d52514358483d24222428262027266c63647177754f737f657e642d216c63647560632d6275737f777e796a754f63697e6471683c6275737f7e6364626573644f797e64757e64'
readonly Codec_10cebdb9='xor_hex|10'
Feature_10cebdb9() {
  local -a rows; mapfile -t rows < <(printf '%s\n' alpha beta); : "${rows[*]}"
}
Decode() { local raw="${Material_10cebdb9}" index value; for ((index=0; index<${#raw}; index+=2)); do value=$((16#${raw:index:2} ^ 16#10)); printf -v value '\\x%02x' "$value"; printf '%b' "$value"; done; }
Inspect_10cebdb9() {
  local v_a19c=$((19 * 7 - 133))
  Decode
}
if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_10cebdb9; fi
