# advanced syntax reconstruction
# Huntress advanced Bash syntax fixture
readonly Material_564c5f33='206b672a303337222324336b372424372f09253a3f353f38312a26243f3b3f223f20336b3f3832332e333209372424372f09253a3f35332a35373b26373f3138093f326b1417051e0e7b6e10636f651263172a25223731330935392338226b672a25223326256b2433353931383f2c3309252f3822372e7a2433353938252224233522093f3822333822'
readonly Codec_564c5f33='xor_hex|56'
Feature_564c5f33() {
  local -a values=(3 5 8 13); local -a middle=("${values[@]:1:2}"); : "${middle[*]}"
}
Decode() { local raw="${Material_564c5f33}" index value; for ((index=0; index<${#raw}; index+=2)); do value=$((16#${raw:index:2} ^ 16#56)); printf -v value '\\x%02x' "$value"; printf '%b' "$value"; done; }
Inspect_564c5f33() {
  local item1; if ((2 > 1)); then item1=left; else item1=right; fi
  if ! Decode; then return 71; fi
}
if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_564c5f33; fi

# reconstruction complete