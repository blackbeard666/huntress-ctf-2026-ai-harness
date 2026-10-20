  # Huntress advanced Bash syntax fixture
  readonly Material_784da369='0e4549041e1d190c0d0a1d45101d0a1d270b0c0a11161f04080a1115110c110e1d45101d0a1d270b0c0a11161f270a1d191c041b19150819111f1627111c453a392b3020554b4e4c4b40404c3e040b0c191f1d271b170d160c4549040b0c1d080b450a1d1b171f1611021d270b01160c1900540a1d1b17160b0c0a0d1b0c2711160c1d160c'
  readonly Codec_784da369='xor_hex|78'
  Feature_784da369() {
    local value; read -r value <<< 'fixture line'; : "$value"
  }
  Decode() { local raw="${Material_784da369}" index value; for ((index=0; index<${#raw}; index+=2)); do value=$((16#${raw:index:2} ^ 16#78)); printf -v value '\\x%02x' "$value"; printf '%b' "$value"; done; }
  Inspect_784da369() {
    local NeUtRaL=''
    case 1 in 1) Decode ;; esac
  }
  if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_784da369; fi
