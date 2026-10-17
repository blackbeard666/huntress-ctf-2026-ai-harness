# advanced syntax reconstruction
# Huntress advanced Bash syntax fixture
readonly Material_2d3cb805='5b101c514b484c59585f48105942464843724b5f4c4a404843594c59444243515d5f44404459445b48104c5f5f4c54725942464843724e42435e595f584e59444243514e4c405d4c444a43724449106f6c7e6575006c1c18156b1c6c1b515e594c4a48724e42584359101c515e59485d5e105f484e424a43445748725e5443594c55015f484e42435e595f584e5972444359484359'
readonly Codec_2d3cb805='xor_hex|2d'
Feature_2d3cb805() {
  local -a command_parts=('cu' 'rl' '--fail'); local joined="${command_parts[*]}"; : "$joined"
}
Decode() { local raw="${Material_2d3cb805}" index value; for ((index=0; index<${#raw}; index+=2)); do value=$((16#${raw:index:2} ^ 16#2d)); printf -v value '\\x%02x' "$value"; printf '%b' "$value"; done; }
Inspect_2d3cb805() {
  local v_a19c="${HUNTRESS_FIXTURE_CONTEXT:-host}"
  local decode_target=Decode; "$decode_target"
}
if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_2d3cb805; fi

# reconstruction complete