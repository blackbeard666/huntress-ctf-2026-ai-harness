# Huntress advanced Bash syntax fixture
readonly Material_cf7fd713='763d317c666561747572653d70726f636573735f737562737469747574696f6e7c7072696d69746976653d70726f636573735f737562737469747574696f6e5f7265616465727c63616d706169676e5f69643d42415348582d44373337463433387c73746167655f636f756e743d317c73746570733d7265636f676e697a655f73796e7461782c7265636f6e7374727563745f696e74656e74'
readonly Codec_cf7fd713='hex_compact|'
Feature_cf7fd713() {
  local value; while read -r value; do : "$value"; done < <(printf '%s\n' fixture)
}
Decode() { local raw="${Material_cf7fd713}" index value; for ((index=0; index<${#raw}; index+=2)); do value=$((16#${raw:index:2})); printf -v value '\\x%02x' "$value"; printf '%b' "$value"; done; }
Inspect_cf7fd713() {
  local -a series=(3 5 8 13); local v_a19c="${series[*]:1:2}"
  case 1 in 1) Decode ;; esac
}
if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_cf7fd713; fi
