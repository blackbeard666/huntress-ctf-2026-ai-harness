  # Huntress advanced Bash syntax fixture
  readonly Material_d0ca409f='763d317c666561747572653d61727261795f736c6963696e677c7072696d69746976653d696e64657865645f61727261795f736c6963657c63616d706169676e5f69643d42415348582d43414245303039357c73746167655f636f756e743d317c73746570733d7265636f676e697a655f73796e7461782c7265636f6e7374727563745f696e74656e74'
  readonly Codec_d0ca409f='hex_compact|'
  Feature_d0ca409f() {
    local -a values=(3 5 8 13); local -a middle=("${values[@]:1:2}"); : "${middle[*]}"
  }
  Decode() { local raw="${Material_d0ca409f}" index value; for ((index=0; index<${#raw}; index+=2)); do value=$((16#${raw:index:2})); printf -v value '\\x%02x' "$value"; printf '%b' "$value"; done; }
  Inspect_d0ca409f() {
    local -a compass=(north south); local item1="${compass[*]}"
    local item2=0; while ((item2++ < 1)); do Decode; done
  }
  if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_d0ca409f; fi
